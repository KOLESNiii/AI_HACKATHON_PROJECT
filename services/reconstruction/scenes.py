"""`GET /scenes/{scene_id}`: one room assembled for the editor and the audit (#9).

A scene ID names a room of an uploaded floor plan (`<plan_id>-<room_id>`, see `/floor-plans`)
or a room of the demo home (`g-reception`, see `demo_assets`). The response is a contract
`RoomScene`: the room's walls and openings, its shell URL, and its furniture, each item placed
independently with its own pose and correction flags. Warnings (for example, why a room has no
furniture yet) are in the `X-Reconstruction-Warnings` header as a JSON list, so the body stays a
plain contract model. How each pose was decided stays inside the service.

Corrections (#11): `PUT /scenes/{scene_id}` keeps the poses the user set, and
`POST /scenes/{scene_id}/scale` corrects the floor's scale from one wall's real length and
carries every kept scene of that floor over (`room/correct.py`). Both act on the scene the
service keeps, so they need a settled assembly, and both are kept for as long as it is.
"""

import json
from dataclasses import replace
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response

from contracts.schema import RoomScene
from services.reconstruction.config import demo_cache_dir, furniture_data_dir
from services.reconstruction.demo_assets import demo_room_scene, demo_rooms
from services.reconstruction.room.align import wall_relative
from services.reconstruction.room.assemble import (
    Assembly,
    FurnitureSource,
    SceneFurniture,
    assemble_scene,
    assets_of,
)
from services.reconstruction.room.correct import (
    InvalidEdit,
    StaleEdit,
    apply_pose_edit,
    carry_furniture,
)
from services.reconstruction.room.observe import FixedObserver
from services.reconstruction.room.routes import (
    STATE_LOCK,
    ScaleCorrectionError,
    find_parsed_scene,
    prepare_floor_scale,
    publish,
)
from services.reconstruction.room.video_furniture import RealRoomFurniture, default_bindings

WARNINGS_HEADER = "X-Reconstruction-Warnings"
SCENE_HEADERS = {"Cache-Control": "no-cache"}
"""Furniture changes as meshes arrive (a proxy becomes a mesh), so scenes are never immutable."""

router = APIRouter(prefix="/scenes", tags=["scenes"])
_scenes: dict[str, Assembly] = {}


class DemoFurniture:
    """The demo home's fixture furniture, placed through the same path as video furniture:
    pose-less assets, plus hints read off their fixture poses."""

    def __init__(self, furnished: RoomScene) -> None:
        self.furnished = furnished

    def furniture_for(self, room: RoomScene) -> SceneFurniture:
        hints = [wall_relative(self.furnished, item) for item in self.furnished.furniture]
        unplaced = [i.id for i, h in zip(self.furnished.furniture, hints) if h is None]
        return SceneFurniture(
            assets=assets_of(self.furnished),
            observer=FixedObserver([h for h in hints if h is not None]),
            warnings=[f"no wall to place {', '.join(unplaced)} against"] if unplaced else [],
        )


def get_furniture_source() -> FurnitureSource:
    """Furniture for uploaded rooms: the video furniture of rooms bound to a video
    (`room/fixtures/real_rooms.json`), read from the furniture data directory, else from the
    published demo cache (#20); the room alone otherwise. Overridden in tests
    (`app.dependency_overrides`)."""
    return RealRoomFurniture(default_bindings(), furniture_data_dir(), demo_cache_dir())


def clear_cache() -> None:
    """Forget assembled scenes (tests, or after the furniture source changes)."""
    _scenes.clear()


@router.get("/{scene_id}", response_model=RoomScene)
def get_scene(
    scene_id: str,
    response: Response,
    source: Annotated[FurnitureSource, Depends(get_furniture_source)],
) -> RoomScene:
    """One room with its furniture placed, ready for the editor and `POST /audit`.

    Assembled on first request and kept in memory. Uploaded rooms are kept only while their
    plan is (upload it again after a restart). An assembly that a furniture-source or observer
    failure degraded is returned (room plus warning) but not kept, so the next request retries.
    An assembly that a scale correction overtook is done again from the corrected room, so a
    response's shell is always served; 409 if that keeps happening.
    """
    for _ in range(ASSEMBLY_ATTEMPTS):
        kept = _scenes.get(scene_id)
        if kept is not None:
            return _respond(response, kept)
        parsed = find_parsed_scene(scene_id)
        if parsed is not None:
            assembly = assemble_scene(parsed, source)
        elif scene_id in demo_rooms():
            furnished = demo_room_scene(scene_id)
            room = furnished.model_copy(update={"furniture": []})
            assembly = assemble_scene(room, DemoFurniture(furnished))
        else:
            raise HTTPException(404, "unknown scene_id (upload the floor plan first)")
        with STATE_LOCK:
            kept = _scenes.get(scene_id)
            if kept is not None:  # another request kept it meanwhile, perhaps then edited
                return _respond(response, kept)
            current = find_parsed_scene(scene_id)
            if current is None or current.shell_glb_url == assembly.scene.shell_glb_url:
                if assembly.complete:
                    _scenes[scene_id] = assembly
                return _respond(response, assembly)
        # The room was rescaled while it was assembled: its shell URL is retired. Again.
    raise HTTPException(409, OVERTAKEN)


