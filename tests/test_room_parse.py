"""Floor-plan parser (Dev 1): synthetic plans with known geometry, the two example plans, and
the floor-plan routes. No network: labels come from fixed annotations."""

from __future__ import annotations

import functools
import json
import math
from pathlib import Path

import pytest

cv2 = pytest.importorskip("cv2")
np = pytest.importorskip("numpy")

from contracts.schema import ParsedFloorPlan, ParsedRoom, RoomScene  # noqa: E402
from services.reconstruction.room.annotate import (  # noqa: E402
    FalVisionAnnotator,
    FixedAnnotator,
    FloorCaption,
    NullAnnotator,
    PlanAnnotations,
    RoomLabel,
    _extract_json,
)
from services.reconstruction.room.parse import _consensus, parse_floor_plan  # noqa: E402
from services.reconstruction.room.raster import UnreadableImage, decode  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples"
FIXTURES = ROOT / "services/reconstruction/room/fixtures"

PX_PER_M = 100  # synthetic plans are drawn at 1 cm per pixel
WALL = 20  # 0.2 m walls
W, H = 1000, 800


def _canvas() -> np.ndarray:
    return np.full((H, W, 3), 255, np.uint8)


def _wall(img: np.ndarray, x0: int, y0: int, x1: int, y1: int) -> None:
    cv2.rectangle(img, (x0, y0), (x1 - 1, y1 - 1), (0, 0, 0), -1)


def _png(img: np.ndarray) -> bytes:
    return bytes(cv2.imencode(".png", img)[1].tobytes())


def _label(name: str, x: float, y: float, w: float, d: float) -> RoomLabel:
    return RoomLabel(name=name, x=x / W, y=y / H, width_m=w, depth_m=d)


def _parse(img: np.ndarray, ann: PlanAnnotations | None) -> ParsedFloorPlan:
    annotator = FixedAnnotator(ann) if ann else NullAnnotator()
    return parse_floor_plan([(_png(img), "image/png")], annotator)


def _rooms(plan: ParsedFloorPlan) -> list[ParsedRoom]:
    return [r for f in plan.floors for r in f.rooms]


def _close(a: float, b: float, tol: float = 0.03) -> bool:
    return abs(a - b) <= tol


def _has_vertex(scene: RoomScene, x: float, z: float, tol: float = 0.03) -> bool:
    return any(_close(p.x, x, tol) and _close(p.z, z, tol) for p in scene.floor_polygon)


def _shoelace(scene: RoomScene) -> float:
    pts = [(p.x, p.z) for p in scene.floor_polygon]
    return sum(pts[i - 1][0] * pts[i][1] - pts[i][0] * pts[i - 1][1] for i in range(len(pts)))


# --- synthetic: one rectangular room with an exterior door and a window --------------------


def single_room() -> np.ndarray:
    """Interior 4.0 x 3.0 m at px (200..600, 200..500). Walls 0.2 m outside it.

    - Door gap in the top wall, x 300..380 (0.8 m). Hinge at x=300, leaf drawn open into the
      room (pointing down the page), arc to the free jamb at x=380.
    - Window in the bottom wall, x 350..500 (1.5 m), drawn as two glazing lines.
    """
    img = _canvas()
    _wall(img, 180, 180, 300, 200)  # top, left of door
    _wall(img, 380, 180, 620, 200)  # top, right of door
    _wall(img, 600, 180, 620, 520)  # right
    _wall(img, 180, 500, 350, 520)  # bottom, left of window
    _wall(img, 500, 500, 620, 520)  # bottom, right of window
    _wall(img, 180, 180, 200, 520)  # left
    cv2.line(img, (300, 200), (300, 280), (0, 0, 0), 2)  # open leaf
    cv2.ellipse(img, (300, 200), (80, 80), 0, 0, 90, (0, 0, 0), 1)  # swing arc
    cv2.line(img, (350, 505), (500, 505), (0, 0, 0), 2)  # glazing
    cv2.line(img, (350, 514), (500, 514), (0, 0, 0), 2)
    return img


@pytest.fixture(scope="module")
def single_plan() -> ParsedFloorPlan:
    ann = PlanAnnotations(rooms=[_label("Studio", 400, 350, 4.0, 3.0)])
    return _parse(single_room(), ann)


