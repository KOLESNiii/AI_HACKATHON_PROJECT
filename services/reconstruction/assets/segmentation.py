"""Selected views -> stored per-item masks and cut-outs (#15). No meshes or poses (#16, #8)."""

from __future__ import annotations

import hashlib
import os
import tempfile
from collections.abc import Sequence
from pathlib import Path

import cv2
import numpy as np
from numpy.typing import NDArray

from .mask_providers import (
    GrabCutProvider,
    Mask,
    MaskError,
    MaskProvider,
    Segment,
    box_pixels,
)
from .providers import RequestBudget
from .registry import Registry
from .selection_models import (
    Box,
    Frame,
    MaskRecord,
    MissingMask,
    RegistryState,
    SegmentationResult,
)
from .video import read_image

MIN_MASK_AREA_PX = 16
MIN_BOX_AGREEMENT = 0.3
"""IoU of the mask's own bounding box with its prompt box. Reviewed boxes are coarse, so a
good mask may leave its box; the live probe gave 0.61-0.76 for correct masks and 0.22 for a
neighbouring item."""
OVERLAP_WARNING = 0.2


def read_mask(data_dir: Path, mask_url: str) -> Mask:
    """Resolve an `EvidenceFrame.mask_url` (relative to the asset data directory)."""
    root = data_dir.resolve()
    path = (root / mask_url).resolve()
    if not path.is_relative_to(root):
        raise ValueError("mask reference is outside the data directory")
    pixels = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if pixels is None:
        raise ValueError("mask artifact unavailable")
    return np.asarray(pixels > 127)


def _bounds(mask: Mask) -> tuple[int, int, int, int]:
    ys, xs = np.nonzero(mask)
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def _check(segment: Segment | None, box: Box, width: int, height: int) -> Segment:
    if segment is None:
        raise MaskError("no mask returned")
    mask = segment.pixels
    if mask.shape != (height, width):
        raise MaskError("mask size differs from its source frame")
    if int(mask.sum()) < MIN_MASK_AREA_PX:
        raise MaskError("empty mask")
    mx0, my0, mx1, my1 = _bounds(mask)
    bx0, by0, bx1, by1 = box_pixels(box, width, height)
    shared = max(0, min(mx1, bx1) - max(mx0, bx0)) * max(0, min(my1, by1) - max(my0, by0))
    union = (mx1 - mx0) * (my1 - my0) + (bx1 - bx0) * (by1 - by0) - shared
    if shared / union < MIN_BOX_AGREEMENT:
        raise MaskError("mask disagrees with the item's box")
    return segment


def _write(path: Path, image: NDArray[np.uint8]) -> None:
    ok, encoded = cv2.imencode(".png", image)
    if not ok:
        raise MaskError("could not encode mask artifact")
    path.parent.mkdir(parents=True, exist_ok=True)
    # Names carry the content digest, so an existing file is already the same bytes.
    handle, temporary = tempfile.mkstemp(dir=path.parent, suffix=".part")
    with os.fdopen(handle, "wb") as file:
        file.write(encoded.tobytes())
    os.replace(temporary, path)


def _store(
    data_dir: Path,
    folder: str,
    frame: Frame,
    image: NDArray[np.uint8],
    segment: Segment,
    box: Box,
    method: str,
) -> MaskRecord:
    mask = segment.pixels
    x0, y0, x1, y1 = _bounds(mask)
    pixels = mask.astype(np.uint8) * 255
    source, stream, ordinal = frame.key.rsplit(":", 2)
    digest = hashlib.sha256(pixels.tobytes()).hexdigest()[:10]
    stem = f"{folder}/{source[:12]}-{stream}-{ordinal}-{digest}"
    cutout = np.dstack([image[y0:y1, x0:x1], pixels[y0:y1, x0:x1]])
    _write(data_dir / f"{stem}.png", pixels)
    _write(data_dir / f"{stem}.crop.png", cutout)
    return MaskRecord.model_validate(
        {
            "frame_key": frame.key,
            "box": box,
            "method": method,
            "mask_path": f"{stem}.png",
            "crop_path": f"{stem}.crop.png",
            "bbox_px": (x0, y0, x1 - x0, y1 - y0),
            "area_px": int(mask.sum()),
            "score": segment.score,
        }
    )


