"""Close door and window gaps, then split free space into rooms and wall masses into floors.

Doors and windows appear as gaps in the structural strokes. A wall that ends at a gap leaves a
skeleton endpoint. A ray cast from that endpoint along its wall finds the far side of the gap
(another wall end, or the side of a perpendicular wall). Where a gap turns a corner (bay
windows), facing wall ends are paired instead. Each accepted gap becomes a *bridge*: it closes
the gap so rooms separate, and it is the opening candidate classified later.

A bridge is accepted when it is short enough to be a door, or long enough to be a window *and*
glazing lines run along it. That stops a wall end that faces across a hallway from sealing it.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import cv2
import numpy as np
from numpy.typing import NDArray

from .raster import Mask, Raster

MIN_GAP_WALLS = 0.25
# Without a known scale, opening sizes are judged in main-wall thicknesses.
DOOR_MAX_WALLS = 5.5
WINDOW_MAX_WALLS = 12.0
# With a known scale (second pass), in metres.
DOOR_MAX_M = 1.25
WINDOW_MAX_M = 2.6
GLAZING_MIN = 0.6
"""Fraction of a bridge's length that must be covered by ink (glazing lines) to be a window."""
PAIR_MAX_ANGLE_DEG = 55.0
"""A bridge between two wall ends may turn this far from each end's direction (bay corners)."""
SNAP_ANGLES_DEG = (0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0)
SNAP_TOLERANCE_DEG = 8.0

Point = tuple[float, float]
Labels = NDArray[np.int32]


@dataclass(frozen=True)
class Bridge:
    a: Point
    """Pixel (x, y) where the gap starts: the face of one wall end."""
    b: Point
    """Pixel (x, y) where the gap ends: the face of the far wall."""
    width_px: float
    """Drawn stroke width (the local wall thickness)."""
    glazing: float
    """Fraction of the gap's length with ink across the wall band (glazing lines)."""

    @property
    def length(self) -> float:
        return math.dist(self.a, self.b)

    @property
    def mid(self) -> Point:
        return ((self.a[0] + self.b[0]) / 2, (self.a[1] + self.b[1]) / 2)


@dataclass(frozen=True)
class GapLimits:
    min_px: float
    door_max_px: float
    window_max_px: float

    @staticmethod
    def for_raster(raster: Raster, px_per_m: float | None) -> GapLimits:
        wall = raster.wall_px
        if px_per_m is None:
            return GapLimits(MIN_GAP_WALLS * wall, DOOR_MAX_WALLS * wall, WINDOW_MAX_WALLS * wall)
        return GapLimits(MIN_GAP_WALLS * wall, DOOR_MAX_M * px_per_m, WINDOW_MAX_M * px_per_m)


@dataclass
class Segmentation:
    enclosure: Mask
    """Structure plus bridges."""
    bridges: list[Bridge]
    room_labels: Labels
    """Free-space components; only ids listed in `room_ids` are rooms."""
    room_ids: list[int]
    floor_labels: Labels
    """Connected wall masses; 0 = none."""
    room_floor: dict[int, int] = field(default_factory=dict)
    """Room region id -> floor label."""


# --- skeleton ---------------------------------------------------------------------------------


def thin(mask: Mask) -> Mask:
    """Zhang-Suen skeleton (opencv-contrib's thinning is not in the headless wheel)."""
    img = mask.astype(np.uint8)
    ys, xs = np.nonzero(img)
    if ys.size == 0:
        return mask.copy()
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    sub = np.pad(img[y0:y1, x0:x1], 1)
    while True:
        changed = False
        for step in (0, 1):
            p2, p3, p4 = sub[:-2, 1:-1], sub[:-2, 2:], sub[1:-1, 2:]
            p5, p6, p7 = sub[2:, 2:], sub[2:, 1:-1], sub[2:, :-2]
            p8, p9 = sub[1:-1, :-2], sub[:-2, :-2]
            ring = [p2, p3, p4, p5, p6, p7, p8, p9, p2]
            b = sum(r.astype(np.int16) for r in ring[:-1])
            a = sum(((ring[i] == 0) & (ring[i + 1] == 1)).astype(np.int16) for i in range(8))
            if step == 0:
                c = ((p2 * p4 * p6) == 0) & ((p4 * p6 * p8) == 0)
            else:
                c = ((p2 * p4 * p8) == 0) & ((p2 * p6 * p8) == 0)
            core = sub[1:-1, 1:-1]
            kill = (core == 1) & (b >= 2) & (b <= 6) & (a == 1) & c
            if kill.any():
                core[kill] = 0
                changed = True
        if not changed:
            break
    out = np.zeros_like(img)
    out[y0:y1, x0:x1] = sub[1:-1, 1:-1]
    return np.asarray(out > 0)


