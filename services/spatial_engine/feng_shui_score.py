"""Deterministic Form School feng shui score from plan geometry; no model call.

Every rule yields a sub-score in [0, 1] with a weight. The score is the weighted mean of the
rules that could be assessed, times 100. `coverage` is the assessed share of the weight that
applies to the room, so a partial assessment never reads as a clean bill of health. Compass
schools (bagua, Flying Stars) are never used. See the spatial service README for the table.
"""

from collections.abc import Iterable
from dataclasses import dataclass
from math import acos, cos, degrees, hypot, radians, sin

from shapely.geometry import LineString, Point, Polygon  # type: ignore[import-untyped]
from shapely.ops import unary_union  # type: ignore[import-untyped]

from contracts.schema import (
    AuditReport,
    DoorOpening,
    FengShuiRuleScore,
    FengShuiScore,
    FengShuiSightline,
    RoomScene,
)
from services.spatial_engine.feng_shui_inputs import (
    FengShuiRequest,
    validate_feng_shui_request,
)
from services.spatial_engine.geometry import (
    FurnitureGeometry,
    SceneGeometry,
    SpatialInputError,
    door_opening_frame,
    prepare_scene,
    window_plan_segment,
)

Vec = tuple[float, float]

KEY_CATEGORIES = ("bed", "desk", "sofa")
"""Items with an occupant whose position the command-position rules judge."""
TALL_M = 1.2
"""Items taller than this block a seated or lying occupant's view of a door."""
LOW_M = 0.4
"""Items lower than this (rugs, mats) neither cut a draught nor aim a corner."""
AUDIT_CAP = 50
"""Highest score while the audit reports collisions, blocked doors or out-of-bounds items."""
NOT_MODELLED = (
    "beams, clutter, materials, colour, plants and lighting are not modelled from geometry",
)

WEIGHTS = {
    "door_visible": 3.0,
    "line_of_sight": 1.0,
    "door_axis": 2.0,
    "backing": 2.0,
    "bed_side_access": 1.0,
    "sharp_corners": 1.0,
    "door_window_draught": 1.0,
    "entry_openness": 1.0,
    "balance": 0.5,
    "mirror_reflection": 1.0,
}
_DOOR_RULES = ("door_visible", "line_of_sight", "door_axis")


# The response models live in contracts/schema.py (FengShuiScore, FengShuiRuleScore).
RuleScore = FengShuiRuleScore


@dataclass(frozen=True)
class _Occupant:
    item: FurnitureGeometry
    position: Vec
    facing: Vec
    back: Vec
    back_edge: LineString
    anchored: bool

    @property
    def label(self) -> str:
        return "anchored occupant" if self.anchored else "default occupant"


@dataclass(frozen=True)
class _Door:
    door: DoorOpening
    centre: Vec
    normal: Vec
    leaf: LineString


def _add(a: Vec, b: Vec, k: float = 1.0) -> Vec:
    return (a[0] + k * b[0], a[1] + k * b[1])


def _sub(a: Vec, b: Vec) -> Vec:
    return (a[0] - b[0], a[1] - b[1])


def _dot(a: Vec, b: Vec) -> float:
    return a[0] * b[0] + a[1] * b[1]


def _unit(v: Vec) -> Vec | None:
    length = hypot(*v)
    return None if length < 1e-9 else (v[0] / length, v[1] / length)


def _yaw(deg: float) -> Vec:
    """Front vector in plan, matching geometry.furniture_footprint."""
    return (sin(radians(deg)), cos(radians(deg)))


def _angle_deg(a: Vec, b: Vec) -> float:
    ua, ub = _unit(a), _unit(b)
    if ua is None or ub is None:
        return 0.0
    return degrees(acos(max(-1.0, min(1.0, _dot(ua, ub)))))