def test_single_room_polygon_is_metric_and_clockwise(single_plan: ParsedFloorPlan) -> None:
    (room,) = _rooms(single_plan)
    sc = room.scene
    assert room.name == "Studio" and room.dimension_source == "measured"
    assert "dimensions" not in room.correction_needed
    assert len(sc.floor_polygon) == 4 and len(sc.walls) == 4
    # Floor frame origin is the top-left of the walls (px 180, 180) => interior starts at 0.2 m.
    for x, z in [(0.2, 0.2), (4.2, 0.2), (4.2, 3.2), (0.2, 3.2)]:
        assert _has_vertex(sc, x, z), (x, z, sc.floor_polygon)
    assert _shoelace(sc) > 0
    assert _close(room.area_m2, 12.0, 0.3)
    assert all(_close(w.thickness_m, 0.2, 0.04) for w in sc.walls)
    assert sc.furniture == [] and sc.north_compass_deg is None
    assert sc.scene_id == f"{single_plan.plan_id}-{room.room_id}"
    assert sc.shell_glb_url.startswith("/")
    RoomScene.model_validate(sc.model_dump())


def test_single_room_door(single_plan: ParsedFloorPlan) -> None:
    sc = _rooms(single_plan)[0].scene
    (door,) = sc.doors
    wall = next(w for w in sc.walls if w.id == door.wall_id)
    assert _close(wall.start.z, 0.2) and _close(wall.end.z, 0.2)  # the top wall
    assert _close(door.hinge_pos.x, 1.2) and _close(door.hinge_pos.z, 0.2)
    assert _close(door.width_m, 0.8)
    assert door.swings_into_room
    # Closed leaf runs +X from the hinge; rotating it clockwise (viewed from above) points +Z,
    # which is into the room.
    assert door.swing_clockwise


def test_single_room_window(single_plan: ParsedFloorPlan) -> None:
    sc = _rooms(single_plan)[0].scene
    (win,) = sc.windows
    wall = next(w for w in sc.walls if w.id == win.wall_id)
    assert _close(wall.start.z, 3.2) and _close(wall.end.z, 3.2)  # the bottom wall
    # The bottom wall runs right -> left (clockwise winding), so the offset is from x = 4.2.
    assert _close(wall.start.x, 4.2)
    assert _close(win.offset_along_wall_m, 1.0) and _close(win.width_m, 1.5)
    assert _close(win.plan_normal_deg, 180.0, 0.5)  # outward = +Z = bearing 180
    assert win.compass_azimuth_deg is None


def test_compass_sets_north_and_window_azimuth() -> None:
    ann = PlanAnnotations(
        rooms=[_label("Studio", 400, 350, 4.0, 3.0)],
        compass={"north_bearing_deg": 90.0},  # type: ignore[arg-type]
    )
    sc = _rooms(_parse(single_room(), ann))[0].scene
    assert sc.north_compass_deg == 90.0
    assert _close(sc.windows[0].compass_azimuth_deg or 0.0, 90.0, 0.5)  # (180 - 90) mod 360


def test_without_labels_scale_is_estimated_and_flagged() -> None:
    plan = _parse(single_room(), None)
    (room,) = _rooms(plan)
    assert room.dimension_source == "estimated"
    assert "dimensions" in room.correction_needed and "orientation" in room.correction_needed
    assert room.name == "Unlabelled space 1" and room.labelled_width_m is None
    assert any("estimated" in w for w in plan.warnings)
    RoomScene.model_validate(room.scene.model_dump())


# --- synthetic: two rooms sharing an interior door ------------------------------------------


def two_rooms() -> np.ndarray:
    """Interiors: left 3.0 x 3.0 m (px 200..500), right 3.0 x 3.0 m (px 520..820), split by a
    0.2 m wall at x 500..520 with a 0.8 m door gap at y 300..380. The leaf is hinged at y=300
    and drawn open into the right room."""
    img = _canvas()
    _wall(img, 180, 180, 840, 200)
    _wall(img, 180, 500, 840, 520)
    _wall(img, 180, 180, 200, 520)
    _wall(img, 820, 180, 840, 520)
    _wall(img, 500, 180, 520, 300)
    _wall(img, 500, 380, 520, 520)
    cv2.line(img, (520, 300), (600, 300), (0, 0, 0), 2)
    cv2.ellipse(img, (520, 300), (80, 80), 0, 0, 90, (0, 0, 0), 1)
    return img


def test_conflicting_labels_are_not_trusted_as_measured() -> None:
    """Two identical rooms printed as 3 x 3 m and 6 x 6 m: no scale satisfies both, so the
    floor must not come back as measured (review on #39)."""
    ann = PlanAnnotations(
        rooms=[_label("Left", 350, 350, 3.0, 3.0), _label("Right", 670, 350, 6.0, 6.0)]
    )
    plan = _parse(two_rooms(), ann)
    rooms = _rooms(plan)
    assert len(rooms) == 2
    for r in rooms:
        assert r.dimension_source == "estimated"
        assert "dimensions" in r.correction_needed
    assert any("conflicting scales" in w for w in plan.warnings)


