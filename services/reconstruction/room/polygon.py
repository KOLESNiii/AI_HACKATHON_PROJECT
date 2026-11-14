"""Room region (pixels) → simple, clean polygon of the interior wall faces.

The free-space region a room occupies is bounded by its walls' room-side faces, so its outer
contour is already `floor_polygon`; this module only straightens it.
"""

from __future__ import annotations

import math

import cv2
import numpy as np
from numpy.typing import NDArray

from .raster import Mask

Point = tuple[float, float]

SNAP_STEP_DEG = 45.0
SNAP_TOLERANCE_DEG = 5.0
PARALLEL_DEG = 10.0


def shoelace(poly: list[Point]) -> float:
    """Sum over (x, z) as the contract defines it; positive means the contract's winding."""
    n = len(poly)
    return sum(poly[i - 1][0] * poly[i][1] - poly[i][0] * poly[i - 1][1] for i in range(n))


def area(poly: list[Point]) -> float:
    return abs(shoelace(poly)) / 2


def _segments_cross(p1: Point, p2: Point, q1: Point, q2: Point) -> bool:
    def orient(a: Point, b: Point, c: Point) -> float:
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    d1, d2 = orient(q1, q2, p1), orient(q1, q2, p2)
    d3, d4 = orient(p1, p2, q1), orient(p1, p2, q2)
    return (d1 > 0) != (d2 > 0) and (d3 > 0) != (d4 > 0)


def is_simple(poly: list[Point]) -> bool:
    n = len(poly)
    if n < 3:
        return False
    for i in range(n):
        a1, a2 = poly[i], poly[(i + 1) % n]
        for j in range(i + 1, n):
            if j == i or (j + 1) % n == i or (i + 1) % n == j:
                continue
            if _segments_cross(a1, a2, poly[j], poly[(j + 1) % n]):
                return False
    return True


def _fit_edge(points: NDArray[np.float64], snap: bool) -> tuple[Point, Point]:
    """Least-squares line through an edge's contour points: (point on line, unit direction).
    Directions within SNAP_TOLERANCE_DEG of a multiple of 45° are snapped to it."""
    # Corners are rounded by rasterisation; fit the middle of the edge.
    n = len(points)
    trim = n // 5 if n >= 10 else 0
    core = points[trim : n - trim] if n - 2 * trim >= 2 else points
    c = core.mean(axis=0)
    if len(core) < 2:
        d = points[-1] - points[0]
    else:
        _, _, vt = np.linalg.svd(core - c)
        d = vt[0]
        if np.dot(d, points[-1] - points[0]) < 0:
            d = -d
    ang = math.degrees(math.atan2(d[1], d[0]))
    if snap:
        snapped = round(ang / SNAP_STEP_DEG) * SNAP_STEP_DEG
        if abs(ang - snapped) <= SNAP_TOLERANCE_DEG:
            ang = snapped
    rad = math.radians(ang)
    return (float(c[0]), float(c[1])), (math.cos(rad), math.sin(rad))


def _intersect(p: Point, d: Point, q: Point, e: Point) -> Point | None:
    den = d[0] * e[1] - d[1] * e[0]
    if abs(den) < math.sin(math.radians(PARALLEL_DEG)):
        return None
    t = ((q[0] - p[0]) * e[1] - (q[1] - p[1]) * e[0]) / den
    return (p[0] + d[0] * t, p[1] + d[1] * t)


def _drop_collinear(poly: list[Point], min_edge: float) -> list[Point]:
    changed = True
    while changed and len(poly) > 3:
        changed = False
        n = len(poly)
        for i in range(n):
            a, b, c = poly[i - 1], poly[i], poly[(i + 1) % n]
            ab = math.dist(a, b)
            cross = (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])
            bc = math.dist(b, c)
            straight = ab > 0 and bc > 0 and abs(cross) / (ab * bc) < math.sin(math.radians(3))
            if straight or ab < min_edge:
                del poly[i]
                changed = True
                break
    return poly


def region_polygon(region: Mask, wall_px: float) -> list[Point] | None:
    """Outer contour of a room region as a simplified polygon in pixels, wound for the contract
    (positive shoelace over (x, y) with y down the image, i.e. (x, z))."""
    contours, _ = cv2.findContours(
        region.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
    )
    if not contours:
        return None
    contour = max(contours, key=cv2.contourArea)
    pts = contour.reshape(-1, 2).astype(np.float64)
    eps = max(2.0, 0.3 * wall_px)
    approx = cv2.approxPolyDP(contour, eps, True).reshape(-1, 2)
    if len(approx) < 3:
        return None
    index = {(int(x), int(y)): i for i, (x, y) in enumerate(pts.astype(int))}
    idx = [index[(int(x), int(y))] for x, y in approx]
    raw: list[Point] = [(float(x), float(y)) for x, y in approx]

    best: list[Point] = raw
    for snap in (True, False):
        lines = []
        for k in range(len(idx)):
            i0, i1 = idx[k], idx[(k + 1) % len(idx)]
            seg = pts[i0 : i1 + 1] if i1 >= i0 else np.vstack([pts[i0:], pts[: i1 + 1]])
            lines.append(_fit_edge(seg, snap))
        poly: list[Point] = []
        for k in range(len(lines)):
            prev, cur = lines[k - 1], lines[k]
            hit = _intersect(prev[0], prev[1], cur[0], cur[1])
            # Parallel neighbours (a small step): keep the raw vertex.
            poly.append(hit if hit is not None else raw[k])
        poly = _drop_collinear(poly, 0.3 * wall_px)
        drift = max(math.dist(p, q) for p, q in zip(poly, raw)) if len(poly) == len(raw) else 0.0
        if len(poly) >= 3 and is_simple(poly) and drift <= 2 * wall_px:
            best = poly
            break
    best = _drop_collinear(list(best), 0.3 * wall_px)
    if len(best) < 3 or not is_simple(best):
        return None
    if shoelace(best) < 0:
        best.reverse()
    return best
