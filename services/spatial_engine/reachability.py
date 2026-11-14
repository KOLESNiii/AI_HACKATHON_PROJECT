"""Door-seeded walking-space approximation, separate from geometric free area."""

from math import isfinite

from shapely.geometry import LineString, Polygon  # type: ignore[import-untyped]
from shapely.ops import unary_union  # type: ignore[import-untyped]

from contracts.schema import WALK_HEADROOM_M, RoomScene
from services.spatial_engine.audit import detect_blocked_doors
from services.spatial_engine.geometry import (
    SceneGeometry,
    SpatialInputError,
    door_entry_segment,
    scene_geometry,
)


def calculate_reachable_floor_ratio(
    scene: RoomScene,
    *,
    passage_width_m: float = 0.5,
    _prepared: SceneGeometry | None = None,
    _blocked_door_ids: set[str] | None = None,
) -> float | None:
    """Fraction of room floor coverable by a person entering through any door.

    Model the person as an upright circle, diameter passage_width_m. Erode free
    floor by its radius to find valid centre locations; retain components seeded
    through door openings, then sweep the circle over those components and clip
    to free floor. Union all doors, never sum overlapping reachable areas.

    Uses the same below-headroom part projections as free-floor calculation.
    Blocked door swings are excluded as entries (a conservative full-opening rule).
    Doors below headroom or narrower than the person cannot seed a component.
    No doors returns None: unknown entry must not suppress other audit findings.
    No fitting/reachable entry returns zero. Fixed items and chairs block walking.

    Circular buffers use 32 segments per quadrant. A 1e-9 m radius reduction
    permits exact-width contact within numerical precision. This is a geometric
    approximation, not accessibility certification or articulated-body motion.
    The report composer exposes this metric; inputs are never modified.
    """
    if not isfinite(passage_width_m) or passage_width_m <= 2e-9:
        raise SpatialInputError("Passage width must be finite and greater than 2e-9 metres")
    prepared = scene_geometry(scene, _prepared)
    floor = prepared.floor
    if not scene.doors:
        return None
    blocked_ids = (
        _blocked_door_ids
        if _blocked_door_ids is not None
        else {issue.door_id for issue in detect_blocked_doors(scene, _prepared=prepared)}
    )
    radius = passage_width_m / 2 - 1e-9
    walls = {wall.id: wall for wall in scene.walls}
    entry_segments: list[LineString] = []
    for door in scene.doors:
        if door.wall_id not in walls:
            raise SpatialInputError(f"Door {door.id} references an unknown wall")
        entry = door_entry_segment(door, walls[door.wall_id], scene.floor_polygon, radius)
        if (
            door.id not in blocked_ids
            and door.head_height_m >= WALK_HEADROOM_M
            and not entry.is_empty
        ):
            entry_segments.append(entry)

    free_floor = prepared.free_floor
    centres = free_floor.buffer(-radius, quad_segs=32)
    if centres.is_empty:
        return 0.0
    regions = [centres] if isinstance(centres, Polygon) else list(centres.geoms)
    reachable = [
        region
        for region in regions
        if isinstance(region, Polygon) and any(region.intersects(entry) for entry in entry_segments)
    ]
    if not reachable:
        return 0.0
    swept = unary_union(reachable).buffer(radius, quad_segs=32).intersection(free_floor)
    area = float(swept.area)
    if not isfinite(area):
        raise SpatialInputError("Reachable floor area must be finite")
    return max(0.0, min(1.0, area / float(floor.area)))
