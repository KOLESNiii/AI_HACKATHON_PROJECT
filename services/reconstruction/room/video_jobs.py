"""Furniture extracted live from the walkthrough videos uploaded with a plan (fal.ai).

`POST /floor-plans` with videos starts one `ExtractionJob` per plan, in the background:

1. frame selection with fal vision proposals (`assets/selection.py`, #14),
2. SAM 3 instance masks (`assets/segmentation.py`, #15),
3. SAM 3D Objects meshes, normalised to metric size (`assets/reconstruction.py`, #16).

Until it finishes, every room of the plan is served without furniture, with a warning, the
`X-Furniture-Pending` header and `complete = False` (so the assembly is not kept and the next
`GET /scenes` asks again). Once done, a room's furniture is the job's items, placed by the fal
vision observer (`observe_vision.py`) from their evidence frames, flagged for correction where
it cannot tell. A failed job says why, and the room falls back to the usual source (reviewed
bindings, demo cache).

Assumption: the videos show the room the user builds. Nothing assigns items to rooms, so a
whole-home walkthrough puts every item it finds into whichever room is opened.

AI proposals are not reviewed here (the CLI's review step is skipped): the editor is where the
user corrects them. Provider requests are capped per job (`*_REQUESTS`); every stage caches its
paid results in the furniture data directory, so re-uploading the same videos is free.
"""

from __future__ import annotations

import hashlib
import logging
import os
import threading
import time
from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from contracts.schema import RoomScene
from services.reconstruction.assets.selection_models import SegmentationResult

from .assemble import FurnitureSource, SceneFurniture

log = logging.getLogger(__name__)

PENDING_HEADER = "X-Furniture-Pending"
PROGRESS_HEADER = "X-Furniture-Progress"
"""JSON `{step, steps, stage, elapsed_s}` while a room's furniture is being extracted."""
STEPS = 3

FRAMES_PER_VIDEO = 16
BATCH_SIZE = 8
MASK_REQUESTS = 32
MESH_REQUESTS = 12
MESH_CONCURRENCY = 4

State = Literal["running", "done", "failed"]


class ExtractionError(RuntimeError):
    """A reason safe to show the user (no keys, paths or provider bodies)."""


@dataclass
class ExtractionJob:
    plan_id: str
    namespace: str
    """The furniture registry's scene ID for these videos."""
    videos: list[Path]
    state: State = "running"
    stage: str = "starting"
    step: int = 0
    """1..STEPS once a stage has started."""
    started_at: float = field(default_factory=time.monotonic)
    warnings: list[str] = field(default_factory=list)
    error: str | None = None
    segmentation: SegmentationResult | None = None
    """Kept for the placement observer's evidence frames."""


Runner = Callable[[ExtractionJob, Path], None]


def namespace_for(plan_id: str, videos: Sequence[Path]) -> str:
    """Same plan and same videos (content-addressed names) -> same registry namespace."""
    digest = hashlib.sha256("\n".join(sorted(v.name for v in videos)).encode()).hexdigest()
    return f"upload-{plan_id}-{digest[:12]}"


