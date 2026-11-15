"""Layout ranking uses real audited geometry and explicit, stable priorities."""

import math
from dataclasses import replace

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
from services.spatial_engine.geometry import SpatialInputError
from services.spatial_engine.objective import (
    NEAR_WINDOW_M,
    beats_original,
    compare_evaluations,
    compare_layouts,
    evaluate_layout,
    is_acceptable_proposal,
)


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
    preferred = compare_layouts(original, candidate, goal="brighter")
    assert preferred.outcome == "better" and preferred.deciding_metric == "brightness_openness"
    candidate.furniture[0].pose.z = 8
    assert compare_layouts(original, candidate, goal="brighter").outcome == "worse"


def test_requested_brightness_without_windows_remains_unknown() -> None:
    original = room([item("a", 2, 2)])
    result = compare_layouts(original, original, goal="brighter")
    assert result.outcome == "equal"
    assert result.candidate.brightness_measured
    assert result.candidate.metrics.brightness_openness is None
    assert result.skipped_unknown_metrics == ("brightness_openness", "reachable_floor_ratio")


def test_requested_brightness_outranks_clearance_only_under_that_goal() -> None:
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
    result = compare_layouts(original, candidate, goal="brighter")
    assert (
        result.baseline.metrics.brightness_openness > result.candidate.metrics.brightness_openness
    )
    assert result.outcome == "worse" and result.deciding_metric == "brightness_openness"
    balanced = compare_layouts(original, candidate)
    assert balanced.outcome == "better" and balanced.deciding_metric == "clearance_deficit"


def test_roomier_ranks_walking_area_above_clearance() -> None:
    # A 0.3 m gap in front of the target is too narrow to walk in. Closing it frees
    # walkable floor elsewhere but leaves the target with no front access at all.
    original = room([item("target", 5, 4, clearance=1), item("blocker", 5, 5.3)], door=True)
    candidate = original.model_copy(deep=True)
    candidate.furniture[1].pose.z = 5
    before = evaluate_layout(original, original).metrics
    after = evaluate_layout(original, candidate).metrics
    assert after.clearance_deficit > before.clearance_deficit
    assert before.reachable_floor_ratio is not None and after.reachable_floor_ratio is not None
    assert after.reachable_floor_ratio > before.reachable_floor_ratio + 1e-3
    roomier = compare_layouts(original, candidate, goal="roomier")
    assert roomier.outcome == "better" and roomier.deciding_metric == "reachable_floor_ratio"
    balanced = compare_layouts(original, candidate)
    assert balanced.outcome == "worse" and balanced.deciding_metric == "clearance_deficit"


def test_minimal_changes_will_not_move_furniture_just_for_walking_area() -> None:
    original = room([item("a", 2, 2), item("b", 2, 3.3)], door=True)
    candidate = original.model_copy(deep=True)
    candidate.furniture[1].pose.z = 3
    assert compare_layouts(original, candidate).deciding_metric == "reachable_floor_ratio"
    assert compare_layouts(original, candidate).outcome == "better"
    minimal = compare_layouts(original, candidate, goal="minimal_changes")
    assert minimal.outcome == "worse" and minimal.deciding_metric == "movement_m"


def test_minimal_changes_still_fixes_access_with_the_smaller_move() -> None:
    original = room([item("target", 2, 2, clearance=1), item("blocker", 2, 3.5)])
    near = original.model_copy(deep=True)
    near.furniture[1].pose.x = 3
    far = original.model_copy(deep=True)
    far.furniture[1].pose.x = 6
    assert compare_layouts(original, near, goal="minimal_changes").outcome == "better"
    result = compare_layouts(original, far, baseline=near, goal="minimal_changes")
    assert result.outcome == "worse" and result.deciding_metric == "movement_m"


