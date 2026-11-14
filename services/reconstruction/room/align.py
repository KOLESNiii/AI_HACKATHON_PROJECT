"""Furniture assets + one room -> initial poses, with the uncertainty exposed.

Dev 2 hands over pose-less `FurnitureAsset`s. An observer says roughly where each one was seen
(`observe.py`); this module turns that into a `Pose2D` per asset, deterministically:

1. Assets with a hint are placed in the hinted wall's frame. An impossible spot (outside the
   room, or inside another item) is moved to the nearest possible one.
2. A chair `seated_at` a desk or table is pushed in as far as the collision parts allow.
3. Assets without a hint get a default spot: back to a wall, facing in, clear of doors,
   windows and other items' access. These are guesses and say so.

Nothing is ever dropped. What is uncertain goes into `FurnitureItem.correction_needed`
(`placement`, `orientation`) for the editor to prompt, and the reason goes into an
`AlignmentRecord` per asset ID, which also links the pose back to its source frame. Records stay
inside the reconstruction service; they are never placed in `RoomScene`.

Takes a single-room scene (what the parser returns). Split a whole-floor scene with
`footprint.split_rooms` first.
"""

from __future__ import annotations

import logging
import math
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel

from contracts.schema import WALK_HEADROOM_M, BBoxM, FurnitureItem, Pose2D, RoomScene
from services.reconstruction.assets.models import EvidenceFrame, FurnitureAsset

from . import footprint as fp
from .footprint import Point, Prism, WallFrame
from .observe import Facing, FrameSource, PlacementHint, PlacementObserver

log = logging.getLogger(__name__)

HIGH_CONFIDENCE = 0.75
"""A hint below this leaves `placement` and `orientation` to be confirmed."""
MOVED_FLAG_M = 0.3
"""A hinted item moved further than this to make it fit needs its placement confirmed."""
SEARCH_STEP_M = 0.05
SEARCH_ALONG_M = 1.5
SEARCH_OUT_M = 1.0
DEFAULT_STEP_M = 0.1
DOOR_APPROACH_M = 0.8
"""Depth of floor kept free inside a doorway by the default layout."""
WINDOW_CLEAR_M = 0.3
"""Depth in front of a window that the default layout keeps free above the sill."""
SEAT_STEP_M = 0.025

Correction = Literal["dimensions", "placement", "orientation"]
_CORRECTION_ORDER: tuple[Correction, ...] = ("dimensions", "placement", "orientation")


class AlignmentRecord(BaseModel):
    """How one asset's pose was decided. Keyed by the asset's stable ID."""

    asset_id: str
    method: Literal["hint", "default", "kept"]
    """`hint`: from an observer's hint. `default`: no usable hint, placed by the default rule.
    `kept`: the scene already had this ID, so its pose was left alone."""
    confidence: float | None = None
    """The hint's confidence; None without a hint."""
    wall_id: str | None = None
    """The wall the pose is expressed against."""
    primary_frame_index: int | None = None
    """The asset's primary evidence frame, linking the pose to its source."""
    moved_m: float = 0.0
    """How far the item was moved from the hinted spot to make it fit."""
    fits: bool = True
    """False when no valid spot exists; the item is still returned, overlapping something."""
    notes: list[str] = []


class AlignmentResult(BaseModel):
    items: list[FurnitureItem]
    """One per asset, in the order given."""
    records: dict[str, AlignmentRecord]
    warnings: list[str] = []

    def place_in(self, scene: RoomScene) -> RoomScene:
        """The scene with these items added; furniture it already had keeps its place."""
        ids = {item.id for item in self.items}
        kept = [item for item in scene.furniture if item.id not in ids]
        return scene.model_copy(update={"furniture": kept + self.items})


# --- the room as obstacles --------------------------------------------------------------------


@dataclass
class _Placed:
    item: FurnitureItem
    parts: list[Prism]
    access: Prism | None
    """Front-clearance strip; None for chairs, which neither need nor block access."""


def _access(category: str, bbox: BBoxM, pose: Pose2D, clear_m: float) -> Prism | None:
    if category == "chair":
        return None
    return fp.front_zone(bbox, pose, clear_m, WALK_HEADROOM_M)


