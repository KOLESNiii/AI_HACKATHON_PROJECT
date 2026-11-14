"""Demo GLBs are backend-provided; the browser needs no copied asset directory."""

from io import BytesIO
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from services.reconstruction import demo_assets
from services.reconstruction.main import app

ROOT = Path(__file__).resolve().parents[1]
client = TestClient(app)


def test_canonical_furniture_is_served_without_copying() -> None:
    asset = next((demo_assets.FIXTURE_ROOT / "assets").glob("*.glb"))
    response = client.get(f"/mock-room/assets/{asset.name}")
    assert response.status_code == 200
    assert response.headers["content-type"] == "model/gltf-binary"
    assert response.headers["cache-control"] == "no-cache"
    assert response.content == asset.read_bytes()
    assert not (ROOT / "frontend/public/mock_room").exists()


def test_all_home_furniture_urls_have_canonical_models() -> None:
    from contracts.schema import RoomScene

    for floor in demo_assets.FLOORS:
        scene = RoomScene.model_validate_json(
            (demo_assets.FIXTURE_ROOT / f"three_floor_{floor}_scene.json").read_text()
        )
        for item in scene.furniture:
            response = client.get(f"/mock-room{item.glb_url}")
            assert response.status_code == 200, item.glb_url
            assert response.content[:4] == b"glTF"


@pytest.mark.parametrize(
    "name",
    ["bed", "wardrobe", "shell", "vid-chair-01", "vid-desk-01", "vid-table-01", "fix-radiator-01"],
)
def test_legacy_models_live_in_the_backend(name: str) -> None:
    response = client.get(f"/mock_room/{name}.glb")
    assert response.status_code == 200
    assert response.content == (demo_assets.LEGACY_ROOT / f"{name}.glb").read_bytes()


@pytest.mark.parametrize("room_id", sorted(demo_assets.demo_rooms()))
def test_each_demo_room_shell_preserves_geometry_and_nodes(room_id: str) -> None:
    trimesh = pytest.importorskip("trimesh")
    response = client.get(f"/mock-room/shells/{room_id}.glb")
    assert response.status_code == 200
    assert response.headers["content-type"] == "model/gltf-binary"
    assert response.headers["cache-control"] == "no-cache"
    mesh = trimesh.load(BytesIO(response.content), file_type="glb", force="scene")
    room = demo_assets.demo_rooms()[room_id]
    assert {"floor", "ceiling", *(f"wall_{w.id}" for w in room.walls)} <= set(mesh.graph.nodes)
    floor_bounds = mesh.geometry["floor"].bounds
    assert floor_bounds[0][0] == pytest.approx(min(p.x for p in room.floor_polygon))
    assert floor_bounds[1][2] == pytest.approx(max(p.z for p in room.floor_polygon))


def test_shell_is_generated_once_per_room_and_cached_in_memory(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    demo_assets.demo_shell.cache_clear()
    calls = 0

    def generate(scene: object) -> bytes:
        nonlocal calls
        calls += 1
        return b"glTF-test"

    monkeypatch.setattr(demo_assets, "shell_glb", generate)
    try:
        assert client.get("/mock-room/shells/g-master.glb").content == b"glTF-test"
        assert client.get("/mock-room/shells/g-master.glb").content == b"glTF-test"
        assert calls == 1
    finally:
        demo_assets.demo_shell.cache_clear()


@pytest.mark.parametrize(
    "path",
    [
        "/mock-room/shells/unknown.glb",
        "/mock-room/assets/missing.glb",
        "/mock-room/assets/README.txt",
        "/mock_room/README.md",
        "/mock-room/assets/%2e%2e%2fmock_scene.json",
        "/mock-room/assets/%2e%2e%2fassets%2fg-master-o01-6c1443f003.glb",
        "/mock_room/%2e%2e%2fmock_room%2fbed.glb",
    ],
)
def test_unknown_assets_and_path_traversal_return_404(path: str) -> None:
    assert client.get(path).status_code == 404


def test_symlinks_cannot_escape_the_asset_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assets = tmp_path / "fixtures" / "assets"
    assets.mkdir(parents=True)
    secret = tmp_path / "outside.glb"
    secret.write_bytes(b"outside fixture root")
    (assets / "escape.glb").symlink_to(secret)
    monkeypatch.setattr(demo_assets, "FIXTURE_ROOT", assets.parent)
    assert client.get("/mock-room/assets/escape.glb").status_code == 404
