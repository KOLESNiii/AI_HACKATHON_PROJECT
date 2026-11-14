"""Occupied-volume integration with the merged Dev 2 contract and fixture."""

from pathlib import Path

import pytest

from contracts.schema import BBoxM, CollisionPart, FurnitureItem, Pose2D, RoomScene
from services.spatial_engine.audit import detect_collisions
from services.spatial_engine.geometry import furniture_collision_volumes


def part(bottom: float = 0, top: float = 1, x: float = 0) -> CollisionPart:
    return CollisionPart(x=x, z=0, width=1, depth=1, y_min=bottom, y_max=top)


def item(item_id: str, parts: list[CollisionPart]) -> FurnitureItem:
    return FurnitureItem(
        id=item_id,
        name=item_id,
        category="desk",
        source="extracted_video",
        glb_url="/mesh.glb",
        bbox_m=BBoxM(width=2, depth=2, height=3),
        pose=Pose2D(x=0, z=0),
        collision_parts=parts,
    )


def test_shared_nested_fixture_has_no_furniture_collisions() -> None:
    path = Path(__file__).resolve().parents[2] / "contracts/mock_room/mock_scene.json"
    scene = RoomScene.model_validate_json(path.read_text(encoding="utf-8"))
    assert detect_collisions(scene.furniture) == []


@pytest.mark.parametrize(
    ("bottom", "top", "collides"),
    [
        (1, 2, False),
        (1.1, 2, False),
        (0.999, 2, False),
        (0.995, 2, False),
        (0.99, 2, True),
        (0, 1, True),
    ],
)
def test_height_separation_and_shared_threshold(bottom: float, top: float, collides: bool) -> None:
    result = detect_collisions([item("a", [part()]), item("b", [part(bottom, top)])])
    assert bool(result) is collides


def test_union_of_intersections_does_not_double_count() -> None:
    result = detect_collisions([item("a", [part(), part()]), item("b", [part()])])
    assert len(result) == 1
    assert result[0].overlap_area_m2 == pytest.approx(1)


def test_disjoint_intersections_are_summed() -> None:
    parts = [part(x=-0.5), part(x=0.5)]
    result = detect_collisions([item("a", parts), item("b", parts)])
    assert result[0].overlap_area_m2 == pytest.approx(2)


def test_fallback_solid_box_and_fixed_item_are_checked() -> None:
    fixed = item("fixed", [])
    fixed.category, fixed.is_fixed = "fixture", True
    result = detect_collisions([fixed, item("other", [part()])])
    assert result[0].overlap_area_m2 == pytest.approx(1)


def test_local_part_offset_rotates_with_item_and_does_not_mutate() -> None:
    furniture = item("a", [part(x=0.5)])
    furniture.pose = Pose2D(x=10, z=20, yaw_deg=90)
    before = furniture.model_dump()
    volume = furniture_collision_volumes(furniture)[0]
    assert (volume.footprint.centroid.x, volume.footprint.centroid.y) == pytest.approx((10, 19.5))
    assert volume.footprint.area == pytest.approx(1)
    assert furniture.model_dump() == before


def test_plan_overlap_without_part_overlap_is_clear() -> None:
    assert detect_collisions([item("a", [part(x=-0.5)]), item("b", [part(x=0.5)])]) == []


def test_parts_within_bbox_tolerance_not_lost_in_broad_phase() -> None:
    a, b = item("a", [part(x=0.5009)]), item("b", [part(x=-0.5009)])
    b.pose.x = 2.001
    assert len(detect_collisions([a, b])) == 1


def test_rejects_parts_corrupted_after_validation() -> None:
    furniture = item("a", [part()])
    furniture.collision_parts[0].width = -1
    with pytest.raises(ValueError):
        furniture_collision_volumes(furniture)


@pytest.mark.parametrize("height", [0, -1, float("nan"), float("inf")])
def test_rejects_invalid_height(height: float) -> None:
    furniture = item("a", [])
    furniture.bbox_m.height = height
    with pytest.raises(ValueError, match="height"):
        detect_collisions([furniture])
