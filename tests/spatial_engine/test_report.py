"""Regression checks for report composition and request-local geometry reuse."""

from pathlib import Path
from unittest.mock import patch

import pytest

from contracts.schema import RoomScene
from services.spatial_engine import geometry
from services.spatial_engine.audit import detect_front_clearance
from services.spatial_engine.report import audit_scene


def scene() -> RoomScene:
    path = Path(__file__).resolve().parents[2] / "contracts/mock_room/mock_scene.json"
    return RoomScene.model_validate_json(path.read_text(encoding="utf-8"))


def test_volumes_built_once_per_item_and_not_retained_across_requests() -> None:
    room = scene()
    with patch.object(
        geometry, "furniture_collision_volumes", wraps=geometry.furniture_collision_volumes
    ) as build:
        first = audit_scene(room)
        assert build.call_count == len(room.furniture)
        # A subsequent edit must rebuild derived geometry instead of reusing a stale cache.
        room.revision += 1
        wardrobe = next(item for item in room.furniture if item.id == "item_wardrobe")
        wardrobe.pose.x, wardrobe.pose.z = 1.35, 1.5
        second = audit_scene(room)
        assert build.call_count == 2 * len(room.furniture)
    assert first.blocked_doors
    assert first.walkable_floor_ratio == 0
    assert second.blocked_doors == []
    assert second.walkable_floor_ratio is not None and second.walkable_floor_ratio > 0
    assert second.scene_revision == first.scene_revision + 1


def test_prepared_geometry_cannot_be_passed_to_different_scene() -> None:
    room = scene()
    prepared = geometry.prepare_scene(room)
    with pytest.raises(ValueError, match="different scene"):
        detect_front_clearance(room.model_copy(deep=True), _prepared=prepared)
