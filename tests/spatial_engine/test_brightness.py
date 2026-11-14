"""Analytic window-area cases for a declared geometric brightness proxy."""

import math

import pytest

from contracts.schema import (
    BBoxM,
    CollisionPart,
    FurnitureItem,
    Pose2D,
    RoomScene,
    Vec2,
    WallSegment,
    WindowOpening,
)
from services.spatial_engine.brightness import calculate_brightness_approximation
from services.spatial_engine.geometry import prepare_scene


def room() -> RoomScene:
    return RoomScene(
        scene_id="room",
        shell_glb_url="/shell.glb",
        floor_polygon=[Vec2(x=x, z=z) for x, z in [(0, 0), (4, 0), (4, 4), (0, 4)]],
        walls=[WallSegment(id="north", start=Vec2(x=0, z=0), end=Vec2(x=4, z=0))],
        windows=[
            WindowOpening(
                id="window",
                wall_id="north",
                offset_along_wall_m=1,
                width_m=2,
                sill_height_m=1,
                head_height_m=2,
                plan_normal_deg=0,
            )
        ],
        doors=[],
        furniture=[],
    )


def item(item_id: str = "wardrobe", x: float = 2, z: float = 0.5) -> FurnitureItem:
    return FurnitureItem(
        id=item_id,
        name=item_id,
        category="wardrobe",
        source="extracted_video",
        glb_url="/mesh.glb",
        bbox_m=BBoxM(width=2, depth=0.5, height=2),
        pose=Pose2D(x=x, z=z),
    )


def test_clear_and_missing_windows_are_distinct() -> None:
    scene = room()
    result = calculate_brightness_approximation(scene)
    assert result.openness_ratio == 1
    assert result.windows[0].window_area_m2 == 2
    assert result.windows[0].blocking_item_ids == ()
    scene.windows = []
    result = calculate_brightness_approximation(scene)
    assert result.openness_ratio is None and result.windows == ()


@pytest.mark.parametrize(("height", "expected"), [(0.75, 1), (1, 1), (1.5, 0.5), (2, 0)])
def test_height_relative_to_sill(height: float, expected: float) -> None:
    scene = room()
    furniture = item()
    furniture.bbox_m.height = height
    scene.furniture = [furniture]
    result = calculate_brightness_approximation(scene)
    assert result.openness_ratio == pytest.approx(expected)
    assert result.windows[0].obstructed_area_m2 == pytest.approx(2 * (1 - expected))


def test_partial_width_and_overlap_counted_once() -> None:
    scene = room()
    a, b = item("a"), item("b")
    a.bbox_m.width = b.bbox_m.width = 1
    scene.furniture = [b, a]
    result = calculate_brightness_approximation(scene)
    assert result.openness_ratio == pytest.approx(0.5)
    assert result.windows[0].blocking_item_ids == ("a", "b")


def test_disjoint_obstructions_combine() -> None:
    scene = room()
    a, b = item("a", x=1.5), item("b", x=2.5)
    a.bbox_m.width = b.bbox_m.width = 1
    scene.furniture = [a, b]
    assert calculate_brightness_approximation(scene).openness_ratio == 0


def test_parts_respect_gaps_and_overlapping_shadows() -> None:
    scene = room()
    furniture = item()
    furniture.collision_parts = [
        CollisionPart(x=0.5, z=0, width=0.5, depth=0.5, y_min=1, y_max=2),
        CollisionPart(x=0.5, z=0, width=0.5, depth=0.5, y_min=1.5, y_max=2),
    ]
    scene.furniture = [furniture]
    assert calculate_brightness_approximation(scene).openness_ratio == pytest.approx(0.75)
    furniture.collision_parts = [CollisionPart(x=0, z=0, width=2, depth=0.5, y_min=2.1, y_max=2.5)]
    furniture.bbox_m.height = 2.5
    assert calculate_brightness_approximation(scene).openness_ratio == 1


@pytest.mark.parametrize(("x", "z"), [(2, -0.5), (2, 1.25), (0, 0.5)])
def test_behind_wall_beyond_depth_and_side_contact_are_clear(x: float, z: float) -> None:
    scene = room()
    scene.furniture = [item(x=x, z=z)]
    assert calculate_brightness_approximation(scene).openness_ratio == 1


