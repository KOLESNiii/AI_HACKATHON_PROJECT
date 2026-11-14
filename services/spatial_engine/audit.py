"""Spatial checks independent of HTTP, mesh loading and provider services."""

from collections.abc import Sequence
from itertools import combinations
from math import isclose, isfinite

from shapely.affinity import rotate  # type: ignore[import-untyped]
from shapely.geometry import Polygon  # type: ignore[import-untyped]
from shapely.ops import unary_union  # type: ignore[import-untyped]

from contracts.schema import (
    MIN_HEIGHT_OVERLAP_M,
    MIN_PLAN_OVERLAP_M2,
    BlockedDoorIssue,
    ClearanceIssue,
    CollisionIssue,
    FurnitureItem,
    RoomScene,
)
from services.spatial_engine.geometry import (
    FurnitureGeometry,
    SceneGeometry,
    SpatialInputError,
    door_swing_sector,
    front_clearance_zone,
    prepare_furniture,
    scene_geometry,
)


def detect_front_clearance(
    scene: RoomScene, *, _prepared: SceneGeometry | None = None
) -> list[ClearanceIssue]:
    """Check full-width front access strips, returning one issue per blocker.

    actual_m is the minimum forward distance from the bbox front to the blocker
    anywhere across that strip, capped to 0..required_m. Boundary incursions use
    blocked_by_item_id=None. Chairs have no front-access checks and never block
    another item's access. Self is ignored; other occupied
    parts below WALK_HEADROOM_M (including fixed items) block access. High parts
    do not. This is a conservative standing-access check, not an articulated
    drawer/door simulation or a reachability assessment.

    Ignore area <= 1e-9 m² and distance deficits <= 1e-9 m as numerical noise.
    Results are ordered by target ID, boundary first, then blocker ID. Invalid
    geometry, invalid required clearance or duplicate item IDs raise ValueError.
    Inputs are never modified.
    """
    prepared = scene_geometry(scene, _prepared)
    floor = prepared.floor
    furniture = [entry.item for entry in prepared.furniture]
    zones = {item.id: front_clearance_zone(item) for item in furniture}
    issues = []
    for target in furniture:
        zone = zones[target.id]
        if target.category == "chair" or zone.is_empty:
            continue
        blockers: list[tuple[str | None, Polygon]] = [(None, zone.difference(floor))]
        for other in prepared.furniture:
            if other.item.id == target.id or other.item.category == "chair":
                continue
            if not other.walking_projection.is_empty:
                blockers.append((other.item.id, zone.intersection(other.walking_projection)))
        for blocker_id, intersection in blockers:
            if intersection.is_empty or intersection.area <= 1e-9:
                continue
            # Undo Three.js yaw around the target; local +Z is forward.
            local = rotate(
                intersection, target.pose.yaw_deg % 360, origin=(target.pose.x, target.pose.z)
            )
            actual = max(
                0.0,
                min(
                    target.requires_front_clear_m,
                    float(local.bounds[1]) - target.pose.z - target.bbox_m.depth / 2,
                ),
            )
            if target.requires_front_clear_m - actual > 1e-9:
                issues.append(
                    ClearanceIssue(
                        item_id=target.id,
                        required_m=target.requires_front_clear_m,
                        actual_m=actual,
                        blocked_by_item_id=blocker_id,
                    )
                )
    return issues


def calculate_free_floor_ratio(
    scene: RoomScene, *, _prepared: SceneGeometry | None = None
) -> float:
    """Return the usable floor fraction not blocked under the shared headroom rule.

    Project occupied parts with y_min < WALK_HEADROOM_M onto the floor, union
    them (including fixed items), and clip to the interior floor polygon. Empty
    parts mean a solid bbox. Parts at or above the headroom threshold do not
    block floor. Overlapping parts/items never subtract area twice.

    This is geometric free area, not reachable circulation, passage width or
    accessibility. Door swings and front-clearance reservations are not deducted.
    No AuditReport field is assigned here. Inputs are not modified; invalid
    floor/furniture geometry and duplicate furniture IDs raise ValueError.
    """
    prepared = scene_geometry(scene, _prepared)
    floor = prepared.floor
    free_area = float(prepared.free_floor.area)
    if not isfinite(free_area):
        raise SpatialInputError("Free floor area must be finite")
    return max(0.0, min(1.0, free_area / float(floor.area)))


