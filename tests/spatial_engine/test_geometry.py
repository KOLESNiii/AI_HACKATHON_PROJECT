"""Footprint examples independent of meshes, providers and HTTP routes."""

import math

import pytest

from contracts.schema import BBoxM, FurnitureItem, Pose2D
from services.spatial_engine.geometry import furniture_footprint


def make_item(**pose: float) -> FurnitureItem:
    return FurnitureItem(
        id="desk",
        name="Desk",
        category="desk",
        source="extracted_video",
        glb_url="/desk.glb",
        bbox_m=BBoxM(width=2, height=0.75, depth=4),
        pose=Pose2D(**pose),
    )


@pytest.mark.parametrize(
    ("yaw", "expected"),
    [
        (0, (9, 18, 11, 22)),
        (90, (8, 19, 12, 21)),
        (180, (9, 18, 11, 22)),
        (270, (8, 19, 12, 21)),
        (-90, (8, 19, 12, 21)),
        (450, (8, 19, 12, 21)),
    ],
)
def test_translated_cardinal_bounds(yaw: float, expected: tuple[float, ...]) -> None:
    polygon = furniture_footprint(make_item(x=10, z=20, yaw_deg=yaw))
    assert polygon.bounds == pytest.approx(expected)
    assert polygon.area == pytest.approx(8)
    assert (polygon.centroid.x, polygon.centroid.y) == pytest.approx((10, 20))


def test_45_degree_corners_follow_threejs_yaw() -> None:
    polygon = furniture_footprint(make_item(x=0, z=0, yaw_deg=45))
    root = math.sqrt(0.5)
    expected = [(-3 * root, -root), (-root, -3 * root), (3 * root, root), (root, 3 * root)]
    for actual, corner in zip(list(polygon.exterior.coords)[:-1], expected, strict=True):
        assert actual == pytest.approx(corner)
    assert polygon.area == pytest.approx(8)


def test_front_edge_rotates_toward_positive_x() -> None:
    polygon = furniture_footprint(make_item(x=0, z=0, yaw_deg=90))
    # Corners 2 and 3 are the original +Z (front) edge.
    front = list(polygon.exterior.coords)[2:4]
    assert [point[0] for point in front] == pytest.approx([2, 2])


def test_does_not_mutate_item() -> None:
    item = make_item(x=-3, z=2, yaw_deg=-45)
    before = item.model_dump()
    furniture_footprint(item)
    assert item.model_dump() == before


@pytest.mark.parametrize("field", ["width", "depth"])
@pytest.mark.parametrize("value", [0, -1, math.nan, math.inf, -math.inf])
def test_rejects_invalid_dimensions(field: str, value: float) -> None:
    item = make_item(x=0, z=0)
    setattr(item.bbox_m, field, value)
    with pytest.raises(ValueError, match="width and depth"):
        furniture_footprint(item)


@pytest.mark.parametrize("field", ["x", "z", "yaw_deg"])
@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_rejects_nonfinite_pose(field: str, value: float) -> None:
    item = make_item(x=0, z=0)
    setattr(item.pose, field, value)
    with pytest.raises(ValueError, match="position and yaw"):
        furniture_footprint(item)


def test_rejects_unrepresentable_footprint() -> None:
    item = make_item(x=1e20, z=1e20)
    with pytest.raises(ValueError, match="valid geometry"):
        furniture_footprint(item)
