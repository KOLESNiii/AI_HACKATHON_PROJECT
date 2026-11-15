"""The first real-input room (Dev 1.6, #10): the parsed reception room of `three_floor.png` with
the furniture Dev 2's pipeline extracted from `three_floor_3.mp4`, served for the editor, and
an audit that follows each move."""

from __future__ import annotations

import json
import shutil
import tempfile
from collections.abc import Collection, Iterator
from pathlib import Path

import pytest

pytest.importorskip("cv2")
pytest.importorskip("shapely")
pytest.importorskip("trimesh")

from fastapi.testclient import TestClient  # noqa: E402

from contracts.schema import FurnitureItem, RoomScene  # noqa: E402
from services.reconstruction import scenes  # noqa: E402
from services.reconstruction.assets.providers import RecordedProvider  # noqa: E402
from services.reconstruction.assets.registry import Registry  # noqa: E402
from services.reconstruction.assets.segmentation import read_mask, segment_furniture  # noqa: E402
from services.reconstruction.assets.selection import select_furniture_frames  # noqa: E402
from services.reconstruction.assets.selection_models import (  # noqa: E402
    Discovery,
    Frame,
    ReconstructionResult,
    RegistryState,
    SelectedObject,
    SelectionOptions,
)
from services.reconstruction.config import furniture_data_dir  # noqa: E402
from services.reconstruction.main import app  # noqa: E402
from services.reconstruction.room import routes, video_furniture  # noqa: E402
from services.reconstruction.room.annotate import (  # noqa: E402
    FixedAnnotator,
    NullAnnotator,
    PlanAnnotations,
)
from services.reconstruction.room.assemble import assemble_scene  # noqa: E402
from services.reconstruction.room.routes import get_annotator  # noqa: E402
from services.reconstruction.room.video_furniture import (  # noqa: E402
    NOT_EXTRACTED,
    RealRoomFurniture,
    geometry_mismatch,
    load_bindings,
    proxy_warning,
    still_extracting,
)
from services.spatial_engine.main import app as spatial_app  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ANNOTATIONS = ROOT / "services/reconstruction/room/fixtures/three_floor.annotations.json"
RECORDING = ROOT / "tests/reconstruction/assets/fixtures/opening_room.reviewed.json"
PROXY_PREFIX = "/api/reconstruction"
(BINDING,) = load_bindings().values()
PLAN = ROOT / BINDING.plan
VIDEO = ROOT / BINDING.video
ALLOCATED = {
    "White coffee table": "vid-000001",
    "Rear sofa": "vid-000002",
    "Right sofa": "vid-000003",
    "Office chair": "vid-000004",
}
"""The IDs frame selection (#14) gives the reviewed recording's items on the real video;
`test_the_real_video_furnishes_the_real_room` checks them (not the recording's order)."""
NAMES = {item_id: name for name, item_id in ALLOCATED.items()}
ITEM_IDS = sorted(NAMES)
SOFA, OTHER_SOFA, TABLE, CHAIR = (hint.asset_id for hint in BINDING.hints)
PLAN_ID = BINDING.scene_id.removesuffix(f"-{BINDING.room_id}")

pytestmark = pytest.mark.skipif(not PLAN.exists(), reason="example plan missing")


def register_reviewed_items(data_dir: Path, only: Collection[str] | None = None) -> None:
    """What frame selection (#14) records for the reviewed recording, without decoding the
    video: one item per reviewed object, with the IDs the real run allocates. `only` stops
    part-way, as a request during selection sees it (selection stores batch by batch)."""
    discovery = Discovery.model_validate_json(RECORDING.read_text())

    def add(state: RegistryState) -> None:
        for obj in discovery.objects:
            for sighting in obj.sightings:
                source, _, index = sighting.frame_key.split(":")
                state.frames[sighting.frame_key] = Frame(
                    key=sighting.frame_key,
                    source_id=source,
                    frame_index=int(index),
                    pts=int(index),
                    timestamp_s=int(index) / 30,
                    image_size_px=(480, 848),
                    image_path=f"frames/{source}/{index}.png",
                    quality=0.8,
                )
            item_id = ALLOCATED[obj.name]
            if only is not None and item_id not in only:
                continue
            state.objects[item_id] = SelectedObject(
                id=item_id,
                name=obj.name,
                category=obj.category,
                appearance=obj.appearance,
                sightings=obj.sightings,
                selected_views=[s.frame_key for s in obj.sightings][:4],
            )
        state.next_id = len(discovery.objects) + 1

    scene = BINDING.furniture_scene_id
    Registry(data_dir, namespace=scene).update(scene, add)


