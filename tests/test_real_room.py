"""The first real-input room (Dev 1.6, #10): the parsed reception room of `three_floor.png` with
the furniture Dev 2's pipeline extracted from `three_floor_3.mp4`, served for the editor, and
an audit that follows each move."""

from __future__ import annotations

import json
import math
import shutil
import tempfile
from collections.abc import Collection, Iterator
from pathlib import Path

import pytest

pytest.importorskip("cv2")
pytest.importorskip("shapely")
pytest.importorskip("trimesh")

from fastapi.testclient import TestClient  # noqa: E402
from httpx import Response  # noqa: E402

from contracts.schema import (  # noqa: E402
    FurnitureItem,
    ParsedFloorPlan,
    RoomScene,
    Vec2,
    WallSegment,
)
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
from services.reconstruction.room.correct import rescale_room  # noqa: E402
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
    routes.clear_corrections()
    with TestClient(app) as c:
        res = c.post("/floor-plans", files=[("files", (PLAN.name, PLAN.read_bytes(), "image/png"))])
        assert res.status_code == 200, res.text
        yield c
    app.dependency_overrides.clear()
    scenes.clear_cache()
    routes.clear_corrections()


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
    original = routes._originals.pop(PLAN_ID, None)
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
        routes._originals.pop(PLAN_ID, None)
        if recorded is not None and original is not None:
            routes._plans[PLAN_ID], routes._originals[PLAN_ID] = recorded, original
        app.dependency_overrides.clear()
        scenes.clear_cache()


def test_the_geometry_check_compares_shape_and_names_a_wrong_wall(client: TestClient) -> None:
    """The binding names a room by its shape: the user may correct its scale (#11)."""
    room = RoomScene.model_validate(
        client.get(f"/floor-plans/{PLAN_ID}/rooms/{BINDING.room_id}").json()
    )

    def stretched(factor: float, only: str | None = None) -> RoomScene:
        def at(p: Vec2) -> Vec2:
            return Vec2(x=p.x * factor, z=p.z * factor)

        walls = [
            w.model_copy(update={"end": at(w.end)})
            if only == w.id
            else w
            if only
            else w.model_copy(update={"start": at(w.start), "end": at(w.end)})
            for w in room.walls
        ]
        return room.model_copy(update={"walls": walls})

    assert geometry_mismatch(BINDING, stretched(1.03)) is None
    assert geometry_mismatch(BINDING, stretched(1.10)) is None  # a corrected scale
    assert geometry_mismatch(BINDING, stretched(0.5)) is None
    assert geometry_mismatch(BINDING, rescale_room(room, 1.2)) is None
    # A single wall out of proportion is another room (it also shifts the fitted scale, so
    # the first wall checked may be the one named).
    reason = geometry_mismatch(BINDING, stretched(1.3, only="w16"))
    assert reason is not None and " m, expected " in reason


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


# --- corrections (#11) ------------------------------------------------------------------------


def _put(client: TestClient, scene: RoomScene) -> RoomScene:
    res = client.put(f"/scenes/{scene.scene_id}", json=scene.model_dump(mode="json"))
    assert res.status_code == 200, res.text
    return RoomScene.model_validate(res.json())


def _rescale(client: TestClient, wall_id: str, length_m: float, revision: int) -> Response:
    params = {"wall_id": wall_id, "length_m": length_m, "revision": revision}
    return client.post(f"/scenes/{BINDING.scene_id}/scale", params=params)


def _length(wall: WallSegment) -> float:
    return math.dist((wall.start.x, wall.start.z), (wall.end.x, wall.end.z))


def _walls(scene: RoomScene) -> dict[str, float]:
    return {w.id: _length(w) for w in scene.walls}


def test_a_placement_correction_is_kept(
    client: TestClient, data_dir: Path, auditor: TestClient
) -> None:
    register_reviewed_items(data_dir)
    scene, _ = _scene(client)
    assert "placement" in _item(scene, CHAIR).correction_needed
    saved = _put(client, _moved(scene, CHAIR, 4.0, 8.6))
    reloaded, _ = _scene(client)
    assert reloaded == saved and reloaded.revision == 1
    chair = _item(reloaded, CHAIR)
    assert (chair.pose.x, chair.pose.z) == (4.0, 8.6)
    assert "placement" not in chair.correction_needed  # the user put it there
    assert "orientation" in chair.correction_needed  # not turned, so still to confirm
    for item_id in (SOFA, OTHER_SOFA, TABLE):
        assert _item(reloaded, item_id) == _item(scene, item_id)
    assert _audit(auditor, reloaded)["blocked_doors"] == []


