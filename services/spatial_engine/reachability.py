"""Door-seeded walking-space approximation, separate from geometric free area."""

from math import isfinite

from shapely.geometry import LineString, Polygon  # type: ignore[import-untyped]
from shapely.ops import unary_union  # type: ignore[import-untyped]

from contracts.schema import WALK_HEADROOM_M, RoomScene
from services.spatial_engine.geometry import (
    door_entry_segment,
    furniture_collision_volumes,
    room_floor_polygon,
)


def calculate_reachable_floor_ratio(scene: RoomScene, *, passage_width_m: float = 0.5) -> float:
    """Fraction of room floor coverable by a person entering through any door.

    Model the person as an upright circle, diameter passage_width_m. Erode free
    floor by its radius to find valid centre locations; retain components seeded
    through door openings, then sweep the circle over those components and clip
    to free floor. Union all doors, never sum overlapping reachable areas.

    Uses the same below-headroom part projections as free-floor calculation.
    Door openings are assumed available for passage; door-leaf obstruction is a
    separate finding. Doors below headroom or narrower than the person cannot
    seed a component. No doors raises ValueError (unknown entry, not zero access).
    No fitting/reachable entry returns zero. Fixed items and chairs block walking.

    Circular buffers use 32 segments per quadrant. A 1e-9 m radius reduction
    permits exact-width contact within numerical precision. This is a geometric
    approximation, not accessibility certification or articulated-body motion.
    No shared report field is assigned and inputs are never modified.
    """
    if not isfinite(passage_width_m) or passage_width_m <= 2e-9:
        raise ValueError("Passage width must be finite and greater than 2e-9 metres")
    floor = room_floor_polygon(scene.floor_polygon)
    if not scene.doors:
        raise ValueError("Reachability needs at least one door as an entry point")
    for objects, label in (
        (scene.walls, "Wall"),
        (scene.doors, "Door"),
        (scene.furniture, "Furniture"),
    ):
        if len({entry.id for entry in objects}) != len(objects):
            raise ValueError(f"{label} IDs must be unique for reachability checks")
    radius = passage_width_m / 2 - 1e-9
    walls = {wall.id: wall for wall in scene.walls}
    entry_segments: list[LineString] = []
    for door in scene.doors:
        if door.wall_id not in walls:
            raise ValueError(f"Door {door.id} references an unknown wall")
        entry = door_entry_segment(door, walls[door.wall_id], scene.floor_polygon, radius)
        if door.head_height_m >= WALK_HEADROOM_M and not entry.is_empty:
            entry_segments.append(entry)

    blockers = [
        part.footprint
        for item in sorted(scene.furniture, key=lambda item: item.id)
        for part in furniture_collision_volumes(item)
        if part.y_min < WALK_HEADROOM_M
    ]
    free_floor = floor.difference(unary_union(blockers))
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
        raise ValueError("Reachable floor area must be finite")
    return max(0.0, min(1.0, area / float(floor.area)))