def _clear(path: Path) -> None:
    for child in path.iterdir():
        shutil.rmtree(child) if child.is_dir() else child.unlink()


@pytest.fixture()
def data_dir() -> Iterator[Path]:
    """The app's furniture data directory: a throwaway one (tests/conftest.py), emptied."""
    path = furniture_data_dir()
    assert path.is_relative_to(Path(tempfile.gettempdir()).resolve()), path
    path.mkdir(parents=True, exist_ok=True)
    _clear(path)
    yield path
    _clear(path)


@pytest.fixture()
def client(data_dir: Path) -> Iterator[TestClient]:
    """The app with `three_floor.png` uploaded (recorded labels, no provider call)."""
    annotations = PlanAnnotations.model_validate_json(ANNOTATIONS.read_text())
    app.dependency_overrides[get_annotator] = lambda: FixedAnnotator(annotations)
    scenes.clear_cache()
    with TestClient(app) as c:
        res = c.post("/floor-plans", files=[("files", (PLAN.name, PLAN.read_bytes(), "image/png"))])
        assert res.status_code == 200, res.text
        yield c
    app.dependency_overrides.clear()
    scenes.clear_cache()


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
    assert (report["scene_id"], report["scene_revision"]) == (scene.scene_id, scene.revision)
    return report


def _findings(report: dict[str, object]) -> dict[str, object]:
    return {k: v for k, v in report.items() if k not in ("scene_id", "scene_revision")}


def _moved(scene: RoomScene, item_id: str, x: float, z: float) -> RoomScene:
    """What the editor sends after a drag: one pose changed, the next revision."""
    furniture = [
        item.model_copy(update={"pose": item.pose.model_copy(update={"x": x, "z": z})})
        if item.id == item_id
        else item
        for item in scene.furniture
    ]
    return scene.model_copy(update={"furniture": furniture, "revision": scene.revision + 1})


def _item(scene: RoomScene, item_id: str) -> FurnitureItem:
    return next(item for item in scene.furniture if item.id == item_id)


def _collides(report: dict[str, object], a: str, b: str) -> bool:
    pairs = report["collisions"]
    assert isinstance(pairs, list)
    return any({c["item_a"], c["item_b"]} == {a, b} for c in pairs)


def test_the_binding_names_a_room_and_walls_of_the_parsed_plan(client: TestClient) -> None:
    res = client.get(f"/floor-plans/{PLAN_ID}/rooms/{BINDING.room_id}")
    assert res.status_code == 200, res.text
    room = RoomScene.model_validate(res.json())
    assert room.scene_id == BINDING.scene_id
    walls = {wall.id for wall in room.walls}
    assert {hint.wall_id for hint in BINDING.hints} <= walls  # parser drift fails here
    assert geometry_mismatch(BINDING, room) is None  # the committed wall lengths are true
    reviewed = Discovery.model_validate_json(RECORDING.read_text()).objects
    assert sorted(obj.name for obj in reviewed) == sorted(ALLOCATED)
    assert sorted(hint.asset_id for hint in BINDING.hints) == ITEM_IDS  # one hint per item
    named = [NAMES[hint.asset_id] for hint in BINDING.hints]  # SOFA, OTHER_SOFA, TABLE, CHAIR
    assert named == ["Rear sofa", "Right sofa", "White coffee table", "Office chair"]


def test_the_real_room_has_its_video_furniture_as_labelled_proxies(
    client: TestClient, data_dir: Path, auditor: TestClient
) -> None:
    register_reviewed_items(data_dir)
    scene, warnings = _scene(client)
    assert {item.id: item.name for item in scene.furniture} == NAMES
    for item in scene.furniture:
        assert item.is_proxy and item.dimension_source == "estimated"
        assert "dimensions" in item.correction_needed  # an estimate, never a measurement
        assert "placement" in item.correction_needed  # reviewed hints, not measured poses
        res = client.get(item.glb_url.removeprefix(PROXY_PREFIX))
        assert res.status_code == 200 and res.content[:4] == b"glTF"
        assert "immutable" in res.headers["cache-control"]
    assert client.get(scene.shell_glb_url.removeprefix(PROXY_PREFIX)).status_code == 200
    assert any(w.startswith("labelled proxies") and all(i in w for i in ITEM_IDS) for w in warnings)
    assert warnings[-1] == proxy_warning(ITEM_IDS)  # every item is present, all are proxies

    room = scene.model_copy(update={"furniture": []})
    records = assemble_scene(room, RealRoomFurniture(load_bindings(), data_dir)).records
    assert {r.method for r in records.values()} == {"hint"}  # every item placed from its hint
    _audit(auditor, scene)


