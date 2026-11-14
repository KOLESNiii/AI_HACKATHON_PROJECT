"""Layout ranking uses real audited geometry and explicit, stable priorities."""

import math

import pytest

from contracts.schema import (
    BBoxM,
    DoorOpening,
    FurnitureItem,
    Pose2D,
    RoomScene,
    Vec2,
    WallSegment,
    WindowOpening,
)
from services.spatial_engine.objective import compare_layouts, evaluate_layout


def item(item_id: str, x: float, z: float, *, clearance: float = 0) -> FurnitureItem:
    return FurnitureItem(
        id=item_id,
        name=item_id,
        category="wardrobe",
        source="extracted_video",
        glb_url="/mesh.glb",
        bbox_m=BBoxM(width=1, height=2, depth=1),
        pose=Pose2D(x=x, z=z),
        requires_front_clear_m=clearance,
    )


def room(furniture: list[FurnitureItem], *, door: bool = False) -> RoomScene:
    return RoomScene(
        scene_id="room",
        shell_glb_url="/shell.glb",
        floor_polygon=[Vec2(x=x, z=z) for x, z in [(0, 0), (8, 0), (8, 8), (0, 8)]],
        walls=[WallSegment(id="north", start=Vec2(x=0, z=0), end=Vec2(x=8, z=0))],
        doors=[DoorOpening(id="door", wall_id="north", hinge_pos=Vec2(x=1, z=0), width_m=1)]
        if door
        else [],
        windows=[],
        furniture=furniture,
    )


def test_identical_and_reordered_layouts_are_equal_without_public_score() -> None:
    original = room([item("a", 2, 2), item("b", 5, 5)])
    candidate = original.model_copy(deep=True)
    candidate.furniture.reverse()
    candidate.revision = 7
    result = compare_layouts(original, candidate)
    assert result.outcome == "equal" and result.deciding_metric is None
    assert result.candidate.metrics.movement_m == 0
    assert result.candidate.metrics.passes_critical_checks
    assert result.candidate.report.overall_score is None


def test_better_clearance_never_outweighs_new_collision() -> None:
    original = room([item("target", 2, 2, clearance=1), item("blocker", 2, 3.5), item("bed", 5, 5)])
    candidate = original.model_copy(deep=True)
    candidate.furniture[1].pose = Pose2D(x=5, z=5)
    result = compare_layouts(original, candidate)
    assert result.candidate.metrics.clearance_deficit < result.baseline.metrics.clearance_deficit
    assert result.outcome == "worse" and result.deciding_metric == "critical_issue_count"


def test_better_clearance_never_outweighs_leaving_the_room() -> None:
    original = room([item("target", 2, 2, clearance=1), item("blocker", 2, 3.5)])
    candidate = original.model_copy(deep=True)
    candidate.furniture[1].pose.x = -1
    result = compare_layouts(original, candidate)
    assert result.outcome == "worse" and result.deciding_metric == "critical_issue_count"
    assert result.candidate.metrics.out_of_bounds_count == 1


def test_blocked_door_is_a_critical_problem() -> None:
    original = room([item("plant", 5, 5)], door=True)
    original.furniture[0].bbox_m.width = original.furniture[0].bbox_m.depth = 0.2
    candidate = original.model_copy(deep=True)
    candidate.furniture[0].pose = Pose2D(x=1.4, z=0.4)
    result = compare_layouts(original, candidate)
    assert result.outcome == "worse" and result.deciding_metric == "critical_issue_count"
    assert result.candidate.metrics.blocked_door_count == 1


def test_smaller_collision_is_progress_but_still_not_feasible() -> None:
    original = room([item("a", 2, 2), item("b", 2, 2)])
    candidate = original.model_copy(deep=True)
    candidate.furniture[1].pose.x = 2.5
    result = compare_layouts(original, candidate)
    assert result.outcome == "better" and result.deciding_metric == "critical_violation_area_m2"
    assert result.baseline.metrics.critical_violation_area_m2 == pytest.approx(1)
    assert result.candidate.metrics.critical_violation_area_m2 == pytest.approx(0.5)
    assert not result.candidate.metrics.passes_critical_checks


def test_reducing_outside_area_is_progress() -> None:
    original = room([item("a", 0, 2)])
    candidate = original.model_copy(deep=True)
    candidate.furniture[0].pose.x = 0.25
    result = compare_layouts(original, candidate)
    assert result.outcome == "better" and result.deciding_metric == "critical_violation_area_m2"
    assert result.candidate.metrics.critical_violation_area_m2 == pytest.approx(0.25)