def _neighbour_count(skel: Mask) -> NDArray[np.int32]:
    k = np.ones((3, 3), np.float32)
    k[1, 1] = 0
    counts = cv2.filter2D(skel.astype(np.float32), -1, k, borderType=cv2.BORDER_CONSTANT)
    return np.asarray(np.round(counts), dtype=np.int32)


def _end_direction(skel: Mask, start: tuple[int, int], steps: int) -> tuple[Point, float]:
    """(unit direction out of the wall end, how far the skeleton extends behind it).

    Averages every skeleton pixel within `steps` geodesic pixels, which is robust to the small
    forks thinning leaves at blunt wall ends.
    """
    h, w = skel.shape
    seen = {start: 0}
    frontier = [start]
    while frontier:
        nxt: list[tuple[int, int]] = []
        for x, y in frontier:
            dcur = seen[(x, y)]
            if dcur >= steps:
                continue
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    q = (x + dx, y + dy)
                    if (
                        (dx or dy)
                        and 0 <= q[0] < w
                        and 0 <= q[1] < h
                        and skel[q[1], q[0]]
                        and q not in seen
                    ):
                        seen[q] = dcur + 1
                        nxt.append(q)
        frontier = nxt
    pts = np.array(list(seen.keys()), dtype=np.float64)
    reach = float(max(seen.values()))
    vx, vy = start[0] - pts[:, 0].mean(), start[1] - pts[:, 1].mean()
    n = math.hypot(vx, vy)
    if n == 0:
        return (0.0, 0.0), 0.0
    return (vx / n, vy / n), reach


@dataclass(frozen=True)
class WallEnd:
    p: Point
    """Skeleton endpoint (x, y), about half a wall thickness inside the blunt end."""
    d: Point
    """Unit direction out of the wall end."""
    half: float
    """Local stroke half-width."""


def wall_ends(raster: Raster) -> list[WallEnd]:
    structure = raster.structure
    wall = raster.wall_px
    skel = thin(structure)
    nbrs = _neighbour_count(skel)
    dist = cv2.distanceTransform(structure.astype(np.uint8), cv2.DIST_L2, 5)
    steps = max(4, int(round(wall * 1.5)))
    out: list[WallEnd] = []
    for y, x in np.argwhere(skel & (nbrs == 1)):
        d, reach = _end_direction(skel, (int(x), int(y)), steps)
        # A branch shorter than about a wall thickness is a thinning spur, not a wall end.
        if reach < max(3.0, 0.6 * wall):
            continue
        out.append(WallEnd(p=(float(x), float(y)), d=d, half=max(1.0, float(dist[y, x]))))
    return out


# --- bridges ----------------------------------------------------------------------------------


def _snap(angle: float) -> float:
    deg = math.degrees(angle) % 360.0
    for s in SNAP_ANGLES_DEG:
        diff = (deg - s + 180.0) % 360.0 - 180.0
        if abs(diff) <= SNAP_TOLERANCE_DEG:
            return math.radians(s)
    return angle


def _inside(shape: tuple[int, ...], x: float, y: float) -> bool:
    return 0 <= round(x) < shape[1] and 0 <= round(y) < shape[0]


def _exit_point(structure: Mask, p: Point, d: Point, limit: float) -> Point | None:
    """March from p along d until leaving the stroke p sits in."""
    t = 0.0
    while t <= limit:
        x, y = p[0] + d[0] * t, p[1] + d[1] * t
        if not _inside(structure.shape, x, y):
            return None
        if not structure[round(y), round(x)]:
            return (x, y)
        t += 1.0
    return None


