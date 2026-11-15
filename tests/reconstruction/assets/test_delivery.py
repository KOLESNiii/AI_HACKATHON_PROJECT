"""The handoff to Dev 1 and its checks (Dev 2.6, #18): two video items are delivered as checked
meshes or labelled proxies, load through Dev 1's scene, and move independently."""

from __future__ import annotations

import io
import json
from collections.abc import Iterator
from pathlib import Path

import numpy as np
import pytest
import trimesh

pytest.importorskip("cv2")
pytest.importorskip("shapely")

from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from test_reconstruction import MeshDouble, masked_scene  # noqa: E402

from contracts.schema import (  # noqa: E402
    GLB_BBOX_TOLERANCE_M,
    BBoxM,
    CollisionPart,
    RoomScene,
)
from services.reconstruction import scenes  # noqa: E402
from services.reconstruction.assets.asset_store import asset_router, store_asset  # noqa: E402
from services.reconstruction.assets.check_delivery import main  # noqa: E402
from services.reconstruction.assets.delivery import (  # noqa: E402
    check_placed,
    deliver_furniture,
    inspect_asset,
)
from services.reconstruction.assets.mesh_providers import MeshError  # noqa: E402
from services.reconstruction.assets.models import FurnitureAsset  # noqa: E402
from services.reconstruction.assets.proxies import CATEGORY_SIZE_M, KnownDimensions  # noqa: E402
from services.reconstruction.assets.reconstruction import reconstruct_furniture  # noqa: E402
from services.reconstruction.room import footprint as fp  # noqa: E402
from services.reconstruction.room.annotate import FixedAnnotator, PlanAnnotations  # noqa: E402
from services.reconstruction.room.assemble import SceneFurniture  # noqa: E402
from services.reconstruction.room.observe import FixedObserver  # noqa: E402
from services.reconstruction.room.routes import get_annotator  # noqa: E402
from services.reconstruction.room.routes import router as floor_plan_router  # noqa: E402
from services.spatial_engine.main import app as spatial_app  # noqa: E402
from tests.test_room_align import _hint  # noqa: E402
from tests.test_room_parse import _label, _png, single_room  # noqa: E402

IDS = ["vid-000001", "vid-000002"]
PROXY_PREFIX = "/api/reconstruction"


def two_meshes(tmp_path: Path) -> None:
    masked_scene(tmp_path)
    assert reconstruct_furniture("scene", data_dir=tmp_path, provider=MeshDouble()).complete


def file_of(tmp_path: Path, asset: FurnitureAsset) -> Path:
    return tmp_path / "assets" / asset.glb_url.rsplit("/", 1)[1]


def bounds_of(glb: bytes) -> np.ndarray:
    return np.asarray(trimesh.load_scene(io.BytesIO(glb), file_type="glb").bounds)


def expected_bounds(box: BBoxM) -> list[list[float]]:
    return [[-box.width / 2, 0, -box.depth / 2], [box.width / 2, box.height, box.depth / 2]]


# --- delivery ---------------------------------------------------------------------------------


def test_two_items_are_delivered_as_checked_meshes_with_their_ids(tmp_path: Path) -> None:
    two_meshes(tmp_path)
    delivery = deliver_furniture("scene", data_dir=tmp_path)
    assert delivery.ok and delivery.warnings == [] and delivery.problems == []
    assert [a.id for a in delivery.assets] == [c.object_id for c in delivery.checks] == IDS
    for asset, check in zip(delivery.assets, delivery.checks, strict=True):
        assert not asset.is_proxy and check.delivered == "mesh" and check.fallback_reason is None
        assert check.problems == [] and check.bounds_error_m < GLB_BBOX_TOLERANCE_M
        assert check.triangles == 24 and check.size_bytes == file_of(tmp_path, asset).stat().st_size
        # A size read off the mesh stays an estimate that asks to be corrected.
        assert asset.dimension_source == "estimated" and "dimensions" in asset.correction_needed
        assert asset.evidence.frames
    # Offline and repeatable: the same immutable files, no provider.
    assert deliver_furniture("scene", data_dir=tmp_path) == delivery


