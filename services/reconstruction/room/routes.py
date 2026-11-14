"""Floor-plan routes. Parsed plans are cached in memory by `plan_id` (derived from the image
bytes), so re-uploading the same plan is free and rooms can be fetched one at a time."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile
from fastapi.concurrency import run_in_threadpool

from contracts.schema import MAX_FLOOR_PLAN_IMAGES, ParsedFloorPlan, RoomScene

from .annotate import FalVisionAnnotator, PlanAnnotator
from .parse import parse_floor_plan, plan_id_for
from .raster import UnreadableImage
from .shell import shell_glb

router = APIRouter(prefix="/floor-plans", tags=["floor plans"])

MAX_IMAGE_BYTES = 20 * 1024 * 1024
_plans: dict[str, ParsedFloorPlan] = {}


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
    _plans[plan.plan_id] = plan
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
    """A room of an uploaded plan by its `scene_id`, or None (plans are kept in memory)."""
    for plan in _plans.values():
        for floor in plan.floors:
            for room in floor.rooms:
                if room.scene.scene_id == scene_id:
                    return room.scene
    return None


@shell_router.get(
    "/{scene_id}.glb",
    response_class=Response,
    responses={200: {"content": {"model/gltf-binary": {}}}},
)
async def get_shell(scene_id: str) -> Response:
    """The room shell `.glb` named by `RoomScene.shell_glb_url` (contracts/schema.py: room
    coordinates, nodes `floor`, `ceiling`, `wall_<id>`). Immutable: a scene ID comes from the
    plan's image bytes and the shell is generated deterministically from the scene."""
    data = _shells.get(scene_id)
    if data is None:
        scene = find_parsed_scene(scene_id)
        if scene is None:
            raise HTTPException(404, "unknown scene_id (plans are kept in memory; upload again)")
        try:
            data = await run_in_threadpool(shell_glb, scene)
        except ValueError as exc:
            raise HTTPException(422, f"cannot build a shell for this room: {exc}") from exc
        _shells[scene_id] = data
    return Response(
        content=data,
        media_type="model/gltf-binary",
        headers={"Cache-Control": SHELL_CACHE_CONTROL},
    )
