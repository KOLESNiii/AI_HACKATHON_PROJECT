"""The M2 demo room from a fresh checkout (Dev 2.8, #20): the real-input room gets its furniture
from the committed demo cache with no provider, key or network, and every asset agrees on its
size with the three readers: the delivered `bbox_m`, the editor's fit (Dev 3) and the auditor's
footprint (Dev 4). Catalog imports go through the same cache and the same checks."""

from __future__ import annotations

import hashlib
import io
import json
import math
import shutil
import socket
import struct
from collections.abc import Iterator
from pathlib import Path

import pytest

pytest.importorskip("cv2")
pytest.importorskip("shapely")
pytest.importorskip("trimesh")

import cv2  # noqa: E402
import numpy as np  # noqa: E402
import trimesh  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from shapely.geometry import LineString  # noqa: E402

from contracts.schema import GLB_BBOX_TOLERANCE_M, FurnitureItem, Pose2D, RoomScene  # noqa: E402
from services.reconstruction import scenes  # noqa: E402
from services.reconstruction.assets.catalog import import_catalog_asset  # noqa: E402
from services.reconstruction.assets.delivery import check_placed  # noqa: E402
from services.reconstruction.assets.demo_cache import (  # noqa: E402
    cache_folder,
    install_demo_cache,
    publish_catalog_scene,
    read_demo_cache,
)
from services.reconstruction.assets.segmentation import read_mask  # noqa: E402
from services.reconstruction.config import REPO_ROOT, furniture_data_dir  # noqa: E402
from services.reconstruction.main import app  # noqa: E402
from services.reconstruction.room import routes  # noqa: E402
from services.reconstruction.room.annotate import FixedAnnotator, PlanAnnotations  # noqa: E402
from services.reconstruction.room.routes import get_annotator  # noqa: E402
from services.reconstruction.room.video_furniture import (  # noqa: E402
    NOT_EXTRACTED,
    RealRoomFurniture,
    broken_cache,
    from_demo_cache,
    load_bindings,
    proxy_warning,
)
from services.spatial_engine.geometry import furniture_footprint  # noqa: E402
from services.spatial_engine.main import app as spatial_app  # noqa: E402

COMMITTED = REPO_ROOT / "services/reconstruction/assets/fixtures/demo_cache"
ANNOTATIONS = REPO_ROOT / "services/reconstruction/room/fixtures/three_floor.annotations.json"
PROXY_PREFIX = "/api/reconstruction"
(BINDING,) = load_bindings().values()
PLAN = REPO_ROOT / BINDING.plan
SOFA, OTHER_SOFA, TABLE, CHAIR = (hint.asset_id for hint in BINDING.hints)
SHOP = "https://shop.example/p/desk-123/"
MODEL = "https://cdn.example/models/desk.glb"

pytestmark = pytest.mark.skipif(not PLAN.exists(), reason="example plan missing")


@pytest.fixture()
def no_network(monkeypatch: pytest.MonkeyPatch) -> None:
    """Any attempt to resolve or connect fails the test: no provider, no retailer."""

    def refuse(*args: object, **kwargs: object) -> None:
        raise AssertionError("network access attempted")

    monkeypatch.setattr(socket.socket, "connect", refuse)
    monkeypatch.setattr(socket, "getaddrinfo", refuse)
    monkeypatch.setattr(socket, "create_connection", refuse)


@pytest.fixture()
def data_dir() -> Iterator[Path]:
    """The app's furniture data directory (a throwaway one, tests/conftest.py), empty: a fresh
    checkout that never ran the pipeline."""
    path = furniture_data_dir()
    shutil.rmtree(path, ignore_errors=True)
    path.mkdir(parents=True)
    yield path
    shutil.rmtree(path, ignore_errors=True)
    path.mkdir(parents=True)


def _client(cache_dir: Path) -> Iterator[TestClient]:
    annotations = PlanAnnotations.model_validate_json(ANNOTATIONS.read_text())
    app.dependency_overrides[get_annotator] = lambda: FixedAnnotator(annotations)
    app.dependency_overrides[scenes.get_furniture_source] = lambda: RealRoomFurniture(
        load_bindings(), furniture_data_dir(), cache_dir
    )
    scenes.clear_cache()
    routes.clear_corrections()
    with TestClient(app) as client:
        res = client.post(
            "/floor-plans", files=[("files", (PLAN.name, PLAN.read_bytes(), "image/png"))]
        )
        assert res.status_code == 200, res.text
        yield client
    app.dependency_overrides.clear()
    scenes.clear_cache()
    routes.clear_corrections()


