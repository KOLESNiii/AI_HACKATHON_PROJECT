"""Placement hints from a vision model on fal.ai (`FAL_KEY`).

The model is shown a plan view of the room with lettered walls, then the evidence frames with
each asset marked and numbered: its #15 instance mask traced when a `MaskSource` provides one,
otherwise its evidence box. It answers, per asset, with a point on the plan, the wall
the item stands against and the wall its back faces. That is all it decides: `hints_from_reply`
converts the answer into wall-relative `PlacementHint`s and `align.py` does the geometry.

Like the floor-plan annotator this never raises. No key, no frames, a failed call or an
unreadable answer all mean "no hints", and the assets get the flagged default placement.
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
import os
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np
from numpy.typing import NDArray
from pydantic import BaseModel, Field, ValidationError

from contracts.schema import RoomScene
from services.reconstruction.assets.models import EvidenceFrame, FurnitureAsset
from services.reconstruction.assets.segmentation import read_mask
from services.reconstruction.assets.selection_models import SegmentationResult, SelectionResult

from . import footprint as fp
from .annotate import DEFAULT_FAL_ENDPOINT, DEFAULT_FAL_MODEL, _extract_json
from .observe import Facing, FrameSource, PlacementHint
from .plan_view import PlanView, render_room, wall_letters

log = logging.getLogger(__name__)

Image = NDArray[np.uint8]
MaskSource = Callable[[str, EvidenceFrame], NDArray[np.bool_] | None]
"""(asset ID, evidence frame) -> that frame's instance mask (True = the item), or None."""
MAX_FRAMES = 6
"""Evidence frames sent per request; chosen to show every asset at least once."""
UNREVIEWED_CONFIDENCE = 0.7
"""Ceiling on a model's own confidence. A vision answer is a proposal: on the reference room
two models put both sofas on the wrong walls at 0.9. Staying below `align.HIGH_CONFIDENCE`
keeps every unreviewed placement flagged for the user; reviewed recordings may say more."""
_BOX_COLOURS = [(40, 40, 230), (40, 170, 40), (230, 120, 30), (200, 40, 200), (30, 190, 220)]

PROMPT = """You are placing furniture on a floor plan, using frames of a video filmed inside
the same room.

Image 1 is a top-down PLAN of the room. Each wall has a letter. A door is a gap in a wall with
a red arc showing how the door swings. A window is a thick blue line on a wall. Items already
placed are filled rectangles with their names.

The other images are FRAMES of the video. Each object to place is outlined and numbered, with
a box or a traced outline; one number is the same physical object in every frame.

Walls:
{walls}

Objects (width x depth x height in metres):
{objects}

First work out where the camera stands (it usually comes in through a door) and which lettered
wall each wall in the frames is. Use doors, windows, corners, wall lengths and items already on
the plan. Then say where each numbered object stands on the PLAN.

Return ONLY a JSON object, no prose:
{{"camera": "one sentence: where the camera stands and which walls it sees",
  "items": [{{"asset": 1, "x": 0.42, "y": 0.31, "against_wall": "A", "back_to_wall": "A",
             "seated_at": null, "confidence": 0.8}}]}}

- x, y: the centre of the object on image 1, as fractions of the image's width and height
  (0..1, origin top-left).
- against_wall: the letter of the wall the object touches or almost touches; null when it
  stands free in the room.
- back_to_wall: the letter of the wall the object's BACK faces. A sofa against wall B has
  back_to_wall "B". null when the object has no front (a plain table) or you cannot tell.
- seated_at: for a chair pushed in at a numbered desk or table, that object's number; else null.
- confidence: 0..1 for the position. Use less than 0.5 when you are guessing.
- Exactly one entry per numbered object. Do not add objects."""


class _Seen(BaseModel):
    asset: int
    x: float = Field(ge=0, le=1)
    y: float = Field(ge=0, le=1)
    against_wall: str | None = None
    back_to_wall: str | None = None
    seated_at: int | None = None
    confidence: float = Field(default=0.5, ge=0, le=1)


class _Reply(BaseModel):
    camera: str = ""
    items: list[_Seen] = []


# --- frame sources ----------------------------------------------------------------------------


def directory_frames(directory: Path) -> FrameSource:
    """Frames of one video stored as `<frame_index>.jpg` or `.png` (upright, as `bbox_px`)."""

    def source(asset_id: str, frame: EvidenceFrame) -> bytes | None:
        for suffix in (".jpg", ".jpeg", ".png"):
            path = directory / f"{frame.frame_index}{suffix}"
            if path.is_file():
                return path.read_bytes()
        return None

    return source