def test_stated_dimensions_are_delivered_as_stated(tmp_path: Path) -> None:
    two_meshes(tmp_path)
    known = KnownDimensions(bbox_m=BBoxM(width=2.0, height=1.0, depth=1.2), source="measured")
    delivery = deliver_furniture("scene", data_dir=tmp_path, dimensions={IDS[0]: known})
    measured, guessed = delivery.assets
    assert delivery.ok and measured.bbox_m == known.bbox_m
    assert measured.dimension_source == "measured" and measured.correction_needed == []
    assert guessed.dimension_source == "estimated"


def test_an_item_without_a_mesh_is_delivered_as_its_labelled_proxy(tmp_path: Path) -> None:
    masked_scene(tmp_path)
    reconstruct_furniture("scene", data_dir=tmp_path, provider=MeshDouble(), object_ids=IDS[:1])
    delivery = deliver_furniture("scene", data_dir=tmp_path)
    mesh, proxy = delivery.assets
    assert delivery.ok  # a proxy is a valid delivery
    assert [c.delivered for c in delivery.checks] == ["mesh", "proxy"]
    assert not mesh.is_proxy and proxy.is_proxy and proxy.id == IDS[1] and proxy.name == IDS[1]
    assert "not_attempted" in delivery.checks[1].fallback_reason
    width, height, depth = CATEGORY_SIZE_M["other"]
    assert proxy.bbox_m == BBoxM(width=width, height=height, depth=depth)
    assert proxy.dimension_source == "estimated" and proxy.correction_needed == ["dimensions"]
    assert delivery.checks[1].problems == []
    assert np.allclose(
        bounds_of(file_of(tmp_path, proxy).read_bytes()), expected_bounds(proxy.bbox_m)
    )


def test_a_provider_failure_keeps_both_items_as_proxies(tmp_path: Path) -> None:
    masked_scene(tmp_path)
    failing = MeshDouble(error=MeshError("remote failure", kind="provider"))
    reconstruct_furniture("scene", data_dir=tmp_path, provider=failing)
    delivery = deliver_furniture("scene", data_dir=tmp_path)
    assert delivery.ok and [a.id for a in delivery.assets] == IDS
    assert all(a.is_proxy for a in delivery.assets)
    assert all(c.fallback_reason and c.problems == [] for c in delivery.checks)


def test_a_mesh_that_cannot_be_normalised_is_delivered_as_its_proxy(tmp_path: Path) -> None:
    masked_scene(tmp_path, two=False)
    dense = trimesh.creation.icosphere(subdivisions=6).export(file_type="glb")
    reconstruct_furniture("scene", data_dir=tmp_path, provider=MeshDouble(glb=dense))
    delivery = deliver_furniture("scene", data_dir=tmp_path)
    (asset,), (check,) = delivery.assets, delivery.checks
    assert delivery.ok and asset.is_proxy and check.delivered == "proxy"
    assert check.fallback_reason == "mesh could not be normalised"
    assert any("normalis" in warning for warning in delivery.warnings)


def test_a_mesh_that_fails_its_checks_falls_back_to_the_proxy(tmp_path: Path) -> None:
    two_meshes(tmp_path)
    # A stated size gives the first item its own file: identical meshes share one otherwise.
    known = KnownDimensions(bbox_m=BBoxM(width=2.0, height=1.0, depth=1.2), source="measured")
    good = deliver_furniture("scene", data_dir=tmp_path, dimensions={IDS[0]: known})
    assert good.ok and not good.assets[0].is_proxy
    file_of(tmp_path, good.assets[0]).write_bytes(b"damaged")
    delivery = deliver_furniture("scene", data_dir=tmp_path, dimensions={IDS[0]: known})
    first, second = delivery.assets
    assert delivery.ok and first.id == IDS[0] and first.is_proxy
    assert first.bbox_m == known.bbox_m and first.dimension_source == "measured"
    assert "content address" in delivery.checks[0].fallback_reason
    assert any(IDS[0] in w and "proxy is delivered" in w for w in delivery.warnings)
    assert second == good.assets[1]  # the other item is untouched