@pytest.fixture()
def client(data_dir: Path, no_network: None) -> Iterator[TestClient]:
    """The app with the committed demo cache, the plan uploaded with its recorded labels."""
    yield from _client(COMMITTED)


@pytest.fixture(scope="module")
def auditor() -> TestClient:
    return TestClient(spatial_app)


def _scene(client: TestClient) -> tuple[RoomScene, list[str]]:
    res = client.get(f"/scenes/{BINDING.scene_id}")
    assert res.status_code == 200, res.text
    return RoomScene.model_validate(res.json()), json.loads(res.headers[scenes.WARNINGS_HEADER])


def _audit(auditor: TestClient, scene: RoomScene) -> dict[str, object]:
    res = auditor.post("/audit", json=scene.model_dump(mode="json"))
    assert res.status_code == 200, res.text
    report: dict[str, object] = res.json()
    return {k: v for k, v in report.items() if k not in ("scene_id", "scene_revision")}


def _collides(report: dict[str, object], a: str, b: str) -> bool:
    pairs = report["collisions"]
    assert isinstance(pairs, list)
    return any({c["item_a"], c["item_b"]} == {a, b} for c in pairs)


def _placed(scene: RoomScene, item_id: str, x: float, z: float, yaw: float = 0.0) -> RoomScene:
    furniture = [
        item.model_copy(update={"pose": Pose2D(x=x, z=z, yaw_deg=yaw)})
        if item.id == item_id
        else item
        for item in scene.furniture
    ]
    return scene.model_copy(update={"furniture": furniture, "revision": scene.revision + 1})


def _item(scene: RoomScene, item_id: str) -> FurnitureItem:
    return next(item for item in scene.furniture if item.id == item_id)


def retailer(url: str, limit: int) -> tuple[bytes, str]:
    """A retailer double: a product page with its published model and size, and its image."""
    if url == SHOP:
        blocks = [
            {
                "@context": "https://schema.org/",
                "@type": "Product",
                "name": "Writing desk",
                "image": "https://shop.example/desk.png",
                "width": "120 cm",
                "height": "75 cm",
                "depth": "60 cm",
            },
            {
                "@type": "3DModel",
                "encoding": [{"contentUrl": MODEL, "encodingFormat": "model/gltf-binary"}],
            },
        ]
        scripts = "".join(
            f'<script type="application/ld+json">{json.dumps(b)}</script>' for b in blocks
        )
        return f"<html><head>{scripts}</head></html>".encode(), url
    if url == MODEL:  # in metres, centred like a retailer's, not standing on the floor
        glb = trimesh.creation.box(extents=(1.21, 0.74, 0.6)).export(file_type="glb")
        assert isinstance(glb, bytes)
        return glb, url
    image = np.full((300, 400, 3), 255, np.uint8)
    image[90:230, 80:330] = (60, 90, 140)
    ok, encoded = cv2.imencode(".png", image)
    assert ok
    return encoded.tobytes(), url


# --- What the three readers see -----------------------------------------------------------------


def _declared_size(glb: bytes) -> tuple[np.ndarray, np.ndarray]:
    """Box3.setFromObject in the editor: the union of the POSITION accessors' min/max (node
    transforms are identity in a delivered file)."""
    length = struct.unpack("<I", glb[12:16])[0]
    document = json.loads(glb[20 : 20 + length])
    accessors = [
        document["accessors"][p["attributes"]["POSITION"]]
        for mesh in document["meshes"]
        for p in mesh["primitives"]
    ]
    low = np.min([a["min"] for a in accessors], axis=0)
    high = np.max([a["max"] for a in accessors], axis=0)
    return low, high


