"""Which plan room each video frame shows, so a whole-home walkthrough furnishes each room.

The furniture pipeline (`assets/selection.py`) finds items in sampled frames but knows nothing
of the plan. Here a vision model on fal.ai (`FAL_KEY`; the floor-plan annotator's endpoint and
model) is shown every storey with its rooms numbered (`plan_view.render_floor`) and a run of
consecutive frames of one video, and says which numbered room each frame was filmed in.

The answers are then smoothed with what a walkthrough implies (`smooth`): the camera stays in
a room for a while and leaves it through a door, so a lone frame in another room is taken as
a mistake, and so is a jump between rooms that share no door. Each item then belongs to the
room most of its sightings were filmed in (`assign_items`).

Like the placement observer this never raises: no key, a failed call or an unreadable answer
leave those frames unassigned, with a warning.

VGGT cameras and depth (probed in #14) could later check a frame's room by its shape; they are
unscaled and not integrated, so they are not used here.
"""

from __future__ import annotations

import json
import logging
import math
import os
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

import cv2
from pydantic import BaseModel, Field, ValidationError

from contracts.schema import ParsedFloorPlan, RoomScene
from services.reconstruction.assets.selection_models import Frame, SelectedObject

from .annotate import DEFAULT_FAL_ENDPOINT, DEFAULT_FAL_MODEL, _extract_json
from .plan_view import render_floor

log = logging.getLogger(__name__)

FRAMES_PER_REQUEST = 8
FRAME_MAX_PX = 640
MIN_CONFIDENCE = 0.35
DOOR_MATCH_SLACK_M = 0.3

Ask = Callable[[str, Sequence[bytes]], str | None]
"""(prompt, images: floor PNGs then frame JPEGs) -> the model's text, or None when unavailable."""


@dataclass(frozen=True)
class PlanRoom:
    number: int
    """1-based, across every floor: the label drawn on the plan."""
    room_id: str
    floor_id: str
    floor_name: str
    name: str
    scene: RoomScene


def plan_rooms(plan: ParsedFloorPlan) -> list[PlanRoom]:
    rooms: list[PlanRoom] = []
    for floor in plan.floors:
        for room in floor.rooms:
            rooms.append(
                PlanRoom(
                    len(rooms) + 1, room.room_id, floor.floor_id, floor.name, room.name, room.scene
                )
            )
    return rooms


def adjacency(rooms: Sequence[PlanRoom]) -> dict[str, set[str]]:
    """Rooms that share a door: on the same floor, with door hinges at most a door's width
    (plus slack) apart. Each room of a shared door holds its own copy of it."""
    doors = {
        r.room_id: [(d.hinge_pos.x, d.hinge_pos.z, d.width_m) for d in r.scene.doors] for r in rooms
    }
    near: dict[str, set[str]] = {r.room_id: set() for r in rooms}
    for i, a in enumerate(rooms):
        for b in rooms[i + 1 :]:
            if a.floor_id != b.floor_id:
                continue
            if any(
                math.dist((ax, az), (bx, bz)) <= max(aw, bw) + DOOR_MATCH_SLACK_M
                for ax, az, aw in doors[a.room_id]
                for bx, bz, bw in doors[b.room_id]
            ):
                near[a.room_id].add(b.room_id)
                near[b.room_id].add(a.room_id)
    return near


def smooth(labels: Sequence[str | None], adjacent: Mapping[str, set[str]]) -> list[str | None]:
    """Walkthrough continuity over one video's frames, in filming order.

    1. A lone frame between two frames of the same room takes that room.
    2. A run of a single frame whose room shares no door with the room before it takes that
       room (the camera cannot have teleported). Unassigned frames (None) stay unassigned and
       do not break continuity checks across them.
    """
    out = list(labels)
    for i in range(1, len(out) - 1):
        if out[i - 1] is not None and out[i - 1] == out[i + 1] != out[i]:
            out[i] = out[i - 1]
    previous: str | None = None
    for i, label in enumerate(out):
        if label is None:
            continue
        lone = (i + 1 >= len(out) or out[i + 1] != label) and (i == 0 or out[i - 1] != label)
        if (
            lone
            and previous is not None
            and label != previous
            and label not in adjacent.get(previous, set())
        ):
            out[i] = previous
        previous = out[i]
    return out


