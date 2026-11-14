"""A window-openness proxy for layout comparison, not a lighting simulation."""

from dataclasses import dataclass
from math import hypot, isfinite

from shapely.geometry import LineString, Point, Polygon, box  # type: ignore[import-untyped]
from shapely.ops import unary_union  # type: ignore[import-untyped]

from contracts.schema import RoomScene
from services.spatial_engine.geometry import SceneGeometry, SpatialInputError, scene_geometry


@dataclass(frozen=True)
class WindowOpenness:
    window_id: str
    window_area_m2: float
    obstructed_area_m2: float
    openness_ratio: float
    blocking_item_ids: tuple[str, ...]


@dataclass(frozen=True)
class BrightnessApproximation:
    """Ratios describe geometric openness, never percentage brightness or lux."""

    openness_ratio: float | None
    obstruction_depth_m: float
    windows: tuple[WindowOpenness, ...]


def calculate_brightness_approximation(
    scene: RoomScene,
    *,
    obstruction_depth_m: float = 1.0,
    _prepared: SceneGeometry | None = None,
) -> BrightnessApproximation:
    """Project nearby occupied parts onto each window and union their shadows.

    The inward strip spans the opening's width and obstruction_depth_m. Parts
    with positive plan area inside that strip cast an orthographic shadow across
    their tangent extent and overlapping glass height. Count overlapping shadows
    only once, and weight the aggregate by glass area. Furniture below the sill,
    above the head or outside the strip does not obstruct that opening.

    All categories, fixed items and proxies participate without exemptions.
    Missing windows => unknown (None), not a dark room. Assumes opaque parts;
    ignores sun, weather, exterior obstructions, materials, glazing and curtains.
    The 1 m cutoff is a declared heuristic, not a physical daylight threshold.
    No shared schema, overall score or HTTP response is changed.
    """
    if not isfinite(obstruction_depth_m) or obstruction_depth_m <= 0:
        raise SpatialInputError("Window obstruction depth must be finite and positive")
    prepared = scene_geometry(scene, _prepared)
    if len({window.id for window in scene.windows}) != len(scene.windows):
        raise SpatialInputError("Window IDs must be unique for brightness checks")
    walls = {wall.id: wall for wall in scene.walls}
    results = []
    for window in sorted(scene.windows, key=lambda window: window.id):
        if window.wall_id not in walls:
            raise SpatialInputError(f"Window {window.id} references an unknown wall")
        wall = walls[window.wall_id]
        values = (
            wall.start.x,
            wall.start.z,
            wall.end.x,
            wall.end.z,
            wall.height_m,
            window.offset_along_wall_m,
            window.width_m,
            window.sill_height_m,
            window.head_height_m,
        )
        if not all(isfinite(value) for value in values):
            raise SpatialInputError("Window and wall geometry must be finite")
        dx, dz = wall.end.x - wall.start.x, wall.end.z - wall.start.z
        length = hypot(dx, dz)
        if not isfinite(length) or length <= 1e-8:
            raise SpatialInputError("Window wall must have nonzero finite length")
        if (
            window.width_m <= 0
            or window.offset_along_wall_m < 0
            or window.offset_along_wall_m + window.width_m > length + 1e-8
        ):
            raise SpatialInputError(
                "Window opening must have positive width and fit within its wall"
            )
        if not 0 <= window.sill_height_m < window.head_height_m <= wall.height_m:
            raise SpatialInputError("Window sill/head heights must fit within its wall")
        wall_line = LineString([(wall.start.x, wall.start.z), (wall.end.x, wall.end.z)])
        if not prepared.floor.boundary.buffer(1e-8).covers(wall_line):
            raise SpatialInputError("Window wall must lie on the room floor boundary")
        tx, tz = dx / length, dz / length
        nx, nz = -tz, tx  # Canonical wall winding: interior is on its left in X/Z.
        start = (
            wall.start.x + tx * window.offset_along_wall_m,
            wall.start.z + tz * window.offset_along_wall_m,
        )
        end = (start[0] + tx * window.width_m, start[1] + tz * window.width_m)
        midpoint = Point((start[0] + end[0]) / 2 + nx * 1e-8, (start[1] + end[1]) / 2 + nz * 1e-8)
        if not prepared.floor.contains(midpoint):
            raise SpatialInputError(
                "Window wall must follow the canonical interior-side convention"
            )
        strip = Polygon(
            [
                start,
                end,
                (end[0] + nx * obstruction_depth_m, end[1] + nz * obstruction_depth_m),
                (start[0] + nx * obstruction_depth_m, start[1] + nz * obstruction_depth_m),
            ]
        )
        if not strip.is_valid or not isfinite(strip.area) or strip.area <= 0:
            raise SpatialInputError("Window obstruction strip must have finite, positive area")
        strip = strip.intersection(prepared.floor)
        height = window.head_height_m - window.sill_height_m
        area = window.width_m * height
        if not isfinite(area) or area <= 0:
            raise SpatialInputError("Window glass area must be finite and positive")
        shadows = []
        blockers = []
        for entry in prepared.furniture:
            item_shadows = []
            for volume in entry.volumes:
                bottom = max(window.sill_height_m, volume.y_min)
                top = min(window.head_height_m, volume.y_max)
                if top <= bottom:
                    continue
                overlap = volume.footprint.intersection(strip)
                if overlap.is_empty or overlap.area <= 1e-9:
                    continue
                components = [overlap] if isinstance(overlap, Polygon) else list(overlap.geoms)
                for component in components:
                    if not isinstance(component, Polygon) or component.area <= 1e-9:
                        continue
                    along = [
                        (x - start[0]) * tx + (z - start[1]) * tz
                        for x, z in component.exterior.coords
                    ]
                    left, right = max(0.0, min(along)), min(window.width_m, max(along))
                    if right > left:
                        item_shadows.append(box(left, bottom, right, top))
            if item_shadows:
                blockers.append(entry.item.id)
                shadows.extend(item_shadows)
        obstructed = min(area, float(unary_union(shadows).area))
        if not isfinite(obstructed):
            raise SpatialInputError("Window obstruction area must be finite")
        results.append(
            WindowOpenness(
                window.id,
                area,
                obstructed,
                max(0.0, min(1.0, 1 - obstructed / area)),
                tuple(blockers),
            )
        )
    total = sum(result.window_area_m2 for result in results)
    if not isfinite(total):
        raise SpatialInputError("Total window area must be finite")
    ratio = (
        sum(r.window_area_m2 - r.obstructed_area_m2 for r in results) / total if results else None
    )
    return BrightnessApproximation(ratio, obstruction_depth_m, tuple(results))
