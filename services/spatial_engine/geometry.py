"""Metric floor geometry using the coordinate conventions in contracts.schema."""

from collections.abc import Sequence
from math import cos, isfinite, radians, sin

# The existing spatial extra ships Shapely without type stubs.
from shapely.geometry import Polygon  # type: ignore[import-untyped]

from contracts.schema import FurnitureItem, Vec2


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
