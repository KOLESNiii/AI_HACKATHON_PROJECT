"""Door sweep checks using the shared stored hinge and opening conventions."""

import math
from pathlib import Path

import pytest
from shapely.geometry import Point

from contracts.schema import (
    BBoxM,
    BlockedDoorIssue,
    CollisionPart,
    DoorOpening,
    FurnitureItem,
    Pose2D,
    RoomScene,
    Vec2,
    WallSegment,
)
from services.spatial_engine.audit import detect_blocked_doors
from services.spatial_engine.geometry import door_swing_sector


def item(item_id: str = "desk", x: float = 2.4, z: float = 0.4) -> FurnitureItem:
    return FurnitureItem(
        id=item_id,
        name=item_id,
        category="desk",
        source="extracted_video",
        glb_url="/desk.glb",
        bbox_m=BBoxM(width=0.1, height=1, depth=0.1),
        pose=Pose2D(x=x, z=z),
    )


def scene() -> RoomScene:
    return RoomScene(
        scene_id="room",
        shell_glb_url="/shell.glb",
        floor_polygon=[Vec2(x=x, z=z) for x, z in [(0, 0), (4, 0), (4, 4), (0, 4)]],
        walls=[WallSegment(id="wall", start=Vec2(x=0, z=0), end=Vec2(x=4, z=0))],
        doors=[DoorOpening(id="door", wall_id="wall", hinge_pos=Vec2(x=2, z=0), width_m=1)],
        windows=[],
        furniture=[],
    )


@pytest.mark.parametrize(
    ("clockwise", "inward", "x", "z"),
    [
        (True, True, 2.4, 0.4),
        (False, True, 1.6, 0.4),
        (True, False, 1.6, -0.4),
        (False, False, 2.4, -0.4),
    ],
)
@pytest.mark.parametrize("reverse_wall", [False, True])
@pytest.mark.parametrize("reverse_floor", [False, True])
def test_opening_direction_independent_of_winding(
    clockwise: bool, inward: bool, x: float, z: float, reverse_wall: bool, reverse_floor: bool
) -> None:
    room = scene()
    room.doors[0].swing_clockwise = clockwise
    room.doors[0].swings_into_room = inward
    if reverse_wall:
        room.walls[0].start, room.walls[0].end = room.walls[0].end, room.walls[0].start
    if reverse_floor:
        room.floor_polygon.reverse()
    room.furniture = [item(x=x, z=z)]
    assert detect_blocked_doors(room) == [
        BlockedDoorIssue(door_id="door", blocked_by_item_id="desk")
    ]
    room.furniture = [item(x=4 - x, z=-z)]
    assert detect_blocked_doors(room) == []


@pytest.mark.parametrize(
    ("start", "end", "hinge", "obstacle"),
    [
        ((4, 0), (4, 4), (4, 2), (3.6, 2.4)),
        ((4, 4), (0, 4), (2, 4), (1.6, 3.6)),
        ((0, 4), (0, 0), (0, 2), (0.4, 1.6)),
    ],
)
def test_other_wall_orientations(
    start: tuple[float, float],
    end: tuple[float, float],
    hinge: tuple[float, float],
    obstacle: tuple[float, float],
) -> None:
    room = scene()
    room.walls[0].start = Vec2(x=start[0], z=start[1])
    room.walls[0].end = Vec2(x=end[0], z=end[1])
    room.doors[0].hinge_pos = Vec2(x=hinge[0], z=hinge[1])
    room.furniture = [item(x=obstacle[0], z=obstacle[1])]
    assert len(detect_blocked_doors(room)) == 1


def test_opening_angle_limits_the_sweep() -> None:
    room = scene()
    room.furniture = [item()]
    room.doors[0].swing_angle_deg = 20
    assert detect_blocked_doors(room) == []
    room.doors[0].swing_angle_deg = 60
    assert len(detect_blocked_doors(room)) == 1
    room.doors[0].swing_angle_deg = 0
    assert detect_blocked_doors(room) == []
    room.doors[0].swing_angle_deg = 180
    room.furniture = [item(x=1.6, z=0.4)]
    assert len(detect_blocked_doors(room)) == 1


