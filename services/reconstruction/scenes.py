"""`GET /scenes/{scene_id}`: one room assembled for the editor and the audit (#9).

A scene ID names a room of an uploaded floor plan (`<plan_id>-<room_id>`, see `/floor-plans`)
or a room of the demo home (`g-reception`, see `demo_assets`). The response is a contract
`RoomScene`: the room's walls and openings, its shell URL, and its furniture, each item placed
independently with its own pose and correction flags. Warnings (for example, why a room has no
furniture yet) are in the `X-Reconstruction-Warnings` header as a JSON list, so the body stays a
plain contract model. How each pose was decided stays inside the service.
"""

import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response

from contracts.schema import RoomScene
from services.reconstruction.config import furniture_data_dir
from services.reconstruction.demo_assets import demo_room_scene, demo_rooms
from services.reconstruction.room.align import wall_relative
from services.reconstruction.room.assemble import (
    Assembly,
    FurnitureSource,
    SceneFurniture,
    assemble_scene,
    assets_of,
)
from services.reconstruction.room.observe import FixedObserver
from services.reconstruction.room.routes import find_parsed_scene
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
    (`room/fixtures/real_rooms.json`), read from the furniture data directory; the room alone
    otherwise. Overridden in tests (`app.dependency_overrides`)."""
    return RealRoomFurniture(default_bindings(), furniture_data_dir())


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
    """
    assembly = _scenes.get(scene_id)
    if assembly is None:
        parsed = find_parsed_scene(scene_id)
        if parsed is not None:
            assembly = assemble_scene(parsed, source)
        elif scene_id in demo_rooms():
            furnished = demo_room_scene(scene_id)
            room = furnished.model_copy(update={"furniture": []})
            assembly = assemble_scene(room, DemoFurniture(furnished))
        else:
            raise HTTPException(404, "unknown scene_id (upload the floor plan first)")
        if assembly.complete:
            _scenes[scene_id] = assembly
    response.headers.update(SCENE_HEADERS)
    response.headers[WARNINGS_HEADER] = json.dumps(assembly.warnings)
    return assembly.scene
