"""Category collision templates fitted to `bbox_m` (spec 6.4, source 1).

Deterministic guesses that work for proxies and meshes alike, so swapping one for the other
at the same `bbox_m` changes no audit. `collision_source` stays `"template"`.
"""

from __future__ import annotations

from contracts.schema import MIN_PART_DIMENSION_M, BBoxM, CollisionPart

SLAB_M = 0.04
"""Thickness of a desk or table top, and width of a desk's side panels."""
LEG_M = 0.06
CHAIR_BACK_SHARE = 0.15
"""The rear share of a chair's depth that rises to full height; the rest is the seat block."""
CHAIR_SEAT_HEIGHT_SHARE = 0.5


def template_parts(category: str, bbox: BBoxM) -> list[CollisionPart]:
    """The category's parts inside `bbox`, or `[]` (one solid box) for solid categories and
    for a box too small to hold its template."""
    w, h, d = bbox.width, bbox.height, bbox.depth

    def part(x: float, z: float, width: float, depth: float, y0: float, y1: float) -> CollisionPart:
        return CollisionPart(x=x, z=z, width=width, depth=depth, y_min=y0, y_max=y1)

    parts: list[CollisionPart] = []
    under = h - SLAB_M
    if category == "desk" and w >= 2 * SLAB_M:
        side = w / 2 - SLAB_M / 2
        parts = [
            part(0, 0, w, d, under, h),
            part(-side, 0, SLAB_M, d, 0, under),
            part(side, 0, SLAB_M, d, 0, under),
        ]
    elif category == "table" and min(w, d) >= 2 * LEG_M:
        x, z = w / 2 - LEG_M / 2, d / 2 - LEG_M / 2
        parts = [part(0, 0, w, d, under, h)] + [
            part(sx * x, sz * z, LEG_M, LEG_M, 0, under) for sx in (-1, 1) for sz in (-1, 1)
        ]
    elif category == "chair":
        back = CHAIR_BACK_SHARE * d
        parts = [
            part(0, back / 2, w, d - back, 0, CHAIR_SEAT_HEIGHT_SHARE * h),
            part(0, back / 2 - d / 2, w, back, 0, h),
        ]
    thinnest = min((min(p.width, p.depth, p.y_max - p.y_min) for p in parts), default=0.0)
    return parts if thinnest >= MIN_PART_DIMENSION_M else []
