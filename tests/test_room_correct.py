"""Room corrections (#11): rescaling a floor, carrying furniture over, and pose edits."""

from __future__ import annotations

import io
import math
from pathlib import Path

import pytest

from contracts.schema import FurnitureItem, ParsedFloor, ParsedRoom, Pose2D, RoomScene
from services.reconstruction.room import footprint as fp
from services.reconstruction.room.correct import (
    InvalidEdit,
    InvalidScale,
    StaleEdit,
    apply_pose_edit,
    carry_furniture,
    rescale_floor,
    rescale_room,
)
from services.reconstruction.room.openings import conform_openings

URL = "/api/reconstruction/shells/plan-x-floor-0-room-0.glb"


def room(width: float = 6.0, depth: float = 4.0) -> RoomScene:
    pts = [(0.0, 0.0), (width, 0.0), (width, depth), (0.0, depth)]
    walls = [
        {
            "id": f"w{i}",
            "start": {"x": pts[i][0], "z": pts[i][1]},
            "end": {"x": pts[(i + 1) % 4][0], "z": pts[(i + 1) % 4][1]},
            "thickness_m": 0.2,
        }
        for i in range(4)
    ]
    return RoomScene.model_validate(
        {
            "scene_id": "plan-x-floor-0-room-0",
            "shell_glb_url": URL,
            "floor_polygon": [{"x": x, "z": z} for x, z in pts],
            "walls": walls,
            "windows": [
                {
                    "id": "win0",
                    "wall_id": "w0",
                    "offset_along_wall_m": 1.0,
                    "width_m": 1.2,
                    "plan_normal_deg": 0.0,
                }
            ],
            "doors": [{"id": "door0", "wall_id": "w2", "hinge_pos": {"x": 5.0, "z": depth}}],
            "furniture": [],
        }
    )


def item(item_id: str, x: float, z: float, yaw: float, w: float, d: float) -> FurnitureItem:
    return FurnitureItem.model_validate(
        {
            "id": item_id,
            "name": item_id,
            "category": "storage",
            "source": "extracted_video",
            "glb_url": f"/api/reconstruction/assets/{item_id}.glb",
            "bbox_m": {"width": w, "height": 1.0, "depth": d},
            "pose": {"x": x, "z": z, "yaw_deg": yaw},
            "correction_needed": ["dimensions", "placement"],
        }
    )


def length(scene: RoomScene, wall_id: str) -> float:
    w = next(w for w in scene.walls if w.id == wall_id)
    return math.dist((w.start.x, w.start.z), (w.end.x, w.end.z))


def inside(scene: RoomScene, it: FurnitureItem) -> bool:
    poly = [(p.x, p.z) for p in scene.floor_polygon]
    return fp.covered_by(fp.footprint(it.bbox_m, it.pose).points, poly)


def test_rescaling_scales_plan_lengths_and_keeps_heights() -> None:
    before = room()
    after = rescale_room(before, 1.1)
    for wall, scaled in zip(before.walls, after.walls):  # exact products, never rounded
        assert (scaled.start.x, scaled.start.z) == (wall.start.x * 1.1, wall.start.z * 1.1)
        assert (scaled.end.x, scaled.end.z) == (wall.end.x * 1.1, wall.end.z * 1.1)
        assert scaled.thickness_m == wall.thickness_m * 1.1  # traced at image scale
        assert scaled.height_m == wall.height_m
    (win,) = after.windows
    assert (win.offset_along_wall_m, win.width_m) == (1.0 * 1.1, 1.2 * 1.1)
    assert (win.sill_height_m, win.plan_normal_deg) == (0.9, 0.0)
    (door,) = after.doors
    assert (door.hinge_pos.x, door.hinge_pos.z) == pytest.approx((5.5, 4.4), abs=1e-12)
    assert door.width_m == before.doors[0].width_m * 1.1
    assert door.head_height_m == before.doors[0].head_height_m
    assert conform_openings(after) == (after, [])  # every door exactly on its wall
    assert after.shell_glb_url.startswith(URL.removesuffix(".glb") + ".")  # a new file


def test_a_rescaled_shell_matches_the_rescaled_room() -> None:
    trimesh = pytest.importorskip("trimesh")
    pytest.importorskip("shapely")
    from services.reconstruction.room.shell import shell_glb

    after = rescale_room(room(), 1.25)
    shell = trimesh.load(io.BytesIO(shell_glb(after)), file_type="glb")
    lo, hi = shell.bounds
    t = 0.2 * 1.25  # walls extend outward by their thickness
    assert lo[0] == pytest.approx(-t, abs=1e-6) and hi[0] == pytest.approx(7.5 + t, abs=1e-6)
    assert lo[2] == pytest.approx(-t, abs=1e-6) and hi[2] == pytest.approx(5.0 + t, abs=1e-6)