def segment_furniture(
    scene_id: str,
    *,
    data_dir: Path,
    provider: MaskProvider | None = None,
    object_ids: Sequence[str] | None = None,
    replace: bool = False,
    max_requests: int = 16,
) -> SegmentationResult:
    """Store a mask and cut-out for every selected view of the scene's (or the named) items.

    Offline unless a live provider is passed. Stored masks are reused unless `replace`, their
    sighting box changed or either artifact is gone. Refuses to overwrite SAM 3 masks with
    approximate GrabCut masks (MaskError); pass a live provider to regenerate them.
    A failed or unusable mask is reported in `missing`; it never raises, never removes an
    item and never discards a stored mask.
    Unknown scenes/items raise ValueError.
    """
    if not scene_id.strip() or len(scene_id) > 200:
        raise ValueError("scene_id must contain 1..200 non-blank characters")
    provider = provider or GrabCutProvider()
    data_dir = data_dir.resolve()
    if not (data_dir / "registry.sqlite3").is_file():  # Never create one in a mistyped folder.
        raise ValueError("no furniture registry in the data directory; run frame selection first")
    registry = Registry(data_dir, namespace=scene_id)
    state = registry.load(scene_id)
    if not state.objects:
        raise ValueError("scene has no selected furniture; run frame selection first")
    wanted = sorted(state.objects) if object_ids is None else sorted(set(object_ids))
    if set(wanted) - state.objects.keys():
        raise ValueError("unknown object ID")
    folder = f"masks/{hashlib.sha256(scene_id.encode()).hexdigest()[:16]}"
    todo: dict[str, list[tuple[str, Box]]] = {}
    for object_id in wanted:
        obj = state.objects[object_id]
        for key in obj.selected_views:
            stored = obj.mask_for(key)
            if (
                replace
                or stored is None
                or not (data_dir / stored.mask_path).is_file()
                or not (data_dir / stored.crop_path).is_file()
            ):
                previous = next((m for m in obj.masks if m.frame_key == key), None)
                if (
                    previous is not None
                    and previous.method == "sam3"
                    and provider.method == "grabcut"
                ):
                    raise MaskError(
                        "refusing to replace stored SAM 3 masks with approximate GrabCut; "
                        "use --live to regenerate SAM 3 masks"
                    )
                box = next(s.box for s in obj.sightings if s.frame_key == key)
                todo.setdefault(key, []).append((object_id, box))
    budget = RequestBudget(max_requests)
    missing: list[MissingMask] = []
    warnings: list[str] = []
    for key in sorted(todo):
        frame, items = state.frames[key], todo[key]
        width, height = frame.image_size_px
        records: dict[str, MaskRecord] = {}
        try:
            image = read_image(data_dir, frame)
            if image.shape[:2] != (height, width):
                raise MaskError("frame artifact size differs from its record")
            masks = provider.segment(
                frame, image, [box for _, box in items], registry, budget=budget
            )
            if len(masks) != len(items):
                raise MaskError("provider did not return one mask per box")
        except (MaskError, ValueError) as exc:
            missing.extend(
                MissingMask(object_id=i, frame_key=key, reason=str(exc)) for i, _ in items
            )
            continue
        for (object_id, box), mask in zip(items, masks, strict=True):
            try:
                records[object_id] = _store(
                    data_dir,
                    f"{folder}/{object_id}",
                    frame,
                    image,
                    _check(mask, box, width, height),
                    box,
                    provider.method,
                )
            except MaskError as exc:
                missing.append(MissingMask(object_id=object_id, frame_key=key, reason=str(exc)))

        superseded: list[MaskRecord] = []

        def attach(
            state: RegistryState,
            key: str = key,
            records: dict[str, MaskRecord] = records,
        ) -> None:
            # Selection may have run meanwhile: attach only to a sighting that still matches.
            for object_id, record in records.items():
                current = state.objects.get(object_id)
                if current is None or not any(
                    s.frame_key == key and s.box == record.box for s in current.sightings
                ):
                    missing.append(
                        MissingMask(
                            object_id=object_id,
                            frame_key=key,
                            reason="selection changed during segmentation; run again",
                        )
                    )
                    continue
                superseded.extend(m for m in current.masks if m.frame_key == key)
                current.masks = sorted(
                    [m for m in current.masks if m.frame_key != key] + [record],
                    key=lambda m: m.frame_key,
                )

        if records:
            attached = registry.update(scene_id, attach)
            retained = {
                path
                for obj in attached.objects.values()
                for record in obj.masks
                for path in (record.mask_path, record.crop_path)
            }
            for record in superseded:
                for reference in (record.mask_path, record.crop_path):
                    path = (data_dir / reference).resolve()
                    # Delete only generated files after their replacement is committed.
                    if reference not in retained and path.is_relative_to(data_dir / folder):
                        try:
                            path.unlink(missing_ok=True)
                        except OSError:
                            warnings.append("could not remove a superseded mask artifact")
    state = registry.load(scene_id)
    objects = [state.objects[i] for i in wanted if i in state.objects]
    warnings.extend(_overlaps(data_dir, state, wanted))
    for obj in objects:
        for record in obj.masks:
            if obj.mask_for(record.frame_key) == record and record.low_confidence:
                frame = state.frames[record.frame_key]
                warnings.append(
                    f"low-confidence mask ({record.score:.2f}) for {obj.id} in source "
                    f"{frame.source_id[:12]} frame {frame.frame_index}; review its overlay"
                )
    if any(
        m.method == "grabcut" and obj.mask_for(m.frame_key) == m
        for obj in objects
        for m in obj.masks
    ):
        warnings.append(
            "local GrabCut masks are approximate and can include floor or an occluder; "
            "inspect the overlays or rerun with a live provider and replace"
        )
    used = {s.frame_key for obj in objects for s in obj.sightings}
    return SegmentationResult(
        scene_id=scene_id,
        registry_revision=state.revision,
        frames=[frame for key, frame in sorted(state.frames.items()) if key in used],
        objects=objects,
        missing=sorted(missing, key=lambda m: (m.object_id, m.frame_key)),
        warnings=warnings,
        complete=not missing,
    )


def _overlaps(data_dir: Path, state: RegistryState, wanted: list[str]) -> list[str]:
    """Masks of different items should not claim the same pixels; flag it, do not edit them."""
    by_frame: dict[str, list[tuple[str, Mask]]] = {}
    for obj in state.objects.values():
        for key in obj.selected_views:
            record = obj.mask_for(key)
            if record is None:
                continue
            try:
                by_frame.setdefault(key, []).append((obj.id, read_mask(data_dir, record.mask_path)))
            except ValueError:
                continue
    warnings = []
    for key, masks in sorted(by_frame.items()):
        for index, (first, a) in enumerate(masks):
            for second, b in masks[index + 1 :]:
                if first not in wanted and second not in wanted:
                    continue
                shared = int((a & b).sum())
                if shared > OVERLAP_WARNING * min(int(a.sum()), int(b.sum())):
                    frame = state.frames[key]
                    warnings.append(
                        f"masks overlap in source {frame.source_id[:12]} frame "
                        f"{frame.frame_index}: {first}, {second}"
                    )
    return warnings