def test_obstruction_depth_is_explicit_and_configurable() -> None:
    scene = room()
    scene.furniture = [item(z=1.5)]
    assert calculate_brightness_approximation(scene).openness_ratio == 1
    result = calculate_brightness_approximation(scene, obstruction_depth_m=2)
    assert result.openness_ratio == 0 and result.obstruction_depth_m == 2


def test_rotation_changes_projected_width() -> None:
    scene = room()
    furniture = item()
    furniture.bbox_m.width, furniture.bbox_m.depth = 0.5, 2
    furniture.pose.z = 0.5
    scene.furniture = [furniture]
    assert calculate_brightness_approximation(scene).openness_ratio == pytest.approx(0.75)
    furniture.pose.yaw_deg = 90
    assert calculate_brightness_approximation(scene).openness_ratio == 0


@pytest.mark.parametrize(
    ("start", "end", "position", "yaw"),
    [
        ((4, 0), (4, 4), (3.5, 2), 90),
        ((4, 4), (0, 4), (2, 3.5), 180),
        ((0, 4), (0, 0), (0.5, 2), 270),
    ],
)
def test_other_wall_orientations(
    start: tuple[float, float], end: tuple[float, float], position: tuple[float, float], yaw: float
) -> None:
    scene = room()
    scene.walls[0].start = Vec2(x=start[0], z=start[1])
    scene.walls[0].end = Vec2(x=end[0], z=end[1])
    furniture = item(x=position[0], z=position[1])
    furniture.pose.yaw_deg = yaw
    scene.furniture = [furniture]
    assert calculate_brightness_approximation(scene).openness_ratio == 0


def test_multiple_windows_weighted_by_area_not_window_count() -> None:
    scene = room()
    scene.windows[0].offset_along_wall_m = 0
    scene.windows[0].width_m = 1
    scene.windows.append(
        WindowOpening(
            id="large",
            wall_id="north",
            offset_along_wall_m=1,
            width_m=2,
            sill_height_m=1,
            head_height_m=2,
            plan_normal_deg=0,
        )
    )
    furniture = item(x=0.5)
    furniture.bbox_m.width = 1
    scene.furniture = [furniture]
    assert calculate_brightness_approximation(scene).openness_ratio == pytest.approx(2 / 3)


def test_fixed_items_and_chairs_are_not_exempt_from_blocking_windows() -> None:
    scene = room()
    furniture = item()
    furniture.category, furniture.is_fixed = "fixture", True
    scene.furniture = [furniture]
    assert calculate_brightness_approximation(scene).openness_ratio == 0
    furniture.category, furniture.is_fixed = "chair", False
    assert calculate_brightness_approximation(scene).openness_ratio == 0


def test_reuses_prepared_geometry_and_does_not_mutate_scene() -> None:
    scene = room()
    scene.furniture = [item()]
    before = scene.model_dump()
    prepared = prepare_scene(scene)
    assert calculate_brightness_approximation(
        scene, _prepared=prepared
    ) == calculate_brightness_approximation(scene)
    assert scene.model_dump() == before


@pytest.mark.parametrize("depth", [0, -1, math.nan, math.inf])
def test_invalid_depth(depth: float) -> None:
    with pytest.raises(ValueError, match="depth"):
        calculate_brightness_approximation(room(), obstruction_depth_m=depth)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("width_m", 0),
        ("width_m", 5),
        ("offset_along_wall_m", -1),
        ("sill_height_m", -1),
        ("head_height_m", 1),
        ("head_height_m", 3),
        ("width_m", math.nan),
        ("offset_along_wall_m", math.inf),
    ],
)
def test_invalid_window_geometry(field: str, value: float) -> None:
    scene = room()
    setattr(scene.windows[0], field, value)
    with pytest.raises(ValueError):
        calculate_brightness_approximation(scene)


def test_duplicate_window_ids_and_unknown_wall_rejected() -> None:
    scene = room()
    scene.windows.append(scene.windows[0].model_copy())
    with pytest.raises(ValueError, match="Window IDs"):
        calculate_brightness_approximation(scene)
    scene.windows.pop()
    scene.windows[0].wall_id = "missing"
    with pytest.raises(ValueError, match="unknown wall"):
        calculate_brightness_approximation(scene)