def _rect(centre: Vec, u: Vec, half_u: float, half_v: float) -> Polygon:
    """Rectangle with half-extent half_u along unit u and half_v along u rotated 90 degrees."""
    v = (-u[1], u[0])
    return Polygon(
        [
            _add(_add(centre, u, su * half_u), v, sv * half_v)
            for su, sv in ((-1, -1), (1, -1), (1, 1), (-1, 1))
        ]
    )


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def _height(entry: FurnitureGeometry) -> float:
    return max((v.y_max for v in entry.volumes), default=entry.item.bbox_m.height)


def _occupants(request: FengShuiRequest, furniture: Iterable[FurnitureGeometry]) -> list[_Occupant]:
    anchors: dict[str, list[tuple[str, Vec, Vec]]] = {}
    for a in request.activities:
        anchors.setdefault(a.item_id, []).append((a.kind, (a.x, a.z), _yaw(a.facing_yaw_deg)))
    result = []
    for entry in furniture:
        item = entry.item
        front = _yaw(item.pose.yaw_deg)
        pose = (item.pose.x, item.pose.z)
        width, depth = item.bbox_m.width, item.bbox_m.depth
        if item.id in anchors:
            for kind, point, facing in anchors[item.id]:
                if kind == "headboard":
                    occupant, back, edge = _add(point, facing, 0.3), point, width
                else:
                    occupant, back, edge = point, _add(point, facing, -0.3), 0.6
                result.append(
                    _Occupant(entry, occupant, facing, back, _edge(back, facing, edge), True)
                )
            continue
        if item.category not in KEY_CATEGORIES:
            continue
        if item.category == "desk":
            occupant = _add(pose, front, depth / 2 + 0.45)
            facing = (-front[0], -front[1])
            back = _add(occupant, front, 0.3)
            result.append(_Occupant(entry, occupant, facing, back, _edge(back, facing, 0.6), False))
        else:
            back = _add(pose, front, -depth / 2)
            occupant = _add(back, front, min(0.3, depth / 2)) if item.category == "bed" else pose
            result.append(_Occupant(entry, occupant, front, back, _edge(back, front, width), False))
    return result


def _edge(centre: Vec, facing: Vec, length: float) -> LineString:
    side = (facing[1], -facing[0])
    return LineString([_add(centre, side, -length / 2), _add(centre, side, length / 2)])


def _doors(request: FengShuiRequest) -> list[_Door]:
    scene = request.scene
    walls = {w.id: w for w in scene.walls}
    doors = []
    for door in scene.doors:
        if request.main_entry_door_id is not None and door.id != request.main_entry_door_id:
            continue
        if door.wall_id not in walls:
            raise SpatialInputError("Door references an unknown wall")
        centre, normal, leaf = door_opening_frame(door, walls[door.wall_id], scene.floor_polygon)
        doors.append(_Door(door, centre, normal, leaf))
    return doors


def _door_strip(door: _Door, reach: float) -> Polygon:
    """The door's width projected straight into the room for `reach` metres."""
    return _rect(
        _add(door.centre, door.normal, reach / 2), door.normal, reach / 2, door.door.width_m / 2
    )