def _cast(structure: Mask, end: WallEnd, d: Point, max_gap: float) -> tuple[Point, Point] | None:
    """Leave the wall end along d, cross the gap, and return (gap start, hit point). A band of
    parallel rays (the wall's width) tolerates small angle errors."""
    a = _exit_point(structure, end.p, d, 4 * end.half + 4)
    if a is None:
        return None
    nx, ny = -d[1], d[0]
    offsets = np.arange(-0.8 * end.half, 0.8 * end.half + 0.5, 2.0)
    t = 1.0
    while t <= max_gap:
        for o in offsets:
            x = a[0] + d[0] * t + nx * o
            y = a[1] + d[1] * t + ny * o
            if not _inside(structure.shape, x, y):
                return None
            if structure[round(y), round(x)]:
                return a, (a[0] + d[0] * t, a[1] + d[1] * t)
        t += 1.0
    return None


def glazing(ink: Mask, a: Point, b: Point, half: float) -> float:
    """Fraction of positions along a→b where ink crosses the wall band (glazing lines run along
    a window; a door gap or a hallway is mostly empty)."""
    length = math.dist(a, b)
    n = max(2, int(length))
    if length == 0:
        return 0.0
    ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
    nx, ny = -uy, ux
    ts = np.linspace(0, length, n)
    offs = np.arange(-half, half + 0.5, 1.0)
    xs = (a[0] + ux * ts[:, None] + nx * offs[None, :]).round().astype(int)
    ys = (a[1] + uy * ts[:, None] + ny * offs[None, :]).round().astype(int)
    h, w = ink.shape
    ok = (xs >= 0) & (xs < w) & (ys >= 0) & (ys < h)
    hits = np.zeros(xs.shape, dtype=bool)
    hits[ok] = ink[ys[ok], xs[ok]]
    return float(hits.any(axis=1).mean())


def _accept(raster: Raster, a: Point, b: Point, half: float, limits: GapLimits) -> Bridge | None:
    gap = math.dist(a, b)
    if gap < limits.min_px or gap > limits.window_max_px:
        return None
    # Glazing lines sit near the wall faces, so sample across the full wall width.
    g = glazing(raster.ink, a, b, max(2.0, 1.3 * half, 0.6 * raster.wall_px))
    if gap > limits.door_max_px and g < GLAZING_MIN:
        return None
    width = min(max(2.0 * half, 0.4 * raster.wall_px), 1.2 * raster.wall_px)
    return Bridge(a=a, b=b, width_px=width, glazing=g)


def _free_fraction(structure: Mask, a: Point, b: Point) -> float:
    n = max(2, int(math.dist(a, b)))
    xs = np.linspace(a[0], b[0], n).round().astype(int)
    ys = np.linspace(a[1], b[1], n).round().astype(int)
    return float(np.mean(~structure[ys, xs]))


def _pair_ends(
    raster: Raster, ends: list[WallEnd], idx: list[int], limits: GapLimits
) -> list[Bridge]:
    """Join wall ends whose gap turns a corner (bay windows), shortest and straightest first."""
    structure = raster.structure
    cos_max = math.cos(math.radians(PAIR_MAX_ANGLE_DEG))
    cands: list[tuple[float, int, int, Bridge]] = []
    for ii, i in enumerate(idx):
        ei = ends[i]
        for j in idx[ii + 1 :]:
            ej = ends[j]
            dist = math.dist(ei.p, ej.p)
            if dist == 0 or dist > limits.window_max_px + ei.half + ej.half:
                continue
            u = ((ej.p[0] - ei.p[0]) / dist, (ej.p[1] - ei.p[1]) / dist)
            ci = ei.d[0] * u[0] + ei.d[1] * u[1]
            cj = -(ej.d[0] * u[0] + ej.d[1] * u[1])
            if ci < cos_max or cj < cos_max:
                continue
            a = _exit_point(structure, ei.p, u, 4 * ei.half + 4)
            b = _exit_point(structure, ej.p, (-u[0], -u[1]), 4 * ej.half + 4)
            if a is None or b is None or _free_fraction(structure, a, b) < 0.9:
                continue
            br = _accept(raster, a, b, (ei.half + ej.half) / 2, limits)
            if br is not None:
                cands.append((dist * (3.0 - ci - cj), i, j, br))
    used: set[int] = set()
    out: list[Bridge] = []
    for _, i, j, br in sorted(cands, key=lambda c: c[0]):
        if i not in used and j not in used:
            out.append(br)
            used.update((i, j))
    return out


