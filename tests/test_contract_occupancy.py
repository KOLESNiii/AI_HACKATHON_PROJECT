"""Box collision parts, fixed items and item IDs on the shared contract."""

from typing import Any

import pytest
from pydantic import ValidationError

from contracts.schema import (
    GLB_BBOX_TOLERANCE_M,
    ITEM_ID_PATTERN,
    MAX_COLLISION_PARTS,
    MIN_HEIGHT_OVERLAP_M,
    MIN_PART_DIMENSION_M,
    MIN_PLAN_OVERLAP_M2,
    WALK_HEADROOM_M,
    FurnitureItem,
)

# The pre-change shape: none of the collision fields.
LEGACY_DESK: dict[str, Any] = {
    "id": "item_desk",
    "name": "Work Desk",
    "category": "desk",
    "source": "extracted_video",
    "glb_url": "/mock_room/desk.glb",
    "bbox_m": {"width": 1.4, "height": 0.75, "depth": 0.7},
    "pose": {"x": 2.1, "z": 2.6, "yaw_deg": 0},
}


def item(**over: Any) -> FurnitureItem:
    return FurnitureItem.model_validate({**LEGACY_DESK, **over})


def part(**over: float) -> dict[str, float]:
    return {"x": 0, "z": 0, "width": 0.1, "depth": 0.1, "y_min": 0, "y_max": 0.1, **over}


def test_legacy_item_still_validates() -> None:
    it = item()
    assert (it.collision_parts, it.collision_source, it.is_fixed) == ([], "template", False)


def test_constants() -> None:
    assert (GLB_BBOX_TOLERANCE_M, MAX_COLLISION_PARTS, MIN_PART_DIMENSION_M) == (0.001, 12, 0.01)
    assert (MIN_PLAN_OVERLAP_M2, MIN_HEIGHT_OVERLAP_M, WALK_HEADROOM_M) == (0.0001, 0.005, 2.0)
    assert ITEM_ID_PATTERN == r"^[a-z0-9][a-z0-9_-]{0,63}$"


def test_part_must_lie_inside_bbox() -> None:
    item(collision_parts=[part(x=0.68, width=0.04)])  # reaches 0.70: allowed
    item(collision_parts=[part(x=0.6805, width=0.04)])  # 0.5 mm over: within tolerance
    with pytest.raises(ValidationError):
        item(collision_parts=[part(x=0.70, width=0.04)])  # 2 cm over
    with pytest.raises(ValidationError):
        item(collision_parts=[part(z=0.35, depth=0.1)])


@pytest.mark.parametrize("bad", [{"y_max": 0.76}, {"y_min": -0.01}, {"y_min": 0.1, "y_max": 0.1}])
def test_part_height_range(bad: dict[str, float]) -> None:
    with pytest.raises(ValidationError):
        item(collision_parts=[part(**bad)])


def test_part_limits() -> None:
    item(collision_parts=[part()] * 12)
    with pytest.raises(ValidationError):
        item(collision_parts=[part()] * 13)
    with pytest.raises(ValidationError):
        item(collision_parts=[part(width=0.005)])


@pytest.mark.parametrize("bad_id", ["Desk 01", "-desk", "", "a" * 65, "desk:1"])
def test_item_id_pattern(bad_id: str) -> None:
    with pytest.raises(ValidationError):
        item(id=bad_id)


def test_new_literals() -> None:
    assert item(id="vid-table-01", category="table").category == "table"
    assert item(category="fixture", is_fixed=True).is_fixed
    assert item(collision_source="mesh").collision_source == "mesh"


@pytest.mark.parametrize("field", ["x", "z", "width", "depth", "y_min", "y_max"])
@pytest.mark.parametrize("value", [float("nan"), float("inf")])
def test_part_values_must_be_finite(field: str, value: float) -> None:
    with pytest.raises(ValidationError):
        item(collision_parts=[part(**{field: value})])
