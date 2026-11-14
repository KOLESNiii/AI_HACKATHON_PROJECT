"""Instance masks from item boxes (#15): local GrabCut offline, fal SAM 3 when asked."""

from __future__ import annotations

import hashlib
import json
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol
from urllib.parse import urlsplit

import cv2
import httpx
import numpy as np
from numpy.typing import NDArray

from .providers import DiscoveryError, RequestBudget
from .registry import Registry
from .selection_models import Box, Frame

Mask = NDArray[np.bool_]


class MaskError(Exception):
    """Safe user-facing provider diagnostic; never reflects credentials or raw HTTP bodies."""


@dataclass(frozen=True)
class Segment:
    pixels: Mask
    """Frame-sized; True = item."""
    score: float | None = None
    """The provider's confidence in 0..1, when it reports one."""


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
    ) -> list[Segment | None]:
        """One segment per box, in order; None where none was produced.

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
    ) -> list[Segment | None]:
        height, width = image.shape[:2]
        masks: list[Segment | None] = []
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
            masks.append(Segment((labels == cv2.GC_FGD) | (labels == cv2.GC_PR_FGD)))
        return masks


MAX_MASK_BYTES = 20_000_000
MAX_BOXES_PER_REQUEST = 32
"""`max_masks` limit of fal-ai/sam-3/image."""


class ArtifactTooLarge(Exception):
    """A provider artifact exceeded its size cap; nothing was kept."""


def fal_media_url(url: str) -> bool:
    """Provider artifacts are fetched over HTTPS from fal's media hosts only."""
    target = urlsplit(url)
    host = target.hostname or ""
    return target.scheme == "https" and (host == "fal.media" or host.endswith(".fal.media"))


def fetch_bounded(url: str, limit: int, *, timeout_s: float = 30) -> bytes:
    """Stream a provider artifact without redirects, enforcing `limit` while reading."""
    with httpx.stream("GET", url, timeout=timeout_s, follow_redirects=False) as response:
        response.raise_for_status()
        length = response.headers.get("Content-Length")
        if length is not None and int(length) > limit:
            raise ArtifactTooLarge
        data = bytearray()
        for chunk in response.iter_bytes():
            if len(data) + len(chunk) > limit:
                raise ArtifactTooLarge
            data.extend(chunk)
        return bytes(data)


def _fetch(url: str) -> bytes:
    try:
        return fetch_bounded(url, MAX_MASK_BYTES)
    except ArtifactTooLarge as exc:
        raise MaskError("mask artifact too large") from exc


