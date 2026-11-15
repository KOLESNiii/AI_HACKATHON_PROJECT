"""Deterministic layout comparison for tools/agents, without a displayed score."""

from collections.abc import Sequence
from dataclasses import dataclass
from math import hypot, isclose, isfinite, radians
from typing import Literal, get_args

from shapely.ops import unary_union  # type: ignore[import-untyped]

from contracts.schema import (
    MIN_HEIGHT_OVERLAP_M,
    MIN_PLAN_OVERLAP_M2,
    AuditReport,
    LayoutGoal,
    RoomScene,
)
from services.spatial_engine.brightness import calculate_brightness_approximation
from services.spatial_engine.feng_shui_inputs import FengShuiRequest
from services.spatial_engine.feng_shui_score import FengShuiScore, score_feng_shui
from services.spatial_engine.geometry import (
    SceneGeometry,
    SpatialInputError,
    door_swing_sector,
    prepare_scene,
    window_plan_segment,
)
from services.spatial_engine.report import audit_scene

"""What the user asked for. It reorders soft priorities only; see `compare_evaluations`."""
LAYOUT_GOALS: tuple[LayoutGoal, ...] = get_args(LayoutGoal)

NEAR_WINDOW_M = 0.5
"""An item counts as near a window when its footprint is within this plan distance of one."""

_HARD_PRIORITIES = ("critical_issue_count", "critical_violation_area_m2")
_SOFT_PRIORITIES: dict[LayoutGoal, tuple[str, ...]] = {
    "balanced": ("clearance_deficit", "reachable_floor_ratio", "movement_m"),
    "brighter": (
        "brightness_openness",
        "clearance_deficit",
        "reachable_floor_ratio",
        "movement_m",
    ),
    "roomier": ("reachable_floor_ratio", "clearance_deficit", "movement_m"),
    "minimal_changes": ("clearance_deficit", "movement_m", "reachable_floor_ratio"),
    # The user wants something we cannot measure, so movement is not penalised: only access
    # may not get worse. See `beats_original`.
    "custom": ("clearance_deficit", "reachable_floor_ratio"),
    "feng_shui": ("feng_shui_score", "clearance_deficit", "reachable_floor_ratio", "movement_m"),
}
# A new measurable goal (e.g. Feng Shui) needs three things: a metric on LayoutMetrics, an
# entry in this table, and a value in contracts.schema.LayoutGoal. Nothing else ranks layouts.
_MAXIMISED = frozenset({"reachable_floor_ratio", "brightness_openness", "feng_shui_score"})


@dataclass(frozen=True)
class LayoutMetrics:
    collision_count: int
    out_of_bounds_count: int
    blocked_door_count: int
    critical_violation_area_m2: float
    clearance_deficit: float
    reachable_floor_ratio: float | None
    translation_m: float
    rotation_equivalent_m: float
    moved_item_count: int
    brightness_openness: float | None
    near_window_shortfall_m: float | None = None
    """Summed distance beyond NEAR_WINDOW_M for the requested items; zero means every one is
    near a window. None when no item was requested or the room has no windows."""

    feng_shui_score: int | None = None
    """Full Stats score, measured on request; None when unassessed or not assessable."""

    @property
    def critical_issue_count(self) -> int:
        return self.collision_count + self.out_of_bounds_count + self.blocked_door_count

    @property
    def passes_critical_checks(self) -> bool:
        """No known collisions, boundary violations or blocked doors; not a safety certification."""
        return self.critical_issue_count == 0

    @property
    def movement_m(self) -> float:
        return self.translation_m + self.rotation_equivalent_m


@dataclass(frozen=True)
class LayoutEvaluation:
    report: AuditReport
    metrics: LayoutMetrics
    brightness_measured: bool
    near_window_item_ids: tuple[str, ...] = ()
    """Items the user asked to place near a window, sorted; empty when none was requested."""
    feng_shui: FengShuiScore | None = None
    """Exact Stats score, rule breakdown, coverage and assumptions."""


@dataclass(frozen=True)
class LayoutComparison:
    baseline: LayoutEvaluation
    candidate: LayoutEvaluation
    outcome: Literal["better", "equal", "worse"]
    deciding_metric: str | None
    skipped_unknown_metrics: tuple[str, ...]