class _Room:
    def __init__(self, scene: RoomScene) -> None:
        self.polygon: list[Point] = [(p.x, p.z) for p in scene.floor_polygon]
        self.frames: dict[str, WallFrame] = {}
        for wall in scene.walls:
            frame = fp.wall_frame(wall)
            if frame is not None:
                self.frames[wall.id] = frame
        self.sweeps: list[tuple[str, Prism]] = []
        self.keep_free: list[Prism] = []
        for door in scene.doors:
            frame = self.frames.get(door.wall_id)
            if frame is None:
                continue
            sweep = fp.door_sweep(door, frame)
            if sweep is not None:
                self.sweeps.append((door.id, sweep))
            self.keep_free.append(fp.door_approach(door, frame, DOOR_APPROACH_M))
        for window in scene.windows:
            frame = self.frames.get(window.wall_id)
            if frame is not None:
                self.keep_free.append(fp.window_zone(window, frame, WINDOW_CLEAR_M))
        self.placed: dict[str, _Placed] = {}
        for item in scene.furniture:
            self.add(item)

    def add(self, item: FurnitureItem) -> None:
        self.placed[item.id] = _Placed(
            item,
            fp.item_occupied(item),
            _access(item.category, item.bbox_m, item.pose, item.requires_front_clear_m),
        )

    def possible(self, asset: FurnitureAsset, pose: Pose2D) -> bool:
        """Physically possible: inside the room and not inside another item."""
        if not fp.covered_by(fp.footprint(asset.bbox_m, pose).points, self.polygon):
            return False
        parts = fp.occupied(asset.bbox_m, asset.collision_parts, pose)
        return not any(fp.any_overlap(parts, other.parts) for other in self.placed.values())

    def swept_by(self, asset: FurnitureAsset, pose: Pose2D) -> list[str]:
        """IDs of the doors whose leaf would hit the item."""
        parts = fp.occupied(asset.bbox_m, asset.collision_parts, pose)
        return [door_id for door_id, sweep in self.sweeps if fp.any_overlap(parts, [sweep])]

    def tidy(self, asset: FurnitureAsset, pose: Pose2D) -> bool:
        """Possible, and also what a sensible default layout respects: door swings and
        doorways, windows above the sill, and front access (its own and everyone else's)."""
        if not self.possible(asset, pose) or self.swept_by(asset, pose):
            return False
        parts = fp.occupied(asset.bbox_m, asset.collision_parts, pose)
        if fp.any_overlap(parts, self.keep_free):
            return False
        blocks_access = asset.category != "chair"
        access = _access(asset.category, asset.bbox_m, pose, asset.requires_front_clear_m)
        if access is not None and not fp.covered_by(access.points, self.polygon):
            return False
        for other in self.placed.values():
            if blocks_access and other.access and fp.any_overlap(parts, [other.access]):
                return False
            if access and other.item.category != "chair" and fp.any_overlap([access], other.parts):
                return False
        return True

    def central_points(self, step: float) -> list[Point]:
        """Grid points inside the room, the most open (furthest from the walls) first."""
        xs, zs = [p[0] for p in self.polygon], [p[1] for p in self.polygon]
        points: list[tuple[float, Point]] = []
        for i in range(int((max(xs) - min(xs)) / step) + 1):
            for j in range(int((max(zs) - min(zs)) / step) + 1):
                p = (min(xs) + i * step, min(zs) + j * step)
                if fp.point_in_polygon(p, self.polygon):
                    points.append((fp.boundary_distance(p, self.polygon), p))
        points.sort(key=lambda entry: (-entry[0], entry[1]))
        return [p for _, p in points]


# --- wall-relative poses ----------------------------------------------------------------------


def _front(frame: WallFrame, facing: Facing) -> Point:
    n, u = frame.inward, frame.along
    return {
        "into_room": n,
        "toward_wall": (-n[0], -n[1]),
        "wall_start": (-u[0], -u[1]),
        "wall_end": u,
    }[facing]


def _extents(bbox: BBoxM, facing: Facing) -> tuple[float, float]:
    """(extent along the wall, extent away from it) for an item facing that way."""
    if facing in ("into_room", "toward_wall"):
        return bbox.width, bbox.depth
    return bbox.depth, bbox.width


def _wall_pose(frame: WallFrame, bbox: BBoxM, t: float, offset: float, facing: Facing) -> Pose2D:
    """Centre `t` metres along the wall, nearest face `offset` metres off it."""
    _, away = _extents(bbox, facing)
    x, z = frame.point(t, offset + away / 2)
    return Pose2D(x=x, z=z, yaw_deg=fp.yaw_of(_front(frame, facing)))