def test_each_item_moves_on_its_own_and_the_audit_follows(
    client: TestClient, data_dir: Path, auditor: TestClient
) -> None:
    register_reviewed_items(data_dir)
    scene, _ = _scene(client)
    before = _audit(auditor, scene)
    assert not _collides(before, TABLE, SOFA)

    sofa = _item(scene, SOFA)
    table_on_sofa = _moved(scene, TABLE, sofa.pose.x, sofa.pose.z)
    after = _audit(auditor, table_on_sofa)
    assert _collides(after, TABLE, SOFA)
    assert _findings(after) != _findings(before)
    for item_id in (SOFA, OTHER_SOFA, CHAIR):  # nothing else moved
        assert _item(table_on_sofa, item_id) == _item(scene, item_id)

    table = _item(scene, TABLE)
    back = _moved(table_on_sofa, TABLE, table.pose.x, table.pose.z)
    assert _findings(_audit(auditor, back)) == _findings(before)

    chair = _item(scene, CHAIR)
    sofa_on_chair = _moved(back, OTHER_SOFA, chair.pose.x, chair.pose.z)
    second = _audit(auditor, sofa_on_chair)
    assert _collides(second, OTHER_SOFA, CHAIR) and not _collides(second, TABLE, SOFA)
    assert _item(sofa_on_chair, TABLE) == table


def test_moving_the_chair_out_of_the_doorway_clears_the_blocked_door(
    client: TestClient, data_dir: Path, auditor: TestClient
) -> None:
    """The reviewed hint puts the chair in the swing of the plan's entrance door; alignment
    flags it and the audit reports it until the user moves the chair."""
    register_reviewed_items(data_dir)
    scene, _ = _scene(client)
    before = _audit(auditor, scene)
    assert before["blocked_doors"] == [{"door_id": "door0", "blocked_by_item_id": CHAIR}]
    after = _audit(auditor, _moved(scene, CHAIR, 4.0, 8.6))  # against the east wall
    assert after["blocked_doors"] == [] and after["out_of_bounds_item_ids"] == []
    assert after["collisions"] == before["collisions"]


def test_a_room_whose_furniture_is_not_extracted_yet_is_asked_again(
    client: TestClient, data_dir: Path
) -> None:
    scene, warnings = _scene(client)
    assert scene.furniture == [] and warnings == [NOT_EXTRACTED]
    register_reviewed_items(data_dir)  # the pipeline runs while the server is up
    scene, _ = _scene(client)
    assert sorted(item.id for item in scene.furniture) == ITEM_IDS


def test_a_partial_inventory_is_shown_but_asked_again(client: TestClient, data_dir: Path) -> None:
    """A request while frame selection is still storing items must not freeze the room."""
    register_reviewed_items(data_dir, only=[TABLE])
    scene, warnings = _scene(client)
    assert [item.id for item in scene.furniture] == [TABLE]
    assert still_extracting(sorted({SOFA, OTHER_SOFA, CHAIR})) in warnings
    assert BINDING.scene_id not in scenes._scenes

    register_reviewed_items(data_dir)  # selection finishes
    scene, warnings = _scene(client)
    assert sorted(item.id for item in scene.furniture) == ITEM_IDS
    assert not any(w.startswith("furniture still being extracted") for w in warnings)
    assert scenes._scenes[BINDING.scene_id].scene == scene  # complete now, so kept


def test_the_plan_parsed_without_its_labels_gets_no_video_furniture(data_dir: Path) -> None:
    """Without labels (no FAL_KEY, or the call fails) the same image, and so the same scene
    ID, parses into a different room: the reception furniture must not be put in it."""
    recorded = routes._plans.pop(PLAN_ID, None)
    app.dependency_overrides[get_annotator] = NullAnnotator
    scenes.clear_cache()
    try:
        with TestClient(app) as client:
            files = [("files", (PLAN.name, PLAN.read_bytes(), "image/png"))]
            assert client.post("/floor-plans", files=files).status_code == 200
            register_reviewed_items(data_dir)
            scene, warnings = _scene(client)
        assert scene.furniture == [] and len(warnings) == 1
        assert "does not match" in warnings[0] and "walls, expected 18" in warnings[0]
    finally:
        routes._plans.pop(PLAN_ID, None)
        if recorded is not None:
            routes._plans[PLAN_ID] = recorded
        app.dependency_overrides.clear()
        scenes.clear_cache()