def test_sector_contains_true_arc_and_has_bounded_area_error() -> None:
    room = scene()
    sector = door_swing_sector(room.doors[0], room.walls[0], room.floor_polygon)
    for angle in [0.5, 20.5, 45.5, 89.5]:
        a = math.radians(angle)
        assert sector.covers(Point(2 + math.cos(a), math.sin(a)))
    assert math.pi / 4 <= sector.area < math.pi / 4 + 0.00003


def test_boundary_contact_and_outside_radius_are_clear() -> None:
    room = scene()
    room.furniture = [item(x=2.4, z=-0.05), item("far", x=3.2, z=0.4)]
    assert detect_blocked_doors(room) == []


def test_multiple_blockers_stable_order_and_no_mutation() -> None:
    room = scene()
    room.furniture = [item("z"), item("a")]
    room.doors.append(room.doors[0].model_copy(update={"id": "another"}))
    before = room.model_dump()
    assert [(i.door_id, i.blocked_by_item_id) for i in detect_blocked_doors(room)] == [
        ("another", "a"),
        ("another", "z"),
        ("door", "a"),
        ("door", "z"),
    ]
    assert room.model_dump() == before


def test_rotated_furniture_uses_its_footprint() -> None:
    room = scene()
    obstacle = item(x=2.7, z=0.7)
    obstacle.bbox_m = BBoxM(width=0.05, height=1, depth=0.6)
    obstacle.pose.yaw_deg = 45
    room.furniture = [obstacle]
    assert len(detect_blocked_doors(room)) == 1


def test_concave_room_wall() -> None:
    room = scene()
    room.floor_polygon = [
        Vec2(x=x, z=z) for x, z in [(0, 0), (4, 0), (4, 2), (2, 2), (2, 4), (0, 4)]
    ]
    room.walls[0].start, room.walls[0].end = Vec2(x=2, z=2), Vec2(x=2, z=4)
    room.doors[0].hinge_pos = Vec2(x=2, z=3)
    room.furniture = [item(x=1.6, z=3.4)]
    assert len(detect_blocked_doors(room)) == 1


@pytest.mark.parametrize("field", ["walls", "doors", "furniture"])
def test_duplicate_ids_rejected(field: str) -> None:
    room = scene()
    room.furniture = [item()]
    entries = getattr(room, field)
    entries.append(entries[0].model_copy(deep=True))
    with pytest.raises(ValueError, match="IDs must be unique"):
        detect_blocked_doors(room)


def test_unknown_wall_rejected_even_without_furniture() -> None:
    room = scene()
    room.doors[0].wall_id = "missing"
    with pytest.raises(ValueError, match="unknown wall"):
        detect_blocked_doors(room)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("width_m", 0),
        ("width_m", -1),
        ("width_m", math.nan),
        ("swing_angle_deg", -1),
        ("swing_angle_deg", 181),
        ("swing_angle_deg", math.inf),
    ],
)
def test_invalid_door_rejected(field: str, value: float) -> None:
    room = scene()
    setattr(room.doors[0], field, value)
    with pytest.raises(ValueError):
        detect_blocked_doors(room)


@pytest.mark.parametrize(
    "case", ["off_wall", "beyond_wall", "leaf_too_long", "zero_wall", "interior_wall"]
)
def test_invalid_wall_or_hinge(case: str) -> None:
    room = scene()
    if case == "off_wall":
        room.doors[0].hinge_pos.z = 0.1
    elif case == "beyond_wall":
        room.doors[0].hinge_pos.x = 5
    elif case == "leaf_too_long":
        room.doors[0].hinge_pos.x = 3.5
    elif case == "zero_wall":
        room.walls[0].end = room.walls[0].start.model_copy()
    else:
        room.walls[0].start.z = room.walls[0].end.z = 1
    with pytest.raises(ValueError):
        detect_blocked_doors(room)