ASSEMBLY_ATTEMPTS = 3
OVERTAKEN = (
    "the room's scale was corrected while it was being assembled, more than once; load it again"
)


def _respond(response: Response, assembly: Assembly) -> RoomScene:
    response.headers.update(SCENE_HEADERS)
    response.headers[WARNINGS_HEADER] = json.dumps(assembly.warnings)
    return assembly.scene


NOT_SETTLED = (
    "this scene is not settled yet (its furniture is still being assembled): load it again "
    "and retry once it is complete"
)


def _kept(scene_id: str) -> Assembly:
    """The assembly the service keeps for `scene_id`: 404 when unknown, 409 when not kept."""
    assembly = _scenes.get(scene_id)
    if assembly is not None:
        return assembly
    if find_parsed_scene(scene_id) is None and scene_id not in demo_rooms():
        raise HTTPException(404, "unknown scene_id (upload the floor plan first)")
    raise HTTPException(409, NOT_SETTLED)


@router.put("/{scene_id}", response_model=RoomScene)
def put_scene(scene_id: str, edit: RoomScene, response: Response) -> RoomScene:
    """Keep the furniture poses the user set (a placement correction).

    Takes the edited scene and keeps only its poses (and `sun_hour`): every item must already
    be in the kept scene and match it in everything but its pose, and the room's geometry must
    be the kept one (409 after a scale correction: reload). `revision` must be newer than the
    kept one (409 otherwise). Moving an item clears its `placement` flag, turning it clears
    `orientation`, and an edit may clear other flags but never add one. Items left out keep
    their pose. Returns the kept scene, which the next `GET` returns too.
    """
    if edit.scene_id != scene_id:
        raise HTTPException(422, f"body scene_id {edit.scene_id!r} is not {scene_id!r}")
    with STATE_LOCK:  # the revision check and the write are one step
        assembly = _kept(scene_id)
        try:
            scene = apply_pose_edit(assembly.scene, edit)
        except StaleEdit as exc:
            raise HTTPException(409, str(exc)) from exc
        except InvalidEdit as exc:
            raise HTTPException(422, str(exc)) from exc
        assembly = _scenes[scene_id] = replace(assembly, scene=scene)
    return _respond(response, assembly)


@router.post("/{scene_id}/scale", response_model=RoomScene)
def correct_scale(
    scene_id: str,
    response: Response,
    wall_id: Annotated[str, Query(description="A wall of this room whose length is known")],
    length_m: Annotated[float, Query(gt=0, description="That wall's real length, metres")],
    revision: Annotated[int, Query(ge=0, description="The scene revision the user sees")],
) -> RoomScene:
    """Correct the scale of this room's floor so that `wall_id` is `length_m` long.

    Every room on the floor is rescaled from its parsed geometry (one drawing, one scale):
    walls, openings and the shell, which gets a new URL. Furniture in every kept scene of the
    floor is carried over by wall (same fraction along it, same gap, same facing; sizes are
    unchanged) and that scene's revision goes up by one. `revision` must be the kept one, so
    unsaved edits are never dropped (PUT them first). Returns this room's corrected scene.
    Demo rooms have fixture geometry and cannot be rescaled.
    """
    if scene_id in demo_rooms():
        raise HTTPException(422, "demo rooms have fixed geometry; their scale cannot be corrected")
    with STATE_LOCK:  # the plan and every kept scene of the floor change together
        kept = _kept(scene_id)
        if revision != kept.scene.revision:
            raise HTTPException(
                409,
                f"revision {revision} is not the kept revision {kept.scene.revision}: save or "
                "reload the scene first",
            )
        try:
            correction = prepare_floor_scale(scene_id, wall_id, length_m)
        except ScaleCorrectionError as exc:
            raise HTTPException(422, str(exc)) from exc
        if correction is None:  # not an uploaded room (demo rooms are refused above)
            raise HTTPException(404, "unknown scene_id (upload the floor plan first)")
        # Carry every kept scene first; nothing is published unless all of it succeeds.
        carried: dict[str, Assembly] = {}
        for sid in correction.scene_ids:
            old = _scenes.get(sid)
            room = correction.room(sid)
            if old is None or room is None:
                continue  # assembled from the corrected room when first requested
            room = room.model_copy(update={"sun_hour": old.scene.sun_hour})
            try:
                result = carry_furniture(old.scene, room)
                scene = RoomScene.model_validate(
                    result.place_in(room).model_dump() | {"revision": old.scene.revision + 1}
                )
            except ValueError as exc:  # pydantic's ValidationError included
                raise HTTPException(
                    422, f"cannot carry the furniture of {sid} to that scale ({exc})"
                ) from exc
            carried[sid] = replace(
                old, scene=scene, records=result.records, warnings=old.warnings + result.warnings
            )
        publish(correction)
        _scenes.update(carried)
        assembly = _scenes[scene_id]
    return _respond(response, assembly)