def test_a_factor_of_one_is_the_parse() -> None:
    assert rescale_room(room(), 1.0) == room()


def test_a_rescaled_floor_has_user_corrected_dimensions() -> None:
    parsed = ParsedRoom(
        room_id="floor-0-room-0",
        name="Bedroom",
        area_m2=24.0,
        dimension_source="estimated",
        correction_needed=["dimensions", "openings"],
        scene=room(),
    )
    floor = ParsedFloor(
        floor_id="floor-0", name="Ground", level=0, source_image_index=0, rooms=[parsed]
    )
    (after,) = rescale_floor(floor, 0.5).rooms
    assert after.dimension_source == "user_corrected"
    assert after.correction_needed == ["openings"]
    assert after.area_m2 == 6.0
    assert length(after.scene, "w0") == pytest.approx(3.0)


def test_furniture_is_carried_along_its_wall_with_its_yaw() -> None:
    before = room()
    flush = item("wardrobe", 6.0 - 0.3, 2.0, 270.0, 1.0, 0.6)  # back on the east wall
    turned = item("table", 2.0, 2.0, 30.0, 0.8, 0.8)
    old = before.model_copy(update={"furniture": [flush, turned]})
    new = rescale_room(before, 1.5)
    result = carry_furniture(old, new)
    wardrobe, table = result.items
    assert (wardrobe.pose.x, wardrobe.pose.z) == pytest.approx((9.0 - 0.3, 3.0))  # still flush
    assert wardrobe.pose.yaw_deg == 270.0 and table.pose.yaw_deg == 30.0
    for a, b in ((flush, wardrobe), (turned, table)):
        assert b.model_dump(exclude={"pose"}) == a.model_dump(exclude={"pose"})
    assert {r.method for r in result.records.values()} == {"kept"}


def test_an_item_pushed_out_of_a_smaller_room_is_placed_again() -> None:
    before = room()
    middle = item("chest", 3.0, 2.0, 0.0, 0.5, 0.5)  # 1.75 m from the north wall
    old = before.model_copy(update={"furniture": [middle]})
    new = rescale_room(before, 0.5)  # 3 x 2 m: 1.75 m from that wall is on the far one
    result = carry_furniture(old, new)
    (moved,) = result.items
    assert inside(new, moved)
    record = result.records["chest"]
    assert record.notes[0].startswith("left the room") and 0 < record.moved_m <= 0.3
    assert moved.pose.yaw_deg == 0.0 and moved.correction_needed == middle.correction_needed


def test_a_displaced_item_keeps_the_users_rotation() -> None:
    """PR #59 review: a turned item pushed out of a smaller room kept a wall-aligned yaw."""
    before = room()
    turned = item("chest", 3.0, 2.0, 30.0, 0.5, 0.5).model_copy(update={"correction_needed": []})
    beside = item("box", 1.5, 0.3, 0.0, 0.6, 0.6)  # flush with the north wall: stays inside
    old = before.model_copy(update={"furniture": [turned, beside]})
    new = rescale_room(before, 0.5)
    result = carry_furniture(old, new)
    chest, box = result.items
    assert chest.pose.yaw_deg == 30.0  # the user's, not the wall's
    assert inside(new, chest)
    parts = [fp.occupied(i.bbox_m, i.collision_parts, i.pose) for i in (chest, box)]
    assert not fp.any_overlap(*parts)
    assert "orientation" not in chest.correction_needed  # nothing about its front is new
    assert result.records["chest"].moved_m > 0 and result.records["box"].moved_m == 0


def test_an_item_that_fits_nowhere_stays_where_carried_and_is_flagged() -> None:
    before = room()
    huge = item("bed", 3.0, 2.0, 0.0, 3.5, 2.5).model_copy(update={"correction_needed": []})
    old = before.model_copy(update={"furniture": [huge]})
    result = carry_furniture(old, rescale_room(before, 0.5))  # 3 x 2 m: a 3.5 x 2.5 m bed
    (bed,) = result.items
    assert bed.correction_needed == ["placement"] and bed.pose.yaw_deg == 0.0
    assert result.records["bed"].fits is False


