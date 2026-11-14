"""Spatial checks independent of HTTP, mesh loading and provider services."""

from collections.abc import Sequence
from itertools import combinations
from math import isfinite

from contracts.schema import BlockedDoorIssue, CollisionIssue, FurnitureItem, RoomScene
from services.spatial_engine.geometry import (
    door_swing_sector,
    furniture_footprint,
    room_floor_polygon,
)


def detect_blocked_doors(
    scene: RoomScene, *, area_tolerance_m2: float = 1e-9
) -> list[BlockedDoorIssue]:
    """Report furniture intersecting door sweeps, sorted by door and item ID.

    Uses full furniture footprints, irrespective of height/parts. This checks
    leaf obstruction, not walking access through the doorway. Boundary-only
    contact is allowed; positive overlap above the numerical tolerance is blocked.
    Outward sweeps are not clipped to the room, so outside items can block them.
    Invalid geometry/references and duplicate IDs raise ValueError, even when no
    furniture is present. Does not modify the scene.
    """
    if not isfinite(area_tolerance_m2) or area_tolerance_m2 < 0:
        raise ValueError("Door overlap tolerance must be finite and non-negative")
    room_floor_polygon(scene.floor_polygon)
    for entries, label in (
        (scene.walls, "Wall"),
        (scene.doors, "Door"),
        (scene.furniture, "Furniture"),
    ):
        if len({entry.id for entry in entries}) != len(entries):
            raise ValueError(f"{label} IDs must be unique for door checks")
    walls = {wall.id: wall for wall in scene.walls}
    footprints = [
        (item.id, furniture_footprint(item)) for item in sorted(scene.furniture, key=lambda i: i.id)
    ]
    issues = []
    for door in sorted(scene.doors, key=lambda d: d.id):
        if door.wall_id not in walls:
            raise ValueError(f"Door {door.id} references an unknown wall")
        sweep = door_swing_sector(door, walls[door.wall_id], scene.floor_polygon)
        for item_id, footprint in footprints:
            area = float(sweep.intersection(footprint).area)
            if not isfinite(area):
                raise ValueError("Door overlap area must be finite")
            if area > area_tolerance_m2:
                issues.append(BlockedDoorIssue(door_id=door.id, blocked_by_item_id=item_id))
    return issues


def detect_out_of_bounds(scene: RoomScene, *, boundary_tolerance_m: float = 1e-9) -> list[str]:
    """Return sorted item IDs whose rectangular footprint leaves the interior floor.

    Boundary contact is allowed. The tolerance expands the floor by this distance
    solely to absorb floating-point noise; it is not wall thickness or clearance.
    Set it to zero for exact containment. Walls/shell meshes and item height do
    not affect this floor-layout check. Inputs are never modified.

    Raises ValueError for invalid floor/footprints, duplicate furniture IDs, or
    a non-finite/negative tolerance. Validates the floor even with no furniture.
    """
    if not isfinite(boundary_tolerance_m) or boundary_tolerance_m < 0:
        raise ValueError("Boundary tolerance must be finite and non-negative")
    floor = room_floor_polygon(scene.floor_polygon)
    if len({item.id for item in scene.furniture}) != len(scene.furniture):
        raise ValueError("Furniture IDs must be unique for containment checks")
    allowed_floor = floor.buffer(boundary_tolerance_m) if boundary_tolerance_m else floor
    return [
        item.id
        for item in sorted(scene.furniture, key=lambda i: i.id)
        if not allowed_floor.covers(furniture_footprint(item))
    ]


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
