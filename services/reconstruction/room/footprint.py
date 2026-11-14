"""Plan geometry for placing furniture, in the conventions of `contracts/schema.py`.

Everything is a `Prism`: a convex polygon on the floor (room X/Z, metres) with a height range.
An item is one prism per collision part, a door sweep is a sector, a keep-out zone is a
rectangle. The rules mirror the contract and the spatial audit, so a layout that is valid here
is clean there:

- Two prisms overlap when they share more than `MIN_PLAN_OVERLAP_M2` in plan and more than
  `MIN_HEIGHT_OVERLAP_M` in height. Touching is not overlap.
- An item is inside the room when its `bbox_m` footprint is covered by `floor_polygon`; contact
  with the boundary is allowed.

Plain Python on purpose: the reconstruction extra has no polygon library.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from contracts.schema import (
    MIN_HEIGHT_OVERLAP_M,
    MIN_PLAN_OVERLAP_M2,
    BBoxM,
    CollisionPart,
    DoorOpening,
    FurnitureItem,
    Pose2D,
    WallSegment,
    WindowOpening,
)

Point = tuple[float, float]

BOUNDARY_TOLERANCE_M = 1e-9
"""Floating-point slack for "on the boundary"; the audit's out-of-bounds check uses the same."""
MIN_WALL_LENGTH_M = 1e-6
"""A wall shorter than this has no direction and gives no placement frame."""


@dataclass(frozen=True)
class Prism:
    points: tuple[Point, ...]
    """Convex polygon in room (x, z), either winding."""
    y_min: float
    y_max: float

    @property
    def bounds(self) -> tuple[float, float, float, float]:
        xs, zs = [p[0] for p in self.points], [p[1] for p in self.points]
        return min(xs), min(zs), max(xs), max(zs)


@dataclass(frozen=True)
class WallFrame:
    """A wall as a placement frame: `along` runs start -> end, `inward` points into the room."""

    wall: WallSegment
    start: Point
    along: Point
    inward: Point
    length: float

    def point(self, t: float, offset: float = 0.0) -> Point:
        """`t` metres from the start along the wall, `offset` metres into the room."""
        return (
            self.start[0] + self.along[0] * t + self.inward[0] * offset,
            self.start[1] + self.along[1] * t + self.inward[1] * offset,
        )

    def locate(self, p: Point) -> tuple[float, float]:
        """Inverse of `point`: (metres along the wall, metres into the room)."""
        dx, dz = p[0] - self.start[0], p[1] - self.start[1]
        return (
            dx * self.along[0] + dz * self.along[1],
            dx * self.inward[0] + dz * self.inward[1],
        )


def wall_frame(wall: WallSegment) -> WallFrame | None:
    dx, dz = wall.end.x - wall.start.x, wall.end.z - wall.start.z
    length = math.hypot(dx, dz)
    if length <= MIN_WALL_LENGTH_M:
        return None
    ux, uz = dx / length, dz / length
    return WallFrame(wall, (wall.start.x, wall.start.z), (ux, uz), (-uz, ux), length)


# --- polygons ---------------------------------------------------------------------------------


def shoelace(poly: Sequence[Point]) -> float:
    """Twice the signed area over (x, z); positive is the contract's `floor_polygon` winding."""
    n = len(poly)
    return sum(poly[i - 1][0] * poly[i][1] - poly[i][0] * poly[i - 1][1] for i in range(n))


def clip_convex(subject: Sequence[Point], clip: Sequence[Point]) -> list[Point]:
    """Sutherland-Hodgman: the part of `subject` inside the convex polygon `clip`."""
    sign = 1.0 if shoelace(clip) > 0 else -1.0
    out = list(subject)
    for i in range(len(clip)):
        if not out:
            break
        a, b = clip[i], clip[(i + 1) % len(clip)]
        ex, ez = b[0] - a[0], b[1] - a[1]

        def side(p: Point, a: Point = a, ex: float = ex, ez: float = ez) -> float:
            return sign * (ex * (p[1] - a[1]) - ez * (p[0] - a[0]))

        inp, out = out, []
        prev, prev_side = inp[-1], side(inp[-1])
        for cur in inp:
            cur_side = side(cur)
            if (cur_side >= 0) != (prev_side >= 0):
                t = prev_side / (prev_side - cur_side)
                out.append((prev[0] + t * (cur[0] - prev[0]), prev[1] + t * (cur[1] - prev[1])))
            if cur_side >= 0:
                out.append(cur)
            prev, prev_side = cur, cur_side
    return out


