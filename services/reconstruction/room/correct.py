"""User corrections of a room (#11): its metric scale, and where its furniture stands.

Scale: the parser reads a floor's scale from printed dimensions, or estimates it and flags
`"dimensions"`. The user corrects it by giving one wall's real length. Every room on that floor
shares the drawing and its frame, so the whole floor is rescaled about the frame's origin, from
the original parse (corrections never compound). Openings scale with their walls, the shell gets
a new immutable URL, and furniture is carried over relative to its wall: same fraction along it,
same gap from it, same facing. Furniture sizes never change: they come from the video, not the
plan.

Placement: the editor saves a scene after the user moves items. Only poses are taken (and
correction flags the user cleared); everything else must match the scene the service keeps, so
asset identity and geometry cannot drift through an edit.
"""

from __future__ import annotations

import hashlib
import json
import math

from pydantic import ValidationError

from contracts.schema import (
    DoorOpening,
    FurnitureItem,
    ParsedFloor,
    ParsedRoom,
    Pose2D,
    RoomScene,
    Vec2,
    WallSegment,
    WindowOpening,
)

from . import footprint as fp
from .align import MOVED_FLAG_M, AlignmentRecord, AlignmentResult, nearest_fit, wall_relative
from .openings import conform_openings

MIN_FACTOR, MAX_FACTOR = 0.25, 4.0
"""A correction outside this range is a misread wall, not a scale error."""
MIN_THICKNESS_M, MAX_THICKNESS_M = 0.05, 0.5
"""The parser's clamp on traced wall thickness (`parse._build_scene`)."""
GEOMETRY_FIELDS = (
    "floor_polygon",
    "walls",
    "windows",
    "doors",
    "shell_glb_url",
    "north_compass_deg",
)
"""What only a scale correction may change; a pose edit must leave these as they are."""
ITEM_EDITABLE = {"pose", "correction_needed"}


class StaleEdit(Exception):
    """The edit was made against a scene the service no longer has (HTTP 409)."""


class InvalidEdit(Exception):
    """The edit changes something a placement correction may not change (HTTP 422)."""


# --- scale ------------------------------------------------------------------------------------


def _point(p: Vec2, factor: float) -> Vec2:
    # Full precision: rounding endpoints and widths separately can make a door wider than its
    # wall (the audit allows only POSITION_TOLERANCE_M). Unrounded, the room is exactly similar.
    return Vec2(x=p.x * factor, z=p.z * factor)


def geometry_digest(scene: RoomScene) -> str:
    """Short hash of the geometry a shell is built from."""
    data = scene.model_dump(mode="json", include={"floor_polygon", "walls", "windows", "doors"})
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:10]


def corrected_shell_url(original_url: str, digest: str) -> str:
    """`.../shells/<scene_id>.glb` -> `.../shells/<scene_id>.<digest>.glb`."""
    return f"{original_url.removesuffix('.glb')}.{digest}.glb"


def rescale_room(original: RoomScene, factor: float) -> RoomScene:
    """The parsed room (no furniture) at `factor` times its size, about the floor's origin.

    Plan lengths scale exactly (polygon, walls and their traced thickness, opening positions
    and widths), so the room is similar to the parse and every opening that fitted its wall
    still does; heights, bearings and IDs do not change. Openings are then clamped to their
    walls against float error, and doors conformed. A room whose geometry changes gets a new
    shell URL. Raises pydantic's `ValidationError` when the scaled room breaks the contract
    (a feature narrower than its checks at a small factor).
    """
    walls = [
        WallSegment(
            id=w.id,
            start=_point(w.start, factor),
            end=_point(w.end, factor),
            height_m=w.height_m,
            thickness_m=min(MAX_THICKNESS_M, max(MIN_THICKNESS_M, w.thickness_m * factor)),
        )
        for w in original.walls
    ]
    lengths = {w.id: math.dist((w.start.x, w.start.z), (w.end.x, w.end.z)) for w in walls}

    def within(wall_id: str, offset: float, width: float) -> tuple[float, float]:
        length = lengths.get(wall_id)
        if length is None:
            return offset, width
        width = min(width, length)
        return min(max(offset, 0.0), length - width), width

    windows = []
    for w in original.windows:
        offset, width = within(w.wall_id, w.offset_along_wall_m * factor, w.width_m * factor)
        windows.append(
            WindowOpening.model_validate(
                w.model_dump() | {"offset_along_wall_m": offset, "width_m": width}
            )
        )
    doors = [
        DoorOpening.model_validate(
            d.model_dump()
            | {
                "hinge_pos": _point(d.hinge_pos, factor).model_dump(),
                "width_m": min(d.width_m * factor, lengths.get(d.wall_id, math.inf)),
            }
        )
        for d in original.doors
    ]
    room = original.model_copy(
        update={
            "floor_polygon": [_point(p, factor) for p in original.floor_polygon],
            "walls": walls,
            "windows": windows,
            "doors": doors,
            "furniture": [],
        }
    )
    room, _ = conform_openings(room)  # the parser's rooms conform, so the rescaled ones do too
    room = RoomScene.model_validate(room.model_dump())
    if geometry_digest(room) != geometry_digest(original):
        url = corrected_shell_url(original.shell_glb_url, geometry_digest(room))
        room = room.model_copy(update={"shell_glb_url": url})
    return room


