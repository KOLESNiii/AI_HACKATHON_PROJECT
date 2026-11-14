"""fal vision proposes instances across full images; reviewed recordings run offline."""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Protocol

import cv2
from pydantic import ValidationError

from .registry import Registry
from .selection_models import Discovery, Frame, SelectedObject
from .video import crop, read_image

PROMPT_VERSION = "furniture-multi-image-v2"
PROMPT = """Identify separate PHYSICAL furniture objects in the video frames F0, F1, etc.
Return ONLY JSON: {"objects":[{"name":"...","category":"sofa","appearance":"...",
"reference_id":null,"uncertain":false,"reflection":false,
"sightings":[{"frame_key":"F0","box":{"x":0.1,"y":0.2,"width":0.3,"height":0.4}}]}],
"empty_frames":[],"warnings":[]}.
Categories: bed, desk, chair, table, wardrobe, sofa, storage, fixture, other.
Include furniture (including radiators), not people, doors/windows, plumbing or kitchen appliances.
Each object has one group across all its visible frames, with at most one sighting per frame.
FIRST inventory every distinct instance visible in each frame, THEN associate across frames.
Two sofas along different walls remain TWO groups even when both are brown and look identical.
Never use one group to represent alternating views of two distinct co-visible pieces of furniture.
Boxes are normalised 0..1 relative to the entire individual input image. There are NO collage tiles.
Use tight visible boxes; do not invent hidden parts. Account for every F frame
with sightings or its label in empty_frames. Furniture-free frames belong in empty_frames only.
The first inputs are individual F frames in order, followed by R reference crops in order.
R images show previously registered furniture. If you can confidently identify the SAME
physical object, set reference_id to that R label, otherwise null. Mere colour/category likeness
is insufficient. Use room context and distinctive structure. Do not group different lookalikes.
If identity is ambiguous, set uncertain=true and explain in warnings. Identify reflections as
reflection=true, rather than treating mirror images as separate real furniture.
Describe distinguishing position/context AND visible colour/material/structure in appearance.
Ignore appliances such as fridges even if they appear in later frames. No metric dimensions,
camera poses, meshes or invented exact floor-plan placement. Only F images need sightings.
Do not split an office chair's seat and back into separate items.
"""


class DiscoveryError(Exception):
    """Safe user-facing provider diagnostic; never reflects credentials or raw HTTP bodies."""


class DiscoveryProvider(Protocol):
    def discover(
        self,
        frames: list[Frame],
        references: list[SelectedObject],
        known_frames: dict[str, Frame],
        data_dir: Path,
        registry: Registry,
    ) -> Discovery: ...


class OfflineProvider:
    def discover(
        self,
        frames: list[Frame],
        references: list[SelectedObject],
        known_frames: dict[str, Frame],
        data_dir: Path,
        registry: Registry,
    ) -> Discovery:
        raise DiscoveryError("offline mode: frames retained; supply recorded detections or --live")


class RecordedProvider:
    """Reviewed detections keyed by full source frame keys, never by batch position."""

    def __init__(self, discovery: Discovery) -> None:
        self.discovery = discovery

    def discover(
        self,
        frames: list[Frame],
        references: list[SelectedObject],
        known_frames: dict[str, Frame],
        data_dir: Path,
        registry: Registry,
    ) -> Discovery:
        keys = {frame.key for frame in frames}
        objects = []
        for obj in self.discovery.objects:
            sightings = [s for s in obj.sightings if s.frame_key in keys]
            if not sightings:
                continue
            # Carry a track across batches using the registry's previously matched evidence.
            reference_id = obj.reference_id
            candidates = [
                ref.id
                for ref in references
                if any(
                    old.frame_key == sighting.frame_key and old.box == sighting.box
                    for old in ref.sightings
                    for sighting in obj.sightings
                )
            ]
            if reference_id is None and len(candidates) == 1:
                reference_id = candidates[0]
            objects.append(
                obj.model_copy(
                    update={
                        "sightings": sightings,
                        "reference_id": reference_id,
                    },
                    deep=True,
                )
            )
        return Discovery(
            objects=objects,
            empty_frames=[key for key in self.discovery.empty_frames if key in keys],
            warnings=self.discovery.warnings,
        )


def parse_discovery(
    output: str, frames: list[Frame], references: list[SelectedObject]
) -> Discovery:
    start, end = output.find("{"), output.rfind("}")
    if start < 0 or end <= start:
        raise DiscoveryError("vision response did not contain a JSON object")
    try:
        mapping = {f"F{i}": frame.key for i, frame in enumerate(frames)}
        refs = {f"R{i}": obj.id for i, obj in enumerate(references)}
        raw = json.loads(output[start : end + 1])
        for obj in raw.get("objects", []):
            reference = obj.get("reference_id")
            if reference is not None:
                obj["reference_id"] = refs[reference]
        discovery = Discovery.model_validate(raw)
        for obj in discovery.objects:
            for sighting in obj.sightings:
                sighting.frame_key = mapping[sighting.frame_key]
        discovery.empty_frames = [mapping[key] for key in discovery.empty_frames]
        discovery.validate_frames(set(mapping.values()))
        return discovery
    except (ValidationError, ValueError, KeyError, TypeError, AttributeError) as exc:
        raise DiscoveryError("invalid or incomplete furniture observations") from exc


