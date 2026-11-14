"""Serve shared demo meshes and generate room shells without frontend asset copies."""

from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse

from contracts.schema import RoomScene
from services.reconstruction.room.footprint import point_in_polygon
from services.reconstruction.room.shell import shell_glb

FIXTURE_ROOT = Path(__file__).resolve().parents[2] / "contracts" / "mock_room"
LEGACY_ROOT = Path(__file__).resolve().parent / "fixtures" / "mock_room"
FLOORS = ("ground", "first", "second")
BROWSER_ROOT = "/api/reconstruction/mock-room"
"""Where the browser reaches `router` (the Vite proxy strips `/api/reconstruction`)."""
GLB_MEDIA_TYPE = "model/gltf-binary"
# Demo IDs are stable names, not content hashes: never cache them as immutable.
DEMO_HEADERS = {"Cache-Control": "no-cache"}

router = APIRouter(prefix="/mock-room", tags=["demo assets"])
legacy_router = APIRouter(prefix="/mock_room", tags=["demo assets"])


def _model_file(directory: Path, filename: str) -> FileResponse:
    path = (directory / filename).resolve()
    if not filename.endswith(".glb") or path.parent != directory.resolve() or not path.is_file():
        raise HTTPException(404, "unknown demo model")
    return FileResponse(path, media_type=GLB_MEDIA_TYPE, headers=DEMO_HEADERS)


@router.get("/assets/{filename}", response_class=FileResponse)
def furniture_model(filename: str) -> FileResponse:
    """Read the canonical furniture fixture in place; do not copy it to the frontend."""
    return _model_file(FIXTURE_ROOT / "assets", filename)


@legacy_router.get("/{filename}", response_class=FileResponse)
def legacy_model(filename: str) -> FileResponse:
    """Keep mock_scene.json's original /mock_room paths usable through the API proxy."""
    return _model_file(LEGACY_ROOT, filename)


@lru_cache(maxsize=1)
def demo_floors() -> dict[str, RoomScene]:
    """The shared three-floor fixtures, one whole-floor scene per floor name."""
    return {
        floor: RoomScene.model_validate_json(
            (FIXTURE_ROOT / f"three_floor_{floor}_scene.json").read_text()
        )
        for floor in FLOORS
    }


@lru_cache(maxsize=1)
def demo_rooms() -> dict[str, RoomScene]:
    """Split the shared floor fixtures by wall prefix, in the original floor coordinates."""
    rooms: dict[str, RoomScene] = {}
    for scene in demo_floors().values():
        for room_id in dict.fromkeys(w.id.rsplit("-w", 1)[0] for w in scene.walls):
            walls = [w for w in scene.walls if w.id.rsplit("-w", 1)[0] == room_id]
            wall_ids = {w.id for w in walls}
            rooms[room_id] = scene.model_copy(
                update={
                    "scene_id": room_id,
                    "floor_polygon": [w.start for w in walls],
                    "walls": walls,
                    "windows": [w for w in scene.windows if w.wall_id in wall_ids],
                    "doors": [d for d in scene.doors if d.wall_id in wall_ids],
                    "furniture": [],
                }
            )
    return rooms


def demo_room_scene(room_id: str) -> RoomScene:
    """One demo room as the editor opens it (`roomScene` in `frontend/src/data/demoHome.ts`).

    The room from `demo_rooms`, plus the furniture of its floor whose pose stands inside its
    outline, with browser URLs for the served shell and furniture. Validated, so the outline's
    winding is checked. Raises KeyError for an unknown room.
    """
    room = demo_rooms()[room_id]
    floor = next(s for s in demo_floors().values() if room.walls[0] in s.walls)
    outline = [(p.x, p.z) for p in room.floor_polygon]
    furniture = [
        item.model_copy(
            update={"glb_url": BROWSER_ROOT + item.glb_url}
            if item.glb_url.startswith("/assets/")
            else {}
        )
        for item in floor.furniture
        if point_in_polygon((item.pose.x, item.pose.z), outline)
    ]
    return RoomScene.model_validate(
        {
            **room.model_dump(),
            "shell_glb_url": f"{BROWSER_ROOT}/shells/{room_id}.glb",
            "furniture": [item.model_dump() for item in furniture],
        }
    )


@lru_cache(maxsize=64)
def demo_shell(room_id: str) -> bytes:
    scene = demo_rooms().get(room_id)
    if scene is None:
        raise HTTPException(404, "unknown demo room")
    return shell_glb(scene)


@router.get("/shells/{room_id}.glb", response_class=Response)
def room_shell(room_id: str) -> Response:
    """Build once per room/process, using the reconstruction service's shell generator."""
    return Response(demo_shell(room_id), media_type=GLB_MEDIA_TYPE, headers=DEMO_HEADERS)
