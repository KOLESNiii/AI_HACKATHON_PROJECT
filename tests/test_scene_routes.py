"""Scene assembly and `GET /scenes/{scene_id}` (Dev 1.5, #9): one room with its furniture,
loadable by the editor and accepted by the spatial audit."""

from __future__ import annotations

import json
import math
from collections.abc import Iterator

import pytest

pytest.importorskip("cv2")
pytest.importorskip("shapely")

from fastapi.testclient import TestClient  # noqa: E402

from contracts.schema import DoorOpening, Pose2D, RoomScene, Vec2  # noqa: E402
from services.reconstruction import scenes  # noqa: E402
from services.reconstruction.demo_assets import demo_room_scene, demo_rooms  # noqa: E402
from services.reconstruction.main import app  # noqa: E402
from services.reconstruction.room import footprint as fp  # noqa: E402
from services.reconstruction.room.annotate import FixedAnnotator, PlanAnnotations  # noqa: E402
from services.reconstruction.room.assemble import (  # noqa: E402
    NO_FURNITURE_YET,
    NoFurniture,
    SceneFurniture,
    assemble_scene,
)
from services.reconstruction.room.observe import FixedObserver  # noqa: E402
from services.reconstruction.room.openings import conform_openings  # noqa: E402
from services.reconstruction.room.routes import get_annotator  # noqa: E402
from services.spatial_engine.main import app as spatial_app  # noqa: E402
from tests.test_room_align import _box, _hint, _room  # noqa: E402
from tests.test_room_parse import _label, _png, single_room  # noqa: E402

PROXY_PREFIX = "/api/reconstruction"


@pytest.fixture()
def client() -> Iterator[TestClient]:
    ann = PlanAnnotations(rooms=[_label("Studio", 400, 350, 4.0, 3.0)])
    app.dependency_overrides[get_annotator] = lambda: FixedAnnotator(ann)
    scenes.clear_cache()
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    scenes.clear_cache()


@pytest.fixture(scope="module")
def auditor() -> TestClient:
    return TestClient(spatial_app)


def _scene(client: TestClient, scene_id: str) -> tuple[RoomScene, list[str]]:
    res = client.get(f"/scenes/{scene_id}")
    assert res.status_code == 200, res.text
    assert res.headers["cache-control"] == "no-cache"
    return RoomScene.model_validate(res.json()), json.loads(res.headers[scenes.WARNINGS_HEADER])


def _served(client: TestClient, url: str) -> int:
    assert url.startswith(f"{PROXY_PREFIX}/"), url
    return client.get(url.removeprefix(PROXY_PREFIX)).status_code


def _audit(auditor: TestClient, scene: RoomScene) -> dict[str, object]:
    res = auditor.post("/audit", json=scene.model_dump(mode="json"))
    assert res.status_code == 200, res.text
    report: dict[str, object] = res.json()
    assert report["scene_id"] == scene.scene_id
    return report


def _upload(client: TestClient) -> str:
    res = client.post(
        "/floor-plans", files=[("files", ("plan.png", _png(single_room()), "image/png"))]
    )
    assert res.status_code == 200, res.text
    scene_id: str = res.json()["floors"][0]["rooms"][0]["scene"]["scene_id"]
    return scene_id


# --- demo home --------------------------------------------------------------------------------


def test_demo_room_is_assembled_for_the_editor(client: TestClient, auditor: TestClient) -> None:
    scene, warnings = _scene(client, "g-reception")
    fixture = demo_room_scene("g-reception")
    assert scene.scene_id == "g-reception" and scene.revision == 0
    assert warnings == []
    assert [f.id for f in scene.furniture] == [f.id for f in fixture.furniture]
    reference = {f.id: f for f in fixture.furniture}
    for item in scene.furniture:
        ref = reference[item.id]
        assert math.hypot(item.pose.x - ref.pose.x, item.pose.z - ref.pose.z) < 0.01, item.id
        assert abs((item.pose.yaw_deg - ref.pose.yaw_deg + 180) % 360 - 180) < 1.5, item.id
        assert set(ref.correction_needed) <= set(item.correction_needed)
        assert item.glb_url == ref.glb_url and item.bbox_m == ref.bbox_m
    # The editor can load it: the shell and every model are served.
    urls = [scene.shell_glb_url, *(item.glb_url for item in scene.furniture)]
    assert {u: _served(client, u) for u in urls} == {u: 200 for u in urls}
    _audit(auditor, scene)


@pytest.mark.parametrize("room_id", sorted(demo_rooms()))
def test_every_demo_room_is_accepted_by_the_audit(
    room_id: str, client: TestClient, auditor: TestClient
) -> None:
    """The fixture's hinges sit ~0.4 µm off their walls, which the audit rejected (422)."""
    scene, _ = _scene(client, room_id)
    assert sorted(f.id for f in scene.furniture) == sorted(
        f.id for f in demo_room_scene(room_id).furniture
    )
    _audit(auditor, scene)


# --- uploaded floor plans ---------------------------------------------------------------------


def test_an_uploaded_room_has_no_furniture_yet_and_says_why(
    client: TestClient, auditor: TestClient
) -> None:
    scene_id = _upload(client)
    scene, warnings = _scene(client, scene_id)
    assert scene.furniture == [] and warnings == [NO_FURNITURE_YET]
    room = client.get(f"/floor-plans/{scene_id.split('-floor-')[0]}").json()
    parsed = RoomScene.model_validate(room["floors"][0]["rooms"][0]["scene"])
    assert scene.model_dump(exclude={"furniture"}) == parsed.model_dump(exclude={"furniture"})
    assert _served(client, scene.shell_glb_url) == 200
    _audit(auditor, scene)