def wall_relative(scene: RoomScene, item: FurnitureItem) -> PlacementHint | None:
    """The hint that reproduces an item's pose: the inverse of placing from a hint.

    Picks the nearest wall the item is square to and stands in front of. Used to turn a
    reference scene into expected hints and to score an observer against it. None when the item
    is in front of no wall.
    """
    front = fp.front_direction(item.pose.yaw_deg)
    best: tuple[tuple[bool, float], PlacementHint] | None = None
    for wall in scene.walls:
        frame = fp.wall_frame(wall)
        if frame is None:
            continue
        facing: Facing = max(
            ("into_room", "toward_wall", "wall_start", "wall_end"),
            key=lambda f: _front(frame, f)[0] * front[0] + _front(frame, f)[1] * front[1],
        )
        direction = _front(frame, facing)
        cosine = max(-1.0, min(1.0, direction[0] * front[0] + direction[1] * front[1]))
        _, away = _extents(item.bbox_m, facing)
        t, depth = frame.locate((item.pose.x, item.pose.z))
        offset = depth - away / 2
        if not 0 <= t <= frame.length or offset < -1e-6:
            continue
        score = (math.degrees(math.acos(cosine)) > 1.0, offset)
        if best is None or score < best[0]:
            hint = PlacementHint(
                asset_id=item.id,
                wall_id=wall.id,
                along_frac=t / frame.length,
                offset_m=max(0.0, offset),
                facing=facing,
                confidence=1.0,
            )
            best = (score, hint)
    return best[1] if best else None


# --- placement --------------------------------------------------------------------------------


@dataclass
class _Choice:
    pose: Pose2D
    wall_id: str | None = None
    moved_m: float = 0.0
    fits: bool = True


def _nearby(frame: WallFrame, t: float, offset: float) -> Iterator[tuple[float, float]]:
    """Spots around (t, offset) in the wall's frame, nearest first, never behind the wall."""
    along = int(SEARCH_ALONG_M / SEARCH_STEP_M)
    out = int(SEARCH_OUT_M / SEARCH_STEP_M)
    shifts = [
        (i * SEARCH_STEP_M, j * SEARCH_STEP_M)
        for i in range(-along, along + 1)
        for j in range(-out, out + 1)
    ]
    shifts.sort(key=lambda s: (math.hypot(*s), s))
    for dt, d_out in shifts:
        if offset + d_out >= 0 and 0 <= t + dt <= frame.length:
            yield t + dt, offset + d_out


def _place_hinted(room: _Room, asset: FurnitureAsset, hint: PlacementHint) -> _Choice | None:
    frame = room.frames[hint.wall_id]
    facing: Facing = hint.facing or "into_room"
    span, _ = _extents(asset.bbox_m, facing)
    t = hint.along_frac * frame.length
    exact = _wall_pose(frame, asset.bbox_m, t, hint.offset_m, facing)
    if room.possible(asset, exact):
        return _Choice(exact, hint.wall_id)
    # "In the corner" arrives as a fraction near 0 or 1: keep the whole item on the wall.
    if frame.length >= span:
        t = min(max(t, span / 2), frame.length - span / 2)
    origin = _wall_pose(frame, asset.bbox_m, t, hint.offset_m, facing)
    for near_t, near_offset in _nearby(frame, t, hint.offset_m):
        pose = _wall_pose(frame, asset.bbox_m, near_t, near_offset, facing)
        if room.possible(asset, pose):
            moved = math.hypot(pose.x - origin.x, pose.z - origin.z)
            return _Choice(pose, hint.wall_id, moved_m=moved)
    return None


def _place_seated(room: _Room, asset: FurnitureAsset, parent: FurnitureItem) -> _Choice | None:
    """In front of the parent, facing it, pushed in as far as the collision parts allow."""
    front = fp.front_direction(parent.pose.yaw_deg)
    side = (front[1], -front[0])  # the parent's local +X in the room
    yaw = (parent.pose.yaw_deg + 180) % 360
    reach = parent.bbox_m.depth / 2 + asset.bbox_m.depth / 2
    deepest = min(asset.bbox_m.depth, parent.bbox_m.depth)
    slack = max(0.0, (parent.bbox_m.width - asset.bbox_m.width) / 2)
    laterals = [0.0]
    for i in range(1, int(slack / SEARCH_STEP_M) + 1):
        laterals += [i * SEARCH_STEP_M, -i * SEARCH_STEP_M]
    for lateral in laterals:
        for i in range(int(deepest / SEAT_STEP_M), -1, -1):
            out = reach - i * SEAT_STEP_M
            pose = Pose2D(
                x=parent.pose.x + front[0] * out + side[0] * lateral,
                z=parent.pose.z + front[1] * out + side[1] * lateral,
                yaw_deg=yaw,
            )
            if room.possible(asset, pose):
                return _Choice(pose)
    return None


