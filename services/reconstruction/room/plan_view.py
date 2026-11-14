"""Plan view of one room: the picture of the contract geometry that people and the vision
observer both read. Walls are lettered in wall order, with a dot at each wall's `start`."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import cv2
import numpy as np
from numpy.typing import NDArray

from contracts.schema import FurnitureItem, RoomScene

from . import footprint as fp
from .align import AlignmentRecord

Image = NDArray[np.uint8]

# OpenCV colours are BGR.
_SETTLED, _CONFIRM, _NO_FIT = (90, 170, 90), (40, 150, 240), (60, 60, 220)
_WALL, _LABEL, _WINDOW, _DOOR = (40, 40, 40), (170, 40, 40), (230, 160, 30), (60, 60, 200)
_PAD_M = 0.6


def wall_letters(scene: RoomScene) -> dict[str, str]:
    """Short labels for a room's walls (A, B, ...), in wall order: wall ID -> letter."""
    return {w.id: chr(ord("A") + i) if i < 26 else f"W{i}" for i, w in enumerate(scene.walls)}


@dataclass
class PlanView:
    image: Image
    origin: fp.Point
    """Room (x, z) of the image's top-left pixel."""
    px_per_m: float

    def to_pixel(self, p: fp.Point) -> tuple[int, int]:
        return (
            int(round((p[0] - self.origin[0]) * self.px_per_m)),
            int(round((p[1] - self.origin[1]) * self.px_per_m)),
        )

    def to_room(self, fx: float, fy: float) -> fp.Point:
        """Room (x, z) of a point given as fractions of the image's width and height."""
        height, width = self.image.shape[:2]
        return (
            self.origin[0] + fx * width / self.px_per_m,
            self.origin[1] + fy * height / self.px_per_m,
        )


def render_room(
    scene: RoomScene,
    records: dict[str, AlignmentRecord] | None = None,
    reference: Sequence[FurnitureItem] = (),
    px_per_m: float = 110.0,
    label_names: bool = False,
) -> PlanView:
    """Walls (lettered), windows, door swings and furniture, +X right and +Z down the page.

    Furniture is green when settled, orange when its placement or orientation needs
    confirming, red when it does not fit; a line from the centre marks its front. `reference`
    poses are drawn as grey outlines. Items are labelled by ID, or by name for a reader who has
    never seen the IDs (`label_names`).
    """
    xs = [p.x for p in scene.floor_polygon]
    zs = [p.z for p in scene.floor_polygon]
    origin = (min(xs) - _PAD_M, min(zs) - _PAD_M)
    height = int((max(zs) - origin[1] + _PAD_M) * px_per_m)
    width = int((max(xs) - origin[0] + _PAD_M) * px_per_m)
    view = PlanView(np.full((height, width, 3), 255, np.uint8), origin, px_per_m)
    img = view.image

    def pts(points: Sequence[fp.Point]) -> NDArray[np.int32]:
        return np.array([view.to_pixel(p) for p in points], np.int32)

    cv2.fillPoly(img, [pts([(p.x, p.z) for p in scene.floor_polygon])], (240, 240, 232))
    frames = {w.id: f for w in scene.walls if (f := fp.wall_frame(w)) is not None}
    letters = wall_letters(scene)
    for wall_id, frame in frames.items():
        cv2.line(
            img, view.to_pixel(frame.point(0)), view.to_pixel(frame.point(frame.length)), _WALL, 3
        )
    for window in scene.windows:
        on = frames.get(window.wall_id)
        if on is not None:
            a = on.point(window.offset_along_wall_m)
            b = on.point(window.offset_along_wall_m + window.width_m)
            cv2.line(img, view.to_pixel(a), view.to_pixel(b), _WINDOW, 7)
    for door in scene.doors:
        on = frames.get(door.wall_id)
        sweep = fp.door_sweep(door, on) if on is not None else None
        if sweep is not None:
            hinge, closed, opened = sweep.points[0], sweep.points[1], sweep.points[-1]
            cv2.polylines(img, [pts(sweep.points)], True, _DOOR, 1)
            cv2.line(img, view.to_pixel(hinge), view.to_pixel(closed), (255, 255, 255), 5)
            cv2.line(img, view.to_pixel(hinge), view.to_pixel(opened), _DOOR, 2)
    for wall_id, frame in frames.items():
        at = view.to_pixel(frame.point(frame.length / 2, -0.3))
        cv2.putText(
            img, letters[wall_id], (at[0] - 7, at[1] + 7), cv2.FONT_HERSHEY_SIMPLEX, 0.65, _LABEL, 2
        )
        cv2.circle(img, view.to_pixel(frame.point(min(0.12, frame.length / 4))), 5, _LABEL, -1)

    for ref in reference:
        outline = fp.footprint(ref.bbox_m, ref.pose).points
        cv2.polylines(img, [pts(outline)], True, (170, 170, 170), 1)
    for item in scene.furniture:
        record = (records or {}).get(item.id)
        uncertain = {"placement", "orientation"} & set(item.correction_needed)
        colour = _NO_FIT if record and not record.fits else _CONFIRM if uncertain else _SETTLED
        outline = fp.footprint(item.bbox_m, item.pose).points
        overlay = img.copy()
        cv2.fillPoly(overlay, [pts(outline)], colour)
        cv2.addWeighted(overlay, 0.45, img, 0.55, 0, dst=img)
        for part in fp.item_occupied(item):
            cv2.polylines(img, [pts(part.points)], True, colour, 1)
        cv2.polylines(img, [pts(outline)], True, (30, 30, 30), 1)
        front = fp.front_direction(item.pose.yaw_deg)
        reach = item.bbox_m.depth / 2
        centre = (item.pose.x, item.pose.z)
        tip = (centre[0] + front[0] * reach, centre[1] + front[1] * reach)
        cv2.line(img, view.to_pixel(centre), view.to_pixel(tip), (20, 20, 20), 2)
        label = item.name if label_names else item.id
        scale = 0.36
        (text_w, _), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, scale, 1)
        at = view.to_pixel(centre)
        left = min(max(2, at[0] - text_w // 2), max(2, width - text_w - 2))
        cv2.putText(img, label, (left, at[1] - 6), cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 0, 0), 1)
    return view
