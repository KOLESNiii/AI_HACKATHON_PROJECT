"""What computer vision cannot read off a floor plan: room labels with their printed metric
dimensions, floor captions, and the compass. Provided by a vision LLM; the geometry never
comes from it.

Positions are normalised image coordinates (0..1, origin top-left), so they survive any
resampling. Annotators never raise: a provider failure returns empty annotations plus a warning,
and the parser falls back to estimated scale.
"""

from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel, Field, ValidationError, field_validator

log = logging.getLogger(__name__)


def _tidy_name(name: str) -> str:
    """Plans print labels in capitals ("BEDROOM (4)"); show them in title case."""
    name = " ".join(name.split())
    return name.title() if name.isupper() else name


class RoomLabel(BaseModel):
    name: str
    _tidy = field_validator("name")(_tidy_name)
    x: float = Field(ge=0, le=1)
    """Centre of the label text, as a fraction of image width."""
    y: float = Field(ge=0, le=1)
    """Centre of the label text, as a fraction of image height."""
    width_m: float | None = Field(default=None, gt=0, lt=50)
    """First printed metric dimension (e.g. 4.42 in "4.42m x 3.30m")."""
    depth_m: float | None = Field(default=None, gt=0, lt=50)
    """Second printed metric dimension."""


class FloorCaption(BaseModel):
    name: str
    _tidy = field_validator("name")(_tidy_name)
    level: int | None = None
    """0 = ground floor, 1 = first floor, -1 = basement."""
    x: float = Field(ge=0, le=1)
    y: float = Field(ge=0, le=1)


class Compass(BaseModel):
    north_bearing_deg: float = Field(ge=0, lt=360)
    """Direction the north arrow points, clockwise from straight up the image."""


class PlanAnnotations(BaseModel):
    rooms: list[RoomLabel] = []
    floors: list[FloorCaption] = []
    compass: Compass | None = None


class AnnotationResult(BaseModel):
    annotations: PlanAnnotations
    warnings: list[str] = []


class PlanAnnotator(Protocol):
    def annotate(self, image: bytes, content_type: str) -> AnnotationResult: ...


class NullAnnotator:
    """No labels: the parser falls back to estimated scale and generic names."""

    def annotate(self, image: bytes, content_type: str) -> AnnotationResult:
        return AnnotationResult(annotations=PlanAnnotations())


class FixedAnnotator:
    """Returns pre-recorded annotations (tests, the debug CLI, cached demo plans)."""

    def __init__(self, annotations: PlanAnnotations | list[PlanAnnotations]) -> None:
        self._queue = annotations if isinstance(annotations, list) else [annotations]
        self._i = 0

    @classmethod
    def from_file(cls, path: Path) -> FixedAnnotator:
        return cls(PlanAnnotations.model_validate_json(path.read_text()))

    def annotate(self, image: bytes, content_type: str) -> AnnotationResult:
        ann = self._queue[min(self._i, len(self._queue) - 1)]
        self._i += 1
        return AnnotationResult(annotations=ann)


PROMPT = """You are reading an architectural floor plan image. Return ONLY a JSON object, no prose,
with this exact shape:

{
  "rooms": [{"name": str, "x": float, "y": float, "width_m": float|null, "depth_m": float|null}],
  "floors": [{"name": str, "level": int|null, "x": float, "y": float}],
  "compass": {"north_bearing_deg": float} | null
}

- rooms: one entry per room label printed on the plan (e.g. "BEDROOM (4)", "KITCHEN"). Use the
  label as printed (title case). x, y = centre of the label text as fractions of the image
  width and height (0..1, origin top-left). width_m, depth_m = the two METRIC dimensions printed
  under the label in the order printed (e.g. "4.52m x 3.68m" -> 4.52, 3.68). Ignore imperial
  dimensions. Use null when no metric dimensions are printed.
- floors: one entry per floor/storey caption (e.g. "GROUND FLOOR", "FIRST FLOOR"), with x, y
  at the caption's centre and level 0 for ground, 1 for first, 2 for second, -1 for basement.
  Empty list if the sheet has no floor captions.
- compass: if a north arrow is drawn, the direction it points as degrees clockwise from
  straight up the image (0 = up, 90 = right). null if there is no north arrow or it is cut off.
- Do not include gardens, driveways or areas outside the building as rooms."""

DEFAULT_FAL_ENDPOINT = "fal-ai/any-llm/vision"
DEFAULT_FAL_MODEL = "google/gemini-2.5-flash"


def _extract_json(text: str) -> str:
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
    if fenced:
        return fenced.group(1)
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        raise ValueError("no JSON object in model output")
    return text[start : end + 1]


class FalVisionAnnotator:
    """Reads labels with a vision LLM on fal.ai (`FAL_KEY`).

    The endpoint and model are configurable (`FAL_VISION_ENDPOINT`, `FAL_VISION_MODEL`). The
    request and response shape follows fal's any-llm vision API: `{prompt, model, image_url}`
    in, `{"output": str}` out.
    """

    def __init__(
        self, endpoint: str | None = None, model: str | None = None, retries: int = 1
    ) -> None:
        self.endpoint = endpoint or os.environ.get("FAL_VISION_ENDPOINT", DEFAULT_FAL_ENDPOINT)
        self.model = model or os.environ.get("FAL_VISION_MODEL", DEFAULT_FAL_MODEL)
        self.retries = retries

    def annotate(self, image: bytes, content_type: str) -> AnnotationResult:
        if not os.environ.get("FAL_KEY"):
            return AnnotationResult(
                annotations=PlanAnnotations(),
                warnings=["FAL_KEY is not set; room labels were not read, so scale is estimated"],
            )
        try:
            import fal_client
        except ImportError:
            return AnnotationResult(
                annotations=PlanAnnotations(),
                warnings=["fal-client is not installed; room labels were not read"],
            )
        last_error = ""
        for _ in range(self.retries + 1):
            try:
                url = fal_client.upload(image, content_type)
                result = fal_client.subscribe(
                    self.endpoint,
                    arguments={"prompt": PROMPT, "model": self.model, "image_url": url},
                )
                text = str(result.get("output", ""))
                ann = PlanAnnotations.model_validate(json.loads(_extract_json(text)))
                return AnnotationResult(annotations=ann)
            except (ValidationError, ValueError) as exc:
                last_error = f"unreadable model output: {exc}"
            except Exception as exc:  # provider/network failures must not break parsing
                last_error = f"{type(exc).__name__}: {exc}"
            log.warning("floor-plan annotation failed: %s", last_error)
        return AnnotationResult(
            annotations=PlanAnnotations(),
            warnings=[f"room labels could not be read ({last_error}); scale is estimated"],
        )