def test_a_damaged_proxy_is_still_delivered_and_fails_the_delivery(tmp_path: Path) -> None:
    masked_scene(tmp_path, two=False)
    proxy = deliver_furniture("scene", data_dir=tmp_path).assets[0]
    file_of(tmp_path, proxy).unlink()
    file_of(tmp_path, proxy).write_bytes(b"damaged")
    delivery = deliver_furniture("scene", data_dir=tmp_path)
    assert not delivery.ok and delivery.assets == [proxy]
    assert delivery.checks[0].problems


def test_unknown_scene_raises(tmp_path: Path) -> None:
    masked_scene(tmp_path)
    with pytest.raises(ValueError):
        deliver_furniture("elsewhere", data_dir=tmp_path)
    with pytest.raises(ValueError):
        deliver_furniture("scene", data_dir=tmp_path / "missing")


# --- checks -----------------------------------------------------------------------------------


def problems(tmp_path: Path, asset: FurnitureAsset) -> str:
    return "; ".join(inspect_asset(asset, data_dir=tmp_path).problems)


def test_each_check_detects_its_fault(tmp_path: Path) -> None:
    two_meshes(tmp_path)
    asset = deliver_furniture("scene", data_dir=tmp_path).assets[0]
    assert problems(tmp_path, asset) == ""

    box = asset.bbox_m
    wider = asset.model_copy(update={"bbox_m": box.model_copy(update={"width": box.width + 0.01})})
    assert "bounds differ from bbox_m by 0.0050 m" in problems(tmp_path, wider)

    silent = asset.model_copy(update={"correction_needed": []})
    assert "does not ask for a dimensions correction" in problems(tmp_path, silent)

    for url in (
        f"/elsewhere/{asset.glb_url.rsplit('/', 1)[1]}",
        f"{PROXY_PREFIX}/assets/{'0' * 64}.glb",
        f"{PROXY_PREFIX}/assets/../registry.sqlite3",
    ):
        moved = asset.model_copy(update={"glb_url": url})
        assert "does not name a file in the asset store" in problems(tmp_path, moved)

    # A collision part that pokes out of the box breaks the FurnitureItem rules.
    outside = CollisionPart(
        x=0, z=0, width=box.width * 2, depth=box.depth, y_min=0, y_max=box.height
    )
    broken = asset.model_copy(update={"collision_parts": [outside]})
    assert "breaks the furniture item rules" in problems(tmp_path, broken)


def test_lifted_or_off_centre_geometry_fails_the_bounds_check(tmp_path: Path) -> None:
    two_meshes(tmp_path)
    asset = deliver_furniture("scene", data_dir=tmp_path).assets[0]
    box = asset.bbox_m
    for offset in ([0, 0.05, 0], [0.05, 0, 0]):
        mesh = trimesh.creation.box(extents=[box.width, box.height, box.depth])
        mesh.apply_translation([offset[0], box.height / 2 + offset[1], offset[2]])
        url = store_asset(tmp_path, mesh.export(file_type="glb"))
        assert "bounds differ" in problems(tmp_path, asset.model_copy(update={"glb_url": url}))


def test_scene_graph_and_budget_faults_are_reported(tmp_path: Path) -> None:
    two_meshes(tmp_path)
    asset = deliver_furniture("scene", data_dir=tmp_path).assets[0]
    box = asset.bbox_m

    scene = trimesh.Scene()
    shift = np.eye(4)
    shift[1, 3] = box.height / 2
    scene.add_geometry(
        trimesh.creation.box(extents=[box.width, box.height, box.depth]), transform=shift
    )
    unbaked = asset.model_copy(
        update={"glb_url": store_asset(tmp_path, scene.export(file_type="glb"))}
    )
    assert problems(tmp_path, unbaked) == (
        "has a node transform that is not baked into the vertices"
    )

    dense = trimesh.creation.icosphere(subdivisions=6)
    heavy = asset.model_copy(
        update={"glb_url": store_asset(tmp_path, dense.export(file_type="glb"))}
    )
    assert "triangles; the limit is 30000" in problems(tmp_path, heavy)

    junk = asset.model_copy(update={"glb_url": store_asset(tmp_path, b"not a mesh")})
    assert "not a binary glTF 2.0 file" in problems(tmp_path, junk)
    assert "no readable triangle geometry" in problems(tmp_path, junk)


