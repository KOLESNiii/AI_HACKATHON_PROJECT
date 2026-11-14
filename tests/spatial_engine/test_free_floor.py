"""Free floor area is distinct from reachable walking space."""

import math

import pytest

from contracts.schema import BBoxM, CollisionPart, FurnitureItem, Pose2D, RoomScene, Vec2
from services.spatial_engine.audit import calculate_free_floor_ratio


def item(item_id: str = "desk", x: float = 2, z: float = 2) -> FurnitureItem:
    return FurnitureItem(
        id=item_id,
        name=item_id,
        category="desk",
        source="extracted_video",
        glb_url="/desk.glb",
        bbox_m=BBoxM(width=2, height=3, depth=2),
        pose=Pose2D(x=x, z=z),
    )


def room(furniture: list[FurnitureItem]) -> RoomScene:
    return RoomScene(
        scene_id="room",
        shell_glb_url="/shell.glb",
        floor_polygon=[Vec2(x=x, z=z) for x, z in [(0, 0), (4, 0), (4, 4), (0, 4)]],
        walls=[],
        doors=[],
        windows=[],
        furniture=furniture,
    )


def test_empty_room_is_entirely_free() -> None:
    assert calculate_free_floor_ratio(room([])) == 1


def test_solid_bbox_fallback() -> None:
    assert calculate_free_floor_ratio(room([item()])) == pytest.approx(12 / 16)


def test_union_avoids_double_counting_items() -> None:
    assert calculate_free_floor_ratio(room([item("a"), item("b")])) == pytest.approx(12 / 16)
    assert calculate_free_floor_ratio(room([item("a"), item("b", x=3)])) == pytest.approx(10 / 16)


def test_fixed_items_block_floor() -> None:
    fixed = item()
    fixed.category, fixed.is_fixed = "fixture", True
    assert calculate_free_floor_ratio(room([fixed])) == pytest.approx(12 / 16)


@pytest.mark.parametrize(("bottom", "ratio"), [(0.7, 0.75), (1.999, 0.75), (2, 1), (2.1, 1)])
def test_headroom_threshold_and_low_overhang(bottom: float, ratio: float) -> None:
    furniture = item()
    furniture.collision_parts = [CollisionPart(x=0, z=0, width=2, depth=2, y_min=bottom, y_max=3)]
    assert calculate_free_floor_ratio(room([furniture])) == pytest.approx(ratio)


def test_sparse_parts_use_actual_projection_and_union() -> None:
    furniture = item()
    furniture.collision_parts = [
        CollisionPart(x=-0.75, z=0, width=0.5, depth=2, y_min=0, y_max=1),
        CollisionPart(x=0.75, z=0, width=0.5, depth=2, y_min=0, y_max=1),
        CollisionPart(x=0.75, z=0, width=0.5, depth=2, y_min=0.5, y_max=1.5),
    ]
    assert calculate_free_floor_ratio(room([furniture])) == pytest.approx(14 / 16)


def test_outside_parts_clipped_to_floor() -> None:
    assert calculate_free_floor_ratio(room([item(x=0)])) == pytest.approx(14 / 16)
    assert calculate_free_floor_ratio(room([item(x=-5)])) == 1


def test_fully_blocked_floor_is_zero() -> None:
    furniture = item()
    furniture.bbox_m.width = furniture.bbox_m.depth = 6
    assert calculate_free_floor_ratio(room([furniture])) == 0


def test_rotated_footprint_maintains_area_when_inside() -> None:
    furniture = item()
    furniture.pose.yaw_deg = 45
    assert calculate_free_floor_ratio(room([furniture])) == pytest.approx(12 / 16)


def test_concave_room_uses_actual_floor_area() -> None:
    scene = room([item(x=1, z=3)])
    scene.floor_polygon = [
        Vec2(x=x, z=z) for x, z in [(0, 0), (4, 0), (4, 2), (2, 2), (2, 4), (0, 4)]
    ]
    assert calculate_free_floor_ratio(scene) == pytest.approx(8 / 12)


def test_disconnected_free_regions_are_both_counted() -> None:
    furniture = item()
    furniture.bbox_m.width, furniture.bbox_m.depth = 1, 4
    # A dividing obstacle cuts the floor in two; this metric does not infer entry reachability.
    assert calculate_free_floor_ratio(room([furniture])) == pytest.approx(12 / 16)


def test_does_not_mutate_scene_and_order_does_not_matter() -> None:
    scene = room([item("a"), item("b", x=3)])
    before = scene.model_dump()
    ratio = calculate_free_floor_ratio(scene)
    assert scene.model_dump() == before
    scene.furniture.reverse()
    assert calculate_free_floor_ratio(scene) == ratio


def test_duplicate_ids_rejected() -> None:
    with pytest.raises(ValueError, match="IDs must be unique"):
        calculate_free_floor_ratio(room([item(), item()]))


def test_invalid_floor_rejected_even_when_empty() -> None:
    scene = room([])
    scene.floor_polygon[1].x = math.nan
    with pytest.raises(ValueError, match="Room floor"):
        calculate_free_floor_ratio(scene)


def test_invalid_part_above_headroom_still_rejected() -> None:
    furniture = item()
    furniture.collision_parts = [CollisionPart(x=0, z=0, width=1, depth=1, y_min=2, y_max=3)]
    furniture.collision_parts[0].width = -1
    with pytest.raises(ValueError):
        calculate_free_floor_ratio(room([furniture]))
