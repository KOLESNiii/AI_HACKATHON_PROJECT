"""Deterministic layout comparison for tools/agents, without a displayed score."""

from dataclasses import dataclass
from math import hypot, isclose, isfinite, radians
from typing import Literal

from shapely.ops import unary_union  # type: ignore[import-untyped]

from contracts.schema import MIN_HEIGHT_OVERLAP_M, MIN_PLAN_OVERLAP_M2, AuditReport, RoomScene
from services.spatial_engine.brightness import calculate_brightness_approximation
from services.spatial_engine.geometry import (
    SceneGeometry,
    SpatialInputError,
    door_swing_sector,
    prepare_scene,
)
from services.spatial_engine.report import audit_scene


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


def evaluate_layout(
    original: RoomScene, candidate: RoomScene, *, measure_brightness: bool = False
) -> LayoutEvaluation:
    """Measure a candidate against the immutable original, without modifying either.

    Critical issue count precedes graded critical area. Severity area sums overlap
    per furniture pair, outside area per offending item, and union obstruction
    per door: these are diagnostics across distinct constraints, not unique floor
    area. Every critical violation still prevents a final feasible recommendation.

    Clearance sums each item's largest missing proportion once. Movement is total
    translation plus shortest-yaw arc length at half each bbox's plan diagonal.
    Brightness is only measured on request. Unknown metrics stay None.
    """
    _check_comparable(original, candidate)
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
        ),
        brightness_measured=measure_brightness,
    )


def compare_layouts(
    original: RoomScene,
    candidate: RoomScene,
    *,
    baseline: RoomScene | None = None,
    prefer_brightness: bool = False,
) -> LayoutComparison:
    """Compare to baseline (default original); movement always references original.

    Minimise critical count, critical area and clearance deficit; maximise walking
    access; optionally maximise window openness; finally minimise movement.
    Any unavailable optional metric is skipped, never replaced by zero or infinity.
    All priorities use 1e-9 absolute/relative float tolerance. Counts are exact.
    """
    baseline_evaluation = evaluate_layout(
        original, original if baseline is None else baseline, measure_brightness=prefer_brightness
    )
    proposed = evaluate_layout(original, candidate, measure_brightness=prefer_brightness)
    a, b = baseline_evaluation.metrics, proposed.metrics
    priorities: list[tuple[str, float | None, float | None, bool]] = [
        ("critical_issue_count", a.critical_issue_count, b.critical_issue_count, False),
        (
            "critical_violation_area_m2",
            a.critical_violation_area_m2,
            b.critical_violation_area_m2,
            False,
        ),
        ("clearance_deficit", a.clearance_deficit, b.clearance_deficit, False),
        ("reachable_floor_ratio", a.reachable_floor_ratio, b.reachable_floor_ratio, True),
    ]
    if prefer_brightness:
        priorities.append(
            ("brightness_openness", a.brightness_openness, b.brightness_openness, True)
        )
    priorities.append(("movement_m", a.movement_m, b.movement_m, False))
    skipped = tuple(
        name for name, before, after, _ in priorities if before is None or after is None
    )
    for name, before, after, maximise in priorities:
        if before is None or after is None:
            continue
        equal = (
            before == after
            if name == "critical_issue_count"
            else isclose(before, after, rel_tol=1e-9, abs_tol=1e-9)
        )
        if not equal:
            better = after > before if maximise else after < before
            return LayoutComparison(
                baseline_evaluation, proposed, "better" if better else "worse", name, skipped
            )
    return LayoutComparison(baseline_evaluation, proposed, "equal", None, skipped)