def window_room(furniture: list[FurnitureItem]) -> RoomScene:
    scene = room(furniture)
    scene.windows = [
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
    return scene


def test_near_window_shortfall_measures_distance_beyond_the_threshold() -> None:
    # The window spans x 1..3 on the z=0 wall; the desk footprint is 1 m square.
    original = window_room([item("desk", 2, 4), item("bed", 6, 6)])
    measured = evaluate_layout(original, original, near_window_item_ids=["desk"])
    assert measured.near_window_item_ids == ("desk",)
    assert measured.metrics.near_window_shortfall_m == pytest.approx(3.5 - NEAR_WINDOW_M)
    assert evaluate_layout(original, original).metrics.near_window_shortfall_m is None

    candidate = original.model_copy(deep=True)
    candidate.furniture[0].pose = Pose2D(x=4.5, z=0.9)  # 1 m along the wall past the window edge
    close = evaluate_layout(original, candidate, near_window_item_ids=["desk"])
    assert close.metrics.near_window_shortfall_m == pytest.approx(
        math.hypot(1, 0.4) - NEAR_WINDOW_M
    )
    candidate.furniture[0].pose = Pose2D(x=2, z=0.9)
    satisfied = evaluate_layout(original, candidate, near_window_item_ids=["desk"])
    assert satisfied.metrics.near_window_shortfall_m == 0


def test_near_window_request_outranks_soft_goals_but_not_feasibility() -> None:
    original = window_room([item("desk", 2, 4), item("bed", 6, 6)])
    candidate = original.model_copy(deep=True)
    candidate.furniture[0].pose = Pose2D(x=2, z=0.6)
    assert compare_layouts(original, candidate).outcome == "worse"
    for goal in ("balanced", "brighter", "roomier", "minimal_changes"):
        result = compare_layouts(original, candidate, goal=goal, near_window_item_ids=["desk"])
        assert result.outcome == "better", goal
        assert result.deciding_metric == "near_window_shortfall_m"
    candidate.furniture[0].pose = Pose2D(x=2, z=0.2)  # nearer still, but through the wall
    result = compare_layouts(original, candidate, near_window_item_ids=["desk"])
    assert result.outcome == "worse" and result.deciding_metric == "critical_issue_count"


def test_near_window_without_windows_is_unknown_and_skipped() -> None:
    original = room([item("desk", 2, 4)])
    result = compare_layouts(original, original, near_window_item_ids=["desk"])
    assert result.candidate.metrics.near_window_shortfall_m is None
    assert "near_window_shortfall_m" in result.skipped_unknown_metrics
    assert result.outcome == "equal"


def test_goal_and_near_window_inputs_are_validated() -> None:
    original = window_room([item("desk", 2, 4)])
    with pytest.raises(SpatialInputError, match="known furniture"):
        evaluate_layout(original, original, near_window_item_ids=["sofa"])
    plain = evaluate_layout(original, original)
    with pytest.raises(SpatialInputError, match="measured window openness"):
        compare_evaluations(plain, plain, "brighter")
    with pytest.raises(SpatialInputError, match="Unknown layout goal"):
        compare_evaluations(plain, plain, "cosier")  # type: ignore[arg-type]
    requested = evaluate_layout(original, original, near_window_item_ids=["desk"])
    with pytest.raises(SpatialInputError, match="same near-window items"):
        compare_evaluations(plain, requested)


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


def test_custom_goal_ignores_movement_but_never_accepts_worse_access() -> None:
    from services.spatial_engine.objective import beats_original

    original = room([item("target", 2, 2, clearance=1), item("a", 6, 6)])
    moved = original.model_copy(deep=True)
    moved.furniture[1].pose = Pose2D(x=7, z=7)
    old, new = evaluate_layout(original, original), evaluate_layout(original, moved)
    assert compare_evaluations(old, new, "custom").outcome == "equal"
    assert beats_original(old, new, "custom") and not beats_original(old, new, "balanced")
    assert not beats_original(old, old, "custom")  # nothing moved
    blocked = original.model_copy(deep=True)
    blocked.furniture[1].pose = Pose2D(x=2, z=3.5)
    assert not beats_original(old, evaluate_layout(original, blocked), "custom")


def test_feng_shui_goal_ranks_the_score_first_and_is_never_traded_for_validity() -> None:
    from contracts.schema import DoorOpening

    desk = item("desk", 4.5, 3)
    desk.category, desk.bbox_m.width, desk.bbox_m.depth = "desk", 1.2, 0.7
    original = room([desk])
    original.doors = [DoorOpening(id="door", wall_id="north", hinge_pos=Vec2(x=2, z=0), width_m=1)]
    original.furniture[0].pose = Pose2D(x=4.5, z=3, yaw_deg=180)  # back to the door
    turned = original.model_copy(deep=True)
    turned.furniture[0].pose = Pose2D(x=4.5, z=3, yaw_deg=0)  # now facing it
    old, new = evaluate_layout(original, original), evaluate_layout(original, turned)
    assert (old.metrics.feng_shui_score, new.metrics.feng_shui_score) == (0, 100)
    better = compare_evaluations(old, new, "feng_shui")
    assert better.outcome == "better" and better.deciding_metric == "feng_shui_score"
    # Under the balanced goal the extra movement makes the same turn a loss.
    assert compare_evaluations(old, new, "balanced").outcome == "worse"
    outside = original.model_copy(deep=True)
    outside.furniture[0].pose = Pose2D(x=-5, z=3, yaw_deg=0)
    assert (
        compare_evaluations(old, evaluate_layout(original, outside), "feng_shui").outcome == "worse"
    )


def test_custom_clearance_gain_cannot_compensate_for_lost_circulation(
    divided_access_room: RoomScene,
) -> None:
    original = divided_access_room
    candidate = original.model_copy(deep=True)
    candidate.furniture[1].pose = Pose2D(x=4, z=7.5)
    before = evaluate_layout(original, original)
    after = evaluate_layout(original, candidate)
    assert after.metrics.passes_critical_checks
    assert before.metrics.clearance_deficit == pytest.approx(0.5)
    assert after.metrics.clearance_deficit == 0
    assert before.metrics.reachable_floor_ratio == pytest.approx(0.86124, abs=1e-5)
    assert after.metrics.reachable_floor_ratio == pytest.approx(0.42108, abs=1e-5)
    assert compare_evaluations(before, after, "custom").outcome == "better"
    assert not beats_original(before, after, "custom")
    assert not is_acceptable_proposal(before, after, "custom")
    assert is_acceptable_proposal(before, after, "balanced")


@pytest.mark.parametrize(
    ("clearance", "reachable", "accepted"),
    [
        (0.6, 0.9, False),
        (0.4, 0.7, False),
        (0.4, None, False),
        (0.5 + 1e-10, 0.8 - 1e-10, True),
        (0.4, 0.9, True),
    ],
)
def test_custom_access_metrics_are_checked_independently(
    clearance: float,
    reachable: float | None,
    accepted: bool,
) -> None:
    measured = evaluate_layout(room([item("box", 2, 2)]), room([item("box", 2, 2)]))
    before = replace(
        measured,
        metrics=replace(
            measured.metrics,
            clearance_deficit=0.5,
            reachable_floor_ratio=0.8,
        ),
    )
    after = replace(
        measured,
        metrics=replace(
            measured.metrics,
            clearance_deficit=clearance,
            reachable_floor_ratio=reachable,
            moved_item_count=1,
            near_window_shortfall_m=0,
        ),
    )
    # A higher-priority placement improvement must not bypass the clearance guard either.
    before = replace(
        before,
        metrics=replace(before.metrics, near_window_shortfall_m=1),
        near_window_item_ids=("box",),
    )
    after = replace(after, near_window_item_ids=("box",))
    assert is_acceptable_proposal(before, after, "custom") is accepted
    assert beats_original(before, after, "custom") is accepted