class FalSamProvider:
    """fal SAM 3 image: every item box of one frame in one request (verified live 2026-11-14).

    Uploads the frame. Masks come back best score first as frame-sized 0/255 PNGs;
    `metadata[i].index` is the position of the prompt box that mask i answers.
    """

    method = "sam3"

    def __init__(
        self,
        *,
        key: str,
        endpoint: str = "fal-ai/sam-3/image",
        timeout_s: float = 120,
        refresh: str = "",
        fetch: Callable[[str], bytes] | None = None,
    ) -> None:
        if not key:
            raise ValueError("FAL_KEY is required for live segmentation")
        if not 1 <= timeout_s <= 600:
            raise ValueError("provider timeout must be between 1 and 600 seconds")
        import fal_client

        self.client = fal_client.SyncClient(key=key, default_timeout=min(timeout_s, 30))
        self.endpoint, self.timeout_s, self.refresh = endpoint, timeout_s, refresh
        self.fetch = fetch or _fetch

    def segment(
        self,
        frame: Frame,
        image: NDArray[np.uint8],
        boxes: list[Box],
        registry: Registry,
        *,
        budget: RequestBudget | None = None,
    ) -> list[Segment | None]:
        if not 1 <= len(boxes) <= MAX_BOXES_PER_REQUEST:
            raise MaskError(f"a frame needs 1..{MAX_BOXES_PER_REQUEST} item boxes per request")
        height, width = image.shape[:2]
        prompts = []
        for number, box in enumerate(boxes, 1):
            x0, y0, x1, y1 = box_pixels(box, width, height)
            prompts.append(
                {"x_min": x0, "y_min": y0, "x_max": x1, "y_max": y1, "object_id": number}
            )
        cache_key = hashlib.sha256(
            json.dumps(
                {
                    "frame": frame.key,
                    "boxes": prompts,
                    "endpoint": self.endpoint,
                    "refresh": self.refresh,
                },
                sort_keys=True,
            ).encode()
        ).hexdigest()
        winner, entry = registry.reserve_request(cache_key)
        if entry["status"] == "failed":
            raise MaskError("previous request failed; inspect it before an explicit refresh")
        if not winner and entry["status"] == "reserved":
            raise MaskError("submission pending/uncertain; will not risk a duplicate charge")
        import fal_client

        submit_started = False
        try:
            if winner:
                if budget is not None:
                    budget.check()
                ok, encoded = cv2.imencode(".png", image)
                if not ok:
                    raise MaskError("could not encode the source frame")
                url = self.client.upload(encoded.tobytes(), "image/png")
                if budget is not None:
                    budget.claim()
                submit_started = True
                handle = self.client.submit(
                    self.endpoint,
                    arguments={
                        "image_url": url,
                        "prompt": "",
                        "box_prompts": prompts,
                        "apply_mask": False,
                        "return_multiple_masks": True,
                        "max_masks": len(prompts),
                        "include_scores": True,
                        "output_format": "png",
                    },
                )
                registry.save_request(
                    cache_key, {"status": "submitted", "request_id": handle.request_id}
                )
            else:
                # A retry, or a replace, re-reads the paid result instead of submitting again.
                handle = self.client.get_handle(self.endpoint, entry["request_id"])
            deadline = time.monotonic() + self.timeout_s
            while not isinstance(handle.status(), fal_client.Completed):
                if time.monotonic() >= deadline:
                    raise MaskError(
                        "segmentation deadline exceeded; remote request still active and "
                        "recoverable on retry"
                    )
                time.sleep(min(1, self.timeout_s))
            result = handle.get()
            try:
                return self._masks(result, len(prompts), (height, width))
            except (KeyError, TypeError, ValueError, AttributeError) as exc:
                registry.save_request(cache_key, {"status": "failed"})
                raise MaskError("segmentation returned a malformed result") from exc
        except MaskError:
            raise
        except DiscoveryError as exc:  # The shared request budget's own safe message.
            raise MaskError(str(exc)) from exc
        except Exception as exc:
            # Keep uncertain submissions/resumable handles. Never echo provider HTTP bodies.
            recovery = (
                "safe to retry; no inference submitted"
                if winner and not submit_started
                else "request state retained"
            )
            raise MaskError(f"segmentation unavailable ({type(exc).__name__}); {recovery}") from exc
        finally:
            if winner and not submit_started:
                registry.release_reservation(cache_key)

    def _masks(self, result: Any, count: int, shape: tuple[int, int]) -> list[Segment | None]:
        files = result["masks"]
        if not isinstance(files, list):
            raise TypeError("masks")
        metadata = result.get("metadata")
        if metadata is None and count == 1 and len(files) == 1:
            metadata = [{"index": 0}]
        if not isinstance(metadata, list) or len(metadata) != len(files):
            raise ValueError("metadata")
        masks: list[Segment | None] = [None] * count
        for file, meta in zip(files, metadata, strict=True):
            index, url, score = meta["index"], file["url"], meta.get("score")
            if not isinstance(index, int) or not isinstance(url, str):
                raise TypeError("mask entry")
            if not isinstance(score, int | float) or not 0 <= score <= 1:
                score = None
            if not 0 <= index < count:
                raise ValueError("mask index")
            if masks[index] is not None:
                continue  # Best score first: keep the first usable mask for each box.
            if not fal_media_url(url):
                raise MaskError("mask artifact location not allowed")
            data = self.fetch(url)
            if len(data) > MAX_MASK_BYTES:
                raise MaskError("mask artifact too large")
            pixels = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_UNCHANGED)
            if pixels is None or pixels.shape[:2] != shape:
                continue  # Reported per item as "no mask returned".
            if pixels.ndim == 3:
                pixels = pixels[..., :3].max(axis=2)
            masks[index] = Segment(
                np.asarray(pixels > np.iinfo(pixels.dtype).max // 2),
                None if score is None else float(score),
            )
        return masks
