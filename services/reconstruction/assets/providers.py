"""fal vision proposes instances across full images; reviewed recordings run offline."""

from __future__ import annotations

import hashlib
import json
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol, get_args

import cv2
from pydantic import ValidationError

from .registry import Registry
from .selection_models import Category, Discovery, Frame, SelectedObject
from .video import crop, read_image

PROMPT_VERSION = "furniture-multi-image-v3"
PROMPT = """Identify separate PHYSICAL furniture objects in the video frames F0, F1, etc.
Return ONLY JSON: {"objects":[{"name":"...","category":"sofa","appearance":"...",
"reference_id":null,"uncertain":false,"reflection":false,
"sightings":[{"frame_key":"F0","box":{"x":0.1,"y":0.2,"width":0.3,"height":0.4}}]}],
"empty_frames":[],"warnings":[]}.
Categories: bed, desk, chair, table, wardrobe, sofa, storage, fixture, other.
Include movable furniture and radiators, not people, doors/windows, plumbing or kitchen appliances.
Use "fixture" ONLY for radiators. Do NOT include ceiling or wall lights, lamps fixed to walls,
stair railings, banisters, stairs, built-in kitchen units, wall-mounted cabinets, worktops,
curtains, blinds, rugs, pictures, mirrors on walls or anything built into the walls.
Never give a box covering (almost) the whole image: box only the visible object itself.
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


@dataclass
class RequestBudget:
    """Per-run inference submission attempts; cache reads and handle recovery are free."""

    limit: int
    used: int = 0
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False, compare=False)

    def check(self) -> None:
        if self.used >= self.limit:
            raise DiscoveryError("request budget exhausted; uncached batch deferred")

    def claim(self) -> None:
        with self._lock:  # #16 reconstructs items concurrently against one budget.
            self.check()
            self.used += 1


class DiscoveryProvider(Protocol):
    def discover(
        self,
        frames: list[Frame],
        references: list[SelectedObject],
        known_frames: dict[str, Frame],
        data_dir: Path,
        registry: Registry,
        *,
        budget: RequestBudget | None = None,
    ) -> Discovery: ...


class OfflineProvider:
    def discover(
        self,
        frames: list[Frame],
        references: list[SelectedObject],
        known_frames: dict[str, Frame],
        data_dir: Path,
        registry: Registry,
        *,
        budget: RequestBudget | None = None,
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
        *,
        budget: RequestBudget | None = None,
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


CATEGORIES = frozenset(get_args(Category))


def _lenient(raw: dict[str, Any], frame_labels: set[str], ref_labels: set[str]) -> list[str]:
    """Repair what a live answer commonly gets wrong instead of rejecting the batch: unknown
    categories become `other`, unknown references are dropped, sightings of unknown frames,
    repeated frames or unusable boxes are dropped (boxes are clipped to the image), objects
    left without sightings are dropped. Returns warnings saying what was repaired."""
    notes: list[str] = []
    objects = []
    for obj in raw.get("objects") or []:
        if not isinstance(obj, dict):
            continue
        if obj.get("category") not in CATEGORIES:
            obj["category"] = "other"
        if obj.get("reference_id") not in ref_labels:
            obj["reference_id"] = None
        obj["name"] = str(obj.get("name") or obj["category"])[:160]
        obj["appearance"] = str(obj.get("appearance") or obj["name"])[:1000]
        sightings, seen = [], set()
        for sighting in obj.get("sightings") or []:
            box = sighting.get("box") if isinstance(sighting, dict) else None
            key = sighting.get("frame_key") if isinstance(sighting, dict) else None
            if key not in frame_labels or key in seen or not isinstance(box, dict):
                continue
            try:
                x = min(max(float(box["x"]), 0.0), 0.999)
                y = min(max(float(box["y"]), 0.0), 0.999)
                w = min(float(box["width"]), 1.0 - x)
                h = min(float(box["height"]), 1.0 - y)
            except (KeyError, TypeError, ValueError):
                continue
            if w <= 0 or h <= 0:
                continue
            seen.add(key)
            sightings.append({**sighting, "box": {"x": x, "y": y, "width": w, "height": h}})
        if sightings:
            obj["sightings"] = sightings
            objects.append(obj)
    raw["objects"] = objects
    seen_frames = {s["frame_key"] for obj in objects for s in obj["sightings"]}
    empty = [k for k in raw.get("empty_frames") or [] if k in frame_labels and k not in seen_frames]
    missing = sorted(frame_labels - seen_frames - set(empty))
    if missing:
        notes.append(f"{len(missing)} frame(s) not accounted for by the model; taken as empty")
    raw["empty_frames"] = empty + missing
    return notes


def parse_discovery(
    output: str,
    frames: list[Frame],
    references: list[SelectedObject],
    *,
    lenient: bool = False,
) -> Discovery:
    """The model's answer as a `Discovery`. Strict by default (the reviewed CLI flow): any
    mistake rejects the batch. `lenient` repairs common mistakes instead (`_lenient`)."""
    start, end = output.find("{"), output.rfind("}")
    if start < 0 or end <= start:
        raise DiscoveryError("vision response did not contain a JSON object")
    try:
        mapping = {f"F{i}": frame.key for i, frame in enumerate(frames)}
        refs = {f"R{i}": obj.id for i, obj in enumerate(references)}
        raw = json.loads(output[start : end + 1])
        notes = _lenient(raw, set(mapping), set(refs)) if lenient else []
        for obj in raw.get("objects", []):
            reference = obj.get("reference_id")
            if reference is not None:
                obj["reference_id"] = refs[reference]
        discovery = Discovery.model_validate(raw)
        discovery.warnings.extend(notes)
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
        lenient: bool = False,
    ) -> None:
        """`lenient` repairs common answer mistakes instead of failing the batch
        (`parse_discovery`); the live server uses it, the reviewed CLI flow does not."""
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
        self.lenient = lenient

    def discover(
        self,
        frames: list[Frame],
        references: list[SelectedObject],
        known_frames: dict[str, Frame],
        data_dir: Path,
        registry: Registry,
        *,
        budget: RequestBudget | None = None,
    ) -> Discovery:
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
                    # A strict failure must not block a lenient retry of the same frames.
                    "lenient": self.lenient,
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

        submit_started = False
        try:
            if winner:
                if budget is not None:
                    budget.check()

                # A large registry must not block a new batch or invalidate a cached result.
                # Prefer references nearest in time within the same source; keep input order
                # fixed in the saved handle so later retries retain the original R mapping.
                def proximity(obj: SelectedObject) -> tuple[float, str]:
                    distances = [
                        abs(known_frames[s.frame_key].timestamp_s - frame.timestamp_s)
                        for s in obj.sightings
                        for frame in frames
                        if known_frames[s.frame_key].source_id == frame.source_id
                    ]
                    return min(distances, default=float("inf")), obj.id

                omitted = max(0, len(references) - 16)
                references = sorted(references, key=proximity)[:16]
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
                if budget is not None:
                    budget.claim()
                submit_started = True
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
                    "omitted_references": omitted,
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
                            str(result.get("output", "")),
                            frames,
                            references,
                            lenient=self.lenient,
                        )
                    except DiscoveryError:
                        registry.save_request(cache_key, {"status": "failed"})
                        raise
                    discovery.warnings.append(
                        "AI inventory requires review: confirm distinct objects and cross-frame "
                        "associations; replay reviewed Discovery JSON with --recorded"
                    )
                    if entry.get("omitted_references", 0):
                        discovery.warnings.append(
                            f"reference context limited to 16 items; "
                            f"{entry['omitted_references']} more require identity review"
                        )
                    registry.save_request(
                        cache_key, {"status": "done", "result": discovery.model_dump()}
                    )
                    return discovery
                time.sleep(min(1, self.timeout_s))
            # A local wait deadline does not cancel remote work: a later run can retrieve it.
            raise DiscoveryError(
                "vision deadline exceeded; remote request still active and recoverable on retry"
            )
        except DiscoveryError:
            raise
        except Exception as exc:
            # Keep uncertain submissions/resumable handles. Never echo provider HTTP bodies.
            recovery = (
                "safe to retry; no inference submitted"
                if winner and not submit_started
                else "request state retained"
            )
            raise DiscoveryError(f"vision unavailable ({type(exc).__name__}); {recovery}") from exc
        finally:
            if winner and not submit_started:
                registry.release_reservation(cache_key)