# --- through Dev 1's scene --------------------------------------------------------------------


@pytest.fixture()
def client(tmp_path: Path) -> Iterator[TestClient]:
    """The reconstruction routes with the asset store mounted on this test's data directory."""
    app = FastAPI()
    app.include_router(floor_plan_router)
    app.include_router(scenes.router)
    app.include_router(asset_router(tmp_path))
    ann = PlanAnnotations(rooms=[_label("Studio", 400, 350, 4.0, 3.0)])
    app.dependency_overrides[get_annotator] = lambda: FixedAnnotator(ann)

    class Video:
        """How Dev 1 consumes the delivery: its assets, plus where one of them was seen."""

        def furniture_for(self, room: RoomScene) -> SceneFurniture:
            frames = [f for w in room.walls if (f := fp.wall_frame(w)) is not None]
            west = max(frames, key=lambda f: f.inward[0]).wall
            hints = [_hint(IDS[0], west.id, 0.5, facing="into_room")]
            assets = deliver_furniture("scene", data_dir=tmp_path).assets
            return SceneFurniture(assets=assets, observer=FixedObserver(hints))

    app.dependency_overrides[scenes.get_furniture_source] = Video
    scenes.clear_cache()
    with TestClient(app) as c:
        yield c
    scenes.clear_cache()


def load_scene(client: TestClient) -> RoomScene:
    res = client.post(
        "/floor-plans", files=[("files", ("plan.png", _png(single_room()), "image/png"))]
    )
    assert res.status_code == 200, res.text
    scene_id = res.json()["floors"][0]["rooms"][0]["scene"]["scene_id"]
    res = client.get(f"/scenes/{scene_id}")
    assert res.status_code == 200, res.text
    return RoomScene.model_validate(res.json())


def audit(scene: RoomScene) -> dict[str, object]:
    res = TestClient(spatial_app).post("/audit", json=scene.model_dump(mode="json"))
    assert res.status_code == 200, res.text
    report: dict[str, object] = res.json()
    return report


def test_two_delivered_items_load_through_the_scene_with_ids_and_bounds(
    tmp_path: Path, client: TestClient
) -> None:
    two_meshes(tmp_path)
    delivered = deliver_furniture("scene", data_dir=tmp_path).assets
    scene = load_scene(client)
    assert [item.id for item in scene.furniture] == IDS
    assert check_placed(scene, delivered) == []
    for item, asset in zip(scene.furniture, delivered, strict=True):
        assert not item.is_proxy and item.bbox_m == asset.bbox_m
        # What the editor fetches is the checked file, and it is exactly `bbox_m`.
        res = client.get(item.glb_url.removeprefix(PROXY_PREFIX))
        assert res.status_code == 200 and "immutable" in res.headers["cache-control"]
        error = np.abs(bounds_of(res.content) - expected_bounds(item.bbox_m)).max()
        assert error < GLB_BBOX_TOLERANCE_M
    report = audit(scene)
    assert report["collisions"] == [] and report["out_of_bounds_item_ids"] == []


def test_delivered_items_move_independently_and_keep_ids_and_bounds(
    tmp_path: Path, client: TestClient
) -> None:
    two_meshes(tmp_path)
    delivered = deliver_furniture("scene", data_dir=tmp_path).assets
    scene = load_scene(client)
    first, second = scene.furniture
    assert (first.pose.x, first.pose.z) != (second.pose.x, second.pose.z)

    # The editor's move: one item's pose changes and the revision goes up.
    pose = second.pose.model_copy(update={"x": second.pose.x + 0.4, "yaw_deg": 90.0})
    moved = second.model_copy(update={"pose": pose})
    edited = RoomScene.model_validate(
        scene.model_dump() | {"furniture": [first.model_dump(), moved.model_dump()], "revision": 1}
    )
    assert edited.furniture[0] == first
    assert edited.furniture[1].pose == pose != second.pose
    assert edited.furniture[1].model_dump(exclude={"pose"}) == second.model_dump(exclude={"pose"})
    assert check_placed(edited, delivered) == []
    assert audit(edited)["scene_revision"] == 1

    # And the other way round: the first moves while the second stays where it was put.
    back = first.model_copy(
        update={"pose": first.pose.model_copy(update={"z": first.pose.z + 0.3})}
    )
    again = edited.model_copy(update={"furniture": [back, edited.furniture[1]], "revision": 2})
    assert again.furniture[1] == edited.furniture[1] and check_placed(again, delivered) == []