def _height_overlaps(bottom_a: float, top_a: float, bottom_b: float, top_b: float) -> bool:
    overlap = min(top_a, top_b) - max(bottom_a, bottom_b)
    # Decimal threshold equality must not become a collision through subtraction noise.
    return overlap > MIN_HEIGHT_OVERLAP_M and not isclose(
        overlap, MIN_HEIGHT_OVERLAP_M, rel_tol=1e-12, abs_tol=1e-12
    )


def detect_blocked_doors(
    scene: RoomScene,
    *,
    area_tolerance_m2: float = MIN_PLAN_OVERLAP_M2,
    _prepared: SceneGeometry | None = None,
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
        raise SpatialInputError("Door overlap tolerance must be finite and non-negative")
    prepared = scene_geometry(scene, _prepared)
    walls = {wall.id: wall for wall in scene.walls}
    issues = []
    for door in sorted(scene.doors, key=lambda d: d.id):
        if door.wall_id not in walls:
            raise SpatialInputError(f"Door {door.id} references an unknown wall")
        sweep = door_swing_sector(door, walls[door.wall_id], scene.floor_polygon)
        for entry in prepared.furniture:
            for part in entry.volumes:
                if not _height_overlaps(0, door.head_height_m, part.y_min, part.y_max):
                    continue
                area = float(sweep.intersection(part.footprint).area)
                if not isfinite(area):
                    raise SpatialInputError("Door overlap area must be finite")
                if area > area_tolerance_m2:
                    issues.append(
                        BlockedDoorIssue(door_id=door.id, blocked_by_item_id=entry.item.id)
                    )
                    break
    return issues


def detect_out_of_bounds(
    scene: RoomScene,
    *,
    boundary_tolerance_m: float = 1e-9,
    _prepared: SceneGeometry | None = None,
) -> list[str]:
    """Return sorted item IDs whose rectangular footprint leaves the interior floor.

    Boundary contact is allowed. The tolerance expands the floor by this distance
    solely to absorb floating-point noise; it is not wall thickness or clearance.
    Set it to zero for exact containment. Walls/shell meshes and item height do
    not affect this floor-layout check. Inputs are never modified.

    Raises ValueError for invalid floor/footprints, duplicate furniture IDs, or
    a non-finite/negative tolerance. Validates the floor even with no furniture.
    """
    if not isfinite(boundary_tolerance_m) or boundary_tolerance_m < 0:
        raise SpatialInputError("Boundary tolerance must be finite and non-negative")
    prepared = scene_geometry(scene, _prepared)
    floor = prepared.floor
    allowed_floor = floor.buffer(boundary_tolerance_m) if boundary_tolerance_m else floor
    return [
        entry.item.id for entry in prepared.furniture if not allowed_floor.covers(entry.footprint)
    ]


def detect_collisions(
    furniture: Sequence[FurnitureItem],
    *,
    area_tolerance_m2: float = MIN_PLAN_OVERLAP_M2,
    _prepared: tuple[FurnitureGeometry, ...] | None = None,
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
        raise SpatialInputError("Collision area tolerance must be finite and non-negative")
    geometry = prepare_furniture(furniture) if _prepared is None else _prepared
    issues = []
    for a, b in combinations(geometry, 2):
        # Parts may extend up to the contract's bbox tolerance, so broad-phase
        # rejection must include their actual bounds as well as the nominal box.
        if not a.broad_bounds.intersects(b.broad_bounds):
            continue
        intersections = []
        for part_a in a.volumes:
            for part_b in b.volumes:
                if not _height_overlaps(part_a.y_min, part_a.y_max, part_b.y_min, part_b.y_max):
                    continue
                intersection = part_a.footprint.intersection(part_b.footprint)
                area = float(intersection.area)
                if not isfinite(area):
                    raise SpatialInputError("Furniture overlap area must be finite")
                if area > area_tolerance_m2:
                    intersections.append(intersection)
        if intersections:
            area = float(unary_union(intersections).area)
            issues.append(CollisionIssue(item_a=a.item.id, item_b=b.item.id, overlap_area_m2=area))
    return issues
