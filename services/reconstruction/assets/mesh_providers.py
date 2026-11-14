"""One raw mesh per furniture item (#16), from a source frame and the item's #15 mask.

There is no offline mesh generator: without a live provider an item is reported as not
attempted and keeps its proxy.
"""

from __future__ import annotations

import hashlib
import io
import json
import math
import struct
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol

import cv2
import numpy as np
import trimesh
from numpy.typing import NDArray

from .mask_providers import ArtifactTooLarge, Mask, fal_media_url, fetch_bounded
from .providers import DiscoveryError, RequestBudget
from .registry import Registry
from .selection_models import FailureKind, Frame

MAX_MESH_BYTES = 20_000_000
"""The live probe returned 1.3 MB for one textured object."""
MAX_POSE_CHARS = 20_000


class MeshError(Exception):
    """Safe user-facing provider diagnostic; never reflects credentials or raw HTTP bodies."""

    def __init__(self, message: str, *, kind: FailureKind = "provider") -> None:
        super().__init__(message)
        self.kind: FailureKind = kind


@dataclass(frozen=True)
class RawMesh:
    glb: bytes
    """glTF 2.0 binary exactly as the provider returned it: its own frame and scale."""
    pose: dict[str, Any] | None = None
    """The provider's per-object metadata, kept verbatim as placement evidence."""


class MeshProvider(Protocol):
    name: str
    """Recorded on every mesh it produces: "sam3d"."""

    def reconstruct(
        self,
        frame: Frame,
        image: NDArray[np.uint8],
        mask: Mask,
        registry: Registry,
        *,
        budget: RequestBudget | None = None,
    ) -> RawMesh:
        """The mesh of the one item `mask` marks in `image`. Raises only MeshError.

        Called from several threads at once, one call per item.
        """
        ...


def _fetch(url: str) -> bytes:
    try:
        return fetch_bounded(url, MAX_MESH_BYTES, timeout_s=60)
    except ArtifactTooLarge as exc:
        raise MeshError("mesh artifact too large", kind="invalid_mesh") from exc


SAM3D_ARGUMENTS = {"export_textured_glb": True, "seed": 0}
"""Textures and UVs instead of vertex colours; a fixed seed so a paid refresh is comparable."""
POSE_FIELDS = ("object_index", "scale", "rotation", "translation", "camera_pose")


def inspect_mesh(glb: bytes) -> tuple[int, tuple[float, float, float]]:
    """(triangles, extents) of a usable glTF 2.0 binary; MeshError("invalid_mesh") otherwise."""
    if len(glb) > MAX_MESH_BYTES:
        raise MeshError("mesh artifact too large", kind="invalid_mesh")
    if len(glb) < 20 or glb[:4] != b"glTF" or struct.unpack("<II", glb[4:12]) != (2, len(glb)):
        raise MeshError("provider did not return a complete glTF 2.0 binary", kind="invalid_mesh")
    try:
        scene = trimesh.load_scene(io.BytesIO(glb), file_type="glb")
        triangles = sum(
            len(geometry.faces)
            for geometry in scene.geometry.values()
            if isinstance(geometry, trimesh.Trimesh)
        )
        extents = None if scene.extents is None else [float(side) for side in scene.extents]
    except Exception as exc:  # An untrusted file: any parser failure means the same thing.
        raise MeshError("provider mesh could not be parsed", kind="invalid_mesh") from exc
    if (
        triangles < 1
        or extents is None
        or len(extents) != 3
        or not all(math.isfinite(side) and side > 1e-6 for side in extents)
    ):
        raise MeshError("provider mesh has no usable geometry", kind="invalid_mesh")
    return triangles, (extents[0], extents[1], extents[2])