def _check_comparable(original: RoomScene, candidate: RoomScene) -> None:
    """Do not improve metrics by changing the room, removing items or shrinking them."""
    excluded = {"furniture", "revision"}
    if original.model_dump(exclude=excluded) != candidate.model_dump(exclude=excluded):
        raise SpatialInputError("Layout comparison requires the same room and non-pose scene data")
    originals = {item.id: item for item in original.furniture}
    if set(originals) != {item.id for item in candidate.furniture}:
        raise SpatialInputError("Layout comparison must preserve furniture IDs")
    for item in candidate.furniture:
        before = originals[item.id]
        if before.model_dump(exclude={"pose"}) != item.model_dump(exclude={"pose"}):
            raise SpatialInputError(
                "Layout comparison must preserve furniture dimensions and metadata"
            )
        if item.is_fixed and item.pose != before.pose:
            raise SpatialInputError("Fixed furniture poses must remain unchanged")


def _door_overlap_area(scene: RoomScene, prepared: SceneGeometry, report: AuditReport) -> float:
    """Grade progress while a door is still blocked, using the audit's same thresholds."""
    walls = {wall.id: wall for wall in scene.walls}
    blockers = {(issue.door_id, issue.blocked_by_item_id) for issue in report.blocked_doors}
    total = 0.0
    for door in scene.doors:
        if not any(door_id == door.id for door_id, _ in blockers):
            continue
        sweep = door_swing_sector(door, walls[door.wall_id], scene.floor_polygon)
        intersections = []
        for entry in prepared.furniture:
            if (door.id, entry.item.id) not in blockers:
                continue
            for volume in entry.volumes:
                height = min(door.head_height_m, volume.y_max) - max(0.0, volume.y_min)
                if height <= MIN_HEIGHT_OVERLAP_M or isclose(
                    height, MIN_HEIGHT_OVERLAP_M, rel_tol=1e-12, abs_tol=1e-12
                ):
                    continue
                overlap = sweep.intersection(volume.footprint)
                if overlap.area > MIN_PLAN_OVERLAP_M2:
                    intersections.append(overlap)
        total += float(unary_union(intersections).area)
    return total


def _near_window_shortfall(
    scene: RoomScene, prepared: SceneGeometry, item_ids: tuple[str, ...]
) -> float | None:
    if not item_ids or not scene.windows:
        return None
    walls = {wall.id: wall for wall in scene.walls}
    segments = []
    for window in scene.windows:
        if window.wall_id not in walls:
            raise SpatialInputError("Window references an unknown wall")
        segments.append(window_plan_segment(window, walls[window.wall_id]))
    footprints = {entry.item.id: entry.footprint for entry in prepared.furniture}
    return sum(
        max(0.0, min(float(footprints[item_id].distance(s)) for s in segments) - NEAR_WINDOW_M)
        for item_id in item_ids
    )