def test_a_scale_correction_rescales_the_floor_and_carries_the_furniture(
    client: TestClient, data_dir: Path, auditor: TestClient
) -> None:
    register_reviewed_items(data_dir)
    scene, _ = _scene(client)
    saved = _put(client, _moved(scene, CHAIR, 4.0, 8.6))
    factor = 1.1
    res = _rescale(client, "w16", BINDING.walls_m["w16"] * factor, saved.revision)
    assert res.status_code == 200, res.text
    corrected = RoomScene.model_validate(res.json())
    assert corrected.revision == saved.revision + 1
    assert _scene(client)[0] == corrected  # kept

    for wall_id, length in _walls(saved).items():
        assert _walls(corrected)[wall_id] == pytest.approx(length * factor, abs=0.002)
    assert [w.height_m for w in corrected.walls] == [w.height_m for w in saved.walls]
    for before, after in zip(saved.doors, corrected.doors):
        assert after.width_m == pytest.approx(before.width_m * factor, abs=0.001)
        assert after.head_height_m == before.head_height_m

    # The shell is a new immutable file; the old URL is gone.
    assert corrected.shell_glb_url != saved.shell_glb_url
    shell = client.get(corrected.shell_glb_url.removeprefix(PROXY_PREFIX))
    assert shell.status_code == 200 and shell.content[:4] == b"glTF"
    assert client.get(saved.shell_glb_url.removeprefix(PROXY_PREFIX)).status_code == 404

    # Same items, meshes and sizes; poses carried; the user's correction survives.
    for before, after in zip(saved.furniture, corrected.furniture):
        assert after.model_dump(exclude={"pose"}) == before.model_dump(exclude={"pose"})
        assert after.pose.yaw_deg == before.pose.yaw_deg
    report = _audit(auditor, corrected)  # the audit accepts the corrected room
    assert report["out_of_bounds_item_ids"] == [] and report["collisions"] == []
    assert report["blocked_doors"] == []  # the moved chair is still clear of the door

    # Every room of the floor is corrected, and stays so on re-upload.
    upload = client.post(
        "/floor-plans", files=[("files", (PLAN.name, PLAN.read_bytes(), "image/png"))]
    )
    plan = ParsedFloorPlan.model_validate(upload.json())
    original = routes._originals[PLAN_ID]
    floor, parsed = plan.floors[0], original.floors[0]
    assert [r.room_id for r in floor.rooms] == [r.room_id for r in parsed.rooms]
    for room, before_room in zip(floor.rooms, parsed.rooms):
        assert room.dimension_source == "user_corrected"
        assert "dimensions" not in room.correction_needed
        assert room.area_m2 == pytest.approx(before_room.area_m2 * factor**2, rel=0.01)
        for wall_id, length in _walls(before_room.scene).items():
            assert _walls(room.scene)[wall_id] == pytest.approx(length * factor, abs=0.002)
    assert plan.floors[1:] == original.floors[1:]  # other floors are other drawings
    assert sum("scale corrected by the user" in w for w in plan.warnings) == 1


def test_every_kept_scene_of_the_floor_is_carried_over(client: TestClient, data_dir: Path) -> None:
    register_reviewed_items(data_dir)
    scene, _ = _scene(client)
    neighbour_id = f"{PLAN_ID}-floor-0-room-0"
    res = client.get(f"/scenes/{neighbour_id}")
    assert res.status_code == 200, res.text
    neighbour = RoomScene.model_validate(res.json())
    assert _rescale(client, "w16", 4.8, scene.revision).status_code == 200
    after = RoomScene.model_validate(client.get(f"/scenes/{neighbour_id}").json())
    factor = 4.8 / BINDING.walls_m["w16"]
    assert after.revision == neighbour.revision + 1  # kept, so its editor must reload
    for wall_id, length in _walls(neighbour).items():
        assert _walls(after)[wall_id] == pytest.approx(length * factor, abs=0.002)
    assert after.shell_glb_url != neighbour.shell_glb_url


def test_correcting_the_scale_back_restores_the_parsed_room(
    client: TestClient, data_dir: Path
) -> None:
    register_reviewed_items(data_dir)
    scene, _ = _scene(client)
    parsed = RoomScene.model_validate(
        client.get(f"/floor-plans/{PLAN_ID}/rooms/{BINDING.room_id}").json()
    )
    res = _rescale(client, "w16", 5.0, scene.revision)
    assert res.status_code == 200, res.text
    res = _rescale(client, "w16", BINDING.walls_m["w16"], scene.revision + 1)
    assert res.status_code == 200, res.text  # from the parse, so nothing compounds
    back = RoomScene.model_validate(res.json())
    assert back.model_dump(exclude={"furniture", "revision"}) == parsed.model_dump(
        exclude={"furniture", "revision"}
    )
    assert client.get(back.shell_glb_url.removeprefix(PROXY_PREFIX)).status_code == 200
    plan = client.get(f"/floor-plans/{PLAN_ID}").json()
    assert sum("scale corrected by the user" in w for w in plan["warnings"]) == 1  # replaced


