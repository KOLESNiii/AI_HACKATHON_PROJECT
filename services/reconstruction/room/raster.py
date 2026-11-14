"""Image → binary masks: all ink, and the structural strokes that are walls.

Everything runs at a fixed working resolution so pixel thresholds behave the same for a
1200 px export and a phone photo of a printout.
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np
from numpy.typing import NDArray

WORK_LONG_SIDE_PX = 2000
"""Images are resampled so their long side is this many pixels before any processing."""

Mask = NDArray[np.bool_]
Gray = NDArray[np.uint8]


@dataclass(frozen=True)
class Raster:
    gray: Gray
    """Illumination-corrected greyscale at working resolution (white paper ~255)."""
    ink: Mask
    """Every dark pixel: walls, text, symbols, window lines, hatching."""
    structure: Mask
    """Wall strokes. Thin detail (door leaves, window glazing lines, furniture symbols, hatching)
    and text glyphs are removed, so doors and windows show up as gaps."""
    wall_px: float
    """Thickness of the plan's main (thickest common) walls, in working pixels."""
    resample: float
    """Working pixels per source-image pixel."""

    @property
    def shape(self) -> tuple[int, int]:
        h, w = self.gray.shape
        return int(h), int(w)


class UnreadableImage(ValueError):
    pass


def decode(data: bytes) -> NDArray[np.uint8]:
    arr = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise UnreadableImage("could not decode the floor-plan image")
    return np.asarray(img, dtype=np.uint8)


def flatten_illumination(gray: Gray) -> Gray:
    """Divide by a smooth estimate of the paper so a photographed printout thresholds evenly."""
    h, w = gray.shape
    k = max(31, (min(h, w) // 20) | 1)
    # Closing removes dark strokes narrower than k and leaves the paper brightness.
    paper = cv2.morphologyEx(
        gray, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (k, k))
    )
    paper = cv2.GaussianBlur(paper, (0, 0), k / 2)
    flat = gray.astype(np.float32) / np.maximum(paper.astype(np.float32), 1.0) * 255.0
    return np.asarray(np.clip(flat, 0, 255), dtype=np.uint8)


def estimate_wall_px(ink: Mask) -> float:
    """Thickness of the main walls: the dominant stroke width, weighted towards thick strokes.

    Ridge pixels of the distance transform carry each stroke's half-width. Counting ridge
    pixels per half-width (smoothed over neighbouring bins) and weighting by the half-width
    makes long thick strokes (walls) beat short thick ones (bold text) and long thin ones
    (hatching, glazing lines).
    """
    dist = cv2.distanceTransform(ink.astype(np.uint8), cv2.DIST_L2, 5)
    ridge = (dist >= cv2.dilate(dist, np.ones((3, 3), np.uint8))) & (dist >= 2.5)
    values = dist[ridge]
    if values.size == 0:
        return 6.0
    bins = np.bincount(np.round(values).astype(int)).astype(np.float64)
    smoothed = np.convolve(bins, np.ones(3), mode="same") * np.arange(bins.size)
    smoothed[:3] = 0
    return float(2 * int(np.argmax(smoothed)))


def structural_strokes(ink: Mask, wall_px: float) -> Mask:
    """Remove strokes much thinner than a wall, then small isolated blobs (text glyphs)."""
    k = max(3, int(round(wall_px * 0.35)))
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
    opened = cv2.morphologyEx(ink.astype(np.uint8), cv2.MORPH_OPEN, kernel)
    n, labels, stats, _ = cv2.connectedComponentsWithStats(opened, connectivity=8)
    # Keep long strokes (walls) and short ones that are wall-thick (stubs between bay windows).
    # Text glyphs are short and thinner than walls.
    long_enough = (
        np.maximum(stats[:, cv2.CC_STAT_WIDTH], stats[:, cv2.CC_STAT_HEIGHT]) >= 3.5 * wall_px
    )
    dist = cv2.distanceTransform(opened, cv2.DIST_L2, 5)
    thickest = np.zeros(n, dtype=np.float32)
    np.maximum.at(thickest, np.asarray(labels, dtype=np.intp).ravel(), dist.ravel())
    keep = long_enough | (thickest >= 0.4 * wall_px)
    keep[0] = False
    return np.asarray(keep[labels])


def rasterise(data: bytes) -> Raster:
    img = decode(data)
    h, w = img.shape[:2]
    resample = WORK_LONG_SIDE_PX / max(h, w)
    interp = cv2.INTER_AREA if resample < 1 else cv2.INTER_CUBIC
    size = (round(w * resample), round(h * resample))
    img = np.asarray(cv2.resize(img, size, interpolation=interp), dtype=np.uint8)
    gray = flatten_illumination(np.asarray(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), dtype=np.uint8))
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    ink = np.asarray(binary > 0)
    wall_px = estimate_wall_px(ink)
    structure = structural_strokes(ink, wall_px)
    return Raster(
        gray=np.asarray(gray, dtype=np.uint8),
        ink=ink,
        structure=structure,
        wall_px=wall_px,
        resample=resample,
    )