def test_door_obstruction_area_grades_progress_without_requiring_a_clear_door() -> None:
    original = room([item("plant", 1.4, 0.4)], door=True)
    original.furniture[0].bbox_m.width = original.furniture[0].bbox_m.depth = 0.2
    candidate = original.model_copy(deep=True)
    candidate.furniture[0].pose = Pose2D(x=1.7, z=0.7)
    result = compare_layouts(original, candidate)
    assert result.candidate.metrics.blocked_door_count == 1
    assert result.outcome == "better" and result.deciding_metric == "critical_violation_area_m2"


def test_one_door_counts_once_and_obstruction_area_is_unioned() -> None:
    original = room([item("a", 1.4, 0.4), item("b", 1.4, 0.4)], door=True)
    for furniture in original.furniture:
        furniture.bbox_m.width = furniture.bbox_m.depth = 0.2
    evaluation = evaluate_layout(original, original)
    assert len(evaluation.report.blocked_doors) == 2
    assert evaluation.metrics.blocked_door_count == 1
    assert evaluation.metrics.critical_issue_count == 2  # one furniture pair + one door
    assert evaluation.metrics.critical_violation_area_m2 == pytest.approx(0.08)


def test_clearance_counts_nearest_blocker_once_per_item() -> None:
    target = item("target", 3, 2, clearance=1)
    target.bbox_m.width = 2
    original = room([target, item("a", 2.5, 3), item("b", 3.5, 3)])
    evaluation = evaluate_layout(original, original)
    assert len(evaluation.report.clearance_issues) == 2
    assert evaluation.metrics.clearance_deficit == pytest.approx(1)
    candidate = original.model_copy(deep=True)
    candidate.furniture[1].pose.x = 6
    assert evaluate_layout(original, candidate).metrics.clearance_deficit == pytest.approx(1)
    candidate.furniture[2].pose.x = 7
    result = compare_layouts(original, candidate)
    assert result.outcome == "better" and result.deciding_metric == "clearance_deficit"


def test_clearance_is_proportional_to_requirement() -> None:
    original = room([item("target", 2, 2, clearance=1), item("blocker", 2, 3.5)])
    assert evaluate_layout(original, original).metrics.clearance_deficit == pytest.approx(0.5)


def test_nearest_of_different_blocker_distances_controls_deficit() -> None:
    target = item("target", 3, 2, clearance=1)
    target.bbox_m.width = 2
    original = room([target, item("near", 2.5, 3), item("far", 3.5, 3.5)])
    metrics = evaluate_layout(original, original).metrics
    assert metrics.clearance_deficit == pytest.approx(1)


def test_known_zero_walking_access_is_not_unknown() -> None:
    original = room([], door=True)
    original.doors[0].head_height_m = 1.9
    result = compare_layouts(original, original)
    assert result.candidate.metrics.reachable_floor_ratio == 0
    assert result.skipped_unknown_metrics == ()


def test_walking_access_improvement_precedes_movement() -> None:
    partition = item("partition", 4, 3.8)
    partition.bbox_m.width, partition.bbox_m.depth = 0.2, 7.6
    original = room([partition], door=True)
    candidate = original.model_copy(deep=True)
    candidate.furniture[0].pose.x = 6
    result = compare_layouts(original, candidate)
    assert result.outcome == "better" and result.deciding_metric == "reachable_floor_ratio"
    assert result.candidate.metrics.movement_m == pytest.approx(2)


def test_unnecessary_movement_loses_and_unknown_is_not_zero() -> None:
    original = room([item("a", 2, 2)])
    candidate = original.model_copy(deep=True)
    candidate.furniture[0].pose.x = 3
    result = compare_layouts(original, candidate)
    assert result.outcome == "worse" and result.deciding_metric == "movement_m"
    assert result.candidate.metrics.reachable_floor_ratio is None
    assert result.skipped_unknown_metrics == ("reachable_floor_ratio",)


def test_rotation_wrap_and_rotation_movement_cost() -> None:
    original = room([item("a", 2, 2)])
    candidate = original.model_copy(deep=True)
    candidate.furniture[0].pose.yaw_deg = 360
    assert compare_layouts(original, candidate).outcome == "equal"
    candidate.furniture[0].pose.yaw_deg = 270
    metrics = evaluate_layout(original, candidate).metrics
    assert metrics.rotation_equivalent_m == pytest.approx(math.sqrt(2) / 2 * math.pi / 2)
    assert metrics.translation_m == 0 and metrics.moved_item_count == 1


def test_movement_is_always_measured_from_original() -> None:
    original = room([item("a", 2, 2)])
    candidate = original.model_copy(deep=True)
    candidate.furniture[0].pose.x = 5
    assert evaluate_layout(original, candidate).metrics.translation_m == pytest.approx(3)
    candidate.furniture[0].pose.x = 3
    assert evaluate_layout(original, candidate).metrics.translation_m == pytest.approx(1)