def evaluate_layout(
    original: RoomScene,
    candidate: RoomScene,
    *,
    measure_brightness: bool = False,
    measure_feng_shui: bool = False,
    near_window_item_ids: Sequence[str] = (),
) -> LayoutEvaluation:
    """Measure a candidate against the immutable original, without modifying either.

    Critical issue count precedes graded critical area. Severity area sums overlap
    per furniture pair, outside area per offending item, and union obstruction
    per door: these are diagnostics across distinct constraints, not unique floor
    area. Every critical violation still prevents a final feasible recommendation.

    Clearance sums each item's largest missing proportion once. Movement is total
    translation plus shortest-yaw arc length at half each bbox's plan diagonal.
    Brightness is only measured on request. Unknown metrics stay None.
    `near_window_item_ids` names items the user wants near a window: their summed
    plan distance beyond NEAR_WINDOW_M to the nearest window is measured.
    """
    _check_comparable(original, candidate)
    near_ids = tuple(sorted(set(near_window_item_ids)))
    if not set(near_ids) <= {item.id for item in original.furniture}:
        raise SpatialInputError("Near-window items must be known furniture IDs")
    prepared = prepare_scene(candidate)
    report = audit_scene(candidate, _prepared=prepared)
    outside_ids = set(report.out_of_bounds_item_ids)
    outside_area = sum(
        float(entry.footprint.difference(prepared.floor).area)
        for entry in prepared.furniture
        if entry.item.id in outside_ids
    )
    critical_area = (
        sum(issue.overlap_area_m2 for issue in report.collisions)
        + outside_area
        + _door_overlap_area(candidate, prepared, report)
    )
    deficits: dict[str, float] = {}
    for issue in report.clearance_issues:
        if issue.required_m > 0:
            missing = max(0.0, min(1.0, (issue.required_m - issue.actual_m) / issue.required_m))
            deficits[issue.item_id] = max(deficits.get(issue.item_id, 0.0), missing)
    originals = {item.id: item for item in original.furniture}
    translation = rotation = 0.0
    moved = 0
    for item in candidate.furniture:
        before = originals[item.id]
        distance = hypot(item.pose.x - before.pose.x, item.pose.z - before.pose.z)
        # Normalize before subtraction so finite but very large yaw values do not overflow.
        turn = abs(((item.pose.yaw_deg % 360 - before.pose.yaw_deg % 360 + 180) % 360) - 180)
        translation += distance
        rotation += hypot(item.bbox_m.width, item.bbox_m.depth) / 2 * radians(turn)
        moved += int(distance > 1e-9 or turn > 1e-9)
    if not all(
        isfinite(value) for value in (critical_area, translation, rotation, translation + rotation)
    ):
        raise SpatialInputError("Layout metrics must be finite")
    brightness = (
        calculate_brightness_approximation(candidate, _prepared=prepared).openness_ratio
        if measure_brightness
        else None
    )
    feng_shui = score_feng_shui(FengShuiRequest(scene=candidate)) if measure_feng_shui else None
    near_window = _near_window_shortfall(candidate, prepared, near_ids)
    if near_window is not None and not isfinite(near_window):
        raise SpatialInputError("Layout metrics must be finite")
    return LayoutEvaluation(
        report=report,
        metrics=LayoutMetrics(
            collision_count=len(report.collisions),
            out_of_bounds_count=len(outside_ids),
            blocked_door_count=len({issue.door_id for issue in report.blocked_doors}),
            critical_violation_area_m2=critical_area,
            clearance_deficit=sum(deficits.values()),
            reachable_floor_ratio=report.walkable_floor_ratio,
            translation_m=translation,
            rotation_equivalent_m=rotation,
            moved_item_count=moved,
            brightness_openness=brightness,
            near_window_shortfall_m=near_window,
            feng_shui_score=None if feng_shui is None else feng_shui.score,
        ),
        brightness_measured=measure_brightness,
        near_window_item_ids=near_ids,
        feng_shui=feng_shui,
    )


def compare_evaluations(
    baseline: LayoutEvaluation, candidate: LayoutEvaluation, goal: LayoutGoal = "balanced"
) -> LayoutComparison:
    """Rank two evaluations of the same original under the user's goal.

    Hard feasibility always comes first: fewer critical issues, then smaller
    critical violation area. A requested near-window placement comes next. The
    goal only reorders the remaining soft priorities:

    - balanced: front clearance, walking area, least movement.
    - brighter: window openness, front clearance, walking area, least movement.
    - roomier: walking area, front clearance, least movement.
    - minimal_changes: front clearance, least movement, walking area.
    - custom: front clearance, walking area; movement is not penalised.
    - feng_shui: Feng Shui score, front clearance, walking area, least movement.

    Any unavailable metric is skipped, never replaced by zero or infinity.
    All priorities use 1e-9 absolute/relative float tolerance. Counts are exact.
    """
    if goal not in _SOFT_PRIORITIES:
        raise SpatialInputError("Unknown layout goal")
    if baseline.near_window_item_ids != candidate.near_window_item_ids:
        raise SpatialInputError("Compared layouts must measure the same near-window items")
    if goal == "brighter" and not (baseline.brightness_measured and candidate.brightness_measured):
        raise SpatialInputError("The brighter goal requires measured window openness")
    if goal == "feng_shui" and (baseline.feng_shui is None or candidate.feng_shui is None):
        raise SpatialInputError("Feng Shui comparison requires measured full-rule scores")
    names = [*_HARD_PRIORITIES]
    if candidate.near_window_item_ids:
        names.append("near_window_shortfall_m")
    names.extend(_SOFT_PRIORITIES[goal])
    a, b = baseline.metrics, candidate.metrics
    values: list[tuple[str, float | None, float | None]] = [
        (name, getattr(a, name), getattr(b, name)) for name in names
    ]
    skipped = tuple(name for name, before, after in values if before is None or after is None)
    for name, before, after in values:
        if before is None or after is None:
            continue
        equal = (
            before == after
            if name == "critical_issue_count"
            else isclose(before, after, rel_tol=1e-9, abs_tol=1e-9)
        )
        if not equal:
            better = after > before if name in _MAXIMISED else after < before
            return LayoutComparison(
                baseline, candidate, "better" if better else "worse", name, skipped
            )
    return LayoutComparison(baseline, candidate, "equal", None, skipped)