def run_live(job: ExtractionJob, data_dir: Path) -> None:
    """The three paid stages, in order. Raises `ExtractionError` with a user-facing reason."""
    key = os.environ.get("FAL_KEY", "")
    if not key:
        raise ExtractionError("FAL_KEY is not set on the reconstruction service")
    # Imported here: fal-client and the pipeline's media stack are the reconstruction extra.
    from services.reconstruction.assets.mask_providers import FalSamProvider
    from services.reconstruction.assets.mesh_providers import FalSam3dProvider
    from services.reconstruction.assets.providers import FalVisionProvider
    from services.reconstruction.assets.reconstruction import reconstruct_furniture
    from services.reconstruction.assets.segmentation import segment_furniture
    from services.reconstruction.assets.selection import select_furniture_frames
    from services.reconstruction.assets.selection_models import SelectionOptions

    job.step, job.stage = 1, "finding furniture in the videos"
    batches = -(-FRAMES_PER_VIDEO // BATCH_SIZE) * len(job.videos)
    selection = select_furniture_frames(
        job.videos,
        job.namespace,
        data_dir=data_dir,
        provider=FalVisionProvider(
            key=key,
            endpoint=os.environ.get("FAL_VISION_ENDPOINT", "fal-ai/any-llm/vision"),
            model=os.environ.get("FAL_VISION_MODEL", "google/gemini-2.5-flash"),
        ),
        options=SelectionOptions(
            max_frames_per_video=FRAMES_PER_VIDEO,
            batch_size=BATCH_SIZE,
            max_requests=batches + 2,
            # The user uploaded these videos for one home: match items across them.
            room_key=job.plan_id,
        ),
    )
    if not selection.objects:
        raise ExtractionError("no furniture was found in the videos")
    job.step, job.stage = 2, f"cutting out {len(selection.objects)} items"
    job.segmentation = segment_furniture(
        job.namespace,
        data_dir=data_dir,
        provider=FalSamProvider(key=key),
        max_requests=MASK_REQUESTS,
    )
    job.step = 3
    job.stage = f"building 3D models of {len(selection.objects)} items (minutes per item)"
    result = reconstruct_furniture(
        job.namespace,
        data_dir=data_dir,
        provider=FalSam3dProvider(key=key),
        max_requests=MESH_REQUESTS,
        concurrency=MESH_CONCURRENCY,
    )
    if failed := [i.object_id for i in result.items if i.failure is not None]:
        job.warnings.append(f"no 3D model for {', '.join(failed)}: shown as sized boxes")


class Extractions:
    """The latest extraction job of each plan, run one at a time in a background thread."""

    def __init__(self, data_dir: Callable[[], Path], run: Runner = run_live) -> None:
        self._data_dir = data_dir
        self._run = run
        self._jobs: dict[str, ExtractionJob] = {}
        self._generations: dict[str, int] = {}
        """Per plan, bumped whenever a job starts: the plan's furniture source changed."""
        self._lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="extract")

    def start(self, plan_id: str, videos: Sequence[Path]) -> bool:
        """Start extracting these videos' furniture for the plan. False when the same videos
        are already being (or were) extracted for it; a failed job is started again."""
        namespace = namespace_for(plan_id, videos)
        with self._lock:
            job = self._jobs.get(plan_id)
            if job is not None and job.namespace == namespace and job.state != "failed":
                return False
            job = ExtractionJob(plan_id, namespace, list(videos))
            self._jobs[plan_id] = job
            self._generations[plan_id] = self._generations.get(plan_id, 0) + 1
        self._executor.submit(self._work, job)
        return True

    def _work(self, job: ExtractionJob) -> None:
        log.info("extracting furniture for %s (%d videos)", job.plan_id, len(job.videos))
        try:
            self._run(job, self._data_dir())
        except ExtractionError as exc:
            job.error, job.state = str(exc), "failed"
        except Exception as exc:  # a provider or media failure must not kill the worker
            log.exception("furniture extraction failed for %s", job.plan_id)
            job.error, job.state = f"the extraction stopped ({type(exc).__name__})", "failed"
        else:
            job.state = "done"
        log.info("furniture extraction for %s: %s", job.plan_id, job.state)

    def for_scene(self, scene_id: str) -> ExtractionJob | None:
        """The job of the plan this room belongs to (`<plan_id>-<room_id>`), if any."""
        with self._lock:
            return next((j for p, j in self._jobs.items() if scene_id.startswith(f"{p}-")), None)

    def generation(self, scene_id: str) -> int:
        """How often the furniture source of this room's plan has changed (0 = never).

        Read before assembling a room and again before keeping it: if it moved, the room was
        assembled from a source that no longer applies and must not be kept."""
        with self._lock:
            return next(
                (g for p, g in self._generations.items() if scene_id.startswith(f"{p}-")), 0
            )

    def pending(self, scene_id: str) -> bool:
        job = self.for_scene(scene_id)
        return job is not None and job.state == "running"

    def progress(self, scene_id: str) -> dict[str, object] | None:
        """Where the running extraction of this room's plan is, or None."""
        job = self.for_scene(scene_id)
        if job is None or job.state != "running":
            return None
        return {
            "step": job.step,
            "steps": STEPS,
            "stage": job.stage,
            "elapsed_s": round(time.monotonic() - job.started_at),
        }

    def clear(self) -> None:
        """Forget every job (tests). Running work finishes but is no longer served."""
        with self._lock:
            self._jobs.clear()


def extracting(stage: str) -> str:
    return (
        f"Extracting furniture from your videos ({stage}). It appears here when ready; "
        "this takes a few minutes."
    )


def extraction_failed(reason: str) -> str:
    return f"Furniture could not be extracted from your videos: {reason}."


class VideoFurniture:
    """Furniture for rooms of plans uploaded with videos; every other room uses `fallback`."""

    def __init__(self, jobs: Extractions, data_dir: Path, fallback: FurnitureSource) -> None:
        self.jobs = jobs
        self.data_dir = data_dir
        self.fallback = fallback

    def furniture_for(self, room: RoomScene) -> SceneFurniture:
        job = self.jobs.for_scene(room.scene_id)
        if job is None:
            return self.fallback.furniture_for(room)
        if job.state == "running":
            return SceneFurniture(
                assets=[], warnings=[extracting(job.stage)], complete=False, pending=True
            )
        if job.state == "failed":
            furniture = self.fallback.furniture_for(room)
            furniture.warnings.insert(0, extraction_failed(job.error or "unknown reason"))
            return furniture
        from services.reconstruction.assets.reconstruction import reconstruct_furniture

        from .observe_vision import FalVisionObserver, selection_frames, selection_masks

        # Offline: reads the meshes the job stored, normalised and checked, or proxies.
        result = reconstruct_furniture(job.namespace, data_dir=self.data_dir)
        assets = [item.asset or item.proxy for item in result.items]
        warnings = [*job.warnings, *result.warnings]
        if proxies := [a.id for a in assets if a.is_proxy]:
            warnings.append(f"sized boxes, no 3D model yet: {', '.join(proxies)}")
        return SceneFurniture(
            assets=assets,
            observer=FalVisionObserver(masks=selection_masks(self.data_dir)),
            frames=(
                selection_frames(job.segmentation, self.data_dir)
                if job.segmentation is not None
                else None
            ),
            warnings=warnings,
        )


EXTRACTIONS: Extractions | None = None


def extractions() -> Extractions:
    """The service's jobs (created on first use, so importing this starts no thread)."""
    global EXTRACTIONS
    if EXTRACTIONS is None:
        from services.reconstruction.config import furniture_data_dir

        EXTRACTIONS = Extractions(furniture_data_dir)
    return EXTRACTIONS