@pytest.mark.parametrize("tolerance", [-1, math.nan, math.inf])
def test_invalid_area_tolerance(tolerance: float) -> None:
    with pytest.raises(ValueError, match="tolerance"):
        detect_blocked_doors(scene(), area_tolerance_m2=tolerance)


def test_shared_fixture_wardrobe_blocks_door_and_can_be_moved_clear() -> None:
    path = Path(__file__).resolve().parents[2] / "contracts/mock_room/mock_scene.json"
    room = RoomScene.model_validate_json(path.read_text(encoding="utf-8"))
    assert detect_blocked_doors(room) == [
        BlockedDoorIssue(door_id="door_1", blocked_by_item_id="item_wardrobe")
    ]
    wardrobe = next(item for item in room.furniture if item.id == "item_wardrobe")
    wardrobe.pose.x = 2
    assert detect_blocked_doors(room) == []


def test_empty_scene_and_invalid_furniture() -> None:
    room = scene()
    assert detect_blocked_doors(room) == []
    room.doors = []
    room.furniture = [item()]
    room.furniture[0].bbox_m.width = -1
    with pytest.raises(ValueError):
        detect_blocked_doors(room)


@pytest.mark.parametrize(
    ("bottom", "blocked"),
    [
        (2.1, False),
        (2.05, False),
        (2.049, False),
        (2.045, False),
        (2.04, True),
        (0, True),
    ],
)
def test_parts_must_overlap_door_height(bottom: float, blocked: bool) -> None:
    room = scene()
    obstacle = item()
    obstacle.bbox_m.height = 3
    obstacle.collision_parts = [
        CollisionPart(x=0, z=0, width=0.1, depth=0.1, y_min=bottom, y_max=3)
    ]
    room.furniture = [obstacle]
    assert bool(detect_blocked_doors(room)) is blocked


def test_door_uses_stored_head_height() -> None:
    room = scene()
    obstacle = item()
    obstacle.bbox_m.height = 3
    obstacle.collision_parts = [CollisionPart(x=0, z=0, width=0.1, depth=0.1, y_min=2.1, y_max=3)]
    room.furniture = [obstacle]
    assert detect_blocked_doors(room) == []
    room.doors[0].head_height_m = 2.5
    assert len(detect_blocked_doors(room)) == 1


def test_bbox_overlap_but_parts_clear_door() -> None:
    room = scene()
    obstacle = item(x=3.2, z=0.4)
    obstacle.bbox_m.width = 2
    obstacle.collision_parts = [CollisionPart(x=0.8, z=0, width=0.1, depth=0.1, y_min=0, y_max=1)]
    room.furniture = [obstacle]
    assert detect_blocked_doors(room) == []
    obstacle.collision_parts[0].x = -0.8
    assert len(detect_blocked_doors(room)) == 1


def test_multiple_blocking_parts_report_pair_once_and_include_fixed_items() -> None:
    room = scene()
    obstacle = item()
    obstacle.is_fixed = True
    obstacle.collision_parts = [CollisionPart(x=0, z=0, width=0.1, depth=0.1, y_min=0, y_max=1)] * 2
    room.furniture = [obstacle]
    assert len(detect_blocked_doors(room)) == 1


@pytest.mark.parametrize("height", [0, -1, math.nan, math.inf])
def test_invalid_door_head_height(height: float) -> None:
    room = scene()
    room.doors[0].head_height_m = height
    with pytest.raises(ValueError):
        detect_blocked_doors(room)


def test_shared_door_area_threshold() -> None:
    room = scene()
    obstacle = item()
    obstacle.bbox_m.width = obstacle.bbox_m.depth = 0.005
    room.furniture = [obstacle]
    assert detect_blocked_doors(room) == []
    assert len(detect_blocked_doors(room, area_tolerance_m2=0)) == 1