def _command_rules(
    occ: _Occupant,
    doors: list[_Door],
    others: list[FurnitureGeometry],
    floor: Polygon,
    reach: float,
) -> tuple[list[RuleScore], list[FengShuiSightline]]:
    item = occ.item.item
    is_bed = item.category == "bed"
    tall = [o.footprint for o in others if _height(o) > TALL_M]
    walkable = floor.buffer(1e-3)
    scores: dict[str, list[float]] = {rule: [] for rule in _DOOR_RULES}
    notes: dict[str, list[str]] = {rule: [] for rule in _DOOR_RULES}
    sightlines = []
    for d in doors:
        to_door = _sub(d.centre, occ.position)
        theta = _angle_deg(occ.facing, to_door)
        visible = 1.0 if theta <= 60 else _clamp((120 - theta) / 60)
        sight = LineString([occ.position, d.centre])
        clear = walkable.covers(sight) and not any(sight.intersects(t) for t in tall)
        rel = _sub(occ.position, d.centre)
        t, offset = _dot(rel, d.normal), abs(rel[0] * d.normal[1] - rel[1] * d.normal[0])
        coffin = (
            is_bed
            and _dot(occ.facing, (-d.normal[0], -d.normal[1])) > cos(radians(20))
            and _door_strip(d, reach).intersects(occ.item.footprint)
        )
        in_line = t > 0 and offset < d.door.width_m / 2 + 0.3
        axis = 0.0 if coffin else 0.5 if in_line else 1.0
        scores["door_visible"].append(visible)
        scores["line_of_sight"].append(1.0 if clear else 0.0)
        scores["door_axis"].append(axis)
        notes["door_visible"].append(f"{d.door.id}: door {theta:.0f}° from facing")
        notes["line_of_sight"].append(f"{d.door.id}: {'clear' if clear else 'blocked'}")
        notes["door_axis"].append(
            f"{d.door.id}: "
            + ("feet toward door in its line" if coffin else f"{offset:.2f} m off door axis")
        )
        if coffin:
            reason = "Bed foot points out of the door, in its direct line"
            sightlines.append(
                FengShuiSightline(
                    from_item_id=item.id,
                    to_door_id=d.door.id,
                    status="coffin_alignment",
                    reason=reason,
                )
            )
        elif theta > 120:
            reason = f"Door is {theta:.0f}° from the occupant's facing direction"
            sightlines.append(
                FengShuiSightline(
                    from_item_id=item.id, to_door_id=d.door.id, status="back_to_door", reason=reason
                )
            )
        elif visible >= 0.8 and clear and axis == 1.0:
            reason = f"Door visible ({theta:.0f}° from facing), clear sightline, off its axis"
            sightlines.append(
                FengShuiSightline(
                    from_item_id=item.id,
                    to_door_id=d.door.id,
                    status="command_position",
                    reason=reason,
                )
            )
    rules = [
        RuleScore(
            rule=rule,
            object_ids=[item.id, *(d.door.id for d in doors)],
            score=round(sum(values) / len(values), 3),
            weight=WEIGHTS[rule],
            detail=f"{occ.label}; " + "; ".join(notes[rule]),
        )
        for rule, values in scores.items()
    ]
    return rules, sightlines


def _backing(occ: _Occupant, floor: Polygon, openings: list[LineString]) -> RuleScore:
    gap = floor.exterior.distance(Point(occ.back))
    near = _clamp(1 - (gap - 0.1) / 0.5)
    band = occ.back_edge.buffer(0.15, cap_style="flat")
    exposed = sum(band.intersection(o).length for o in openings)
    exposure = _clamp(exposed / max(occ.back_edge.length, 1e-9))
    return RuleScore(
        rule="backing",
        object_ids=[occ.item.item.id],
        score=round(near * (1 - exposure), 3),
        weight=WEIGHTS["backing"],
        detail=f"{occ.label}; back {gap:.2f} m from a wall, {exposure:.0%} against an opening",
    )


def _bed_side_access(bed: FurnitureGeometry, floor: Polygon, blockers: Polygon) -> RuleScore:
    item = bed.item
    front = _yaw(item.pose.yaw_deg)
    right = (front[1], -front[0])
    free = []
    for side in (-1, 1):
        centre = _add((item.pose.x, item.pose.z), right, side * (item.bbox_m.width / 2 + 0.3))
        strip = _rect(centre, front, item.bbox_m.depth / 2, 0.3)
        free.append(strip.intersection(floor).difference(blockers).area / strip.area)
    return RuleScore(
        rule="bed_side_access",
        object_ids=[item.id],
        score=round(_clamp(min(free)), 3),
        weight=WEIGHTS["bed_side_access"],
        detail=f"0.6 m strips beside the bed are {free[0]:.0%} and {free[1]:.0%} free",
    )