def test_two_improved_drafts_share_the_same_original_movement_reference() -> None:
    original = room([item("target", 2, 2, clearance=1), item("blocker", 2, 3.5)])
    best = original.model_copy(deep=True)
    best.furniture[1].pose.x = 4
    candidate = original.model_copy(deep=True)
    candidate.furniture[1].pose.x = 3
    result = compare_layouts(original, candidate, baseline=best)
    assert result.outcome == "better" and result.deciding_metric == "movement_m"
    assert result.baseline.metrics.translation_m == pytest.approx(2)
    assert result.candidate.metrics.translation_m == pytest.approx(1)


def test_brightness_is_opt_in_and_cannot_overrule_critical_problems() -> None:
    original = room([item("wardrobe", 2, 0.5)])
    original.windows = [
        WindowOpening(
            id="window",
            wall_id="north",
            offset_along_wall_m=1,
            width_m=2,
            sill_height_m=1,
            head_height_m=2,
            plan_normal_deg=0,
        )
    ]
    candidate = original.model_copy(deep=True)
    candidate.furniture[0].pose.z = 2
    default = compare_layouts(original, candidate)
    assert default.outcome == "worse" and default.deciding_metric == "movement_m"
    assert default.candidate.metrics.brightness_openness is None
    assert not default.candidate.brightness_measured
    preferred = compare_layouts(original, candidate, prefer_brightness=True)
    assert preferred.outcome == "better" and preferred.deciding_metric == "brightness_openness"
    candidate.furniture[0].pose.z = 8
    assert compare_layouts(original, candidate, prefer_brightness=True).outcome == "worse"


def test_requested_brightness_without_windows_remains_unknown() -> None:
    original = room([item("a", 2, 2)])
    result = compare_layouts(original, original, prefer_brightness=True)
    assert result.outcome == "equal"
    assert result.candidate.brightness_measured
    assert result.candidate.metrics.brightness_openness is None
    assert result.skipped_unknown_metrics == ("reachable_floor_ratio", "brightness_openness")


def test_clearance_precedes_even_explicit_brightness_preference() -> None:
    original = room([item("target", 2, 2, clearance=1), item("blocker", 2, 3.5)])
    original.windows = [
        WindowOpening(
            id="window",
            wall_id="north",
            offset_along_wall_m=1,
            width_m=2,
            sill_height_m=1,
            head_height_m=2,
            plan_normal_deg=0,
        )
    ]
    candidate = original.model_copy(deep=True)
    candidate.furniture[1].pose.z = 0.5
    result = compare_layouts(original, candidate, prefer_brightness=True)
    assert (
        result.baseline.metrics.brightness_openness > result.candidate.metrics.brightness_openness
    )
    assert result.outcome == "better" and result.deciding_metric == "clearance_deficit"


def test_tiny_movement_is_a_numerical_tie() -> None:
    original = room([item("a", 2, 2)])
    candidate = original.model_copy(deep=True)
    candidate.furniture[0].pose.x += 1e-10
    assert compare_layouts(original, candidate).outcome == "equal"


@pytest.mark.parametrize("change", ["room", "remove", "dimensions", "requirement", "fixed"])
def test_candidates_cannot_game_metrics_by_changing_non_pose_data(change: str) -> None:
    original = room([item("a", 2, 2)])
    if change == "fixed":
        original.furniture[0].is_fixed = True
    candidate = original.model_copy(deep=True)
    if change == "room":
        candidate.floor_polygon[1].x = 9
    elif change == "remove":
        candidate.furniture = []
    elif change == "dimensions":
        candidate.furniture[0].bbox_m.width = 0.1
    elif change == "requirement":
        candidate.furniture[0].requires_front_clear_m = 0.1
    else:
        candidate.furniture[0].pose.x = 3
    with pytest.raises(ValueError):
        compare_layouts(original, candidate)


def test_invalid_pose_and_duplicate_ids_rejected() -> None:
    original = room([item("a", 2, 2)])
    candidate = original.model_copy(deep=True)
    candidate.furniture[0].pose.x = math.nan
    with pytest.raises(ValueError):
        compare_layouts(original, candidate)
    candidate = original.model_copy(deep=True)
    candidate.furniture.append(candidate.furniture[0].model_copy(deep=True))
    with pytest.raises(ValueError, match="IDs must be unique"):
        compare_layouts(original, candidate)


def test_inputs_and_nullable_scores_unchanged() -> None:
    original = room([item("a", 2, 2)])
    candidate = original.model_copy(deep=True)
    candidate.furniture[0].pose.x = 3
    before = original.model_dump(), candidate.model_dump()
    result = compare_layouts(original, candidate)
    assert (original.model_dump(), candidate.model_dump()) == before
    assert (
        result.baseline.report.overall_score is None
        and result.candidate.report.overall_score is None
    )
