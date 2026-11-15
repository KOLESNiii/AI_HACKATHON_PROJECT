"""Sizes of video furniture, measured against the floor plan (fal.ai vision).

A SAM 3D mesh comes in model units: without stated dimensions `normalise_mesh` scales it so its
height is its category's typical height. That turns a storage bed modelled with its lid up
(0.72 x 1.00 x 0.90 raw) into a 0.4 m toy. The floor plan, though, gives true metres for what
the frames show around the furniture: every wall's length and height, every door's width and
height and every window's width, sill and head.

`FalSizeEstimator` shows a vision model the room's plan (lettered walls, `plan_view`) with those
numbers, and the evidence frames with each item marked as the placement observer marks them,
and asks it to measure each item against those references. Answers are checked (`plausible`):
against the item's category, the room's longest wall and its floor area. An item without a
usable answer is scaled from its category by the side that is reliable for it (`fallback`):
its longest horizontal side for low items (beds, tables, desks, sofas), its height otherwise.

Every size here is `estimated`: it is used, and the item still asks the user to confirm it.
Like the observer this never raises: no key, a failed call or an unreadable answer give the
fallback sizes, with a warning.
"""

from __future__ import annotations

import json
import logging
import math
import os
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from pydantic import BaseModel, Field, ValidationError

from contracts.schema import BBoxM, RoomScene
from services.reconstruction.assets.models import FurnitureAsset
from services.reconstruction.assets.proxies import CATEGORY_SIZE_M, KnownDimensions

from . import footprint as fp
from .annotate import DEFAULT_FAL_ENDPOINT, DEFAULT_FAL_MODEL, _extract_json
from .observe import FrameSource
from .observe_vision import MaskSource, _draw_marks, _encode, _shots
from .plan_view import render_room, wall_letters

log = logging.getLogger(__name__)

MIN_CONFIDENCE = 0.35
CATEGORY_RATIO = (0.2, 2.5)
"""A measured side must lie within these multiples of its category's typical side. Wide on
purpose: a radiator is a quarter as deep as the typical fixture."""
MAX_FOOTPRINT_SHARE = 0.6
"""An item cannot cover more than this share of the room's floor."""
FLAT = frozenset({"bed", "table", "desk", "sofa"})
"""Categories whose longest horizontal side is reliable, and whose height is not: a mesh of a
bed may have its lid up, a table may be modelled with things on it."""

Ask = Callable[[str, Sequence[bytes]], str | None]
"""(prompt, images: plan PNG then frame JPEGs) -> the model's text, or None when unavailable."""


@dataclass(frozen=True)
class Sizes:
    dimensions: dict[str, KnownDimensions]
    """Asset ID -> its size (always `estimated`)."""
    warnings: list[str]


def _bbox(width: float, height: float, depth: float) -> BBoxM:
    return BBoxM(width=round(width, 3), height=round(height, 3), depth=round(depth, 3))


def fallback(asset: FurnitureAsset) -> BBoxM:
    """The asset's own proportions (its mesh's, uniformly scaled), sized from its category by
    the side that is reliable for it."""
    tw, th, td = CATEGORY_SIZE_M[asset.category]
    w, h, d = asset.bbox_m.width, asset.bbox_m.height, asset.bbox_m.depth
    factor = max(tw, td) / max(w, d) if asset.category in FLAT else th / h
    return _bbox(w * factor, h * factor, d * factor)


def _polygon_area(scene: RoomScene) -> float:
    pts = scene.floor_polygon
    return abs(sum(a.x * b.z - b.x * a.z for a, b in zip(pts, [*pts[1:], pts[0]], strict=True)) / 2)


def plausible(category: str, bbox: BBoxM, scene: RoomScene) -> str | None:
    """Why this size cannot be right for this item in this room, or None when it can."""
    typical = CATEGORY_SIZE_M[category]  # type: ignore[index]
    lo, hi = CATEGORY_RATIO
    for side, value, usual in zip(
        ("width", "height", "depth"), (bbox.width, bbox.height, bbox.depth), typical, strict=True
    ):
        if not lo * usual <= value <= hi * usual:
            return f"{side} {value:.2f} m is not plausible for a {category}"
    longest = max(
        (f.length for w in scene.walls if (f := fp.wall_frame(w)) is not None), default=math.inf
    )
    if max(bbox.width, bbox.depth) > longest:
        return f"{max(bbox.width, bbox.depth):.2f} m is longer than the room's longest wall"
    if bbox.width * bbox.depth > MAX_FOOTPRINT_SHARE * _polygon_area(scene):
        return "it would cover most of the room's floor"
    return None


PROMPT = """You are measuring furniture in a room, using its floor plan for true sizes.

Image 1 is a top-down PLAN of the room. Each wall has a letter. A door is a gap in a wall with
a red arc showing how it swings. A window is a thick blue line on a wall.

The other images are FRAMES of a video filmed inside this room. Each object to measure is
outlined and numbered; one number is the same physical object in every frame.

True sizes from the plan, in metres. Use them as rulers: compare each object with the walls,
doors and windows next to it in the frames.
{references}

Objects:
{objects}

For each numbered object give its real size in metres: width (side to side, seen from its
front), depth (front to back) and height (floor to top). Measure the object as it normally
stands: a bed or chest with a lid or drawer open is measured closed.

Return ONLY a JSON object, no prose:
{{"items": [{{"asset": 1, "width": 1.5, "depth": 2.0, "height": 0.5,
             "reference": "half the length of wall B", "confidence": 0.7}}]}}
Use confidence below 0.35 when you cannot see enough of an object to measure it."""