def selection_frames(
    result: SelectionResult | SegmentationResult,
    data_dir: Path,
    source_ids: Mapping[str, str] | None = None,
) -> FrameSource:
    """The upright frames Dev 2's pipeline stored, for evidence made by
    `assets.selection.object_evidence` from the same selection (#14) or segmentation (#15)
    result.

    Frame ordinals repeat across videos, so each object is read from one source, by the rule
    `object_evidence` uses: `source_ids[object_id]` when given, else the object's only source.
    An object sighted in several videos without a chosen source gets no frames, never another
    video's frame with the same ordinal. Raises ValueError for a chosen source the object was
    not sighted in.
    """
    root = data_dir.resolve()
    by_key = {frame.key: frame for frame in result.frames}
    chosen = source_ids or {}
    paths: dict[tuple[str, int], Path] = {}
    for obj in result.objects:
        sources = {by_key[s.frame_key].source_id for s in obj.sightings}
        source_id = chosen.get(obj.id)
        if source_id is None:
            if len(sources) != 1:
                continue  # ambiguous: which video the evidence came from is unknown
            source_id = next(iter(sources))
        elif source_id not in sources:
            raise ValueError(f"{obj.id} was not sighted in the chosen source")
        for sighting in obj.sightings:
            frame = by_key[sighting.frame_key]
            if frame.source_id == source_id:
                paths[(obj.id, frame.frame_index)] = root / frame.image_path

    def source(asset_id: str, frame: EvidenceFrame) -> bytes | None:
        path = paths.get((asset_id, frame.frame_index))
        if path is None or not path.resolve().is_relative_to(root) or not path.is_file():
            return None
        return path.read_bytes()

    return source


def selection_masks(data_dir: Path) -> MaskSource:
    """The #15 instance masks named by `EvidenceFrame.mask_url`, relative to the asset data
    directory. A missing, unreadable or out-of-directory mask is None (the box is drawn)."""

    def source(asset_id: str, frame: EvidenceFrame) -> NDArray[np.bool_] | None:
        if frame.mask_url is None:
            return None
        try:
            return read_mask(data_dir, frame.mask_url)
        except ValueError:
            return None

    return source


# --- what the model is shown ------------------------------------------------------------------


@dataclass
class _Mark:
    number: int
    box: tuple[float, float, float, float] | None
    """(x, y, w, h) in frame pixels."""
    mask: NDArray[np.bool_] | None = None


@dataclass
class _Shot:
    data: bytes
    marks: list[_Mark] = field(default_factory=list)
    shows: set[int] = field(default_factory=set)
    primary_for: int = 0


def _shots(
    assets: Sequence[FurnitureAsset], frames: FrameSource, masks: MaskSource | None = None
) -> list[_Shot]:
    """The evidence frames worth sending: every asset shown at least once, widest views first."""
    shots: dict[str, _Shot] = {}
    for number, asset in enumerate(assets, start=1):
        for frame in asset.evidence.frames:
            data = frames(asset.id, frame)
            if data is None:
                continue
            shot = shots.setdefault(hashlib.sha256(data).hexdigest(), _Shot(data))
            shot.shows.add(number)
            mask = masks(asset.id, frame) if masks is not None else None
            if frame.bbox_px is not None or mask is not None:
                shot.marks.append(_Mark(number, frame.bbox_px, mask))
            if frame.frame_index == asset.evidence.primary_frame_index:
                shot.primary_for += 1
    remaining = list(shots.values())
    chosen: list[_Shot] = []
    uncovered = {n for shot in remaining for n in shot.shows}
    while remaining and len(chosen) < MAX_FRAMES:
        # Greedy cover of the assets not yet shown; then the most informative of the rest.
        best = max(remaining, key=lambda s: (len(s.shows & uncovered), s.primary_for, len(s.shows)))
        remaining.remove(best)
        chosen.append(best)
        uncovered -= best.shows
    return chosen


def _mark_box(mark: _Mark) -> tuple[int, int, int, int] | None:
    if mark.mask is not None and mark.mask.any():
        ys, xs = np.nonzero(mark.mask)
        return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1
    if mark.box is None:
        return None
    x, y, w, h = mark.box
    return int(x), int(y), int(x + w), int(y + h)