def _place_default(room: _Room, asset: FurnitureAsset) -> _Choice:
    """Back to a wall, facing in: the longest wall with a free spot. `tidy` spots first, then
    spots that only stay out of door swings, then any possible spot, then open floor. An item
    that fits nowhere goes to the middle."""
    walls = sorted(room.frames.values(), key=lambda f: -f.length)  # stable: ties keep wall order
    span = asset.bbox_m.width

    def clear_of_doors(a: FurnitureAsset, pose: Pose2D) -> bool:
        return room.possible(a, pose) and not room.swept_by(a, pose)

    for check in (room.tidy, clear_of_doors, room.possible):
        for frame in walls:
            if frame.length < span:
                continue
            steps = int((frame.length - span) / DEFAULT_STEP_M)
            spots = [span / 2 + i * DEFAULT_STEP_M for i in range(steps + 1)]
            spots.append(frame.length - span / 2)
            for t in spots:
                pose = _wall_pose(frame, asset.bbox_m, t, 0.0, "into_room")
                if check(asset, pose):
                    return _Choice(pose, frame.wall.id)
    centre = room.central_points(DEFAULT_STEP_M)
    for x, z in centre:
        for yaw in (0.0, 90.0, 180.0, 270.0):
            pose = Pose2D(x=x, z=z, yaw_deg=yaw)
            if room.possible(asset, pose):
                return _Choice(pose)
    x, z = centre[0] if centre else room.polygon[0]
    return _Choice(Pose2D(x=x, z=z, yaw_deg=0.0), fits=False)


# --- alignment --------------------------------------------------------------------------------


def _no_frames(asset_id: str, frame: EvidenceFrame) -> bytes | None:
    return None


def _usable_hints(
    scene: RoomScene,
    room: _Room,
    assets: Sequence[FurnitureAsset],
    hints: Sequence[PlacementHint],
    warnings: list[str],
) -> dict[str, PlacementHint]:
    """Drop hints that name an unknown asset or wall; keep the most confident per asset."""
    known = {a.id for a in assets}
    # A chair is pushed in at a desk or a table, nothing else.
    seats = {a.id for a in assets if a.category in ("desk", "table")}
    seats |= {item.id for item in scene.furniture if item.category in ("desk", "table")}
    usable: dict[str, PlacementHint] = {}
    for hint in hints:
        if hint.asset_id not in known:
            warnings.append(f"ignored a hint for unknown asset {hint.asset_id!r}")
            continue
        if hint.wall_id not in room.frames:
            warnings.append(f"ignored a hint placing {hint.asset_id} on unknown wall")
            continue
        if hint.seated_at is not None and (
            hint.seated_at not in seats or hint.seated_at == hint.asset_id
        ):
            warnings.append(f"{hint.asset_id}: seated_at names no desk or table; using the wall")
            hint = hint.model_copy(update={"seated_at": None})
        current = usable.get(hint.asset_id)
        if current is None or hint.confidence > current.confidence:
            usable[hint.asset_id] = hint
    return usable


def _with_flags(asset: FurnitureAsset, pose: Pose2D, flags: set[Correction]) -> FurnitureItem:
    merged = set(asset.correction_needed) | flags
    ordered = [c for c in _CORRECTION_ORDER if c in merged]
    return asset.model_copy(update={"correction_needed": ordered}).to_item(pose)


