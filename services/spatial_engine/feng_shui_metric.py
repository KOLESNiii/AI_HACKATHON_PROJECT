"""A small, transparent Feng Shui placement metric from the command-position tradition.

Only what the scene geometry can show is judged, using three traditional preferences:

- **Command position** - a desk or bed from which the entrance can be seen without being
  directly in line with it.
- **Back to the door** - sitting at a desk, or lying in a bed, where the entrance is behind you.
- **Coffin position** - a bed whose foot points straight at the door.

These are design traditions, not predictions of health, wealth or luck. The score is a plain
average over the beds and desks that can be judged, so it says nothing about the rest of the
room. No beds or desks, or no doors, means the room is not assessed (None), never a score of
zero or a perfect one. Facing uses the furniture convention: a desk's front is the side the
sitter occupies, and a bed's front is its foot end.
"""

from math import acos, cos, degrees, hypot, radians, sin

from shapely.geometry import LineString  # type: ignore[import-untyped]

from contracts.schema import FengShuiReport, FengShuiSightline, FurnitureItem, RoomScene
from services.spatial_engine.geometry import SceneGeometry, door_center, scene_geometry

VIEW_HALF_ANGLE_DEG = 100.0
"""The entrance counts as seen when it lies within this angle of the occupant's facing."""
COFFIN_HALF_ANGLE_DEG = 20.0
"""A bed's foot points at the door when the door lies within this angle of its foot direction."""
COFFIN_SIDE_MARGIN_M = 0.3
DESK_SEAT_OFFSET_M = 0.45

_POINTS = {"command_position": 1.0, "unclear": 0.5, "back_to_door": 0.0, "coffin_alignment": 0.0}


def _front(item: FurnitureItem) -> tuple[float, float]:
    yaw = radians(item.pose.yaw_deg)
    return sin(yaw), cos(yaw)


def _angle_deg(a: tuple[float, float], b: tuple[float, float]) -> float:
    la, lb = hypot(*a), hypot(*b)
    if la == 0 or lb == 0:
        return 0.0
    dot = (a[0] * b[0] + a[1] * b[1]) / (la * lb)
    return degrees(acos(max(-1.0, min(1.0, dot))))


def _occupant(item: FurnitureItem) -> tuple[tuple[float, float], tuple[float, float]] | None:
    """Where a person is and which way they face, or None for items we do not judge."""
    fx, fz = _front(item)
    x, z = item.pose.x, item.pose.z
    if item.category == "desk":
        reach = item.bbox_m.depth / 2 + DESK_SEAT_OFFSET_M
        return (x + fx * reach, z + fz * reach), (-fx, -fz)
    if item.category == "bed":
        head = item.bbox_m.depth / 4
        return (x - fx * head, z - fz * head), (fx, fz)
    return None


def _wording(item: FurnitureItem, status: str) -> str:
    noun = "desk" if item.category == "desk" else "bed"
    if status == "command_position":
        return f"From this {noun} you can see the door without facing it head-on."
    if status == "back_to_door":
        return (
            f"Sitting at this {noun} puts the door behind you."
            if noun == "desk"
            else f"Lying in this {noun}, the door is behind you."
        )
    return "The foot of this bed points straight at the door."


def calculate_feng_shui(
    scene: RoomScene, *, _prepared: SceneGeometry | None = None
) -> FengShuiReport | None:
    prepared = scene_geometry(scene, _prepared)
    if not scene.doors:
        return None
    walls = {wall.id: wall for wall in scene.walls}
    doors = [
        (door, door_center(door, walls[door.wall_id], scene.floor_polygon)) for door in scene.doors
    ]
    room = prepared.floor.buffer(0.05)
    sightlines: list[FengShuiSightline] = []
    points: list[float] = []
    for item in sorted(scene.furniture, key=lambda i: i.id):
        occupant = _occupant(item)
        if occupant is None:
            continue
        (ox, oz), facing = occupant
        door, (dx, dz) = min(doors, key=lambda entry: hypot(entry[1][0] - ox, entry[1][1] - oz))
        toward = (dx - ox, dz - oz)
        angle = _angle_deg(facing, toward)
        status = "unclear"
        if item.category == "bed" and angle <= COFFIN_HALF_ANGLE_DEG:
            across = abs(toward[0] * facing[1] - toward[1] * facing[0]) / (hypot(*facing) or 1.0)
            if across <= item.bbox_m.width / 2 + COFFIN_SIDE_MARGIN_M:
                status = "coffin_alignment"
        if status == "unclear":
            if angle > VIEW_HALF_ANGLE_DEG:
                status = "back_to_door"
            elif room.covers(LineString([(ox, oz), (dx, dz)])):
                status = "command_position"
        points.append(_POINTS[status])
        if status != "unclear":
            sightlines.append(
                FengShuiSightline(
                    from_item_id=item.id,
                    to_door_id=door.id,
                    status=status,  # type: ignore[arg-type]
                    reason=_wording(item, status),
                )
            )
    if not points:
        return None
    return FengShuiReport(score=round(100 * sum(points) / len(points)), sightlines=sightlines)
