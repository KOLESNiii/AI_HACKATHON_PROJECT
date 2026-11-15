"""Floor-plan routes. Parsed plans are cached in memory by `plan_id` (derived from the image
bytes), so re-uploading the same plan is free and rooms can be fetched one at a time.

A floor whose scale the user corrected (#11, `correct_floor_scale`) is served corrected: by
these routes, by re-upload and to `/scenes`. The original parse is kept beside it, so every
correction is made from the parse and correcting back restores it exactly.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile
from fastapi.concurrency import run_in_threadpool

from contracts.schema import MAX_FLOOR_PLAN_IMAGES, ParsedFloorPlan, RoomScene

from . import correct
from .annotate import FalVisionAnnotator, PlanAnnotator
from .parse import parse_floor_plan, plan_id_for
from .raster import UnreadableImage
from .shell import shell_glb

router = APIRouter(prefix="/floor-plans", tags=["floor plans"])

MAX_IMAGE_BYTES = 20 * 1024 * 1024
_plans: dict[str, ParsedFloorPlan] = {}
"""The plans as served: corrected where the user corrected a floor's scale."""
_originals: dict[str, ParsedFloorPlan] = {}
"""The plans as parsed."""


def get_annotator() -> PlanAnnotator:
    """Overridden in tests (`app.dependency_overrides`)."""
    return FalVisionAnnotator()


@router.post("", response_model=ParsedFloorPlan)
async def parse_plan(
    files: Annotated[list[UploadFile], File(description="Floor-plan images (PNG/JPEG)")],
    annotator: Annotated[PlanAnnotator, Depends(get_annotator)],
) -> ParsedFloorPlan:
    """Parse every floor and room on 1..MAX_FLOOR_PLAN_IMAGES floor-plan images."""
    if not 1 <= len(files) <= MAX_FLOOR_PLAN_IMAGES:
        raise HTTPException(422, f"upload 1 to {MAX_FLOOR_PLAN_IMAGES} floor-plan images")
    images: list[tuple[bytes, str]] = []
    for f in files:
        data = await f.read()
        if len(data) > MAX_IMAGE_BYTES:
            raise HTTPException(413, f"{f.filename} is larger than {MAX_IMAGE_BYTES} bytes")
        images.append((data, f.content_type or "image/png"))
    plan_id = plan_id_for([d for d, _ in images])
    if plan_id in _plans:
        return _plans[plan_id]
    try:
        plan = await run_in_threadpool(parse_floor_plan, images, annotator)
    except UnreadableImage as exc:
        raise HTTPException(422, str(exc)) from exc
    _plans[plan.plan_id] = _originals[plan.plan_id] = plan
    return plan


@router.get("/{plan_id}", response_model=ParsedFloorPlan)
def get_plan(plan_id: str) -> ParsedFloorPlan:
    plan = _plans.get(plan_id)
    if plan is None:
        raise HTTPException(404, "unknown plan_id (plans are kept in memory; upload again)")
    return plan


@router.get("/{plan_id}/rooms/{room_id}", response_model=RoomScene)
def get_room(plan_id: str, room_id: str) -> RoomScene:
    """One room as a `RoomScene`, ready to load into the editor."""
    plan = get_plan(plan_id)
    for floor in plan.floors:
        for room in floor.rooms:
            if room.room_id == room_id:
                return room.scene
    raise HTTPException(404, "unknown room_id")


# --- room shells ------------------------------------------------------------------------------

shell_router = APIRouter(prefix="/shells", tags=["room shells"])
_shells: dict[str, bytes] = {}
SHELL_CACHE_CONTROL = "public, max-age=31536000, immutable"


def find_parsed_scene(scene_id: str) -> RoomScene | None:
    """A room of an uploaded plan by its `scene_id`, or None (plans are kept in memory).
    Corrected when the user corrected its floor's scale."""
    for plan in _plans.values():
        for floor in plan.floors:
            for room in floor.rooms:
                if room.scene.scene_id == scene_id:
                    return room.scene
    return None