def _sharp_corners(occ: _Occupant, others: list[FurnitureGeometry]) -> RuleScore:
    aimed = []
    for other in others:
        if _height(other) < LOW_M:
            continue
        centroid = (other.footprint.centroid.x, other.footprint.centroid.y)
        for corner in list(other.footprint.exterior.coords)[:-1]:
            to_occ = _sub(occ.position, corner)
            bisector = _unit(_sub(corner, centroid))
            direction = _unit(to_occ)
            if hypot(*to_occ) > 1.5 or bisector is None or direction is None:
                continue
            if _dot(bisector, direction) > cos(radians(30)):
                aimed.append(other.item.id)
    return RuleScore(
        rule="sharp_corners",
        object_ids=[occ.item.item.id, *sorted(set(aimed))],
        score=max(0.0, 1 - 0.25 * len(aimed)),
        weight=WEIGHTS["sharp_corners"],
        detail=f"{occ.label}; {len(aimed)} furniture corner(s) within 1.5 m aimed at it",
    )


def _draught(d: _Door, scene: RoomScene, reach: float, solid: list[Polygon]) -> RuleScore:
    walls = {w.id: w for w in scene.walls}
    strip = _door_strip(d, reach)
    overlap, ids = 0.0, [d.door.id]
    for window in scene.windows:
        if window.wall_id == d.door.wall_id or window.wall_id not in walls:
            continue
        length = (
            window_plan_segment(window, walls[window.wall_id])
            .intersection(strip.buffer(0.05))
            .length
        )
        if length > 0:
            overlap += length
            ids.append(window.id)
    shielded = overlap > 0 and any(strip.intersects(s) for s in solid)
    score = 1.0 if shielded else _clamp(1 - overlap / d.door.width_m)
    detail = (
        "no window opposite the door"
        if overlap == 0
        else f"{overlap:.2f} m of window opposite the door, "
        + ("shielded by furniture" if shielded else "unshielded")
    )
    return RuleScore(
        rule="door_window_draught",
        object_ids=ids,
        score=round(score, 3),
        weight=WEIGHTS["door_window_draught"],
        detail=detail,
    )


def _entry_openness(d: _Door, floor: Polygon, blockers: Polygon) -> RuleScore:
    half_disc = (
        Point(d.centre)
        .buffer(1.0)
        .intersection(_rect(_add(d.centre, d.normal, 0.5), d.normal, 0.5, 1.0))
        .intersection(floor)
    )
    free = half_disc.difference(blockers).area / half_disc.area if half_disc.area > 0 else 0.0
    return RuleScore(
        rule="entry_openness",
        object_ids=[d.door.id],
        score=round(_clamp(free), 3),
        weight=WEIGHTS["entry_openness"],
        detail=f"{free:.0%} of the 1 m area inside is free",
    )


def _balance(furniture: tuple[FurnitureGeometry, ...], floor: Polygon) -> RuleScore:
    mass = unary_union([f.footprint for f in furniture]).centroid
    minx, miny, maxx, maxy = floor.bounds
    shift = mass.distance(floor.centroid)
    half_diagonal = hypot(maxx - minx, maxy - miny) / 2
    return RuleScore(
        rule="balance",
        object_ids=[f.item.id for f in furniture],
        score=round(_clamp(1 - shift / half_diagonal), 3),
        weight=WEIGHTS["balance"],
        detail=f"furniture centre of mass is {shift:.2f} m from the room centre",
    )


def _mirror(
    request: FengShuiRequest, beds: list[_Occupant], furniture: tuple[FurnitureGeometry, ...]
) -> list[RuleScore]:
    rules = []
    for mirror in request.mirrors or []:
        normal, origin, seen = _yaw(mirror.normal_yaw_deg), (mirror.x, mirror.z), []
        for bed in beds:
            to_bed = _sub(bed.position, origin)
            if _dot(to_bed, normal) <= 0 or _angle_deg(normal, to_bed) > 60:
                continue
            ray = LineString([origin, bed.position])
            blockers = [
                f.footprint
                for f in furniture
                if f.item.id != bed.item.item.id and _height(f) > TALL_M
            ]
            if not any(ray.intersects(b) for b in blockers):
                seen.append(bed.item.item.id)
        rules.append(
            RuleScore(
                rule="mirror_reflection",
                object_ids=[mirror.id, *seen],
                score=0.0 if seen else 1.0,
                weight=WEIGHTS["mirror_reflection"],
                detail="faces a bed with nothing tall between" if seen else "faces no bed",
            )
        )
    return rules


