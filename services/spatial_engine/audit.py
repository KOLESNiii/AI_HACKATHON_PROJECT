"""Spatial checks independent of HTTP, mesh loading and provider services."""

from collections.abc import Sequence
from itertools import combinations
from math import isfinite

from contracts.schema import CollisionIssue, FurnitureItem
from services.spatial_engine.geometry import furniture_footprint


def detect_collisions(
    furniture: Sequence[FurnitureItem], *, area_tolerance_m2: float = 1e-9
) -> list[CollisionIssue]:
    """Report each overlapping pair once, in stable item-ID order.

    Uses conservative rectangular floor footprints. Edge/corner contact is
    allowed; only intersection area strictly above the tolerance is reported.
    The default tolerance is numerical noise suppression, not a safety margin.
    Reported areas are the full intersection areas, without subtracting tolerance.

    Raises ValueError for duplicate IDs, invalid footprints, or a non-finite or
    negative tolerance. Input items and their order are never modified.
    """
    if not isfinite(area_tolerance_m2) or area_tolerance_m2 < 0:
        raise ValueError("Collision area tolerance must be finite and non-negative")
    if len({item.id for item in furniture}) != len(furniture):
        raise ValueError("Furniture IDs must be unique for collision detection")

    footprints = [
        (item.id, furniture_footprint(item)) for item in sorted(furniture, key=lambda i: i.id)
    ]
    issues = []
    for (id_a, footprint_a), (id_b, footprint_b) in combinations(footprints, 2):
        area = float(footprint_a.intersection(footprint_b).area)
        if not isfinite(area):
            raise ValueError("Furniture overlap area must be finite")
        if area > area_tolerance_m2:
            issues.append(CollisionIssue(item_a=id_a, item_b=id_b, overlap_area_m2=area))
    return issues