def assign_items(
    objects: Sequence[SelectedObject], frame_rooms: Mapping[str, str | None]
) -> dict[str, str | None]:
    """Each item's room: the room most of its sightings were filmed in. None when no sighting
    has a room, or when two rooms tie."""
    rooms: dict[str, str | None] = {}
    for obj in objects:
        votes = Counter(
            room for s in obj.sightings if (room := frame_rooms.get(s.frame_key)) is not None
        )
        ranked = votes.most_common(2)
        if not ranked or (len(ranked) == 2 and ranked[0][1] == ranked[1][1]):
            rooms[obj.id] = None
        else:
            rooms[obj.id] = ranked[0][0]
    return rooms


PROMPT = """You are matching frames of a walkthrough video of a home to the rooms of its floor plan.
The first {floors} image(s) are the floor plan, one per storey ({floor_names}), with every room
numbered. Then come video frames {first}..{last}, in filming order, a few seconds apart.

Rooms:
{rooms}
{previous}
For each frame, say which numbered room the camera is standing in. Use what is visible (beds:
bedroom; oven, sink, worktops: kitchen; toilet, shower, bath: bathroom; stairs: hall or landing),
the printed room names, sizes, doors and windows, and continuity: the camera walks from room to
room through doors, so consecutive frames are usually in the same room or in rooms that share a
door. If a frame is too blurry or shows nothing recognisable, use null.
Return ONLY JSON: {{"frames":[{{"frame":"{first}","room":3,"confidence":0.8}}]}}"""


class _Seen(BaseModel):
    frame: str
    room: int | None = None
    confidence: float = Field(default=0.5, ge=0, le=1)


class _Reply(BaseModel):
    frames: list[_Seen]


def build_prompt(rooms: Sequence[PlanRoom], count: int, previous: PlanRoom | None) -> str:
    lines = []
    for r in rooms:
        xs = [p.x for p in r.scene.floor_polygon]
        zs = [p.z for p in r.scene.floor_polygon]
        lines.append(
            f"- {r.number}: {r.name} ({r.floor_name}), {max(xs) - min(xs):.1f} x "
            f"{max(zs) - min(zs):.1f} m, {len(r.scene.doors)} door(s), "
            f"{len(r.scene.windows)} window(s)"
        )
    floors = list(dict.fromkeys(r.floor_name for r in rooms))
    return PROMPT.format(
        floors=len(floors),
        floor_names=", ".join(floors),
        first="F0",
        last=f"F{count - 1}",
        rooms="\n".join(lines),
        previous=(
            f"The frame just before F0 was in room {previous.number} ({previous.name}).\n"
            if previous
            else ""
        ),
    )


def parse_reply(text: str, count: int, rooms: Sequence[PlanRoom]) -> list[PlanRoom | None]:
    """The room of each of `count` frames; raises ValueError for an unreadable answer."""
    by_number = {r.number: r for r in rooms}
    try:
        reply = _Reply.model_validate(json.loads(_extract_json(text)))
    except (ValidationError, json.JSONDecodeError) as exc:
        raise ValueError("unreadable room answer") from exc
    out: list[PlanRoom | None] = [None] * count
    for seen in reply.frames:
        if not seen.frame.startswith("F") or not seen.frame[1:].isdigit():
            continue
        index = int(seen.frame[1:])
        if 0 <= index < count and seen.room is not None and seen.confidence >= MIN_CONFIDENCE:
            out[index] = by_number.get(seen.room)
    return out


def _encode(image: cv2.typing.MatLike, suffix: str) -> bytes:
    ok, data = cv2.imencode(suffix, image)
    if not ok:
        raise ValueError("could not encode an image for the vision model")
    return bytes(data.tobytes())


def _frame_jpeg(data_dir: Path, frame: Frame) -> bytes | None:
    from services.reconstruction.assets.video import read_image

    try:
        image = read_image(data_dir, frame)
    except ValueError:
        return None
    height, width = image.shape[:2]
    scale = FRAME_MAX_PX / max(height, width)
    if scale >= 1:
        return _encode(image, ".jpg")
    return _encode(cv2.resize(image, (int(width * scale), int(height * scale))), ".jpg")