class FalVisionProvider:
    def __init__(
        self,
        *,
        key: str,
        endpoint: str = "fal-ai/any-llm/vision",
        model: str = "google/gemini-2.5-flash",
        timeout_s: float = 120,
        refresh: str = "",
    ) -> None:
        if not key:
            raise ValueError("FAL_KEY is required for live discovery")
        if not 1 <= timeout_s <= 600:
            raise ValueError("provider timeout must be between 1 and 600 seconds")
        import fal_client

        self.client = fal_client.SyncClient(key=key, default_timeout=min(timeout_s, 30))
        self.endpoint, self.model, self.timeout_s, self.refresh = (
            endpoint,
            model,
            timeout_s,
            refresh,
        )

    def discover(
        self,
        frames: list[Frame],
        references: list[SelectedObject],
        known_frames: dict[str, Frame],
        data_dir: Path,
        registry: Registry,
    ) -> Discovery:
        if len(references) > 16:
            raise DiscoveryError("reference budget exceeded; narrow the room/range")
        # The original reference mapping is stored with the request. Retries must not change it.
        cache_key = hashlib.sha256(
            json.dumps(
                {
                    "frames": [f.key for f in frames],
                    "endpoint": self.endpoint,
                    "model": self.model,
                    "prompt": hashlib.sha256(PROMPT.encode()).hexdigest(),
                    "version": PROMPT_VERSION,
                    "refresh": self.refresh,
                },
                sort_keys=True,
            ).encode()
        ).hexdigest()
        winner, entry = registry.reserve_request(cache_key)
        if entry["status"] == "done":
            return Discovery.model_validate(entry["result"])
        if entry["status"] == "failed":
            raise DiscoveryError(
                "previous request failed; inspect report before an explicit refresh"
            )
        if not winner and entry["status"] == "reserved":
            raise DiscoveryError("submission pending/uncertain; will not risk a duplicate charge")
        import fal_client

        try:
            if winner:
                images = [read_image(data_dir, frame) for frame in frames]
                for obj in references:
                    primary = obj.selected_views[0]
                    sighting = next(s for s in obj.sightings if s.frame_key == primary)
                    images.append(crop(read_image(data_dir, known_frames[primary]), sighting.box))
                urls = []
                for image in images:
                    ok, encoded = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, 95])
                    if not ok:
                        raise DiscoveryError("could not encode discovery image")
                    urls.append(self.client.upload(encoded.tobytes(), "image/jpeg"))
                order = [f"F{i}" for i in range(len(frames))]
                order.extend(f"R{i} ({obj.category})" for i, obj in enumerate(references))
                handle = self.client.submit(
                    self.endpoint,
                    arguments={
                        "model": self.model,
                        "image_urls": urls,
                        "prompt": PROMPT + "\nInput image order: " + ", ".join(order),
                        "temperature": 0,
                        "max_tokens": 6000,
                    },
                )
                entry = {
                    "status": "submitted",
                    "request_id": handle.request_id,
                    "references": [obj.model_dump() for obj in references],
                }
                registry.save_request(cache_key, entry)
            else:
                handle = self.client.get_handle(self.endpoint, entry["request_id"])
                references = [SelectedObject.model_validate(obj) for obj in entry["references"]]
            deadline = time.monotonic() + self.timeout_s
            while time.monotonic() < deadline:
                if isinstance(handle.status(), fal_client.Completed):
                    result = handle.get()
                    if result.get("partial") or result.get("error"):
                        registry.save_request(cache_key, {"status": "failed"})
                        raise DiscoveryError("vision returned a partial/failed result")
                    try:
                        discovery = parse_discovery(
                            str(result.get("output", "")), frames, references
                        )
                    except DiscoveryError:
                        registry.save_request(cache_key, {"status": "failed"})
                        raise
                    discovery.warnings.append(
                        "AI inventory requires review: confirm distinct objects and cross-frame "
                        "associations; replay reviewed Discovery JSON with --recorded"
                    )
                    registry.save_request(
                        cache_key, {"status": "done", "result": discovery.model_dump()}
                    )
                    return discovery
                time.sleep(min(1, self.timeout_s))
            # Keep the handle: recovery can retrieve a completed result without resubmission.
            handle.cancel()
            raise DiscoveryError(
                "vision deadline exceeded; saved request can be recovered on retry"
            )
        except DiscoveryError:
            raise
        except Exception as exc:
            # Keep uncertain submissions/resumable handles. Never echo provider HTTP bodies.
            raise DiscoveryError(
                f"vision unavailable ({type(exc).__name__}); request state retained"
            ) from exc