def test_the_geometry_check_allows_a_small_scale_change_and_names_a_wrong_wall(
    client: TestClient,
) -> None:
    room = RoomScene.model_validate(
        client.get(f"/floor-plans/{PLAN_ID}/rooms/{BINDING.room_id}").json()
    )

    def scaled(factor: float) -> RoomScene:
        walls = [
            w.model_copy(
                update={
                    "start": w.start.model_copy(
                        update={"x": w.start.x * factor, "z": w.start.z * factor}
                    ),
                    "end": w.end.model_copy(update={"x": w.end.x * factor, "z": w.end.z * factor}),
                }
            )
            for w in room.walls
        ]
        return room.model_copy(update={"walls": walls})

    assert geometry_mismatch(BINDING, scaled(1.03)) is None  # labels read slightly differently
    assert geometry_mismatch(BINDING, scaled(1.10)) == "w0 is 1.19 m, expected 1.08 m"


def test_a_normalised_mesh_is_served_instead_of_its_proxy(
    client: TestClient, data_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Once #17 normalises an item's mesh, the room shows that mesh, not the box."""
    real = video_furniture.reconstruct_furniture

    def with_chair_mesh(scene_id: str, *, data_dir: Path) -> ReconstructionResult:
        result = real(scene_id, data_dir=data_dir)
        items = [
            item.model_copy(
                update={"asset": item.proxy.model_copy(update={"is_proxy": False, "name": "mesh"})}
            )
            if item.object_id == CHAIR
            else item
            for item in result.items
        ]
        return result.model_copy(update={"items": items})

    monkeypatch.setattr(video_furniture, "reconstruct_furniture", with_chair_mesh)
    register_reviewed_items(data_dir)
    scene, warnings = _scene(client)
    chair = _item(scene, CHAIR)
    assert not chair.is_proxy and chair.name == "mesh"
    assert proxy_warning([TABLE, SOFA, OTHER_SOFA]) in warnings


def test_furniture_files_are_served_only_by_content_hash(
    client: TestClient, data_dir: Path
) -> None:
    register_reviewed_items(data_dir)
    _scene(client)  # writes the proxies
    assert any((data_dir / "assets").iterdir())
    for name in ("registry.sqlite3", "..%2Fregistry.sqlite3", f"{'0' * 64}.glb", "x.glb"):
        res = client.get(f"/assets/{name}")
        assert res.status_code == 404, name
        assert str(data_dir) not in res.text and "sqlite" not in res.text


@pytest.mark.skipif(
    shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None or not VIDEO.exists(),
    reason="needs FFmpeg/FFprobe and the example video",
)
def test_the_real_video_furnishes_the_real_room(
    client: TestClient, data_dir: Path, auditor: TestClient
) -> None:
    """End to end and offline: frames of the real video with the reviewed recording (#14),
    GrabCut masks (#15), proxies (#16), placed in the parsed room and audited."""
    scene_id = BINDING.furniture_scene_id
    discovery = Discovery.model_validate_json(RECORDING.read_text())
    select_furniture_frames(
        [VIDEO],
        scene_id,
        data_dir=data_dir,
        provider=RecordedProvider(discovery),
        options=SelectionOptions(end_s=6, max_frames_per_video=8, batch_size=3),
    )
    assert segment_furniture(scene_id, data_dir=data_dir).complete

    scene, warnings = _scene(client)
    assert {item.id: item.name for item in scene.furniture} == NAMES  # the real allocation
    assert all(item.is_proxy for item in scene.furniture)
    assert warnings == [proxy_warning(ITEM_IDS)]  # all items present; no mesh failures
    furniture = RealRoomFurniture(load_bindings(), data_dir).furniture_for(scene)
    for asset in furniture.assets:
        primary = next(
            f for f in asset.evidence.frames if f.frame_index == asset.evidence.primary_frame_index
        )
        assert primary.mask_url is not None and read_mask(data_dir, primary.mask_url).any()

    before = _audit(auditor, scene)
    sofa = _item(scene, SOFA)
    after = _audit(auditor, _moved(scene, TABLE, sofa.pose.x, sofa.pose.z))
    assert _collides(after, TABLE, SOFA) and _findings(after) != _findings(before)