def overlap_area(a: Sequence[Point], b: Sequence[Point]) -> float:
    """Plan area shared by two convex polygons."""
    return abs(shoelace(clip_convex(a, b))) / 2


def _bounds_apart(a: Prism, b: Prism) -> bool:
    ax0, az0, ax1, az1 = a.bounds
    bx0, bz0, bx1, bz1 = b.bounds
    return ax1 <= bx0 or bx1 <= ax0 or az1 <= bz0 or bz1 <= az0


def prisms_overlap(a: Prism, b: Prism) -> bool:
    """The contract's collision rule for one pair of parts."""
    height = min(a.y_max, b.y_max) - max(a.y_min, b.y_min)
    if height <= MIN_HEIGHT_OVERLAP_M or math.isclose(
        height, MIN_HEIGHT_OVERLAP_M, rel_tol=1e-12, abs_tol=1e-12
    ):
        return False
    if _bounds_apart(a, b):
        return False
    return overlap_area(a.points, b.points) > MIN_PLAN_OVERLAP_M2


def any_overlap(a: Sequence[Prism], b: Sequence[Prism]) -> bool:
    return any(prisms_overlap(pa, pb) for pa in a for pb in b)


def _segment_distance(p: Point, a: Point, b: Point) -> float:
    ex, ez = b[0] - a[0], b[1] - a[1]
    length2 = ex * ex + ez * ez
    if length2 == 0:
        return math.hypot(p[0] - a[0], p[1] - a[1])
    t = max(0.0, min(1.0, ((p[0] - a[0]) * ex + (p[1] - a[1]) * ez) / length2))
    return math.hypot(p[0] - a[0] - t * ex, p[1] - a[1] - t * ez)


def boundary_distance(p: Point, poly: Sequence[Point]) -> float:
    return min(_segment_distance(p, poly[i - 1], poly[i]) for i in range(len(poly)))


def point_in_polygon(p: Point, poly: Sequence[Point]) -> bool:
    """Strictly inside a simple polygon (even-odd rule); use `boundary_distance` for contact."""
    x, z = p
    hits = False
    for i in range(len(poly)):
        (x0, z0), (x1, z1) = poly[i - 1], poly[i]
        if (z0 > z) != (z1 > z) and x < x0 + (z - z0) * (x1 - x0) / (z1 - z0):
            hits = not hits
    return hits


def _crosses_interior(a: Point, b: Point, convex: Sequence[Point], margin: float) -> bool:
    """Whether segment a-b passes through `convex` more than `margin` inside every edge."""
    sign = 1.0 if shoelace(convex) > 0 else -1.0
    dx, dz = b[0] - a[0], b[1] - a[1]
    t0, t1 = 0.0, 1.0
    for i in range(len(convex)):
        p, q = convex[i - 1], convex[i]
        ex, ez = q[0] - p[0], q[1] - p[1]
        length = math.hypot(ex, ez)
        if length == 0:
            continue
        # Signed distance inside this edge, as value + t * slope along the segment.
        value = sign * (ex * (a[1] - p[1]) - ez * (a[0] - p[0])) / length - margin
        slope = sign * (ex * dz - ez * dx) / length
        if slope == 0:
            if value <= 0:
                return False
            continue
        t = -value / slope
        if slope > 0:
            t0 = max(t0, t)
        else:
            t1 = min(t1, t)
        if t0 >= t1:
            return False
    return t1 - t0 > 0


def covered_by(
    convex: Sequence[Point], polygon: Sequence[Point], tolerance: float = BOUNDARY_TOLERANCE_M
) -> bool:
    """Whether a convex polygon lies within a simple polygon; boundary contact is allowed."""
    for p in convex:
        if not point_in_polygon(p, polygon) and boundary_distance(p, polygon) > tolerance:
            return False
    return not any(
        _crosses_interior(polygon[i - 1], polygon[i], convex, tolerance)
        for i in range(len(polygon))
    )


# --- furniture --------------------------------------------------------------------------------


def front_direction(yaw_deg: float) -> Point:
    yaw = math.radians(yaw_deg)
    return math.sin(yaw), math.cos(yaw)


def yaw_of(front: Point) -> float:
    """The yaw whose front direction is `front`, in [0, 360)."""
    yaw = math.degrees(math.atan2(front[0], front[1])) % 360
    # Snap the float noise of axis-aligned walls so poses read 90, not 90.00000000000001.
    return 0.0 if abs(yaw - 360) < 1e-9 else round(yaw, 9)


