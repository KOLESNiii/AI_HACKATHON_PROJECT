"""Spatial checks independent of HTTP, mesh loading and provider services."""

from collections.abc import Sequence
from itertools import combinations
from math import isclose, isfinite

from shapely.ops import unary_union  # type: ignore[import-untyped]

from contracts.schema import (
    MIN_HEIGHT_OVERLAP_M,
    MIN_PLAN_OVERLAP_M2,
    BlockedDoorIssue,
    CollisionIssue,
    FurnitureItem,
    RoomScene,
)
from services.spatial_engine.geometry import (
    door_swing_sector,
    furniture_collision_volumes,
    furniture_footprint,
    room_floor_polygon,
)


def _height_overlaps(bottom_a: float, top_a: float, bottom_b: float, top_b: float) -> bool:
    overlap = min(top_a, top_b) - max(bottom_a, bottom_b)
    # Decimal threshold equality must not become a collision through subtraction noise.
    return overlap > MIN_HEIGHT_OVERLAP_M and not isclose(
        overlap, MIN_HEIGHT_OVERLAP_M, rel_tol=1e-12, abs_tol=1e-12
    )


def detect_blocked_doors(
    scene: RoomScene, *, area_tolerance_m2: float = MIN_PLAN_OVERLAP_M2
) -> list[BlockedDoorIssue]:
    """Report furniture intersecting door sweeps, sorted by door and item ID.

    Tests occupied parts against the door sweep from floor to head_height_m,
    using shared plan/height thresholds. Empty parts mean a solid bbox. This
    checks leaf obstruction, not walking access through the doorway. Contact
    alone is allowed; each door/item pair is reported only once.
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
    volumes = [
        (item.id, furniture_collision_volumes(item))
        for item in sorted(scene.furniture, key=lambda i: i.id)
    ]
    issues = []
    for door in sorted(scene.doors, key=lambda d: d.id):
        if door.wall_id not in walls:
            raise ValueError(f"Door {door.id} references an unknown wall")
        sweep = door_swing_sector(door, walls[door.wall_id], scene.floor_polygon)
        for item_id, parts in volumes:
            for part in parts:
                if not _height_overlaps(0, door.head_height_m, part.y_min, part.y_max):
                    continue
                area = float(sweep.intersection(part.footprint).area)
                if not isfinite(area):
                    raise ValueError("Door overlap area must be finite")
                if area > area_tolerance_m2:
                    issues.append(BlockedDoorIssue(door_id=door.id, blocked_by_item_id=item_id))
                    break
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
    furniture: Sequence[FurnitureItem], *, area_tolerance_m2: float = MIN_PLAN_OVERLAP_M2
) -> list[CollisionIssue]:
    """Report each overlapping pair once, in stable item-ID order.

    Whole bounding footprints provide a broad phase. Occupied parts must overlap
    in plan above the area tolerance and in height above MIN_HEIGHT_OVERLAP_M.
    Empty parts fall back to a solid bbox. Report the union area of qualifying
    part intersections, without double counting. Defaults follow shared contracts.

    Raises ValueError for duplicate IDs, invalid footprints, or a non-finite or
    negative tolerance. Input items and their order are never modified.
    """
    if not isfinite(area_tolerance_m2) or area_tolerance_m2 < 0:
        raise ValueError("Collision area tolerance must be finite and non-negative")
    if len({item.id for item in furniture}) != len(furniture):
        raise ValueError("Furniture IDs must be unique for collision detection")

    geometry = [
        (item.id, furniture_footprint(item), furniture_collision_volumes(item))
        for item in sorted(furniture, key=lambda i: i.id)
    ]
    issues = []
    for (id_a, footprint_a, parts_a), (id_b, footprint_b, parts_b) in combinations(geometry, 2):
        # Parts may extend up to the contract's bbox tolerance, so broad-phase
        # rejection must include their actual bounds as well as the nominal box.
        bounds_a = unary_union([footprint_a, *(p.footprint for p in parts_a)]).envelope
        bounds_b = unary_union([footprint_b, *(p.footprint for p in parts_b)]).envelope
        if not bounds_a.intersects(bounds_b):
            continue
        intersections = []
        for part_a in parts_a:
            for part_b in parts_b:
                if not _height_overlaps(part_a.y_min, part_a.y_max, part_b.y_min, part_b.y_max):
                    continue
                intersection = part_a.footprint.intersection(part_b.footprint)
                area = float(intersection.area)
                if not isfinite(area):
                    raise ValueError("Furniture overlap area must be finite")
                if area > area_tolerance_m2:
                    intersections.append(intersection)
        if intersections:
            area = float(unary_union(intersections).area)
            issues.append(CollisionIssue(item_a=id_a, item_b=id_b, overlap_area_m2=area))
    return issues