def test_scale_consensus_needs_a_majority() -> None:
    agree = _consensus([100.0, 101.0, 99.0, 200.0])
    assert agree.consistent and abs(agree.px_per_m - 100.0) < 1.0
    assert not _consensus([100.0, 200.0]).consistent
    assert _consensus([150.0]).consistent


def test_interior_door_is_shared_by_both_rooms() -> None:
    ann = PlanAnnotations(
        rooms=[_label("Left", 350, 350, 3.0, 3.0), _label("Right", 670, 350, 3.0, 3.0)]
    )
    plan = _parse(two_rooms(), ann)
    rooms = {r.name: r for r in _rooms(plan)}
    assert set(rooms) == {"Left", "Right"}
    (left_door,) = rooms["Left"].scene.doors
    (right_door,) = rooms["Right"].scene.doors
    # Same physical door in the shared floor frame.
    assert _close(left_door.width_m, 0.8) and _close(right_door.width_m, 0.8)
    assert _close(left_door.hinge_pos.z, 1.2) and _close(right_door.hinge_pos.z, 1.2)
    assert _close(left_door.hinge_pos.x, 3.2, 0.25) and _close(right_door.hinge_pos.x, 3.4, 0.25)
    # It opens into the right room only.
    assert right_door.swings_into_room and not left_door.swings_into_room
    assert all(not r.scene.windows for r in rooms.values())


# --- synthetic: L-shape and a 45-degree bay --------------------------------------------------


def l_room() -> np.ndarray:
    """L-shaped interior: 4 x 3 m with the 2 x 1.5 m bottom-right corner removed."""
    img = _canvas()
    _wall(img, 180, 180, 620, 200)
    _wall(img, 600, 180, 620, 370)
    _wall(img, 400, 350, 620, 370)
    _wall(img, 400, 350, 420, 520)
    _wall(img, 180, 500, 420, 520)
    _wall(img, 180, 180, 200, 520)
    return img


def test_l_shaped_room() -> None:
    ann = PlanAnnotations(rooms=[_label("L", 300, 300, 4.0, 3.0)])
    (room,) = _rooms(_parse(l_room(), ann))
    sc = room.scene
    assert len(sc.floor_polygon) == 6
    for x, z in [(0.2, 0.2), (4.2, 0.2), (4.2, 1.7), (2.2, 1.7), (2.2, 3.2), (0.2, 3.2)]:
        assert _has_vertex(sc, x, z, 0.05), (x, z, sc.floor_polygon)
    assert _shoelace(sc) > 0


def bay_room() -> np.ndarray:
    """4 x 3 m interior whose bottom-right corner is chamfered at 45 degrees (1 m legs). The
    middle 40% of the chamfer is a window drawn as two glazing lines."""
    img = _canvas()
    _wall(img, 180, 180, 620, 200)
    _wall(img, 600, 180, 620, 400)
    _wall(img, 180, 500, 500, 520)
    _wall(img, 180, 180, 200, 520)
    # Chamfer: interior face (600, 400) -> (500, 500); thickness extends outward (+x, +y).
    band = np.array(
        [[600, 400], [620, 400], [620, 420], [520, 520], [500, 520], [500, 500]], np.int32
    )
    cv2.fillPoly(img, [band], (0, 0, 0))
    gap = np.array([[570, 430], [530, 470], [560, 500], [600, 460]], np.int32)
    cv2.fillPoly(img, [gap], (255, 255, 255))
    for k in (5, 14):
        o = k / math.sqrt(2)
        cv2.line(
            img, (round(570 + o), round(430 + o)), (round(530 + o), round(470 + o)), (0, 0, 0), 2
        )
    return img


def test_bay_window_on_a_diagonal_wall() -> None:
    ann = PlanAnnotations(rooms=[_label("Bay", 350, 350, 4.0, 3.0)])
    (room,) = _rooms(_parse(bay_room(), ann))
    sc = room.scene
    diagonal = [
        w
        for w in sc.walls
        if not _close(w.start.x, w.end.x, 0.05) and not _close(w.start.z, w.end.z, 0.05)
    ]
    assert diagonal, sc.walls
    (win,) = sc.windows
    assert win.wall_id in {w.id for w in diagonal}
    assert _close(win.plan_normal_deg, 135.0, 5.0)  # outward normal points +X +Z


# --- the example plans ------------------------------------------------------------------------


@functools.cache
def _example(name: str, fixture: str) -> ParsedFloorPlan:
    ann = PlanAnnotations.model_validate_json((FIXTURES / fixture).read_text())
    data = (EXAMPLES / name).read_bytes()
    ctype = "image/png" if name.endswith(".png") else "image/jpeg"
    return parse_floor_plan([(data, ctype)], FixedAnnotator(ann))