def compare_layouts(
    original: RoomScene,
    candidate: RoomScene,
    *,
    baseline: RoomScene | None = None,
    goal: LayoutGoal = "balanced",
    near_window_item_ids: Sequence[str] = (),
) -> LayoutComparison:
    """Compare to baseline (default original); movement always references original.

    Evaluates both layouts and ranks them with `compare_evaluations`. Window
    openness is measured only for the brighter goal.
    """
    measure = goal == "brighter"
    baseline_evaluation = evaluate_layout(
        original,
        original if baseline is None else baseline,
        measure_brightness=measure,
        measure_feng_shui=(goal == "feng_shui"),
        near_window_item_ids=near_window_item_ids,
    )
    proposed = evaluate_layout(
        original,
        candidate,
        measure_brightness=measure,
        measure_feng_shui=(goal == "feng_shui"),
        near_window_item_ids=near_window_item_ids,
    )
    return compare_evaluations(baseline_evaluation, proposed, goal)


def _access_not_worse(original: LayoutEvaluation, candidate: LayoutEvaluation) -> bool:
    """Check access independently; lexicographic ranking can hide a regression."""
    before, after = original.metrics, candidate.metrics
    if after.clearance_deficit > before.clearance_deficit and not isclose(
        after.clearance_deficit, before.clearance_deficit, rel_tol=1e-9, abs_tol=1e-9
    ):
        return False
    if before.reachable_floor_ratio is not None:
        if after.reachable_floor_ratio is None:
            return False
        if after.reachable_floor_ratio < before.reachable_floor_ratio and not isclose(
            after.reachable_floor_ratio, before.reachable_floor_ratio, rel_tol=1e-9, abs_tol=1e-9
        ):
            return False
    return True


def is_acceptable_proposal(
    original: LayoutEvaluation, candidate: LayoutEvaluation, goal: LayoutGoal = "balanced"
) -> bool:
    """Whether a layout may be recommended at all, before it is ranked.

    Never with overlapping furniture or anything outside the room: those are physically
    impossible. A blocked door swing is tolerated only when that same door was already
    blocked in the original, so a room with a problem no move can fix (a fixed item in a
    door's swing) can still receive suggestions. Blocking a previously clear door is refused.
    Custom requests also require each known access metric not to regress from the original.
    """
    blocked_before = {issue.door_id for issue in original.report.blocked_doors}
    blocked_after = {issue.door_id for issue in candidate.report.blocked_doors}
    metrics = candidate.metrics
    return (
        metrics.collision_count == 0
        and metrics.out_of_bounds_count == 0
        and blocked_after <= blocked_before
        and (goal != "custom" or _access_not_worse(original, candidate))
    )


def beats_original(
    baseline: LayoutEvaluation, candidate: LayoutEvaluation, goal: LayoutGoal
) -> bool:
    """Whether a candidate is a worthwhile suggestion compared with the original.

    A measurable goal needs a strictly better ranking. A `custom` request cannot be measured,
    so moving something is the point: the candidate must not rank worse, each access metric
    must independently not regress, and at least one item must actually move.
    """
    outcome = compare_evaluations(baseline, candidate, goal).outcome
    if goal == "custom":
        return (
            _access_not_worse(baseline, candidate)
            and outcome != "worse"
            and candidate.metrics.moved_item_count > 0
        )
    return outcome == "better"
