"""Serve shared demo meshes and generate room shells without frontend asset copies."""

from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse

from contracts.schema import RoomScene
from services.reconstruction.room.shell import shell_glb

FIXTURE_ROOT = Path(__file__).resolve().parents[2] / "contracts" / "mock_room"
LEGACY_ROOT = Path(__file__).resolve().parent / "fixtures" / "mock_room"
FLOORS = ("ground", "first", "second")
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
def demo_rooms() -> dict[str, RoomScene]:
    """Split the shared floor fixtures by wall prefix, in the original floor coordinates."""
    rooms: dict[str, RoomScene] = {}
    for floor in FLOORS:
        scene = RoomScene.model_validate_json(
            (FIXTURE_ROOT / f"three_floor_{floor}_scene.json").read_text()
        )
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
