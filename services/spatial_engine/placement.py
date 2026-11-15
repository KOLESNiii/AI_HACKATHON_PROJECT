"""Find a spot for one new item without moving anything else.

Used when the user adds a searched product: the item arrives from the reconstruction import
with its real (catalog) size, and this picks a pose that passes the same hard checks as the
agent's `add_item` (no overlap, inside the floor, out of every door swing, room still
enterable). Candidates are cheap shapely tests first; only the best few get a full audit.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import atan2, degrees, hypot

from shapely.geometry import Point, Polygon  # type: ignore[import-untyped]

from contracts.schema import MIN_PLAN_OVERLAP_M2, AuditReport, FurnitureItem, Pose2D, RoomScene
from services.spatial_engine.audit import height_overlaps
from services.spatial_engine.geometry import (
    CollisionVolume,
    SpatialInputError,
    door_center,
    door_swing_sector,
    furniture_collision_volumes,
    furniture_footprint,
    prepare_scene,
)
from services.spatial_engine.report import audit_scene

WALL_GAP_M = 0.02
STEP_M = 0.2
MAX_AUDITS = 10


@dataclass(frozen=True)
class Placement:
    item: FurnitureItem
    report: AuditReport
    against_wall: bool


def _wall_poses(floor: Polygon, item: FurnitureItem) -> list[tuple[Pose2D, bool]]:
    """Back to each floor edge, front facing into the room, sampled along the edge."""
    ring = list(floor.exterior.coords)
    counter_clockwise = floor.exterior.is_ccw
    width, depth = item.bbox_m.width, item.bbox_m.depth
    poses: list[tuple[Pose2D, bool]] = []
    for (ax, az), (bx, bz) in zip(ring, ring[1:], strict=False):
        length = hypot(bx - ax, bz - az)
        if length < width:
            continue
        tx, tz = (bx - ax) / length, (bz - az) / length
        # Interior is to the left of a counter-clockwise ring.
        nx, nz = (-tz, tx) if counter_clockwise else (tz, -tx)
        yaw = degrees(atan2(nx, nz)) % 360
        offset = depth / 2 + WALL_GAP_M
        steps = max(1, int((length - width) / STEP_M))
        for index in range(steps + 1):
            along = width / 2 + (length - width) * index / steps
            x = ax + tx * along + nx * offset
            z = az + tz * along + nz * offset
            poses.append((Pose2D(x=round(x, 3), z=round(z, 3), yaw_deg=round(yaw, 3)), True))
    return poses


def _open_poses(floor: Polygon, item: FurnitureItem) -> list[tuple[Pose2D, bool]]:
    """A coarse grid over the floor, facing the four axes."""
    min_x, min_z, max_x, max_z = floor.bounds
    step = max(STEP_M * 2, min(item.bbox_m.width, item.bbox_m.depth) / 2)
    poses: list[tuple[Pose2D, bool]] = []
    x = min_x + step / 2
    while x < max_x:
        z = min_z + step / 2
        while z < max_z:
            for yaw in (0.0, 90.0, 180.0, 270.0):
                poses.append((Pose2D(x=round(x, 3), z=round(z, 3), yaw_deg=yaw), False))
            z += step
        x += step
    return poses


def _overlaps(volumes: list[CollisionVolume], obstacles: list[CollisionVolume]) -> bool:
    """The audit's own test: plan overlap above tolerance where the heights also overlap.

    Uses occupied collision parts, not whole bounding boxes, so a chair can nest under a
    tabletop exactly when the collision audit would accept it.
    """
    return any(
        part.footprint.intersects(obstacle.footprint)
        and height_overlaps(part.y_min, part.y_max, obstacle.y_min, obstacle.y_max)
        and part.footprint.intersection(obstacle.footprint).area > MIN_PLAN_OVERLAP_M2
        for part in volumes
        for obstacle in obstacles
    )


def place_item(scene: RoomScene, item: FurnitureItem) -> Placement:
    """The best audited pose for `item` in `scene`. Raises SpatialInputError if none fits.

    Wall-flush items prefer a wall; everything prefers keeping clear of doors, fewer access
    warnings and more reachable floor. The scene is never modified.
    """
    if any(existing.id == item.id for existing in scene.furniture):
        raise SpatialInputError("The item is already in the room")
    prepared = prepare_scene(scene)
    floor = prepared.floor
    walls = {wall.id: wall for wall in scene.walls}
    # Existing items' occupied parts, then each door sweep from the floor to its head.
    obstacles = [volume for entry in prepared.furniture for volume in entry.volumes]
    doors: list[tuple[float, float]] = []
    for door in scene.doors:
        wall = walls.get(door.wall_id)
        if wall is None:
            continue
        sweep = door_swing_sector(door, wall, scene.floor_polygon)
        obstacles.append(CollisionVolume(sweep, 0.0, door.head_height_m))
        doors.append(door_center(door, wall, scene.floor_polygon))
    inside = floor.buffer(1e-6)

    candidates = _wall_poses(floor, item) + _open_poses(floor, item)
    centre = floor.centroid
    ranked: list[tuple[tuple[float, ...], FurnitureItem, bool]] = []
    for pose, against_wall in candidates:
        placed = item.model_copy(update={"pose": pose})
        footprint = furniture_footprint(placed)
        if not inside.contains(footprint):
            continue
        if _overlaps(furniture_collision_volumes(placed), obstacles):
            continue
        spot = Point(pose.x, pose.z)
        door_distance = min((hypot(pose.x - dx, pose.z - dz) for dx, dz in doors), default=5.0)
        wall_penalty = 0.0 if against_wall == item.wall_flush_preferred else 1.0
        ranked.append(
            (
                (wall_penalty, -min(door_distance, 3.0), spot.distance(centre) * 0.1),
                placed,
                against_wall,
            )
        )
    ranked.sort(key=lambda entry: entry[0])

    reachable_before = bool(audit_scene(scene, _prepared=prepared).walkable_floor_ratio)
    best: tuple[tuple[float, ...], Placement] | None = None
    for heuristic, placed, against_wall in ranked[:MAX_AUDITS]:
        candidate = scene.model_copy(update={"furniture": [*scene.furniture, placed]})
        report = audit_scene(candidate)
        if any(placed.id in (c.item_a, c.item_b) for c in report.collisions):
            continue
        if placed.id in report.out_of_bounds_item_ids or any(
            d.blocked_by_item_id == placed.id for d in report.blocked_doors
        ):
            continue
        if reachable_before and report.walkable_floor_ratio == 0:
            continue  # This item would close the room off.
        warnings = sum(
            1
            for issue in report.clearance_issues
            if placed.id in (issue.item_id, issue.blocked_by_item_id)
        )
        score = (heuristic[0], float(warnings), -(report.walkable_floor_ratio or 0), *heuristic[1:])
        if best is None or score < best[0]:
            best = (score, Placement(placed, report, against_wall))
    if best is None:
        raise SpatialInputError(
            f"No free spot fits {item.name} "
            f"({item.bbox_m.width:g} × {item.bbox_m.depth:g} m). Make room and try again."
        )
    return best[1]