def test_a_pose_edit_keeps_poses_only() -> None:
    kept = room().model_copy(
        update={
            "furniture": [
                item("a", 1.0, 1.0, 0.0, 0.5, 0.5),
                item("b", 3.0, 1.0, 0.0, 0.5, 0.5).model_copy(
                    update={"correction_needed": ["placement", "orientation"]}
                ),
            ]
        }
    )
    a, b = kept.furniture
    turned = b.model_copy(update={"pose": Pose2D(x=3.0, z=1.0, yaw_deg=90.0)})
    edit = kept.model_copy(update={"furniture": [turned], "revision": 3, "sun_hour": 9.0})
    saved = apply_pose_edit(kept, edit)
    assert saved.revision == 3 and saved.sun_hour == 9.0
    assert saved.furniture[0] == a  # left out of the edit: unchanged
    assert saved.furniture[1].pose.yaw_deg == 90.0
    assert saved.furniture[1].correction_needed == ["placement"]  # turned, not moved

    with pytest.raises(StaleEdit):
        apply_pose_edit(saved, edit)  # not newer
    with pytest.raises(StaleEdit):
        apply_pose_edit(kept, edit.model_copy(update={"walls": rescale_room(kept, 2).walls}))
    with pytest.raises(InvalidEdit, match="twice"):
        apply_pose_edit(kept, edit.model_copy(update={"furniture": [turned, turned]}))
    for bad in ({"x": math.nan}, {"z": math.inf}, {"yaw_deg": -math.inf}):
        pose = turned.pose.model_copy(update=bad)
        nan_edit = edit.model_copy(update={"furniture": [turned.model_copy(update={"pose": pose})]})
        with pytest.raises(InvalidEdit, match="finite"):
            apply_pose_edit(kept, nan_edit)
    with pytest.raises(InvalidEdit, match="is_proxy"):
        proxy = turned.model_copy(update={"is_proxy": True})
        apply_pose_edit(kept, edit.model_copy(update={"furniture": [proxy]}))


FIXTURES = Path(__file__).resolve().parents[1] / "services/reconstruction/room/fixtures"
EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
FACTORS = (0.25, 0.33, 0.5, 0.9, 1.1, 2.0, 4.0)


@pytest.mark.parametrize(
    ("image", "annotations"),
    [
        ("three_floor.png", "three_floor.annotations.json"),
        ("one_floor.jpg", "one_floor.annotations.json"),
    ],
)
def test_every_example_room_is_rescaled_validly_or_refused(image: str, annotations: str) -> None:
    """PR #59 review: rounding made a door wider than its rescaled wall (the audit refused the
    room), and a small factor broke the contract (HTTP 500). Every room of both example plans,
    at factors across the allowed range: either `InvalidScale`, or a room the audit accepts."""
    pytest.importorskip("cv2")
    pytest.importorskip("shapely")
    from fastapi.testclient import TestClient

    from services.reconstruction.room.annotate import FixedAnnotator, PlanAnnotations
    from services.reconstruction.room.parse import parse_floor_plan
    from services.spatial_engine.main import app

    if not (EXAMPLES / image).exists():
        pytest.skip("example plan missing")
    labels = PlanAnnotations.model_validate_json((FIXTURES / annotations).read_text())
    plan = parse_floor_plan(
        [((EXAMPLES / image).read_bytes(), "image/png")], FixedAnnotator(labels)
    )
    audit = TestClient(app)
    refused = []
    for factor in FACTORS:
        for floor in plan.floors:
            try:
                corrected = rescale_floor(floor, factor)
            except InvalidScale as exc:
                refused.append((factor, str(exc)))
                continue
            for parsed in corrected.rooms:
                scene = parsed.scene
                assert conform_openings(scene)[1] == [], (factor, parsed.room_id)
                res = audit.post("/audit", json=scene.model_dump(mode="json"))
                assert res.status_code == 200, (factor, parsed.room_id, res.text)
    assert all(factor < 0.5 for factor, _ in refused), refused  # only narrow features, small


def test_a_door_that_fills_a_diagonal_wall_still_fits_it() -> None:
    """The reviewer's case in miniature: a 45-degree wall whose door is exactly as wide."""
    pts = [(0.0, 0.0), (3.0, 0.0), (3.0, 2.0), (2.567, 2.433), (0.0, 2.433)]
    walls = [
        {
            "id": f"w{i}",
            "start": {"x": pts[i][0], "z": pts[i][1]},
            "end": {"x": pts[(i + 1) % 5][0], "z": pts[(i + 1) % 5][1]},
        }
        for i in range(5)
    ]
    diagonal = math.dist(pts[2], pts[3])
    base = RoomScene.model_validate(
        {
            "scene_id": "diag",
            "shell_glb_url": "/api/reconstruction/shells/diag.glb",
            "floor_polygon": [{"x": x, "z": z} for x, z in pts],
            "walls": walls,
            "windows": [],
            "doors": [
                {
                    "id": "door0",
                    "wall_id": "w2",
                    "hinge_pos": {"x": 3.0, "z": 2.0},
                    "width_m": round(diagonal, 3),
                }
            ],
            "furniture": [],
        }
    )
    base, _ = conform_openings(base)
    for factor in FACTORS:
        scaled = rescale_room(base, factor)
        (door,) = scaled.doors
        assert door.width_m <= length(scaled, "w2") + 1e-12, factor