def _rect(pose: Pose2D, x: float, z: float, width: float, depth: float) -> tuple[Point, ...]:
    """A local rectangle (centre x/z, extents along local X/Z) in room coordinates."""
    yaw = math.radians(pose.yaw_deg % 360)
    c, s = math.cos(yaw), math.sin(yaw)
    return tuple(
        (pose.x + lx * c + lz * s, pose.z - lx * s + lz * c)
        for lx, lz in (
            (x - width / 2, z - depth / 2),
            (x + width / 2, z - depth / 2),
            (x + width / 2, z + depth / 2),
            (x - width / 2, z + depth / 2),
        )
    )


def footprint(bbox: BBoxM, pose: Pose2D) -> Prism:
    """The whole `bbox_m` box: what must stay inside the room."""
    return Prism(_rect(pose, 0, 0, bbox.width, bbox.depth), 0.0, bbox.height)


def occupied(bbox: BBoxM, parts: Sequence[CollisionPart], pose: Pose2D) -> list[Prism]:
    """The occupied volume: one prism per collision part, or the whole box when there are none."""
    if not parts:
        return [footprint(bbox, pose)]
    return [Prism(_rect(pose, p.x, p.z, p.width, p.depth), p.y_min, p.y_max) for p in parts]


def item_occupied(item: FurnitureItem) -> list[Prism]:
    return occupied(item.bbox_m, item.collision_parts, item.pose)


def front_zone(bbox: BBoxM, pose: Pose2D, clear_m: float, headroom_m: float) -> Prism | None:
    """The strip in front of an item that should stay free for access."""
    if clear_m <= 0:
        return None
    centre_z = bbox.depth / 2 + clear_m / 2
    return Prism(_rect(pose, 0, centre_z, bbox.width, clear_m), 0.0, headroom_m)


# --- openings ---------------------------------------------------------------------------------


def closed_leaf(door: DoorOpening, frame: WallFrame) -> tuple[Point, Point]:
    """(direction of the closed leaf from the hinge, side the leaf opens towards)."""
    n = frame.inward
    side = n if door.swings_into_room else (-n[0], -n[1])
    leaf = frame.along
    for sgn in (1.0, -1.0):
        leaf = (frame.along[0] * sgn, frame.along[1] * sgn)
        clockwise = (-leaf[1], leaf[0])
        # Rotating the closed leaf 90 degrees in the swing direction must point to `side`.
        if (clockwise[0] * side[0] + clockwise[1] * side[1] > 0) == door.swing_clockwise:
            break
    return leaf, side


def door_sweep(door: DoorOpening, frame: WallFrame) -> Prism | None:
    """The area the leaf sweeps, bounded from outside like the audit's sector (1 degree steps)."""
    angle = min(max(door.swing_angle_deg, 0.0), 180.0)
    if angle == 0 or door.width_m <= 0:
        return None
    leaf, side = closed_leaf(door, frame)
    hx, hz = door.hinge_pos.x, door.hinge_pos.z
    w = door.width_m

    def at(theta: float, radius: float) -> Point:
        c, s = math.cos(theta), math.sin(theta)
        return (
            hx + radius * (leaf[0] * c + side[0] * s),
            hz + radius * (leaf[1] * c + side[1] * s),
        )

    steps = math.ceil(angle)
    step = math.radians(angle) / steps
    points = [(hx, hz), at(0.0, w)]
    points += [at((i + 0.5) * step, w / math.cos(step / 2)) for i in range(steps)]
    points.append(at(steps * step, w))
    return Prism(tuple(points), 0.0, door.head_height_m)


def _strip(frame: WallFrame, t0: float, t1: float, depth: float) -> tuple[Point, ...]:
    return (frame.point(t0), frame.point(t1), frame.point(t1, depth), frame.point(t0, depth))


def door_approach(door: DoorOpening, frame: WallFrame, depth_m: float) -> Prism:
    """The floor just inside a doorway, which a default layout keeps free."""
    leaf, _ = closed_leaf(door, frame)
    t_hinge, _ = frame.locate((door.hinge_pos.x, door.hinge_pos.z))
    direction = leaf[0] * frame.along[0] + leaf[1] * frame.along[1]
    t_end = t_hinge + direction * door.width_m
    return Prism(
        _strip(frame, min(t_hinge, t_end), max(t_hinge, t_end), depth_m), 0.0, door.head_height_m
    )


def window_zone(window: WindowOpening, frame: WallFrame, depth_m: float) -> Prism:
    """The space in front of the glazing; items below the sill do not reach it."""
    t0 = window.offset_along_wall_m
    return Prism(
        _strip(frame, t0, t0 + window.width_m, depth_m),
        window.sill_height_m,
        window.head_height_m,
    )