class FalSam3dProvider:
    """fal SAM 3D Objects: one frame and one item mask per request (verified live 2026-11-14).

    Uploads the frame and the mask. `model_glb` is a textured glTF 2.0 binary centred on the
    origin with its longest side about 1 unit; `metadata[0]` holds the provider's own scale,
    rotation (quaternion) and translation for the object. One object took 170 s.
    """

    name = "sam3d"

    def __init__(
        self,
        *,
        key: str,
        endpoint: str = "fal-ai/sam-3/3d-objects",
        timeout_s: float = 420,
        refresh: str = "",
        fetch: Callable[[str], bytes] | None = None,
    ) -> None:
        if not key:
            raise ValueError("FAL_KEY is required for live reconstruction")
        if not 1 <= timeout_s <= 600:
            raise ValueError("provider timeout must be between 1 and 600 seconds")
        import fal_client

        self.client = fal_client.SyncClient(key=key, default_timeout=min(timeout_s, 30))
        self.endpoint, self.timeout_s, self.refresh = endpoint, timeout_s, refresh
        self.fetch = fetch or _fetch

    def reconstruct(
        self,
        frame: Frame,
        image: NDArray[np.uint8],
        mask: Mask,
        registry: Registry,
        *,
        budget: RequestBudget | None = None,
    ) -> RawMesh:
        if mask.shape != image.shape[:2] or not mask.any():
            raise MeshError("mask does not match its source frame", kind="no_view")
        image_ok, image_png = cv2.imencode(".png", image)
        mask_ok, mask_png = cv2.imencode(".png", mask.astype(np.uint8) * 255)
        if not image_ok or not mask_ok:
            raise MeshError("could not encode the source frame or its mask")
        cache_key = hashlib.sha256(
            json.dumps(
                {
                    "frame": frame.key,
                    "mask": hashlib.sha256(mask_png.tobytes()).hexdigest(),
                    "endpoint": self.endpoint,
                    "arguments": SAM3D_ARGUMENTS,
                    "refresh": self.refresh,
                },
                sort_keys=True,
            ).encode()
        ).hexdigest()
        winner, entry = registry.reserve_request(cache_key)
        if entry["status"] == "failed":
            raise MeshError(
                "previous request failed; use --refresh with a new namespace for a paid retry"
            )
        if not winner and entry["status"] == "reserved":
            raise MeshError("submission pending/uncertain; will not risk a duplicate charge")
        import fal_client

        submit_started = False
        try:
            if winner:
                if budget is not None:
                    budget.check()
                image_url = self.client.upload(image_png.tobytes(), "image/png")
                mask_url = self.client.upload(mask_png.tobytes(), "image/png")
                if budget is not None:
                    budget.claim()
                submit_started = True
                handle = self.client.submit(
                    self.endpoint,
                    arguments={"image_url": image_url, "mask_urls": [mask_url], **SAM3D_ARGUMENTS},
                )
                registry.save_request(
                    cache_key, {"status": "submitted", "request_id": handle.request_id}
                )
            else:
                # A retry, or a replace, re-reads the paid result instead of submitting again.
                handle = self.client.get_handle(self.endpoint, entry["request_id"])
            deadline = time.monotonic() + self.timeout_s
            while True:
                status = handle.status()
                if isinstance(status, fal_client.Completed):
                    break
                if time.monotonic() >= deadline:
                    raise MeshError(
                        "reconstruction deadline exceeded; remote request still active and "
                        "collected by the next run without a new charge",
                        kind="timeout",
                    )
                time.sleep(min(2, self.timeout_s))
            if status.error is not None:
                registry.save_request(cache_key, {"status": "failed"})
                raise MeshError(
                    "remote reconstruction failed; use --refresh with a new namespace "
                    "for a paid retry"
                )
            result = handle.get()
            try:
                url, pose = self._parse(result)
                glb = self.fetch(url)
                inspect_mesh(glb)
            except (MeshError, KeyError, TypeError, ValueError, AttributeError, IndexError) as exc:
                registry.save_request(cache_key, {"status": "failed"})
                reason = (
                    str(exc)
                    if isinstance(exc, MeshError)
                    else "reconstruction returned a malformed result"
                )
                raise MeshError(
                    f"{reason}; use --refresh with a new namespace for a paid retry",
                    kind=exc.kind if isinstance(exc, MeshError) else "invalid_mesh",
                ) from exc
            return RawMesh(glb, pose)
        except MeshError:
            raise
        except DiscoveryError as exc:  # The shared request budget's own safe message.
            raise MeshError(str(exc), kind="budget") from exc
        except Exception as exc:
            # Keep uncertain submissions/resumable handles. Never echo provider HTTP bodies.
            recovery = (
                "safe to retry; no inference submitted"
                if winner and not submit_started
                else "request state retained"
            )
            raise MeshError(
                f"reconstruction unavailable ({type(exc).__name__}); {recovery}"
            ) from exc
        finally:
            if winner and not submit_started:
                registry.release_reservation(cache_key)

    def _parse(self, result: Any) -> tuple[str, dict[str, Any] | None]:
        url = result["model_glb"]["url"]
        if not isinstance(url, str):
            raise TypeError("model_glb")
        if not fal_media_url(url):
            raise MeshError("mesh artifact location not allowed")
        metadata = result.get("metadata")
        entry = metadata[0] if isinstance(metadata, list) and metadata else None
        if not isinstance(entry, dict):
            return url, None
        try:
            # Evidence must survive the registry's JSON snapshot unchanged.
            text = json.dumps({k: entry[k] for k in POSE_FIELDS if k in entry}, allow_nan=False)
        except (TypeError, ValueError):
            return url, None
        pose = json.loads(text) if len(text) <= MAX_POSE_CHARS else None
        return url, pose or None