@dataclass
class RoomAssignment:
    frame_rooms: dict[str, str | None]
    """Frame key -> room ID (None: unassigned)."""
    item_rooms: dict[str, str | None]
    """Object ID -> room ID (None: unassigned)."""
    warnings: list[str]


class FalRoomClassifier:
    """Asks a vision LLM on fal.ai which plan room each frame shows. Never raises."""

    def __init__(
        self, endpoint: str | None = None, model: str | None = None, ask: Ask | None = None
    ) -> None:
        self.endpoint = endpoint or os.environ.get("FAL_VISION_ENDPOINT", DEFAULT_FAL_ENDPOINT)
        self.model = model or os.environ.get("FAL_VISION_MODEL", DEFAULT_FAL_MODEL)
        self.ask = ask or self._ask

    def assign(
        self,
        plan: ParsedFloorPlan,
        frames: Sequence[Frame],
        objects: Sequence[SelectedObject],
        data_dir: Path,
    ) -> RoomAssignment:
        rooms = plan_rooms(plan)
        warnings: list[str] = []
        if not rooms:
            return RoomAssignment({}, {o.id: None for o in objects}, ["the plan has no rooms"])
        floors = []
        for floor in plan.floors:
            numbered = [(r.number, r.scene) for r in rooms if r.floor_id == floor.floor_id]
            if numbered:
                floors.append(_encode(render_floor(numbered), ".png"))
        adjacent = adjacency(rooms)
        frame_rooms: dict[str, str | None] = {}
        by_source: dict[str, list[Frame]] = {}
        for frame in frames:
            by_source.setdefault(frame.source_id, []).append(frame)
        failed = 0
        for source in by_source.values():
            source.sort(key=lambda f: f.timestamp_s)
            labels: list[str | None] = []
            previous: PlanRoom | None = None
            for start in range(0, len(source), FRAMES_PER_REQUEST):
                batch = source[start : start + FRAMES_PER_REQUEST]
                answer = self._classify(rooms, floors, batch, previous, data_dir)
                if answer is None:
                    failed += 1
                    answer = [None] * len(batch)
                labels.extend(r.room_id if r else None for r in answer)
                previous = next((r for r in reversed(answer) if r is not None), previous)
            for frame, label in zip(source, smooth(labels, adjacent), strict=True):
                frame_rooms[frame.key] = label
        if failed:
            warnings.append(f"{failed} frame batch(es) could not be matched to rooms")
        item_rooms = assign_items(objects, frame_rooms)
        return RoomAssignment(frame_rooms, item_rooms, warnings)

    def _classify(
        self,
        rooms: Sequence[PlanRoom],
        floors: Sequence[bytes],
        batch: Sequence[Frame],
        previous: PlanRoom | None,
        data_dir: Path,
    ) -> list[PlanRoom | None] | None:
        images = [img for f in batch if (img := _frame_jpeg(data_dir, f)) is not None]
        if len(images) != len(batch):
            return None
        prompt = build_prompt(rooms, len(batch), previous)
        for _ in range(2):  # one retry for an unreadable answer
            try:
                text = self.ask(prompt, [*floors, *images])
            except Exception as exc:  # provider/network failures must not stop extraction
                log.warning("room classification unavailable (%s)", type(exc).__name__)
                return None
            if text is None:
                return None
            try:
                return parse_reply(text, len(batch), rooms)
            except ValueError:
                continue
        return None

    def _ask(self, prompt: str, images: Sequence[bytes]) -> str | None:
        if not os.environ.get("FAL_KEY"):
            return None
        import fal_client

        urls = [
            fal_client.upload(data, "image/png" if data[:4] == b"\x89PNG" else "image/jpeg")
            for data in images
        ]
        result = fal_client.subscribe(
            self.endpoint,
            arguments={
                "prompt": prompt,
                "model": self.model,
                "image_urls": urls,
                "temperature": 0,
                "max_tokens": 2000,
                "reasoning": True,
            },
        )
        return str(result.get("output", ""))
