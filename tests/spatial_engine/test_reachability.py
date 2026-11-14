"""Door-seeded circulation with a 50 cm person, distinct from raw empty floor."""

import math
from pathlib import Path

import pytest

from contracts.schema import (
    BBoxM,
    CollisionPart,
    DoorOpening,
    FurnitureItem,
    Pose2D,
    RoomScene,
    Vec2,
    WallSegment,
)
from services.spatial_engine.audit import calculate_free_floor_ratio
from services.spatial_engine.reachability import calculate_reachable_floor_ratio


def room() -> RoomScene:
    return RoomScene(
        scene_id="room",
        shell_glb_url="/shell.glb",
        floor_polygon=[Vec2(x=x, z=z) for x, z in [(0, 0), (6, 0), (6, 6), (0, 6)]],
        walls=[WallSegment(id="north", start=Vec2(x=0, z=0), end=Vec2(x=6, z=0))],
        doors=[DoorOpening(id="entry", wall_id="north", hinge_pos=Vec2(x=1, z=0), width_m=1)],
        windows=[],
        furniture=[],
    )


def obstacle(item_id: str, x: float, z: float, width: float, depth: float) -> FurnitureItem:
    return FurnitureItem(
        id=item_id,
        name=item_id,
        category="fixture",
        is_fixed=True,
        source="extracted_video",
        glb_url="/fixture.glb",
        bbox_m=BBoxM(width=width, depth=depth, height=3),
        pose=Pose2D(x=x, z=z),
    )


def divided_room(gap: float) -> RoomScene:
    scene = room()
    scene.furniture = [obstacle("partition", 3, (6 - gap) / 2, 0.2, 6 - gap)]
    return scene


def test_empty_room_is_almost_entirely_reachable() -> None:
    scene = room()
    # A circular person cannot occupy the very tips of square corners.
    assert 0.99 < calculate_reachable_floor_ratio(scene) <= calculate_free_floor_ratio(scene)


@pytest.mark.parametrize(
    ("gap", "passes"), [(0.1, False), (0.49, False), (0.5, True), (0.51, True)]
)
def test_passage_width_threshold(gap: float, passes: bool) -> None:
    ratio = calculate_reachable_floor_ratio(divided_room(gap))
    assert (ratio > 0.9) is passes
    if not passes:
        assert ratio < 0.55


def test_all_door_regions_union_without_double_counting() -> None:
    scene = divided_room(0)
    one_door = calculate_reachable_floor_ratio(scene)
    scene.doors.append(
        DoorOpening(id="right", wall_id="north", hinge_pos=Vec2(x=4, z=0), width_m=1)
    )
    two_doors = calculate_reachable_floor_ratio(scene)
    assert one_door < 0.5 < 0.9 < two_doors <= calculate_free_floor_ratio(scene)
    scene.doors.append(scene.doors[0].model_copy(update={"id": "same-opening"}))
    assert calculate_reachable_floor_ratio(scene) == pytest.approx(two_doors)


def test_custom_width_changes_passage_access() -> None:
    scene = divided_room(0.4)
    assert calculate_reachable_floor_ratio(scene) < 0.55
    assert calculate_reachable_floor_ratio(scene, passage_width_m=0.3) > 0.9


@pytest.mark.parametrize(("width", "passes"), [(0.49, False), (0.5, True), (0.51, True)])
def test_door_must_be_wide_enough(width: float, passes: bool) -> None:
    scene = room()
    scene.doors[0].width_m = width
    assert (calculate_reachable_floor_ratio(scene) > 0) is passes


def test_furniture_blocking_entrance_prevents_seeding_far_side() -> None:
    scene = room()
    scene.furniture = [obstacle("entrance-blocker", 1.5, 0.15, 1.5, 0.1)]
    assert calculate_reachable_floor_ratio(scene) == 0
    assert calculate_free_floor_ratio(scene) > 0.99


def test_wide_door_uses_available_sides_not_just_midpoint() -> None:
    scene = room()
    scene.doors[0].width_m = 2
    scene.furniture = [obstacle("centre-blocker", 2, 0.15, 0.2, 0.1)]
    assert calculate_reachable_floor_ratio(scene) > 0.98


def test_outward_opening_uses_interior_entry() -> None:
    scene = room()
    scene.doors[0].hinge_pos.x = 2
    scene.doors[0].swings_into_room = False
    assert calculate_reachable_floor_ratio(scene) > 0.99


def test_headroom_parts_and_chairs_remain_walking_obstacles() -> None:
    scene = divided_room(0)
    partition = scene.furniture[0]
    partition.collision_parts = [CollisionPart(x=0, z=0, width=0.2, depth=6, y_min=2, y_max=3)]
    assert calculate_reachable_floor_ratio(scene) > 0.99
    partition.collision_parts[0].y_min = 1.99
    assert calculate_reachable_floor_ratio(scene) < 0.5
    partition.category, partition.is_fixed = "chair", False
    assert calculate_reachable_floor_ratio(scene) < 0.5


def test_short_door_cannot_seed_standing_access() -> None:
    scene = room()
    scene.doors[0].head_height_m = 1.9
    assert calculate_reachable_floor_ratio(scene) == 0


def test_fully_occupied_floor_is_zero() -> None:
    scene = room()
    scene.furniture = [obstacle("solid", 3, 3, 6, 6)]
    assert calculate_reachable_floor_ratio(scene) == 0


def test_enclosed_empty_pocket_is_not_reachable() -> None:
    scene = room()
    scene.furniture = [
        obstacle("top", 3, 2, 2, 0.2),
        obstacle("bottom", 3, 4, 2, 0.2),
        obstacle("left", 2, 3, 0.2, 2.4),
        obstacle("right", 4, 3, 0.2, 2.4),
    ]
    assert calculate_reachable_floor_ratio(scene) < calculate_free_floor_ratio(scene) - 0.08


def test_shared_fixture_result_is_bounded_by_free_floor() -> None:
    path = Path(__file__).resolve().parents[2] / "contracts/mock_room/mock_scene.json"
    scene = RoomScene.model_validate_json(path.read_text(encoding="utf-8"))
    assert 0 <= calculate_reachable_floor_ratio(scene) <= calculate_free_floor_ratio(scene)


@pytest.mark.parametrize("width", [0, -1, math.nan, math.inf])
def test_invalid_width(width: float) -> None:
    with pytest.raises(ValueError, match="Passage width"):
        calculate_reachable_floor_ratio(room(), passage_width_m=width)


def test_missing_door_is_unknown_not_clear() -> None:
    scene = room()
    scene.doors = []
    with pytest.raises(ValueError, match="at least one door"):
        calculate_reachable_floor_ratio(scene)


def test_unknown_wall_and_duplicate_ids_rejected() -> None:
    scene = room()
    scene.doors[0].wall_id = "missing"
    with pytest.raises(ValueError, match="unknown wall"):
        calculate_reachable_floor_ratio(scene)
    scene = room()
    scene.doors.append(scene.doors[0].model_copy())
    with pytest.raises(ValueError, match="IDs must be unique"):
        calculate_reachable_floor_ratio(scene)


def test_invalid_geometry_and_immutable_input() -> None:
    scene = divided_room(0.51)
    before = scene.model_dump()
    calculate_reachable_floor_ratio(scene)
    assert scene.model_dump() == before
    scene.furniture[0].bbox_m.height = math.nan
    with pytest.raises(ValueError):
        calculate_reachable_floor_ratio(scene)