def _draw_marks(shot: _Shot) -> Image | None:
    """The frame with every asset numbered: its mask tinted and traced when the mask matches
    the frame's size, its evidence box otherwise."""
    image = cv2.imdecode(np.frombuffer(shot.data, np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        return None
    thickness = max(2, round(min(image.shape[:2]) / 200))
    scale = max(0.6, min(image.shape[:2]) / 600)
    usable = [
        mark.mask
        if mark.mask is not None and mark.mask.shape == image.shape[:2] and mark.mask.any()
        else None
        for mark in shot.marks
    ]
    tint = image.copy()
    for mark, mask in zip(shot.marks, usable):
        if mask is not None:
            tint[mask] = _BOX_COLOURS[(mark.number - 1) % len(_BOX_COLOURS)]
    cv2.addWeighted(tint, 0.3, image, 0.7, 0, dst=image)
    for mark, mask in zip(shot.marks, usable):
        colour = _BOX_COLOURS[(mark.number - 1) % len(_BOX_COLOURS)]
        box = _mark_box(_Mark(mark.number, mark.box, mask))
        if mask is not None:
            contours, _ = cv2.findContours(
                mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            cv2.drawContours(image, contours, -1, colour, thickness)
        elif box is not None:
            cv2.rectangle(image, box[:2], box[2:], colour, thickness)
        if box is None:
            continue
        top_left = box[:2]
        label = str(mark.number)
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, scale, 2)
        cv2.rectangle(image, top_left, (top_left[0] + tw + 8, top_left[1] + th + 10), colour, -1)
        cv2.putText(
            image,
            label,
            (top_left[0] + 4, top_left[1] + th + 4),
            cv2.FONT_HERSHEY_SIMPLEX,
            scale,
            (255, 255, 255),
            2,
        )
    return image.astype(np.uint8, copy=False)


def _encode(image: Image, suffix: str) -> bytes:
    ok, encoded = cv2.imencode(suffix, image)
    if not ok:
        raise ValueError("could not encode an image for the vision model")
    return encoded.tobytes()


def build_prompt(scene: RoomScene, assets: Sequence[FurnitureAsset]) -> str:
    letters = wall_letters(scene)
    doors = {d.wall_id for d in scene.doors}
    windows = {w.wall_id for w in scene.windows}
    walls = []
    for wall in scene.walls:
        frame = fp.wall_frame(wall)
        if frame is None:
            continue
        features = [
            n for n, has in (("door", wall.id in doors), ("window", wall.id in windows)) if has
        ]
        walls.append(
            f"- {letters[wall.id]}: {frame.length:.1f} m"
            + (", " + ", ".join(features) if features else "")
        )
    objects = [
        f"- {number}: {asset.name} ({asset.category}), "
        f"{asset.bbox_m.width:.2f} x {asset.bbox_m.depth:.2f} x {asset.bbox_m.height:.2f}"
        for number, asset in enumerate(assets, start=1)
    ]
    return PROMPT.format(walls="\n".join(walls), objects="\n".join(objects))


# --- the answer -> hints ----------------------------------------------------------------------


def _facing(frame: fp.WallFrame, back: fp.WallFrame) -> Facing:
    """Front points away from wall `back`; express that in quarter turns of wall `frame`."""
    front = back.inward
    options: dict[Facing, fp.Point] = {
        "into_room": frame.inward,
        "toward_wall": (-frame.inward[0], -frame.inward[1]),
        "wall_start": (-frame.along[0], -frame.along[1]),
        "wall_end": frame.along,
    }
    return max(options, key=lambda f: options[f][0] * front[0] + options[f][1] * front[1])


def _distance_to_wall(frame: fp.WallFrame, p: fp.Point) -> float:
    t, depth = frame.locate(p)
    return math.hypot(max(0.0, -t, t - frame.length), depth)


def hints_from_reply(
    reply: _Reply, scene: RoomScene, assets: Sequence[FurnitureAsset], view: PlanView
) -> list[PlacementHint]:
    """Convert the model's plan points and wall letters into wall-relative hints.

    Entries that name no numbered asset are dropped. An unknown wall letter is treated as not
    given: the nearest wall is used for position and the front stays unknown.
    """
    frames = {w.id: f for w in scene.walls if (f := fp.wall_frame(w)) is not None}
    by_letter = {
        letter: frames[wall_id]
        for wall_id, letter in wall_letters(scene).items()
        if wall_id in frames
    }
    hints: list[PlacementHint] = []
    seen: set[int] = set()
    for entry in reply.items:
        if not 1 <= entry.asset <= len(assets) or entry.asset in seen or not frames:
            continue
        seen.add(entry.asset)
        asset = assets[entry.asset - 1]
        point = view.to_room(entry.x, entry.y)
        against = by_letter.get((entry.against_wall or "").strip().upper())
        back = by_letter.get((entry.back_to_wall or "").strip().upper())
        frame = against or min(frames.values(), key=lambda f: _distance_to_wall(f, point))
        facing = _facing(frame, back) if back is not None else None
        t, depth = frame.locate(point)
        away = asset.bbox_m.width if facing in ("wall_start", "wall_end") else asset.bbox_m.depth
        offset = 0.0 if against is not None else max(0.0, depth - away / 2)
        seated = entry.seated_at
        hints.append(
            PlacementHint(
                asset_id=asset.id,
                wall_id=frame.wall.id,
                along_frac=min(1.0, max(0.0, t / frame.length)),
                offset_m=min(offset, 20.0),
                facing=facing,
                seated_at=assets[seated - 1].id
                if seated is not None and 1 <= seated <= len(assets) and seated != entry.asset
                else None,
                confidence=min(entry.confidence, UNREVIEWED_CONFIDENCE),
            )
        )
    return hints


class FalVisionObserver:
    """Asks a vision LLM on fal.ai where each asset stands (`FAL_KEY`).

    Endpoint and model are the floor-plan annotator's (`FAL_VISION_ENDPOINT`,
    `FAL_VISION_MODEL`). Request shape: `{prompt, model, image_urls}` in, `{"output": str}` out.
    `warnings` and `camera` describe the last call.
    """

    def __init__(
        self,
        endpoint: str | None = None,
        model: str | None = None,
        retries: int = 1,
        masks: MaskSource | None = None,
    ) -> None:
        self.masks = masks
        self.endpoint = endpoint or os.environ.get("FAL_VISION_ENDPOINT", DEFAULT_FAL_ENDPOINT)
        self.model = model or os.environ.get("FAL_VISION_MODEL", DEFAULT_FAL_MODEL)
        self.retries = retries
        self.warnings: list[str] = []
        self.camera = ""

    def observe(
        self, scene: RoomScene, assets: Sequence[FurnitureAsset], frames: FrameSource
    ) -> list[PlacementHint]:
        self.warnings, self.camera = [], ""
        try:
            return self._observe(scene, assets, frames)
        except Exception as exc:  # provider/network failures must not break alignment
            self._warn(f"placement hints unavailable ({type(exc).__name__})")
            return []

    def _warn(self, message: str) -> None:
        log.warning("%s", message)
        self.warnings.append(message)

    def _observe(
        self, scene: RoomScene, assets: Sequence[FurnitureAsset], frames: FrameSource
    ) -> list[PlacementHint]:
        shots = _shots(assets, frames, self.masks)
        images = [img for shot in shots if (img := _draw_marks(shot)) is not None]
        if not images:
            self._warn("no evidence frames available; placement hints were not requested")
            return []
        view = render_room(scene, label_names=True)
        payload = [_encode(view.image, ".png"), *(_encode(img, ".jpg") for img in images)]
        prompt = build_prompt(scene, assets)
        for _ in range(self.retries + 1):
            text = self._ask(prompt, payload)
            if text is None:
                return []
            try:
                reply = _Reply.model_validate(json.loads(_extract_json(text)))
            except (ValidationError, ValueError) as exc:
                self._warn(f"unreadable placement answer ({type(exc).__name__})")
                continue
            self.camera = reply.camera
            return hints_from_reply(reply, scene, assets, view)
        return []

    def _ask(self, prompt: str, images: Sequence[bytes]) -> str | None:
        """One request: the plan (PNG) first, then the frames (JPEG). None when unavailable."""
        if not os.environ.get("FAL_KEY"):
            self._warn("FAL_KEY is not set; placement hints were not requested")
            return None
        try:
            import fal_client
        except ImportError:
            self._warn("fal-client is not installed; placement hints were not requested")
            return None
        urls = [
            fal_client.upload(data, "image/png" if i == 0 else "image/jpeg")
            for i, data in enumerate(images)
        ]
        result = fal_client.subscribe(
            self.endpoint,
            arguments={
                "prompt": prompt,
                "model": self.model,
                "image_urls": urls,
                "temperature": 0,
                "max_tokens": 4000,
                # Matching a video to a plan is spatial reasoning; some models also require it.
                "reasoning": True,
            },
        )
        return str(result.get("output", ""))