def assert_readers_agree(item: FurnitureItem, glb: bytes) -> None:
    """The editor draws the mesh where the auditor measures it.

    Editor (`frontend/src/components/editor/Furniture.tsx`): scale = bbox_m / declared size,
    offset = -declared bottom-centre, then the item's group is placed at the pose with
    `rotation.y = yaw`. Auditor: `furniture_footprint(item)`, the rotated width x depth box.
    """
    low, high = _declared_size(glb)
    box = np.array([item.bbox_m.width, item.bbox_m.height, item.bbox_m.depth])
    scale = box / (high - low)
    offset = -np.array([(low[0] + high[0]) / 2, low[1], (low[2] + high[2]) / 2]) * scale
    assert np.allclose(scale, 1, atol=1e-3), f"{item.id}: editor would rescale by {scale}"
    assert np.allclose(offset, 0, atol=GLB_BBOX_TOLERANCE_M), f"{item.id}: editor offset {offset}"

    vertices = trimesh.load_scene(io.BytesIO(glb), file_type="glb").to_mesh().vertices
    local = vertices * scale + offset
    yaw = math.radians(item.pose.yaw_deg)
    c, s = math.cos(yaw), math.sin(yaw)  # three.js rotation.y: local +Z faces +X at 90 deg
    xs = item.pose.x + local[:, 0] * c + local[:, 2] * s
    zs = item.pose.z - local[:, 0] * s + local[:, 2] * c
    assert abs(local[:, 1].min()) < GLB_BBOX_TOLERANCE_M  # stands on the floor
    assert abs(local[:, 1].max() - item.bbox_m.height) < GLB_BBOX_TOLERANCE_M

    footprint = furniture_footprint(item)
    points = np.column_stack([xs, zs])
    inside = footprint.buffer(GLB_BBOX_TOLERANCE_M)
    assert all(inside.covers(LineString([p, p])) for p in points[:: max(1, len(points) // 400)])
    corners = list(footprint.exterior.coords)
    for a, b in zip(corners, corners[1:], strict=False):  # the mesh reaches every side
        side = np.array(b) - np.array(a)
        normal = np.array([-side[1], side[0]]) / np.linalg.norm(side)
        distance = np.abs((points - np.array(a)) @ normal).min()
        assert distance < GLB_BBOX_TOLERANCE_M, f"{item.id}: {distance:.4f} m short of a side"


# --- Tests ------------------------------------------------------------------------------------


def test_a_fresh_checkout_shows_the_real_meshes_without_a_provider(
    client: TestClient, data_dir: Path, auditor: TestClient
) -> None:
    scene, warnings = _scene(client)
    cache = read_demo_cache(BINDING.furniture_scene_id, cache_dir=COMMITTED)
    assert cache is not None
    assert warnings == [from_demo_cache(BINDING.furniture_scene_id)]
    assert sorted(item.id for item in scene.furniture) == sorted(h.asset_id for h in BINDING.hints)
    assert not any(item.is_proxy for item in scene.furniture)  # meshes, not boxes
    assert check_placed(scene, cache.assets) == []  # IDs, bounds and meshes unchanged
    for item in scene.furniture:
        assert {"dimensions", "placement"} <= set(item.correction_needed)
        res = client.get(item.glb_url.removeprefix(PROXY_PREFIX))
        assert res.status_code == 200 and "immutable" in res.headers["cache-control"]
        assert f"{hashlib.sha256(res.content).hexdigest()}.glb" == item.glb_url.rsplit("/", 1)[1]
        assert_readers_agree(item, res.content)
    for asset in cache.assets:  # placement evidence still resolves to the masks
        primary = next(
            f for f in asset.evidence.frames if f.frame_index == asset.evidence.primary_frame_index
        )
        assert primary.mask_url is not None and read_mask(data_dir, primary.mask_url).any()
    assert BINDING.scene_id in scenes._scenes  # settled: kept like any complete assembly
    _audit(auditor, scene)


def test_the_auditor_measures_the_cached_meshes_at_their_drawn_size(
    client: TestClient, auditor: TestClient
) -> None:
    """Two solid sofas side by side: 5 mm apart is clear, 5 mm overlapping collides. The
    auditor's edge is the mesh's edge, to the millimetre."""
    scene, _ = _scene(client)
    sofa, other = _item(scene, SOFA), _item(scene, OTHER_SOFA)
    assert sofa.collision_parts == [] and other.collision_parts == []  # one solid box each
    x, z = 3.0, 6.5
    touching = (sofa.bbox_m.width + other.bbox_m.width) / 2
    for gap, collides in ((0.005, False), (-0.005, True)):
        moved = _placed(_placed(scene, SOFA, x, z), OTHER_SOFA, x + touching + gap, z)
        assert _collides(_audit(auditor, moved), SOFA, OTHER_SOFA) is collides, gap
    for yaw in (0.0, 90.0, 37.0):  # the editor's transform agrees at any turn
        turned = _placed(scene, SOFA, x, z, yaw)
        glb = client.get(sofa.glb_url.removeprefix(PROXY_PREFIX)).content
        assert_readers_agree(_item(turned, SOFA), glb)


def test_each_cached_item_moves_on_its_own_and_the_audit_follows(
    client: TestClient, auditor: TestClient
) -> None:
    scene, _ = _scene(client)
    before = _audit(auditor, scene)
    sofa = _item(scene, SOFA)
    moved = _placed(scene, TABLE, sofa.pose.x, sofa.pose.z, sofa.pose.yaw_deg)
    after = _audit(auditor, moved)
    assert _collides(after, TABLE, SOFA) and after != before
    for item_id in (SOFA, OTHER_SOFA, CHAIR):
        assert _item(moved, item_id) == _item(scene, item_id)
    table = _item(scene, TABLE)
    back = _placed(moved, TABLE, table.pose.x, table.pose.z, table.pose.yaw_deg)
    assert _audit(auditor, back) == before


def test_pipeline_data_wins_over_the_cache(client: TestClient, data_dir: Path) -> None:
    """Running the pipeline still takes effect: its (here: proxy-only) inventory is used."""
    from test_real_room import register_reviewed_items

    register_reviewed_items(data_dir)
    scene, warnings = _scene(client)
    assert all(item.is_proxy for item in scene.furniture)
    assert from_demo_cache(BINDING.furniture_scene_id) not in warnings
    assert warnings[-1] == proxy_warning(sorted(h.asset_id for h in BINDING.hints))


def test_a_broken_cache_leaves_the_room_empty_and_is_asked_again(
    data_dir: Path, no_network: None, tmp_path: Path
) -> None:
    cache_dir = tmp_path / "cache"
    shutil.copytree(COMMITTED, cache_dir)
    folder = cache_folder(cache_dir, BINDING.furniture_scene_id)
    glb = next(folder.rglob("*.glb"))
    good = glb.read_bytes()
    glb.write_bytes(good[:-1] + bytes([good[-1] ^ 0xFF]))
    clients = _client(cache_dir)
    client = next(clients)
    try:
        scene, warnings = _scene(client)
        assert scene.furniture == [] and warnings[0] == NOT_EXTRACTED
        assert warnings[1].startswith(broken_cache("")) and "altered" in warnings[1]
        assert str(tmp_path) not in warnings[1]  # no server paths in the response
        assert BINDING.scene_id not in scenes._scenes
        glb.write_bytes(good)  # repaired: the next request is furnished
        scene, _ = _scene(client)
        assert len(scene.furniture) == len(BINDING.hints)
    finally:
        clients.close()


def test_a_cached_catalog_import_is_placed_and_measured_alike(
    client: TestClient, data_dir: Path, auditor: TestClient, tmp_path: Path
) -> None:
    """A retailer product imported elsewhere (#19), published, then installed and placed here
    offline: same checks, same agreement between editor and auditor, provenance kept."""
    pipeline, cache_dir = tmp_path / "pipeline", tmp_path / "cache"
    import_catalog_asset(SHOP, "demo", data_dir=pipeline, fetch=retailer)
    publish_catalog_scene("demo", data_dir=pipeline, cache_dir=cache_dir)

    cache = install_demo_cache("catalog:demo", cache_dir=cache_dir, data_dir=data_dir)
    assert cache is not None
    (desk,) = cache.assets
    assert desk.product_url == SHOP and desk.dimension_source == "catalog" and not desk.is_proxy
    scene, _ = _scene(client)
    item = desk.to_item(Pose2D(x=3.2, z=7.9, yaw_deg=90))
    furnished = scene.model_copy(
        update={"furniture": [*scene.furniture, item], "revision": scene.revision + 1}
    )
    report = _audit(auditor, RoomScene.model_validate(furnished.model_dump()))
    assert isinstance(report["collisions"], list)
    glb = client.get(item.glb_url.removeprefix(PROXY_PREFIX))
    assert glb.status_code == 200
    assert_readers_agree(item, glb.content)