class InvalidScale(ValueError):
    """A room of the floor cannot exist at that scale (it would break the contract)."""


def rescale_floor(original: ParsedFloor, factor: float) -> ParsedFloor:
    """Every room of the floor rescaled; the dimensions now come from the user. Raises
    `InvalidScale` naming the first room that would not be valid: the floor shares one scale,
    so it is corrected whole or not at all."""
    rooms = []
    for room in original.rooms:
        try:
            scene = rescale_room(room.scene, factor)
            rooms.append(
                ParsedRoom.model_validate(
                    room.model_dump()
                    | {
                        "area_m2": round(room.area_m2 * factor * factor, 2),
                        "dimension_source": "user_corrected",
                        "correction_needed": [
                            c for c in room.correction_needed if c != "dimensions"
                        ],
                        "scene": scene.model_dump(),
                    }
                )
            )
        except ValidationError as exc:
            raise InvalidScale(f"{room.name}: {exc.errors()[0]['msg']}") from exc
        except ValueError as exc:
            raise InvalidScale(f"{room.name}: {exc}") from exc
    return original.model_copy(update={"rooms": rooms})


def _perimeter(scene: RoomScene) -> float:
    return sum(math.dist((w.start.x, w.start.z), (w.end.x, w.end.z)) for w in scene.walls)


def carry_furniture(old: RoomScene, room: RoomScene) -> AlignmentResult:
    """`old`'s furniture in the rescaled `room`, relative to the same walls.

    Each item's centre keeps its fraction along the wall it stands in front of
    (`align.wall_relative`) and its distance from that wall, so an item flush with a wall stays
    flush. An item in front of no wall has its centre scaled. Yaws never change: a uniform
    rescale turns no wall, and a yaw may be the user's. IDs, meshes, sizes and correction flags
    are kept; overlaps are left for the audit to report, as the user may have made them.

    An item the rescale pushes out of the room (a smaller room) moves to the nearest spot where
    it fits with its yaw (`align.nearest_fit`), flagged `placement` if that is more than
    `MOVED_FLAG_M` away. One that fits nowhere stays where it was carried, flagged.
    """
    factor = _perimeter(room) / _perimeter(old)
    old_frames = {w.id: fp.wall_frame(w) for w in old.walls}
    new_frames = {w.id: fp.wall_frame(w) for w in room.walls}
    old_poly = [(p.x, p.z) for p in old.floor_polygon]
    new_poly = [(p.x, p.z) for p in room.floor_polygon]
    carried: list[FurnitureItem] = []
    displaced: list[FurnitureItem] = []
    records: dict[str, AlignmentRecord] = {}
    for item in old.furniture:
        hint = wall_relative(old, item)
        before = old_frames.get(hint.wall_id) if hint else None
        after = new_frames.get(hint.wall_id) if hint else None
        if before is not None and after is not None:
            t, depth = before.locate((item.pose.x, item.pose.z))
            x, z = after.point(t * after.length / before.length, depth)
        else:
            x, z = item.pose.x * factor, item.pose.z * factor
        moved = item.model_copy(update={"pose": Pose2D(x=x, z=z, yaw_deg=item.pose.yaw_deg)})
        records[item.id] = AlignmentRecord(
            asset_id=item.id,
            method="kept",
            wall_id=hint.wall_id if hint else None,
            notes=["carried over the scale correction along its wall"],
        )
        was_inside = fp.covered_by(fp.footprint(item.bbox_m, item.pose).points, old_poly)
        inside = fp.covered_by(fp.footprint(moved.bbox_m, moved.pose).points, new_poly)
        (carried if inside or not was_inside else displaced).append(moved)

    placed = {item.id: item for item in carried}
    obstacles = room.model_copy(update={"furniture": carried})
    for item in displaced:
        record = records[item.id]
        fit = nearest_fit(obstacles, item, item.pose)
        flags = set(item.correction_needed)
        if fit is None:
            pose, record.fits = item.pose, False
            flags.add("placement")
            record.notes = ["left the room when rescaled and fits nowhere; left where carried"]
        else:
            pose, moved_m = fit
            record.moved_m = round(moved_m, 3)
            if moved_m > MOVED_FLAG_M:
                flags.add("placement")
            record.notes = [f"left the room when rescaled; moved {moved_m:.2f} m, yaw kept"]
        order = ("dimensions", "placement", "orientation")
        final = item.model_copy(
            update={"pose": pose, "correction_needed": [c for c in order if c in flags]}
        )
        placed[item.id] = final
        obstacles = obstacles.model_copy(update={"furniture": [*obstacles.furniture, final]})
    return AlignmentResult(
        items=[placed[item.id] for item in old.furniture],
        records={item.id: records[item.id] for item in old.furniture},
        warnings=[],
    )


