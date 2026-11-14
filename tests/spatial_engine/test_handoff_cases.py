"""Reusable scene variants and expected findings for Dev 3/4 integration."""

import json
from pathlib import Path
from typing import Any

import pytest

from contracts.schema import BlockedDoorIssue, CollisionIssue, Pose2D, RoomScene
from services.spatial_engine.audit import (
    detect_blocked_doors,
    detect_collisions,
    detect_out_of_bounds,
)

ROOT = Path(__file__).resolve().parents[2]
PACK = json.loads((ROOT / "services/spatial_engine/fixtures/audit_cases.json").read_text("utf-8"))


@pytest.mark.parametrize("case", PACK["cases"], ids=lambda case: case["id"])
def test_shared_handoff_case(case: dict[str, Any]) -> None:
    # Every case starts from the unchanged base, not the previous case.
    scene = RoomScene.model_validate_json((ROOT / PACK["base_scene"]).read_text("utf-8"))
    overrides = case["pose_overrides"]
    assert set(overrides) <= {item.id for item in scene.furniture}
    for item in scene.furniture:
        if item.id in overrides:
            item.pose = Pose2D.model_validate(overrides[item.id])
    scene.revision = case["revision"]
    scene = RoomScene.model_validate(scene.model_dump())
    before = scene.model_dump()
    expected = case["expected"]

    actual = detect_collisions(scene.furniture)
    wanted = [CollisionIssue.model_validate(entry) for entry in expected["collisions"]]
    assert [(entry.item_a, entry.item_b) for entry in actual] == [
        (entry.item_a, entry.item_b) for entry in wanted
    ]
    assert [entry.overlap_area_m2 for entry in actual] == pytest.approx(
        [entry.overlap_area_m2 for entry in wanted], abs=1e-9
    )
    assert detect_out_of_bounds(scene) == expected["out_of_bounds_item_ids"]
    assert detect_blocked_doors(scene) == [
        BlockedDoorIssue.model_validate(entry) for entry in expected["blocked_doors"]
    ]
    assert scene.model_dump() == before


def test_case_ids_are_unique_and_base_has_not_been_replaced() -> None:
    assert len({case["id"] for case in PACK["cases"]}) == len(PACK["cases"])
    assert PACK["base_scene"] == "contracts/mock_room/mock_scene.json"
