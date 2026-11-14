"""Front access distance across the whole width, including rotated arrangements."""

import math
from pathlib import Path

import pytest

from contracts.schema import BBoxM, CollisionPart, FurnitureItem, Pose2D, RoomScene, Vec2
from services.spatial_engine.audit import detect_front_clearance


def item(item_id: str = "target", x: float = 2, z: float = 2) -> FurnitureItem:
    return FurnitureItem(
        id=item_id,
        name=item_id,
        category="wardrobe",
        source="extracted_video",
        glb_url="/mesh.glb",
        bbox_m=BBoxM(width=1, height=3, depth=1),
        pose=Pose2D(x=x, z=z),
        requires_front_clear_m=1,
    )


def room(furniture: list[FurnitureItem]) -> RoomScene:
    return RoomScene(
        scene_id="room",
        shell_glb_url="/shell.glb",
        floor_polygon=[Vec2(x=x, z=z) for x, z in [(0, 0), (6, 0), (6, 6), (0, 6)]],
        walls=[],
        windows=[],
        doors=[],
        furniture=furniture,
    )


def obstacle(x: float = 2, z: float = 3.5) -> FurnitureItem:
    furniture = item("blocker", x, z)
    furniture.requires_front_clear_m = 0
    return furniture


def test_clear_self_and_zero_requirement() -> None:
    assert detect_front_clearance(room([])) == []
    assert detect_front_clearance(room([item()])) == []
    target = item()
    target.requires_front_clear_m = 0
    assert detect_front_clearance(room([target, obstacle()])) == []


def test_furniture_blocker_distance() -> None:
    result = detect_front_clearance(room([item(), obstacle()]))
    assert len(result) == 1
    assert result[0].item_id == "target"
    assert result[0].blocked_by_item_id == "blocker"
    assert result[0].required_m == 1
    assert result[0].actual_m == pytest.approx(0.5)


@pytest.mark.parametrize(("x", "z"), [(2, 4), (3, 3), (2, 1)])
def test_touching_far_edge_side_edge_and_behind_are_clear(x: float, z: float) -> None:
    assert detect_front_clearance(room([item(), obstacle(x, z)])) == []


def test_blocker_overlapping_front_edge_has_zero_clearance() -> None:
    result = detect_front_clearance(room([item(), obstacle(z=2.5)]))
    assert result[0].actual_m == 0


@pytest.mark.parametrize("yaw", [0, 45, 90, 180, 270, -90])
def test_rotation_uses_full_width_not_centre_ray(yaw: float) -> None:
    target = item(x=3, z=3)
    target.pose.yaw_deg = yaw
    angle = math.radians(yaw)
    # Small blocker only across one side of the strip, 0.5 m from its front.
    local_x, local_z = 0.4, 1.1
    blocker = obstacle(
        x=3 + local_x * math.cos(angle) + local_z * math.sin(angle),
        z=3 - local_x * math.sin(angle) + local_z * math.cos(angle),
    )
    blocker.bbox_m.width = blocker.bbox_m.depth = 0.2
    blocker.pose.yaw_deg = yaw
    result = detect_front_clearance(room([target, blocker]))
    assert len(result) == 1
    assert result[0].actual_m == pytest.approx(0.5)


def test_room_boundary_limits_clearance_and_exact_contact_allowed() -> None:
    result = detect_front_clearance(room([item(z=5)]))
    assert len(result) == 1
    assert result[0].blocked_by_item_id is None
    assert result[0].actual_m == pytest.approx(0.5)
    assert detect_front_clearance(room([item(z=4.5)])) == []


def test_concave_floor_notch_catches_side_obstruction() -> None:
    scene = room([item()])
    scene.floor_polygon = [
        Vec2(x=x, z=z)
        for x, z in [(0, 0), (6, 0), (6, 6), (2.4, 6), (2.4, 3), (2.2, 3), (2.2, 6), (0, 6)]
    ]
    result = detect_front_clearance(scene)
    assert len(result) == 1
    assert result[0].blocked_by_item_id is None
    assert result[0].actual_m == pytest.approx(0.5)


def test_chair_is_ignored_but_not_other_categories() -> None:
    blocker = obstacle()
    blocker.category = "chair"
    assert detect_front_clearance(room([item(), blocker])) == []
    blocker.category, blocker.is_fixed = "fixture", True
    assert len(detect_front_clearance(room([item(), blocker]))) == 1


def test_chair_has_no_own_clearance_zone_but_still_occupies_space() -> None:
    from services.spatial_engine.audit import calculate_free_floor_ratio, detect_collisions

    chair = item()
    chair.category = "chair"
    assert detect_front_clearance(room([chair, obstacle()])) == []
    assert calculate_free_floor_ratio(room([chair])) < 1
    assert len(detect_collisions([chair, obstacle(z=2)])) == 1


@pytest.mark.parametrize(
    ("bottom", "blocks"), [(0.7, True), (1.99, True), (2, False), (2.1, False)]
)
def test_height_exception(bottom: float, blocks: bool) -> None:
    blocker = obstacle()
    blocker.collision_parts = [CollisionPart(x=0, z=0, width=1, depth=1, y_min=bottom, y_max=3)]
    assert bool(detect_front_clearance(room([item(), blocker]))) is blocks


def test_parts_outside_strip_do_not_block_even_if_bbox_does() -> None:
    blocker = obstacle(x=3)
    blocker.bbox_m.width = 3
    blocker.collision_parts = [CollisionPart(x=1, z=0, width=0.2, depth=1, y_min=0, y_max=1)]
    assert detect_front_clearance(room([item(), blocker])) == []


def test_multiple_parts_are_one_issue_per_blocker_and_order_is_stable() -> None:
    a, b = obstacle(), obstacle()
    a.id, b.id = "a", "b"
    a.collision_parts = [CollisionPart(x=0, z=0, width=1, depth=1, y_min=0, y_max=1)] * 2
    scene = room([item(), b, a])
    before = scene.model_dump()
    result = detect_front_clearance(scene)
    assert [issue.blocked_by_item_id for issue in result] == ["a", "b"]
    assert scene.model_dump() == before


@pytest.mark.parametrize("value", [-1, math.nan, math.inf])
def test_invalid_requirement_rejected(value: float) -> None:
    target = item()
    target.requires_front_clear_m = value
    with pytest.raises(ValueError, match="clearance"):
        detect_front_clearance(room([target]))


def test_duplicate_ids_and_invalid_geometry_rejected() -> None:
    with pytest.raises(ValueError, match="IDs must be unique"):
        detect_front_clearance(room([item(), item()]))
    scene = room([])
    scene.floor_polygon[0].x = math.nan
    with pytest.raises(ValueError):
        detect_front_clearance(scene)


def test_shared_fixture_reports_actual_access_requirements() -> None:
    path = Path(__file__).resolve().parents[2] / "contracts/mock_room/mock_scene.json"
    scene = RoomScene.model_validate_json(path.read_text(encoding="utf-8"))
    issues = detect_front_clearance(scene)
    assert [(issue.item_id, issue.blocked_by_item_id) for issue in issues] == [
        ("item_bed", "item_wardrobe"),
    ]
    assert [issue.actual_m for issue in issues] == pytest.approx([0.25])