def test_stale_and_invalid_corrections_are_refused(client: TestClient, data_dir: Path) -> None:
    register_reviewed_items(data_dir)
    scene, _ = _scene(client)
    url = f"/scenes/{BINDING.scene_id}"

    def put(edit: RoomScene) -> int:
        return client.put(url, json=edit.model_dump(mode="json")).status_code

    def with_item(**update: object) -> RoomScene:
        chair = _item(scene, CHAIR).model_copy(update=update)
        others = [item for item in scene.furniture if item.id != CHAIR]
        return scene.model_copy(update={"furniture": [*others, chair], "revision": 1})

    assert put(scene) == 409  # not newer than the kept revision
    assert put(with_item(id="vid-000099")) == 422  # unknown item
    bigger = _item(scene, CHAIR).bbox_m.model_copy(update={"width": 2.0})
    assert put(with_item(bbox_m=bigger)) == 422  # sizes are not a placement correction
    assert put(with_item(glb_url="/api/reconstruction/assets/other.glb")) == 422
    assert put(_moved(scene, CHAIR, 4.0, 8.6).model_copy(update={"scene_id": "other"})) == 422
    kept, _ = _scene(client)

    # Scale: unknown wall, implausible factor, a revision other than the kept one.
    assert _rescale(client, "w99", 4.0, kept.revision).status_code == 422
    assert _rescale(client, "w16", 40.0, kept.revision).status_code == 422
    assert _rescale(client, "w16", 0.0, kept.revision).status_code == 422
    assert _rescale(client, "w16", 4.5, kept.revision + 5).status_code == 409
    assert _rescale(client, "w16", 4.5, kept.revision).status_code == 200
    # An edit made against the room before the correction is stale.
    assert put(_moved(kept, CHAIR, 4.1, 8.6).model_copy(update={"revision": 99})) == 409
    demo = client.post(
        "/scenes/g-reception/scale", params={"wall_id": "w0", "length_m": 4, "revision": 0}
    )
    assert demo.status_code == 422
    unknown = client.put(
        "/scenes/nope", json=scene.model_copy(update={"scene_id": "nope"}).model_dump(mode="json")
    )
    assert unknown.status_code == 404


def test_an_added_correction_flag_is_refused(client: TestClient, data_dir: Path) -> None:
    register_reviewed_items(data_dir)
    scene, _ = _scene(client)
    table = _item(scene, TABLE)
    assert "orientation" in table.correction_needed
    cleared = [c for c in table.correction_needed if c != "orientation"]
    edit = scene.model_copy(
        update={
            "furniture": [table.model_copy(update={"correction_needed": cleared})],
            "revision": 1,
        }
    )
    assert _item(_put(client, edit), TABLE).correction_needed == cleared  # confirmed by the user
    readded = edit.model_copy(update={"furniture": [table], "revision": 2})
    res = client.put(f"/scenes/{BINDING.scene_id}", json=readded.model_dump(mode="json"))
    assert res.status_code == 422 and "cannot add" in res.text


def test_corrections_need_a_settled_scene(client: TestClient, data_dir: Path) -> None:
    """While its furniture is still being extracted the scene is not kept, so there is nothing
    to correct yet."""
    scene, warnings = _scene(client)
    assert warnings == [NOT_EXTRACTED]
    res = client.put(
        f"/scenes/{scene.scene_id}", json=_moved(scene, CHAIR, 1, 1).model_dump(mode="json")
    )
    assert res.status_code == 409
    assert _rescale(client, "w16", 4.5, scene.revision).status_code == 409


def test_a_rescaled_bound_room_still_gets_its_furniture_when_assembled_again(
    client: TestClient, data_dir: Path
) -> None:
    register_reviewed_items(data_dir)
    scene, _ = _scene(client)
    assert _rescale(client, "w16", 4.8, scene.revision).status_code == 200
    scenes.clear_cache()  # assembled from the corrected room, from scratch
    again, warnings = _scene(client)
    assert sorted(item.id for item in again.furniture) == ITEM_IDS
    assert not any("does not match" in w for w in warnings)
    assert _walls(again)["w16"] == pytest.approx(4.8, abs=0.002)


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
