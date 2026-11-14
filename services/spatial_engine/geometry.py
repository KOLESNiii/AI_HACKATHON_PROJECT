"""Metric floor geometry using the coordinate conventions in contracts.schema."""

from collections.abc import Sequence
from dataclasses import dataclass
from math import atan2, ceil, cos, hypot, isfinite, radians, sin

# The existing spatial extra ships Shapely without type stubs.
from shapely.affinity import rotate, translate  # type: ignore[import-untyped]
from shapely.geometry import LineString, Point, Polygon  # type: ignore[import-untyped]

from contracts.schema import CollisionPart, DoorOpening, FurnitureItem, Vec2, WallSegment


def front_clearance_zone(item: FurnitureItem) -> Polygon:
    """Full-width rectangle from the bbox front, rotated/placed in room X/Z.

    Zero required clearance returns an empty polygon. Reject invalid dimensions,
    pose or clearance instead of interpreting them as a clear access zone.
    """
    furniture_footprint(item)
    required = item.requires_front_clear_m
    if not isfinite(required) or required < 0:
        raise ValueError("Required front clearance must be finite and non-negative")
    if required == 0:
        return Polygon()
    half_width, front = item.bbox_m.width / 2, item.bbox_m.depth / 2
    zone = Polygon(
        [
            (-half_width, front),
            (half_width, front),
            (half_width, front + required),
            (-half_width, front + required),
        ]
    )
    zone = translate(
        rotate(zone, -(item.pose.yaw_deg % 360), origin=(0, 0)), xoff=item.pose.x, yoff=item.pose.z
    )
    if not zone.is_valid or not isfinite(zone.area) or zone.area <= 0:
        raise ValueError("Front clearance zone must have valid geometry and finite, positive area")
    return zone


@dataclass(frozen=True)
class CollisionVolume:
    """An item's occupied box transformed into a vertical prism in room space."""

    footprint: Polygon
    y_min: float
    y_max: float


def furniture_collision_volumes(item: FurnitureItem) -> list[CollisionVolume]:
    """Transform validated local collision boxes; absent parts mean one solid bbox.

    Revalidate parts because model instances can be mutated after construction.
    Item placement stays at Y=0; this does not introduce elevated item poses.
    """
    furniture_footprint(item)
    if not isfinite(item.bbox_m.height) or item.bbox_m.height <= 0:
        raise ValueError("Furniture height must be finite and positive")
    validated = FurnitureItem.model_validate(item.model_dump())
    box = validated.bbox_m
    parts = validated.collision_parts or [
        CollisionPart(x=0, z=0, width=box.width, depth=box.depth, y_min=0, y_max=box.height)
    ]
    angle = radians(item.pose.yaw_deg % 360)
    c, s = cos(angle), sin(angle)
    volumes = []
    for part in parts:
        points = []
        for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            x, z = part.x + sx * part.width / 2, part.z + sz * part.depth / 2
            points.append((item.pose.x + x * c + z * s, item.pose.z - x * s + z * c))
        footprint = Polygon(points)
        if not footprint.is_valid or not isfinite(footprint.area) or footprint.area <= 0:
            raise ValueError("Collision part must have valid geometry with finite, positive area")
        volumes.append(CollisionVolume(footprint, part.y_min, part.y_max))
    return volumes


@dataclass(frozen=True)
class _DoorFrame:
    hinge: tuple[float, float]
    endpoint: tuple[float, float]
    inward_normal: tuple[float, float]
    start_angle: float
    swing_sign: int


def _door_frame(door: DoorOpening, wall: WallSegment, floor_points: Sequence[Vec2]) -> _DoorFrame:
    """Validate and resolve a door's closed leaf and room side once for all checks."""
    tolerance = 1e-8
    floor = room_floor_polygon(floor_points)
    values = (
        wall.start.x,
        wall.start.z,
        wall.end.x,
        wall.end.z,
        door.hinge_pos.x,
        door.hinge_pos.z,
        door.width_m,
        door.head_height_m,
        door.swing_angle_deg,
    )
    if not all(isfinite(value) for value in values):
        raise ValueError("Door and wall geometry must be finite")
    if door.wall_id != wall.id:
        raise ValueError("Door references a different wall")
    if door.width_m <= 0 or not 0 <= door.swing_angle_deg <= 180:
        raise ValueError("Door width must be positive and opening angle must be in 0..180 degrees")
    if door.head_height_m <= 0:
        raise ValueError("Door head height must be positive")

    dx, dz = wall.end.x - wall.start.x, wall.end.z - wall.start.z
    length = hypot(dx, dz)
    if not isfinite(length) or length <= tolerance:
        raise ValueError("Door wall must have nonzero finite length")
    wall_line = LineString([(wall.start.x, wall.start.z), (wall.end.x, wall.end.z)])
    if not floor.boundary.buffer(tolerance).covers(wall_line):
        raise ValueError("Door wall must lie on the room floor boundary")
    hinge = (door.hinge_pos.x, door.hinge_pos.z)
    if wall_line.distance(Point(hinge)) > tolerance:
        raise ValueError("Door hinge must lie on its wall segment")

    # Find a parallel, overlapping floor edge; the ring winding identifies its interior side.
    tx, tz = dx / length, dz / length
    coords = list(floor.exterior.coords)
    interior_sign = None
    for a, b in zip(coords, coords[1:]):
        ex, ez = b[0] - a[0], b[1] - a[1]
        edge_length = hypot(ex, ez)
        if edge_length == 0 or abs(tx * ez - tz * ex) > tolerance * edge_length:
            continue
        edge = LineString([a, b])
        if edge.distance(wall_line) > tolerance:
            continue
        projections = [((p[0] - wall.start.x) * tx + (p[1] - wall.start.z) * tz) for p in (a, b)]
        if min(length, max(projections)) - max(0.0, min(projections)) <= tolerance:
            continue
        alignment = 1 if tx * ex + tz * ez > 0 else -1
        interior_sign = alignment * (1 if floor.exterior.is_ccw else -1)
        break
    if interior_sign is None:
        raise ValueError("Cannot determine the room side of the door wall")

    # In X/Z plan coordinates, clockwise on screen is positive mathematical rotation.
    swing_sign = 1 if door.swing_clockwise else -1
    side_sign = interior_sign * (1 if door.swings_into_room else -1)
    leaf_sign = side_sign * swing_sign
    start = atan2(leaf_sign * tz, leaf_sign * tx)
    endpoint = (hinge[0] + door.width_m * leaf_sign * tx, hinge[1] + door.width_m * leaf_sign * tz)
    if wall_line.distance(Point(endpoint)) > tolerance:
        raise ValueError("Closed door leaf must fit within its wall segment")
    return _DoorFrame(hinge, endpoint, (-tz * interior_sign, tx * interior_sign), start, swing_sign)