def find_bridges(raster: Raster, px_per_m: float | None = None) -> list[Bridge]:
    """Every wall end casts a ray along its wall; ends whose ray finds no acceptable gap are
    then paired with each other (gaps that turn a corner)."""
    limits = GapLimits.for_raster(raster, px_per_m)
    ends = wall_ends(raster)
    bridges: list[Bridge] = []
    unmatched: list[int] = []
    for i, e in enumerate(ends):
        ang = _snap(math.atan2(e.d[1], e.d[0]))
        d = (math.cos(ang), math.sin(ang))
        hit = _cast(raster.structure, e, d, limits.window_max_px)
        br = _accept(raster, hit[0], hit[1], e.half, limits) if hit else None
        if br is None:
            unmatched.append(i)
        else:
            bridges.append(br)
    bridges += _pair_ends(raster, ends, unmatched, limits)
    return _dedupe(bridges, raster.wall_px)


def _seg_dist(p: Point, br: Bridge) -> float:
    ax, ay = br.a
    dx, dy = br.b[0] - ax, br.b[1] - ay
    l2 = dx * dx + dy * dy
    if l2 == 0:
        return math.dist(p, br.a)
    t = max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / l2))
    return math.dist(p, (ax + t * dx, ay + t * dy))


def _dedupe(bridges: list[Bridge], wall: float) -> list[Bridge]:
    """Two wall ends facing each other each cast a ray; keep one bridge per gap (the longer,
    which spans the whole gap)."""
    kept: list[Bridge] = []
    for br in sorted(bridges, key=lambda b: -b.length):
        if not any(_seg_dist(br.a, k) < wall and _seg_dist(br.b, k) < wall for k in kept):
            kept.append(br)
    return kept


def draw_bridges(mask: Mask, bridges: list[Bridge]) -> Mask:
    canvas = mask.astype(np.uint8).copy()
    for br in bridges:
        a = (int(round(br.a[0])), int(round(br.a[1])))
        b = (int(round(br.b[0])), int(round(br.b[1])))
        cv2.line(canvas, a, b, 1, thickness=max(2, int(round(br.width_px))))
    return np.asarray(canvas > 0)


# --- regions ----------------------------------------------------------------------------------


def segment(raster: Raster, px_per_m: float | None = None) -> Segmentation:
    bridges = find_bridges(raster, px_per_m)
    enclosure = draw_bridges(raster.structure, bridges)

    free = (~enclosure).astype(np.uint8)
    n, labels, stats, _ = cv2.connectedComponentsWithStats(free, connectivity=4)
    edge = np.concatenate([labels[0], labels[-1], labels[:, 0], labels[:, -1]])
    outside = set(np.unique(edge).tolist())
    min_area = (2.0 * raster.wall_px) ** 2
    candidates = [
        i for i in range(1, n) if i not in outside and stats[i, cv2.CC_STAT_AREA] >= min_area
    ]

    k = max(3, int(round(raster.wall_px)))
    grown = cv2.dilate(
        enclosure.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
    )
    _, floor_labels = cv2.connectedComponents(grown, connectivity=8)

    ring_k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    room_floor: dict[int, int] = {}
    for rid in candidates:
        x, y, w, h = stats[rid, :4]
        pad = 4
        ys, xs = slice(max(0, y - pad), y + h + pad), slice(max(0, x - pad), x + w + pad)
        region = (labels[ys, xs] == rid).astype(np.uint8)
        ring = (cv2.dilate(region, ring_k) > 0) & enclosure[ys, xs]
        ids, counts = np.unique(floor_labels[ys, xs][ring], return_counts=True)
        counts, ids = counts[ids > 0], ids[ids > 0]
        if ids.size:
            room_floor[rid] = int(ids[np.argmax(counts)])

    return Segmentation(
        enclosure=enclosure,
        bridges=bridges,
        room_labels=np.asarray(labels, dtype=np.int32),
        room_ids=[r for r in candidates if r in room_floor],
        floor_labels=np.asarray(floor_labels, dtype=np.int32),
        room_floor=room_floor,
    )