# --- scale correction (#11) -------------------------------------------------------------------


class ScaleCorrectionError(ValueError):
    """The correction names no such wall, or implies an implausible scale."""


@dataclass(frozen=True)
class ScaleCorrection:
    factor: float
    """Corrected size over parsed size, for the whole floor."""
    scene_ids: list[str]
    """Every room of the floor, all rescaled."""


CORRECTION_NOTE = "scale corrected by the user"


def correct_floor_scale(scene_id: str, wall_id: str, length_m: float) -> ScaleCorrection | None:
    """Rescale the floor of `scene_id` so that its wall `wall_id` is `length_m` long.

    The factor is taken against the original parse, so corrections never compound. Every room
    on the floor is rescaled (one drawing, one scale, one frame), and the plan's warnings say
    so, replacing an earlier correction note for that floor. None for an unknown scene; raises
    `ScaleCorrectionError` for an unknown wall or a factor outside
    [`correct.MIN_FACTOR`, `correct.MAX_FACTOR`].
    """
    for plan_id, original in _originals.items():
        for f, floor in enumerate(original.floors):
            room = next((r for r in floor.rooms if r.scene.scene_id == scene_id), None)
            if room is None:
                continue
            wall = next((w for w in room.scene.walls if w.id == wall_id), None)
            if wall is None:
                raise ScaleCorrectionError(f"{room.name} has no wall {wall_id!r}")
            parsed_m = math.dist((wall.start.x, wall.start.z), (wall.end.x, wall.end.z))
            factor = length_m / parsed_m
            if not correct.MIN_FACTOR <= factor <= correct.MAX_FACTOR:
                raise ScaleCorrectionError(
                    f"{wall_id} was parsed as {parsed_m:.2f} m; {length_m} m would scale the "
                    f"floor by {factor:.2f}, which is not a scale error (check the wall)"
                )
            served = _plans[plan_id]
            floors = list(served.floors)
            floors[f] = correct.rescale_floor(floor, factor)
            prefix = f"{floor.name}: {CORRECTION_NOTE}"
            warnings = [w for w in served.warnings if not w.startswith(prefix)]
            warnings.append(f"{prefix} ({room.name} {wall_id} = {length_m:.2f} m, x{factor:.3f})")
            _plans[plan_id] = served.model_copy(update={"floors": floors, "warnings": warnings})
            return ScaleCorrection(factor, [r.scene.scene_id for r in floor.rooms])
    return None


def clear_corrections() -> None:
    """Serve every plan as parsed again (tests)."""
    _plans.update(_originals)


@shell_router.get(
    "/{name}.glb",
    response_class=Response,
    responses={200: {"content": {"model/gltf-binary": {}}}},
)
async def get_shell(name: str) -> Response:
    """The room shell `.glb` named by `RoomScene.shell_glb_url` (contracts/schema.py: room
    coordinates, nodes `floor`, `ceiling`, `wall_<id>`): `<scene_id>.glb` as parsed,
    `<scene_id>.<digest>.glb` after a scale correction. Immutable: a scene ID comes from the
    plan's image bytes, the digest from the corrected geometry, and the shell is generated
    deterministically from the scene."""
    scene = find_parsed_scene(name.split(".", 1)[0])
    if scene is None:
        raise HTTPException(404, "unknown scene_id (plans are kept in memory; upload again)")
    if not scene.shell_glb_url.endswith(f"/{name}.glb"):
        raise HTTPException(404, "superseded by a scale correction; reload the scene")
    data = _shells.get(name)
    if data is None:
        try:
            data = await run_in_threadpool(shell_glb, scene)
        except ValueError as exc:
            raise HTTPException(422, f"cannot build a shell for this room: {exc}") from exc
        _shells[name] = data
    return Response(
        content=data,
        media_type="model/gltf-binary",
        headers={"Cache-Control": SHELL_CACHE_CONTROL},
    )