def door_entry_segment(
    door: DoorOpening, wall: WallSegment, floor_points: Sequence[Vec2], radius_m: float
) -> LineString:
    """Possible person-centre entry locations, one radius inside the door opening.

    Trim a radius off both jambs. A tiny inset avoids round-off at exact-width
    thresholds. The caller checks these locations against obstacle-free space.
    """
    if not isfinite(radius_m) or radius_m <= 0:
        raise ValueError("Entry radius must be finite and positive")
    frame = _door_frame(door, wall, floor_points)
    if door.width_m < 2 * radius_m:
        return LineString()
    tx = (frame.endpoint[0] - frame.hinge[0]) / door.width_m
    tz = (frame.endpoint[1] - frame.hinge[1]) / door.width_m
    inset = radius_m + 1e-9
    points = [
        (
            frame.hinge[0] + along * tx + inset * frame.inward_normal[0],
            frame.hinge[1] + along * tz + inset * frame.inward_normal[1],
        )
        for along in (radius_m, door.width_m - radius_m)
    ]
    return LineString(points)


def door_swing_sector(
    door: DoorOpening, wall: WallSegment, floor_points: Sequence[Vec2]
) -> Polygon:
    """Conservative zero-thickness door sweep, using stored opening conventions.

    Validate wall/closed leaf on the floor boundary within 1e-8 m. Support angles
    0..180 degrees; zero returns an empty sweep. Arc tangents at intervals of at
    most one degree bound the sector from outside (radial excess <= about
    0.000039 * door width). No handle or access margin is added.
    """
    frame = _door_frame(door, wall, floor_points)
    hinge, endpoint, start = frame.hinge, frame.endpoint, frame.start_angle
    if door.swing_angle_deg == 0:
        return Polygon()

    steps = ceil(door.swing_angle_deg)
    step = frame.swing_sign * radians(door.swing_angle_deg) / steps
    tangent_radius = door.width_m / cos(abs(step) / 2)
    points = [hinge, endpoint]
    for index in range(steps):
        angle = start + (index + 0.5) * step
        points.append(
            (hinge[0] + tangent_radius * cos(angle), hinge[1] + tangent_radius * sin(angle))
        )
    end = start + steps * step
    points.append((hinge[0] + door.width_m * cos(end), hinge[1] + door.width_m * sin(end)))
    sector = Polygon(points)
    if not sector.is_valid or not isfinite(sector.area) or sector.area <= 0:
        raise ValueError("Door sweep must have valid geometry with finite, positive area")
    return sector


def room_floor_polygon(points: Sequence[Vec2]) -> Polygon:
    """Build the usable interior floor, accepting either winding and a closed ring.

    Reject invalid geometry instead of silently repairing the room boundary.
    """
    if len(points) < 3 or not all(isfinite(v) for point in points for v in (point.x, point.z)):
        raise ValueError("Room floor requires at least three finite X/Z points")
    polygon = Polygon([(point.x, point.z) for point in points])
    if not polygon.is_valid or not isfinite(polygon.area) or polygon.area <= 0:
        raise ValueError("Room floor must be a valid polygon with finite, positive area")
    return polygon


def furniture_footprint(item: FurnitureItem) -> Polygon:
    """Return the rotated width/depth rectangle in room X/Z coordinates.

    Pose is the bounding-box bottom-centre. Positive yaw matches Three.js +Y
    rotation: the local front (+Z) faces +X at 90 degrees. Height and mesh shape
    do not affect this conservative floor footprint. The item is never modified.

    Raises ValueError for non-finite placement or non-positive/non-finite planar
    dimensions, including coordinates that overflow during transformation.
    """
    width, depth = item.bbox_m.width, item.bbox_m.depth
    if not all(isfinite(value) and value > 0 for value in (width, depth)):
        raise ValueError("Furniture width and depth must be finite and positive")
    if not all(isfinite(value) for value in (item.pose.x, item.pose.z, item.pose.yaw_deg)):
        raise ValueError("Furniture position and yaw must be finite")

    angle = radians(item.pose.yaw_deg % 360)
    c, s = cos(angle), sin(angle)
    corners = [
        (-width / 2, -depth / 2),
        (width / 2, -depth / 2),
        (width / 2, depth / 2),
        (-width / 2, depth / 2),
    ]
    points = [(item.pose.x + x * c + z * s, item.pose.z - x * s + z * c) for x, z in corners]
    if not all(isfinite(value) for point in points for value in point):
        raise ValueError("Furniture footprint coordinates must be finite")
    footprint = Polygon(points)
    if not footprint.is_valid or not isfinite(footprint.area) or footprint.area <= 0:
        raise ValueError("Furniture footprint must have finite, positive area and valid geometry")
    return footprint