def test_a_furniture_source_places_items_independently(
    client: TestClient, auditor: TestClient
) -> None:
    """The seam Dev 2's video pipeline plugs into: assets plus an observer, per room."""
    scene_id = _upload(client)
    sofa = _box("vid-sofa-01", width=1.6, depth=0.8, category="sofa")
    table = _box("vid-table-01", width=1.0, depth=0.6, category="table")

    class Video:
        def furniture_for(self, room: RoomScene) -> SceneFurniture:
            assert room.scene_id == scene_id
            frames = [f for w in room.walls if (f := fp.wall_frame(w)) is not None]
            west = max(frames, key=lambda f: f.inward[0]).wall  # its room side faces +X
            hints = [_hint(sofa.id, west.id, 0.5, facing="into_room")]
            return SceneFurniture(assets=[sofa, table], observer=FixedObserver(hints))

    app.dependency_overrides[scenes.get_furniture_source] = Video
    scene, warnings = _scene(client, scene_id)
    assert warnings == []
    placed = {f.id: f for f in scene.furniture}
    assert sorted(placed) == ["vid-sofa-01", "vid-table-01"]
    assert placed["vid-sofa-01"].correction_needed == []  # confident hint
    assert {"placement", "orientation"} <= set(placed["vid-table-01"].correction_needed)
    report = _audit(auditor, scene)
    assert report["collisions"] == [] and report["out_of_bounds_item_ids"] == []

    # Independent: moving one item in the editor changes nothing about the other.
    moved = placed["vid-table-01"].model_copy(
        update={"pose": placed["vid-table-01"].pose.model_copy(update={"x": 1.0})}
    )
    edited = scene.model_copy(update={"furniture": [placed["vid-sofa-01"], moved]})
    assert edited.furniture[0] == placed["vid-sofa-01"]
    _audit(auditor, edited)


def test_a_failing_source_still_returns_the_room(client: TestClient) -> None:
    scene_id = _upload(client)

    class Broken:
        def furniture_for(self, room: RoomScene) -> SceneFurniture:
            raise RuntimeError("provider down")

    app.dependency_overrides[scenes.get_furniture_source] = Broken
    scene, warnings = _scene(client, scene_id)
    assert scene.furniture == [] and warnings == ["furniture unavailable (RuntimeError)"]


def test_scenes_are_assembled_once_and_cached(client: TestClient) -> None:
    scene_id = _upload(client)
    calls = 0

    class Counting(NoFurniture):
        def furniture_for(self, room: RoomScene) -> SceneFurniture:
            nonlocal calls
            calls += 1
            return super().furniture_for(room)

    app.dependency_overrides[scenes.get_furniture_source] = Counting
    first = client.get(f"/scenes/{scene_id}")
    second = client.get(f"/scenes/{scene_id}")
    assert first.json() == second.json() and calls == 1


def test_unknown_scene_is_404(client: TestClient) -> None:
    assert client.get("/scenes/no-such-room").status_code == 404


# --- assembly and openings --------------------------------------------------------------------


def test_assembly_keeps_the_rooms_identity_and_furniture() -> None:
    kept = _box("kept").to_item(Pose2D(x=2.0, z=1.5, yaw_deg=0.0))
    room = _room().model_copy(update={"revision": 7, "furniture": [kept]})
    assembly = assemble_scene(room, NoFurniture())
    assert assembly.scene.scene_id == room.scene_id
    assert assembly.scene.shell_glb_url == room.shell_glb_url
    assert assembly.scene.revision == 0
    assert assembly.scene.furniture == [kept] and assembly.records == {}
    assert assembly.warnings == [NO_FURNITURE_YET]


def _door(x: float, z: float, width: float = 0.8, clockwise: bool = True) -> DoorOpening:
    return DoorOpening(
        id="d", wall_id="n", hinge_pos=Vec2(x=x, z=z), width_m=width, swing_clockwise=clockwise
    )


def _leaf_end(scene: RoomScene) -> tuple[float, float]:
    door = scene.doors[0]
    frame = fp.wall_frame(scene.walls[0])
    assert frame is not None
    leaf, _ = fp.closed_leaf(door, frame)
    return door.hinge_pos.x + leaf[0] * door.width_m, door.hinge_pos.z + leaf[1] * door.width_m


def test_conform_puts_an_off_line_hinge_on_its_wall() -> None:
    room = _room(doors=[_door(1.0, 0.0009)])  # 0.9 mm into the room, as parsed plans drift
    fixed, warnings = conform_openings(room)
    assert warnings == [] and fixed.doors[0].hinge_pos == Vec2(x=1.0, z=0.0)


def test_conform_pulls_an_overshooting_leaf_back_onto_the_wall() -> None:
    # Clockwise into the room on wall `n` (+X, room on +Z): the closed leaf runs toward +X.
    room = _room(doors=[_door(3.201, 0.0)])  # leaf ends 1 mm past the wall's end at x = 4
    fixed, warnings = conform_openings(room)
    assert warnings == []
    assert fixed.doors[0].hinge_pos.x == pytest.approx(3.2)
    assert _leaf_end(fixed)[0] == pytest.approx(4.0)
    assert fixed.doors[0].width_m == 0.8


def test_conform_leaves_large_errors_and_reports_them() -> None:
    room = _room(doors=[_door(1.0, 0.05)])  # 5 cm off: not rounding
    fixed, warnings = conform_openings(room)
    assert fixed == room
    assert warnings == ["door d is 50 mm off wall n; left unchanged"]


def test_conform_leaves_a_valid_room_unchanged() -> None:
    room = _room(doors=[_door(1.0, 0.0)])
    fixed, warnings = conform_openings(room)
    assert fixed is room and warnings == []
