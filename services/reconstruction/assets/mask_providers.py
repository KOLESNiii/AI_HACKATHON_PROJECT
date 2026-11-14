"""Instance masks from item boxes (#15): local GrabCut offline, fal SAM 3 when asked."""

from __future__ import annotations

from typing import Protocol

import cv2
import numpy as np
from numpy.typing import NDArray

from .providers import RequestBudget
from .registry import Registry
from .selection_models import Box, Frame

Mask = NDArray[np.bool_]


class MaskError(Exception):
    """Safe user-facing provider diagnostic; never reflects credentials or raw HTTP bodies."""


def box_pixels(box: Box, width: int, height: int) -> tuple[int, int, int, int]:
    """(x0, y0, x1, y1) with at least one pixel, matching `video.crop`."""
    x0, y0 = min(width - 1, int(box.x * width)), min(height - 1, int(box.y * height))
    x1 = min(width, max(x0 + 1, round((box.x + box.width) * width)))
    y1 = min(height, max(y0 + 1, round((box.y + box.height) * height)))
    return x0, y0, x1, y1


class MaskProvider(Protocol):
    method: str
    """Recorded on every mask it produces: "sam3" or "grabcut"."""

    def segment(
        self,
        frame: Frame,
        image: NDArray[np.uint8],
        boxes: list[Box],
        registry: Registry,
        *,
        budget: RequestBudget | None = None,
    ) -> list[Mask | None]:
        """One frame-sized mask per box, in order; None where none was produced.

        Raises MaskError when the whole frame failed.
        """
        ...


class GrabCutProvider:
    """No network or cost. Approximate: it can keep floor or an occluder inside the box."""

    method = "grabcut"

    def segment(
        self,
        frame: Frame,
        image: NDArray[np.uint8],
        boxes: list[Box],
        registry: Registry,
        *,
        budget: RequestBudget | None = None,
    ) -> list[Mask | None]:
        height, width = image.shape[:2]
        masks: list[Mask | None] = []
        for box in boxes:
            x0, y0, x1, y1 = box_pixels(box, width, height)
            labels = np.zeros((height, width), np.uint8)
            cv2.setRNGSeed(0)  # GrabCut seeds its colour models randomly; keep reruns identical.
            try:
                cv2.grabCut(
                    image,
                    labels,
                    (x0, y0, x1 - x0, y1 - y0),
                    np.zeros((1, 65)),
                    np.zeros((1, 65)),
                    5,
                    cv2.GC_INIT_WITH_RECT,
                )
            except cv2.error:
                masks.append(None)
                continue
            masks.append((labels == cv2.GC_FGD) | (labels == cv2.GC_PR_FGD))
        return masks