def references(scene: RoomScene) -> str:
    """Every metric reference the plan gives for this room, one per line."""
    letters = wall_letters(scene)
    lines = []
    for wall in scene.walls:
        frame = fp.wall_frame(wall)
        if frame is not None:
            lines.append(
                f"- wall {letters[wall.id]}: {frame.length:.2f} long, {wall.height_m:.2f} high"
            )
    for door in scene.doors:
        if door.wall_id in letters:
            lines.append(
                f"- door in wall {letters[door.wall_id]}: {door.width_m:.2f} wide, "
                f"{door.head_height_m:.2f} high"
            )
    for window in scene.windows:
        if window.wall_id in letters:
            lines.append(
                f"- window in wall {letters[window.wall_id]}: {window.width_m:.2f} wide, from "
                f"{window.sill_height_m:.2f} to {window.head_height_m:.2f} above the floor"
            )
    return "\n".join(lines)


def build_prompt(scene: RoomScene, assets: Sequence[FurnitureAsset]) -> str:
    objects = "\n".join(
        f"- {number}: {asset.name} ({asset.category})"
        for number, asset in enumerate(assets, start=1)
    )
    return PROMPT.format(references=references(scene), objects=objects)


class _Measured(BaseModel):
    asset: int
    width: float = Field(gt=0)
    depth: float = Field(gt=0)
    height: float = Field(gt=0)
    reference: str = ""
    confidence: float = Field(default=0.5, ge=0, le=1)


class _Reply(BaseModel):
    items: list[_Measured]


def parse_reply(text: str, count: int) -> dict[int, _Measured]:
    """Confident measurements by object number (1-based); raises ValueError when unreadable."""
    try:
        reply = _Reply.model_validate(json.loads(_extract_json(text)))
    except (ValidationError, json.JSONDecodeError) as exc:
        raise ValueError("unreadable size answer") from exc
    return {
        m.asset: m for m in reply.items if 1 <= m.asset <= count and m.confidence >= MIN_CONFIDENCE
    }


class FalSizeEstimator:
    """Measures furniture against the plan with a vision LLM on fal.ai. Never raises."""

    def __init__(
        self, endpoint: str | None = None, model: str | None = None, ask: Ask | None = None
    ) -> None:
        self.endpoint = endpoint or os.environ.get("FAL_VISION_ENDPOINT", DEFAULT_FAL_ENDPOINT)
        self.model = model or os.environ.get("FAL_VISION_MODEL", DEFAULT_FAL_MODEL)
        self.ask = ask or self._ask

    def estimate(
        self,
        scene: RoomScene,
        assets: Sequence[FurnitureAsset],
        frames: FrameSource | None,
        masks: MaskSource | None = None,
    ) -> Sizes:
        measured = self._measure(scene, assets, frames, masks) if assets else {}
        dimensions: dict[str, KnownDimensions] = {}
        fell_back: list[str] = []
        for number, asset in enumerate(assets, start=1):
            m = measured.get(number)
            bbox = _bbox(m.width, m.height, m.depth) if m else None
            if bbox is None or plausible(asset.category, bbox, scene) is not None:
                bbox = fallback(asset)
                fell_back.append(asset.name)
            dimensions[asset.id] = KnownDimensions(bbox_m=bbox, source="estimated")
        warnings = (
            [f"sized from their category, could not be measured: {', '.join(fell_back)}"]
            if fell_back
            else []
        )
        return Sizes(dimensions, warnings)

    def _measure(
        self,
        scene: RoomScene,
        assets: Sequence[FurnitureAsset],
        frames: FrameSource | None,
        masks: MaskSource | None,
    ) -> dict[int, _Measured]:
        if frames is None:
            return {}
        try:
            shots = _shots(assets, frames, masks)
            images = [img for shot in shots if (img := _draw_marks(shot)) is not None]
            if not images:
                return {}
            payload = [
                _encode(render_room(scene, label_names=True).image, ".png"),
                *(_encode(img, ".jpg") for img in images),
            ]
            prompt = build_prompt(scene, assets)
            for _ in range(2):  # one retry for an unreadable answer
                text = self.ask(prompt, payload)
                if text is None:
                    return {}
                try:
                    return parse_reply(text, len(assets))
                except ValueError:
                    continue
        except Exception as exc:  # provider/network failures must not lose the furniture
            log.warning("furniture sizes unavailable (%s)", type(exc).__name__)
        return {}

    def _ask(self, prompt: str, images: Sequence[bytes]) -> str | None:
        if not os.environ.get("FAL_KEY"):
            return None
        import fal_client

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
                "max_tokens": 3000,
                "reasoning": True,
            },
        )
        return str(result.get("output", ""))
