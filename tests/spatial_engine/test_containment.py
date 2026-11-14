"""Whole-footprint containment against the authoritative usable floor boundary."""

import math

import pytest
from pydantic import ValidationError

from contracts.schema import BBoxM, FurnitureItem, Pose2D, RoomScene, Vec2
from services.spatial_engine.audit import detect_out_of_bounds
from services.spatial_engine.geometry import room_floor_polygon


def item(item_id: str = "desk", x: float = 2, z: float = 2, yaw: float = 0) -> FurnitureItem:
    return FurnitureItem(
        id=item_id,
        name=item_id,
        category="desk",
        source="extracted_video",
        glb_url="/desk.glb",
        bbox_m=BBoxM(width=2, height=1, depth=2),
        pose=Pose2D(x=x, z=z, yaw_deg=yaw),
    )


def room(
    furniture: list[FurnitureItem], points: list[tuple[float, float]] | None = None
) -> RoomScene:
    if points is None:
        points = [(0, 0), (4, 0), (4, 4), (0, 4)]
    return RoomScene(
        scene_id="room",
        shell_glb_url="/shell.glb",
        floor_polygon=[Vec2(x=x, z=z) for x, z in points],
        walls=[],
        windows=[],
        doors=[],
        furniture=furniture,
    )


@pytest.mark.parametrize(("x", "z"), [(2, 2), (1, 2), (1, 1), (3, 3)])
def test_inside_and_boundary_contact_are_allowed(x: float, z: float) -> None:
    assert detect_out_of_bounds(room([item(x=x, z=z)])) == []


@pytest.mark.parametrize(("x", "z"), [(0.5, 2), (-5, 2), (2, 3.5), (4.5, 4.5)])
def test_partly_or_fully_outside(x: float, z: float) -> None:
    assert detect_out_of_bounds(room([item(x=x, z=z)])) == ["desk"]


def test_rotated_footprint_not_just_centre_is_checked() -> None:
    assert detect_out_of_bounds(room([item(x=1, z=2, yaw=45)])) == ["desk"]
    assert detect_out_of_bounds(room([item(x=2, z=2, yaw=45)])) == []


def test_concave_floor_checks_entire_edges_not_just_corners() -> None:
    # A notch cuts into the footprint although all four footprint corners are inside.
    points = [(0, 0), (4, 0), (4, 4), (2.5, 4), (2.5, 2), (1.5, 2), (1.5, 4), (0, 4)]
    assert detect_out_of_bounds(room([item()], points)) == ["desk"]


def test_l_shaped_floor() -> None:
    points = [(0, 0), (4, 0), (4, 2), (2, 2), (2, 4), (0, 4)]
    scene = room([item("inside", x=1, z=3), item("outside", x=3, z=3)], points)
    assert detect_out_of_bounds(scene) == ["outside"]


def test_clockwise_floor_and_explicit_closure_are_accepted() -> None:
    points = [(0, 0), (4, 0), (4, 4), (0, 4)]
    for ring in (points, [*points, points[0]]):
        assert detect_out_of_bounds(room([item()], ring)) == []


def test_scene_rejects_reversed_floor_winding() -> None:
    with pytest.raises(ValidationError, match="clockwise"):
        room([], [(0, 0), (0, 4), (4, 4), (4, 0)])


def test_noise_tolerance_is_not_a_clearance_requirement() -> None:
    scene = room([item(x=1 - 1e-10)])
    assert detect_out_of_bounds(scene) == []
    assert detect_out_of_bounds(scene, boundary_tolerance_m=0) == ["desk"]
    assert detect_out_of_bounds(room([item(x=1 - 1e-6)])) == ["desk"]


def test_sorted_ids_and_immutable_scene() -> None:
    scene = room([item("z", x=0), item("a", z=0), item("inside")])
    before = scene.model_dump()
    assert detect_out_of_bounds(scene) == ["a", "z"]
    assert scene.model_dump() == before


def test_empty_furniture_in_valid_room() -> None:
    assert detect_out_of_bounds(room([])) == []


@pytest.mark.parametrize(
    "points",
    [
        [],
        [(0, 0), (1, 1)],
        [(0, 0), (1, 1), (2, 2)],
        [(0, 0), (4, 4), (4, 0), (0, 4)],
        [(0, 0), (math.nan, 0), (0, 1)],
        [(0, 0), (math.inf, 0), (0, 1)],
    ],
)
def test_invalid_floor_rejected_even_without_furniture(points: list[tuple[float, float]]) -> None:
    with pytest.raises(ValueError, match="Room floor"):
        room_floor_polygon([Vec2(x=x, z=z) for x, z in points])


def test_containment_rejects_floor_corrupted_after_validation() -> None:
    scene = room([])
    scene.floor_polygon = [Vec2(x=0, z=0)]
    with pytest.raises(ValueError, match="Room floor"):
        detect_out_of_bounds(scene)


@pytest.mark.parametrize("tolerance", [-1, math.nan, math.inf])
def test_invalid_tolerance(tolerance: float) -> None:
    with pytest.raises(ValueError, match="tolerance"):
        detect_out_of_bounds(room([]), boundary_tolerance_m=tolerance)


def test_duplicate_ids_rejected() -> None:
    with pytest.raises(ValueError, match="IDs must be unique"):
        detect_out_of_bounds(room([item(), item()]))


def test_invalid_item_rejected() -> None:
    invalid = item()
    invalid.bbox_m.depth = -1
    with pytest.raises(ValueError, match="width and depth"):
        detect_out_of_bounds(room([invalid]))
