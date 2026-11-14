"""Bridges → doors and windows on specific room walls.

A bridge is attached to every room polygon edge it runs along (two rooms for an interior door,
one for an exterior door or window). A bridge with glazing lines on an exterior wall is a
window; anything else is a door. Door hinge and swing side come from the leaf/arc ink drawn
next to the gap.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal

import numpy as np

from contracts.schema import RoomScene, Vec2

from . import footprint as fp
from .raster import Mask
from .regions import GLAZING_MIN, Bridge

Point = tuple[float, float]

PARALLEL_COS = math.cos(math.radians(20))
LEAF_MIN_SCORE = 0.35
"""Below this, no door leaf was found and the hinge/swing are defaults (flagged for correction)."""


@dataclass(frozen=True)
class EdgeHit:
    edge: int
    """Index of the polygon edge (wall) the bridge runs along."""
    t0: float
    """Distance along the edge from its start to the near end of the opening, pixels."""
    t1: float
    """Distance along the edge to the far end of the opening, pixels."""


def attach(bridge: Bridge, poly: list[Point], tolerance: float) -> EdgeHit | None:
    """The polygon edge the bridge runs along: parallel, within `tolerance` of the edge line,
    and overlapping it."""
    bx, by = bridge.b[0] - bridge.a[0], bridge.b[1] - bridge.a[1]
    blen = math.hypot(bx, by)
    if blen == 0:
        return None
    best: tuple[float, EdgeHit] | None = None
    n = len(poly)
    for i in range(n):
        s, e = poly[i], poly[(i + 1) % n]
        ex, ey = e[0] - s[0], e[1] - s[1]
        elen = math.hypot(ex, ey)
        if elen == 0:
            continue
        ux, uy = ex / elen, ey / elen
        if abs((bx * ux + by * uy) / blen) < PARALLEL_COS:
            continue
        da = abs((bridge.a[0] - s[0]) * -uy + (bridge.a[1] - s[1]) * ux)
        db = abs((bridge.b[0] - s[0]) * -uy + (bridge.b[1] - s[1]) * ux)
        if max(da, db) > tolerance:
            continue
        ta = (bridge.a[0] - s[0]) * ux + (bridge.a[1] - s[1]) * uy
        tb = (bridge.b[0] - s[0]) * ux + (bridge.b[1] - s[1]) * uy
        t0, t1 = max(0.0, min(ta, tb)), min(elen, max(ta, tb))
        # Most of the opening must lie along this edge.
        if t1 - t0 < 0.6 * blen:
            continue
        score = da + db
        if best is None or score < best[0]:
            best = (score, EdgeHit(edge=i, t0=t0, t1=t1))
    return best[1] if best else None


def kind(bridge: Bridge, rooms_touching: int) -> Literal["door", "window"]:
    return "window" if rooms_touching == 1 and bridge.glazing >= GLAZING_MIN else "door"


@dataclass(frozen=True)
class Leaf:
    hinge: Point
    """Pixel position of the hinge (one end of the gap)."""
    free_end: Point
    """The other end of the gap: where the closed leaf reaches."""
    side: Point
    """Unit vector (pixels) towards the side the leaf swings to."""
    found: bool
    """False when no leaf ink was found and these are defaults."""


def _ink_along(ink: Mask, p: Point, d: Point, length: float) -> float:
    n = max(2, int(length))
    ts = np.linspace(length * 0.15, length * 0.95, n)
    xs = np.round(p[0] + d[0] * ts).astype(int)
    ys = np.round(p[1] + d[1] * ts).astype(int)
    h, w = ink.shape
    ok = (xs >= 0) & (xs < w) & (ys >= 0) & (ys < h)
    if not ok.any():
        return 0.0
    hits = np.zeros(n, dtype=bool)
    # A leaf drawn 1-3 px thick: accept ink within one pixel of the ray.
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            xx, yy = np.clip(xs + dx, 0, w - 1), np.clip(ys + dy, 0, h - 1)
            hits |= ok & ink[yy, xx]
    return float(hits.mean())


def door_leaf(ink: Mask, structure: Mask, bridge: Bridge) -> Leaf:
    """Score the four hinge × swing-side hypotheses by ink along the open leaf (any angle from
    20° to 90° off the wall) and pick the best. Structural pixels are excluded so walls beside
    the gap do not count as a leaf."""
    detail = ink & ~structure
    a, b = bridge.a, bridge.b
    gap = bridge.length
    best: tuple[float, Leaf] | None = None
    for hinge, free in ((a, b), (b, a)):
        cx, cy = (free[0] - hinge[0]) / gap, (free[1] - hinge[1]) / gap
        for sgn in (1.0, -1.0):
            side = (-cy * sgn, cx * sgn)
            score = 0.0
            for deg in range(20, 95, 5):
                r = math.radians(deg)
                d = (
                    cx * math.cos(r) + side[0] * math.sin(r),
                    cy * math.cos(r) + side[1] * math.sin(r),
                )
                score = max(score, _ink_along(detail, hinge, d, gap))
            if best is None or score > best[0]:
                best = (score, Leaf(hinge=hinge, free_end=free, side=side, found=True))
    assert best is not None
    score, leaf = best
    if score < LEAF_MIN_SCORE:
        cx, cy = (b[0] - a[0]) / gap, (b[1] - a[1]) / gap
        return Leaf(hinge=a, free_end=b, side=(-cy, cx), found=False)
    return leaf


# --- contract geometry the audit accepts --------------------------------------------------------

CONFORM_TOLERANCE_M = 0.005
"""Largest door error `conform_openings` treats as rounding. Parsed coordinates are rounded to the
millimetre, so hinges drift up to ~1 mm off their wall line and closed leaves up to ~1 mm past
the wall's end; the audit allows 1e-8 m."""


def conform_openings(
    scene: RoomScene, tolerance_m: float = CONFORM_TOLERANCE_M
) -> tuple[RoomScene, list[str]]:
    """Put every door exactly on its wall, so the spatial audit accepts the room.

    Each hinge is projected onto its wall segment; if the closed leaf then runs past the wall's
    end, the hinge moves back along the wall by that much (the width is unchanged). A door that is
    further off than `tolerance_m` is left as it is and reported: that is a geometry error to
    fix, not rounding. Returns the scene (unchanged if nothing moved) and the warnings.
    """
    frames = {w.id: fp.wall_frame(w) for w in scene.walls}
    doors = []
    warnings: list[str] = []
    for door in scene.doors:
        frame = frames.get(door.wall_id)
        if frame is None:
            doors.append(door)
            continue
        t, off = frame.locate((door.hinge_pos.x, door.hinge_pos.z))
        leaf, _ = fp.closed_leaf(door, frame)
        direction = leaf[0] * frame.along[0] + leaf[1] * frame.along[1]  # +1 or -1 along the wall
        hinge = min(max(t, 0.0), frame.length)
        end = hinge + direction * door.width_m
        hinge -= max(0.0, end - frame.length) - max(0.0, -end)
        hinge = min(max(hinge, 0.0), frame.length)
        error = max(abs(off), abs(hinge - t))
        if error > tolerance_m:
            warnings.append(
                f"door {door.id} is {error * 1000:.0f} mm off wall {door.wall_id}; left unchanged"
            )
            doors.append(door)
            continue
        x, z = frame.point(hinge)
        if (x, z) != (door.hinge_pos.x, door.hinge_pos.z):
            door = door.model_copy(update={"hinge_pos": Vec2(x=x, z=z)})
        doors.append(door)
    if doors == scene.doors:
        return scene, warnings
    return scene.model_copy(update={"doors": doors}), warnings