def test_a_proxy_fallback_also_loads_and_moves_through_the_scene(
    tmp_path: Path, client: TestClient
) -> None:
    masked_scene(tmp_path)
    reconstruct_furniture("scene", data_dir=tmp_path, provider=MeshDouble(), object_ids=IDS[:1])
    delivered = deliver_furniture("scene", data_dir=tmp_path).assets
    scene = load_scene(client)
    mesh, proxy = scene.furniture
    assert check_placed(scene, delivered) == []
    assert not mesh.is_proxy and proxy.is_proxy and proxy.id == IDS[1]
    assert "dimensions" in proxy.correction_needed
    assert client.get(proxy.glb_url.removeprefix(PROXY_PREFIX)).status_code == 200
    audit(scene)


def test_check_placed_reports_what_placement_changed(tmp_path: Path, client: TestClient) -> None:
    two_meshes(tmp_path)
    delivered = deliver_furniture("scene", data_dir=tmp_path).assets
    scene = load_scene(client)
    first, second = scene.furniture

    assert check_placed(scene.model_copy(update={"furniture": [first]}), delivered) == [
        f"{IDS[1]}: in the scene 0 times, expected once"
    ]
    twice = scene.model_copy(update={"furniture": [first, second, second]})
    assert check_placed(twice, delivered) == [f"{IDS[1]}: in the scene 2 times, expected once"]

    box = second.bbox_m.model_copy(update={"depth": second.bbox_m.depth + 0.1})
    other = f"{PROXY_PREFIX}/assets/{'0' * 64}.glb"
    resized = second.model_copy(update={"bbox_m": box, "glb_url": other})
    assert check_placed(scene.model_copy(update={"furniture": [first, resized]}), delivered) == [
        f"{IDS[1]}: changed by placement: bbox_m, glb_url"
    ]
    cleared = second.model_copy(update={"correction_needed": []})
    assert check_placed(scene.model_copy(update={"furniture": [first, cleared]}), delivered) == [
        f"{IDS[1]}: changed by placement: correction_needed"
    ]


# --- CLI --------------------------------------------------------------------------------------


def test_cli_runs_the_checks_and_reports(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    masked_scene(tmp_path)
    reconstruct_furniture("scene", data_dir=tmp_path, provider=MeshDouble(), object_ids=IDS[:1])
    out = tmp_path / "report"
    argv = ["--scene-id", "scene", "--data-dir", str(tmp_path), "--out", str(out)]
    assert main(argv) == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary == {"items": 2, "meshes": 1, "proxies": 1, "failed": [], "ok": True}
    assets = [
        FurnitureAsset.model_validate(a) for a in json.loads((out / "assets.json").read_text())
    ]
    assert [a.id for a in assets] == IDS and [a.is_proxy for a in assets] == [False, True]
    assert json.loads((out / "delivery.json").read_text())["checks"][1]["delivered"] == "proxy"
    report = (out / "report.md").read_text()
    assert "| pass |" in report and "not_attempted" in report

    assert main([*argv, "--min-items", "3"]) == 2
    assert main([*argv, "--scene-id", "unknown"]) == 1
    assert main([*argv, "--object-id", "vid-999999"]) == 1

    # A damaged proxy cannot be replaced by anything, so the check fails. Both items' proxies
    # are the same content-addressed box, so the first cannot fall back to a sound one either.
    for asset in assets:
        file_of(tmp_path, asset).write_bytes(b"damaged")
    capsys.readouterr()
    assert main(argv) == 2
    assert json.loads(capsys.readouterr().out)["failed"] == IDS
