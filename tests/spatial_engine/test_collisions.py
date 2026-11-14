"""Known-area collision cases using shared contracts and real footprint geometry."""

import math

import pytest

from contracts.schema import BBoxM, CollisionIssue, FurnitureItem, Pose2D
from services.spatial_engine.audit import detect_collisions


def item(item_id: str, x: float = 0, z: float = 0, yaw: float = 0) -> FurnitureItem:
    return FurnitureItem(
        id=item_id,
        name=item_id,
        category="desk",
        source="catalog_search",
        glb_url="/unused.glb",
        bbox_m=BBoxM(width=2, height=1, depth=2),
        pose=Pose2D(x=x, z=z, yaw_deg=yaw),
    )


def test_empty_and_single_item() -> None:
    assert detect_collisions([]) == []
    assert detect_collisions([item("a")]) == []


@pytest.mark.parametrize(("x", "z"), [(3, 0), (2, 0), (2, 2)])
def test_separation_edge_and_corner_contact_are_allowed(x: float, z: float) -> None:
    assert detect_collisions([item("a"), item("b", x, z)]) == []


def test_partial_overlap_reports_true_area() -> None:
    assert detect_collisions([item("a"), item("b", 1, 0.5)]) == [
        CollisionIssue(item_a="a", item_b="b", overlap_area_m2=1.5)
    ]


def test_containment_and_identical_footprints_are_collisions() -> None:
    smaller = item("small")
    smaller.bbox_m = BBoxM(width=1, height=1, depth=1)
    assert detect_collisions([item("large"), smaller])[0].overlap_area_m2 == pytest.approx(1)
    assert detect_collisions([item("a"), item("b")])[0].overlap_area_m2 == pytest.approx(4)


def test_45_degree_rotation_has_known_intersection_area() -> None:
    # Unit-half-width squares, one rotated 45 degrees: subtract four corner triangles.
    result = detect_collisions([item("a"), item("b", yaw=45)])
    assert len(result) == 1
    assert result[0].overlap_area_m2 == pytest.approx(8 * (math.sqrt(2) - 1))


def test_rotated_rectangle_does_not_use_axis_aligned_bounds() -> None:
    diagonal = item("a", yaw=45)
    diagonal.bbox_m = BBoxM(width=0.2, height=1, depth=4)
    outside = item("b", x=1.2, z=-1.2)
    outside.bbox_m = BBoxM(width=0.2, height=1, depth=0.2)
    assert detect_collisions([diagonal, outside]) == []


def test_each_pair_once_with_stable_order_without_mutation() -> None:
    furniture = [item("c"), item("a"), item("b")]
    before = [entry.model_dump() for entry in furniture]
    result = detect_collisions(furniture)
    assert [(entry.item_a, entry.item_b) for entry in result] == [
        ("a", "b"),
        ("a", "c"),
        ("b", "c"),
    ]
    assert result == detect_collisions(list(reversed(furniture)))
    assert [entry.model_dump() for entry in furniture] == before


def test_tolerance_is_strict_and_does_not_change_reported_area() -> None:
    furniture = [item("a"), item("b", x=1)]  # 2 m² overlap
    assert detect_collisions(furniture, area_tolerance_m2=2) == []
    result = detect_collisions(furniture, area_tolerance_m2=1)
    assert result[0].overlap_area_m2 == pytest.approx(2)
    assert detect_collisions(furniture, area_tolerance_m2=0) == result


def test_default_tolerance_suppresses_tiny_overlap() -> None:
    assert detect_collisions([item("a"), item("b", x=2 - 1e-10)]) == []
    assert detect_collisions([item("a"), item("b", x=2 - 1e-6)]) == []
    assert len(detect_collisions([item("a"), item("b", x=2 - 1e-3)])) == 1


@pytest.mark.parametrize("tolerance", [-1, math.nan, math.inf, -math.inf])
def test_rejects_invalid_tolerance(tolerance: float) -> None:
    with pytest.raises(ValueError, match="tolerance"):
        detect_collisions([], area_tolerance_m2=tolerance)


def test_rejects_duplicate_ids() -> None:
    with pytest.raises(ValueError, match="IDs must be unique"):
        detect_collisions([item("same"), item("same", x=10)])


def test_validates_even_a_single_item() -> None:
    invalid = item("a")
    invalid.bbox_m.width = 0
    with pytest.raises(ValueError, match="width and depth"):
        detect_collisions([invalid])