# --- placement --------------------------------------------------------------------------------


def apply_pose_edit(kept: RoomScene, edit: RoomScene) -> RoomScene:
    """`kept` with the edit's poses: what `PUT /scenes/{scene_id}` stores.

    Raises `StaleEdit` when the edit is not newer than `kept` or was made against other
    geometry, and `InvalidEdit` when it names an unknown item, changes anything of an item but
    its pose, or adds a correction flag. Moving an item clears its `placement` flag and turning
    it clears `orientation`: the user has put it there. Items left out keep their pose.
    """
    if edit.scene_id != kept.scene_id:
        raise InvalidEdit(f"scene_id is {edit.scene_id!r}, expected {kept.scene_id!r}")
    if edit.revision <= kept.revision:
        raise StaleEdit(
            f"revision {edit.revision} is not newer than the kept revision {kept.revision}; "
            "reload the scene"
        )
    changed = [f for f in GEOMETRY_FIELDS if getattr(edit, f) != getattr(kept, f)]
    if changed:
        raise StaleEdit(
            f"the room's {', '.join(changed)} differ from the kept scene (its scale was "
            "corrected?); reload the scene"
        )
    by_id = {item.id: item for item in kept.furniture}
    edited: dict[str, FurnitureItem] = {}
    for item in edit.furniture:
        current = by_id.get(item.id)
        if current is None:
            raise InvalidEdit(f"unknown item {item.id!r}: a placement correction cannot add items")
        if item.id in edited:
            raise InvalidEdit(f"item {item.id!r} appears twice")
        fields = [
            name
            for name in FurnitureItem.model_fields
            if name not in ITEM_EDITABLE and getattr(item, name) != getattr(current, name)
        ]
        if fields:
            raise InvalidEdit(f"{item.id}: only the pose can be corrected, not {', '.join(fields)}")
        if not all(map(math.isfinite, (item.pose.x, item.pose.z, item.pose.yaw_deg))):
            raise InvalidEdit(f"{item.id}: the pose must be finite numbers")
        if added := sorted(set(item.correction_needed) - set(current.correction_needed)):
            raise InvalidEdit(f"{item.id}: cannot add correction flags ({', '.join(added)})")
        cleared = set(current.correction_needed) - set(item.correction_needed)
        if (item.pose.x, item.pose.z) != (current.pose.x, current.pose.z):
            cleared.add("placement")
        if item.pose.yaw_deg != current.pose.yaw_deg:
            cleared.add("orientation")
        flags = [c for c in current.correction_needed if c not in cleared]
        edited[item.id] = current.model_copy(update={"pose": item.pose, "correction_needed": flags})
    furniture = [edited.get(item.id, item) for item in kept.furniture]
    return kept.model_copy(
        update={"furniture": furniture, "revision": edit.revision, "sun_hour": edit.sun_hour}
    )