def score_feng_shui(
    request: FengShuiRequest,
    *,
    _audit: AuditReport | None = None,
    _prepared: SceneGeometry | None = None,
) -> FengShuiScore:
    """Score a room read-only. Raises SpatialInputError for invalid scenes or references.

    The layout optimiser passes the audit and geometry it already computed for the same
    scene. That skips the assessment-only request checks (such as IDs unique across object
    types), which a scene the audit accepts may not meet.
    """
    if _audit is None or _prepared is None:
        _audit, _ = validate_feng_shui_request(request)
        _prepared = prepare_scene(request.scene)
    audit = _audit
    scene = request.scene
    prepared = _prepared
    floor = prepared.floor
    furniture = prepared.furniture
    minx, miny, maxx, maxy = floor.bounds
    reach = hypot(maxx - minx, maxy - miny)
    doors = _doors(request)
    occupants = _occupants(request, furniture)
    blockers = unary_union([f.footprint for f in furniture]) if furniture else Polygon()
    solid = [f.footprint for f in furniture if _height(f) >= LOW_M]
    walls = {w.id: w for w in scene.walls}
    openings = [d.leaf for d in doors] + [
        window_plan_segment(w, walls[w.wall_id]) for w in scene.windows if w.wall_id in walls
    ]
    rules: list[RuleScore] = []
    sightlines: list[FengShuiSightline] = []
    unassessed: list[str] = list(NOT_MODELLED)
    missing_weight = 0.0

    for occ in occupants:
        others = [f for f in furniture if f.item.id != occ.item.item.id]
        if doors:
            found, lines = _command_rules(occ, doors, others, floor, reach)
            rules += found
            sightlines += lines
        else:
            missing_weight += sum(WEIGHTS[r] for r in _DOOR_RULES)
        rules.append(_backing(occ, floor, openings))
        rules.append(_sharp_corners(occ, others))
    for bed in (f for f in furniture if f.item.category == "bed"):
        others = unary_union([f.footprint for f in furniture if f.item.id != bed.item.id])
        rules.append(_bed_side_access(bed, floor, others))
    for d in doors:
        rules.append(_draught(d, scene, reach, solid))
        rules.append(_entry_openness(d, floor, blockers))
    if furniture:
        rules.append(_balance(furniture, floor))
    beds = [o for o in occupants if o.item.item.category == "bed"]
    if request.mirrors is None:
        if beds:
            missing_weight += WEIGHTS["mirror_reflection"]
            unassessed.append("mirror_reflection: no mirror inventory supplied")
    else:
        rules += _mirror(request, beds, furniture)

    if not doors:
        missing_weight += WEIGHTS["door_window_draught"] + WEIGHTS["entry_openness"]
        unassessed.append("door rules: the room has no known door")
    if not occupants:
        unassessed.append("command position: no bed, desk, sofa or activity anchor")
    elif not any(o.anchored for o in occupants):
        unassessed.append("occupant positions inferred from furniture category; add anchors")

    total = sum(r.weight for r in rules)
    coverage = total / (total + missing_weight) if total + missing_weight > 0 else 0.0
    score = None
    capped = False
    if doors and occupants and total > 0:
        score = round(100 * sum(r.weight * r.score for r in rules) / total)
        if audit.collisions or audit.blocked_doors or audit.out_of_bounds_item_ids:
            capped = True
            score = min(score, AUDIT_CAP)
    return FengShuiScore(
        scene_id=scene.scene_id,
        revision=scene.revision,
        score=score,
        coverage=round(coverage, 3),
        capped_by_audit=capped,
        sightlines=sightlines,
        rules=rules,
        unassessed=unassessed,
    )