def _rect_sides(scene: RoomScene) -> tuple[float, float]:
    pts = np.array([[p.x, p.z] for p in scene.floor_polygon], np.float32)
    (_, _), (a, b), _ = cv2.minAreaRect(pts)
    return max(a, b), min(a, b)


@pytest.mark.skipif(not (EXAMPLES / "one_floor.jpg").exists(), reason="example plan missing")
def test_one_floor_example() -> None:
    plan = _example("one_floor.jpg", "one_floor.annotations.json")
    assert len(plan.floors) == 1
    rooms = _rooms(plan)
    labelled = [r for r in rooms if r.labelled_width_m]
    assert sorted(r.name for r in labelled) == [
        "Bedroom 1",
        "Bedroom 2",
        "Bedroom 3",
        "Kitchen",
        "Reception Room",
    ]
    for r in labelled:
        assert r.dimension_source == "measured"
        got = _rect_sides(r.scene)
        want = sorted((r.labelled_width_m or 0, r.labelled_depth_m or 0), reverse=True)
        assert all(abs(g - w) / w <= 0.08 for g, w in zip(got, want)), (r.name, got, want)
    # Hallway and bathroom are found as unlabelled spaces.
    assert len(rooms) >= 7
    assert sum(len(r.scene.windows) for r in rooms) >= 8
    assert all(r.scene.doors for r in rooms)


@pytest.mark.skipif(not (EXAMPLES / "three_floor.png").exists(), reason="example plan missing")
def test_three_floor_example() -> None:
    plan = _example("three_floor.png", "three_floor.annotations.json")
    assert [(f.name, f.level) for f in plan.floors] == [
        ("Ground Floor", 0),
        ("First Floor", 1),
        ("Second Floor", 2),
    ]
    labelled = [r for r in _rooms(plan) if r.labelled_width_m or "/" in r.name]
    assert len(labelled) >= 10
    # The recorded model output reads the (partly cut-off) north arrow, so rooms are grounded.
    assert all(r.scene.north_compass_deg is not None for r in _rooms(plan))
    assert all("orientation" not in r.correction_needed for r in _rooms(plan))
    for f in plan.floors:
        assert len({r.room_id for r in f.rooms}) == len(f.rooms)
        for r in f.rooms:
            RoomScene.model_validate(r.scene.model_dump())
    # A traced size that disagrees with the printed label is flagged in the structured field,
    # not only in the warning text (review on #39).
    (bedroom2,) = [r for r in _rooms(plan) if r.name == "Bedroom (2)"]
    assert "dimensions" in bedroom2.correction_needed
    assert any(w.startswith("Bedroom (2): traced") for w in plan.warnings)


@pytest.mark.parametrize(
    "name, fixture",
    [
        ("one_floor.jpg", "one_floor.annotations.json"),
        ("three_floor.png", "three_floor.annotations.json"),
    ],
)
def test_every_example_room_is_accepted_by_the_audit(name: str, fixture: str) -> None:
    """Coordinates are rounded to the millimetre, which left hinges up to 0.9 mm off their walls
    and leaves up to 1 mm past them: the audit rejected 13 of these 30 rooms (422)."""
    if not (EXAMPLES / name).exists():
        pytest.skip("example plan missing")
    pytest.importorskip("shapely")
    from fastapi.testclient import TestClient

    from services.spatial_engine.main import app

    plan = _example(name, fixture)
    client = TestClient(app)
    rejected = {
        room.scene.scene_id: res.text
        for floor in plan.floors
        for room in floor.rooms
        if (res := client.post("/audit", json=room.scene.model_dump(mode="json"))).status_code
        != 200
    }
    assert rejected == {}
    assert not [w for w in plan.warnings if "off wall" in w]


def test_empty_or_corrupt_image_is_unreadable() -> None:
    for data in (b"", b"not an image"):
        with pytest.raises(UnreadableImage):
            decode(data)


# --- annotator --------------------------------------------------------------------------------


def test_fal_annotator_without_key_warns_and_returns_nothing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("FAL_KEY", raising=False)
    result = FalVisionAnnotator().annotate(b"", "image/png")
    assert result.annotations == PlanAnnotations()
    assert result.warnings and "FAL_KEY" in result.warnings[0]


def test_model_output_json_is_extracted() -> None:
    body = {
        "rooms": [{"name": "Kitchen", "x": 0.2, "y": 0.4, "width_m": 4.42, "depth_m": 3.3}],
        "floors": [{"name": "Ground Floor", "level": 0, "x": 0.5, "y": 0.9}],
        "compass": None,
    }
    text = "Here you go:\n```json\n" + json.dumps(body) + "\n```"
    ann = PlanAnnotations.model_validate_json(_extract_json(text))
    assert ann.rooms[0].width_m == 4.42 and ann.floors == [
        FloorCaption(name="Ground Floor", level=0, x=0.5, y=0.9)
    ]