def align_assets(
    scene: RoomScene,
    assets: Sequence[FurnitureAsset],
    observer: PlacementObserver,
    frames: FrameSource | None = None,
) -> AlignmentResult:
    """Place every asset in the room. Deterministic for a given scene, assets and hints.

    Furniture already in `scene` is an obstacle and is never moved. An asset whose ID is already
    in the scene keeps that pose (`method = "kept"`), so re-running after edits changes nothing
    the user has touched. Raises ValueError for duplicate asset IDs.
    """
    if len({a.id for a in assets}) != len(assets):
        raise ValueError("asset IDs must be unique")
    room = _Room(scene)
    existing = {item.id: item for item in scene.furniture}
    warnings: list[str] = []
    records: dict[str, AlignmentRecord] = {}
    items: dict[str, FurnitureItem] = {}

    pending: list[FurnitureAsset] = []
    for asset in assets:
        if asset.id in existing:
            items[asset.id] = existing[asset.id]
            records[asset.id] = AlignmentRecord(
                asset_id=asset.id,
                method="kept",
                primary_frame_index=asset.evidence.primary_frame_index,
                notes=["already placed in the scene; pose left unchanged"],
            )
        else:
            pending.append(asset)

    hints: dict[str, PlacementHint] = {}
    if pending:
        try:
            observed = observer.observe(scene, pending, frames or _no_frames)
        except Exception as exc:  # an observer failure must not lose the furniture
            log.warning("placement observer failed: %s", exc)
            warnings.append(f"placement observer failed ({type(exc).__name__}); default layout")
            observed = []
        hints = _usable_hints(scene, room, pending, observed, warnings)

    def area(a: FurnitureAsset) -> float:
        return a.bbox_m.width * a.bbox_m.depth

    # Evidence outranks guesses: hinted items claim their spots first, the most certain first.
    # Seated chairs wait until whatever they sit at is placed.
    hinted = [a for a in pending if a.id in hints and hints[a.id].seated_at is None]
    hinted.sort(key=lambda a: (not a.is_fixed, -hints[a.id].confidence, a.id))
    unhinted = [a for a in pending if a.id not in hints]
    unhinted.sort(key=lambda a: (not a.is_fixed, -area(a), a.id))
    seated = [a for a in pending if a.id in hints and hints[a.id].seated_at is not None]
    seated.sort(key=lambda a: a.id)

    for asset in [*hinted, *unhinted, *seated]:
        hint = hints.get(asset.id)
        record = AlignmentRecord(
            asset_id=asset.id,
            method="default",
            primary_frame_index=asset.evidence.primary_frame_index,
        )
        flags: set[Correction] = set()
        choice: _Choice | None = None
        if hint is not None:
            record.confidence = hint.confidence
            parent = room.placed.get(hint.seated_at) if hint.seated_at else None
            if parent is not None:
                choice = _place_seated(room, asset, parent.item)
                if choice is not None:
                    record.notes.append(f"pushed in at {parent.item.id}")
                else:
                    record.notes.append(f"no room at {parent.item.id}; placed from the wall hint")
            elif hint.seated_at:
                record.notes.append(f"{hint.seated_at} is not placed; placed from the wall hint")
            if choice is None:
                choice = _place_hinted(room, asset, hint)
            if choice is None:
                record.notes.append("no possible spot near the hinted one; default placement")
            else:
                record.method = "hint"
                if hint.confidence < HIGH_CONFIDENCE:
                    flags |= {"placement", "orientation"}
                    record.notes.append("low-confidence hint")
                if hint.facing is None:
                    flags.add("orientation")
                    record.notes.append("front direction unknown; placed back to the wall")
                if choice.moved_m > MOVED_FLAG_M:
                    flags.add("placement")
                    record.notes.append(f"moved {choice.moved_m:.2f} m from the hinted spot to fit")
                swept = room.swept_by(asset, choice.pose)
                if swept:
                    # Furniture does stand in door swings, and the swing itself is inferred from
                    # the plan. Keep what was seen; the audit reports the blocked door.
                    flags.add("placement")
                    record.notes.append("in the swing of " + ", ".join(sorted(swept)))
        if choice is None:
            choice = _place_default(room, asset)
            flags |= {"placement", "orientation"}
            if hint is None:
                record.notes.append("no placement hint; default placement")
            if not choice.fits:
                record.notes.append("does not fit in the room; placed in the middle, overlapping")
        if choice.wall_id is None and hint is not None and record.method == "hint":
            record.wall_id = hint.wall_id
        else:
            record.wall_id = choice.wall_id
        record.moved_m = round(choice.moved_m, 3)
        record.fits = choice.fits
        item = _with_flags(asset, choice.pose, flags)
        room.add(item)
        items[asset.id] = item
        records[asset.id] = record

    return AlignmentResult(
        items=[items[a.id] for a in assets],
        records={a.id: records[a.id] for a in assets},
        warnings=warnings,
    )
