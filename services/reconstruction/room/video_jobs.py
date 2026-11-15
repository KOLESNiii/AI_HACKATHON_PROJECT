"""Furniture extracted live from the walkthrough videos uploaded with a plan (fal.ai).

`POST /floor-plans` with videos starts one `ExtractionJob` per plan, in the background:

1. frame selection with fal vision proposals (`assets/selection.py`, #14), read leniently;
2. matching every sampled frame, then every item, to a plan room (`room_frames.py`);
3. SAM 3 instance masks of the items matched to a room (`assets/segmentation.py`, #15);
4. per room, when it is first opened: SAM 3D Objects meshes of its items, normalised to
   metric size (`assets/reconstruction.py`, #16). Only rooms the user opens cost mesh time.

Until a room's furniture is ready it is served without furniture, with a warning, the
`X-Furniture-Pending` header and `complete = False` (so the assembly is not kept and the next
`GET /scenes` asks again). Then the room's items are placed by the fal vision observer
(`observe_vision.py`) from their evidence frames, flagged for correction where it cannot tell.
A failed job says why, and the room falls back to the usual source (reviewed bindings, demo
cache).

AI proposals are not reviewed here (the CLI's review step is skipped): the editor is where the
user corrects them. Provider requests are capped (`*_REQUESTS`); every stage caches its paid
results in the furniture data directory, so re-uploading the same videos is free.
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

from contracts.schema import ParsedFloorPlan, RoomScene
from services.reconstruction.assets.selection_models import (
    SegmentationResult,
    SelectedObject,
    SelectionResult,
)

from .assemble import FurnitureSource, SceneFurniture

log = logging.getLogger(__name__)

PENDING_HEADER = "X-Furniture-Pending"
PROGRESS_HEADER = "X-Furniture-Progress"
"""JSON `{step, steps, stage, elapsed_s}` while a room's furniture is being extracted."""
STEPS = 4

FRAMES_PER_VIDEO = 32
"""Whole-home walkthroughs visit many rooms: sample densely enough to see each."""
BATCH_SIZE = 4
"""Frames per discovery request: the reviewed CLI's default; larger batches fail more often."""
DISCOVERY_TIMEOUT_S = 300
MASK_REQUESTS = 48
MESH_REQUESTS_PER_ROOM = 8
MESH_CONCURRENCY = 4
FULL_FRAME_AREA = 0.85
"""An item boxed this large in every sighting is the whole view, not an object."""

State = Literal["running", "done", "failed"]
MeshState = Literal["queued", "running", "done", "failed"]


class ExtractionError(RuntimeError):
    """A reason safe to show the user (no keys, paths or provider bodies)."""


@dataclass
class RoomMeshes:
    object_ids: list[str]
    state: MeshState = "queued"
    started_at: float = field(default_factory=time.monotonic)
    error: str | None = None


@dataclass
class ExtractionJob:
    plan_id: str
    namespace: str
    """The furniture registry's scene ID for these videos."""
    videos: list[Path]
    plan: ParsedFloorPlan | None = None
    """The plan the videos were uploaded with: its rooms are what items are matched to."""
    state: State = "running"
    stage: str = "starting"
    step: int = 0
    """1..STEPS once a stage has started."""
    started_at: float = field(default_factory=time.monotonic)
    warnings: list[str] = field(default_factory=list)
    error: str | None = None
    segmentation: SegmentationResult | None = None
    """Kept for the placement observer's evidence frames."""
    rooms: dict[str, str | None] = field(default_factory=dict)
    """Object ID -> room ID it was matched to (None: seen, but not matched to a room)."""
    names: dict[str, str] = field(default_factory=dict)
    """Object ID -> its name, for warnings."""
    meshes: dict[str, RoomMeshes] = field(default_factory=dict)
    """Room ID -> its 3D model build, started when the room is first opened."""

    def room_name(self, room_id: str) -> str:
        for floor in self.plan.floors if self.plan else []:
            for room in floor.rooms:
                if room.room_id == room_id:
                    return room.name
        return room_id

    def items_in(self, room_id: str) -> list[str]:
        return sorted(obj for obj, room in self.rooms.items() if room == room_id)

    def unassigned(self) -> list[str]:
        return sorted(self.names.get(obj, obj) for obj, room in self.rooms.items() if room is None)


Runner = Callable[[ExtractionJob, Path], None]
MeshRunner = Callable[[ExtractionJob, str, list[str], Path], None]
"""(job, room ID, object IDs, data dir): build those items' meshes."""


def namespace_for(plan_id: str, videos: Sequence[Path]) -> str:
    """Same plan and same videos (content-addressed names) -> same registry namespace."""
    digest = hashlib.sha256("\n".join(sorted(v.name for v in videos)).encode()).hexdigest()
    return f"upload-{plan_id}-{digest[:12]}"


def batch_failures(selection: SelectionResult) -> tuple[int, int]:
    """(failed, total) discovery batches of a selection run."""
    per_source: dict[str, int] = {}
    for frame in selection.frames:
        per_source[frame.source_id] = per_source.get(frame.source_id, 0) + 1
    total = sum(-(-n // BATCH_SIZE) for n in per_source.values())
    failed = len({w.split(":", 1)[0] for w in selection.warnings if w.startswith("batch ")})
    return failed, total


def whole_view(obj: SelectedObject) -> bool:
    return all(s.box.width * s.box.height >= FULL_FRAME_AREA for s in obj.sightings)


def run_live(job: ExtractionJob, data_dir: Path) -> None:
    """Stages 1-3 (find, match to rooms, cut out). Raises `ExtractionError` with a
    user-facing reason."""
    key = os.environ.get("FAL_KEY", "")
    if not key:
        raise ExtractionError("FAL_KEY is not set on the reconstruction service")
    if job.plan is None:
        raise ExtractionError("the plan of these videos is unknown; upload them with the plan")
    # Imported here: fal-client and the pipeline's media stack are the reconstruction extra.
    from services.reconstruction.assets.mask_providers import FalSamProvider
    from services.reconstruction.assets.providers import FalVisionProvider
    from services.reconstruction.assets.segmentation import segment_furniture
    from services.reconstruction.assets.selection import select_furniture_frames
    from services.reconstruction.assets.selection_models import SelectionOptions

    from .room_frames import FalRoomClassifier

    job.step, job.stage = 1, "finding furniture in the videos"
    provider = FalVisionProvider(
        key=key,
        endpoint=os.environ.get("FAL_VISION_ENDPOINT", "fal-ai/any-llm/vision"),
        model=os.environ.get("FAL_VISION_MODEL", "google/gemini-2.5-flash"),
        timeout_s=DISCOVERY_TIMEOUT_S,
        lenient=True,
    )
    batches = -(-FRAMES_PER_VIDEO // BATCH_SIZE) * len(job.videos)
    options = SelectionOptions(
        max_frames_per_video=FRAMES_PER_VIDEO,
        batch_size=BATCH_SIZE,
        max_requests=min(100, batches + 4),
        # The user uploaded these videos for one home: match items across them.
        room_key=job.plan_id,
    )
    selection = select_furniture_frames(
        job.videos, job.namespace, data_dir=data_dir, provider=provider, options=options
    )
    if batch_failures(selection)[0]:
        # Free: cached answers are re-read and requests still running remotely are collected.
        selection = select_furniture_frames(
            job.videos, job.namespace, data_dir=data_dir, provider=provider, options=options
        )
    failed, total = batch_failures(selection)
    if total and failed == total:
        raise ExtractionError("the vision model could not read any frames of the videos")
    if failed:
        job.warnings.append(
            f"{failed} of {total} frame batches could not be read; some furniture may be missing"
        )
    objects = [o for o in selection.objects if not whole_view(o)]
    if dropped := len(selection.objects) - len(objects):
        job.warnings.append(f"{dropped} item(s) boxed as the whole view were left out")
    if not objects:
        raise ExtractionError("no furniture was found in the videos")
    job.names = {o.id: o.name for o in objects}

    job.step, job.stage = 2, f"matching {len(objects)} items to the plan's rooms"
    assignment = FalRoomClassifier().assign(job.plan, selection.frames, objects, data_dir)
    job.warnings += assignment.warnings
    job.rooms = assignment.item_rooms
    assigned = sorted(obj for obj, room in job.rooms.items() if room is not None)
    if not assigned:
        raise ExtractionError("none of the furniture could be matched to a room of the plan")

    job.step, job.stage = 3, f"cutting out {len(assigned)} items"
    job.segmentation = segment_furniture(
        job.namespace,
        data_dir=data_dir,
        provider=FalSamProvider(key=key),
        object_ids=assigned,
        max_requests=MASK_REQUESTS,
    )


def mesh_live(job: ExtractionJob, room_id: str, object_ids: list[str], data_dir: Path) -> None:
    """Stage 4 for one room: its items' meshes."""
    key = os.environ.get("FAL_KEY", "")
    if not key:
        raise ExtractionError("FAL_KEY is not set on the reconstruction service")
    from services.reconstruction.assets.mesh_providers import FalSam3dProvider
    from services.reconstruction.assets.reconstruction import reconstruct_furniture

    result = reconstruct_furniture(
        job.namespace,
        data_dir=data_dir,
        provider=FalSam3dProvider(key=key),
        object_ids=object_ids,
        max_requests=MESH_REQUESTS_PER_ROOM,
        concurrency=MESH_CONCURRENCY,
    )
    if failed := [i.object_id for i in result.items if i.failure is not None]:
        names = ", ".join(job.names.get(o, o) for o in failed)
        job.warnings.append(f"no 3D model for {names}: shown as sized boxes")


class Extractions:
    """The latest extraction job of each plan. Jobs and room mesh builds run one at a time in a
    background thread, in the order they were asked for."""

    def __init__(
        self, data_dir: Callable[[], Path], run: Runner = run_live, mesh: MeshRunner = mesh_live
    ) -> None:
        self._data_dir = data_dir
        self._run = run
        self._mesh = mesh
        self._jobs: dict[str, ExtractionJob] = {}
        self._generations: dict[str, int] = {}
        """Per plan, bumped whenever a job starts: the plan's furniture source changed."""
        self._lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="extract")

    def start(
        self, plan_id: str, videos: Sequence[Path], plan: ParsedFloorPlan | None = None
    ) -> bool:
        """Start extracting these videos' furniture for the plan. False when the same videos
        are already being (or were) extracted for it; a failed job is started again."""
        namespace = namespace_for(plan_id, videos)
        with self._lock:
            job = self._jobs.get(plan_id)
            if job is not None and job.namespace == namespace and job.state != "failed":
                return False
            job = ExtractionJob(plan_id, namespace, list(videos), plan)
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

    def mesh_room(self, job: ExtractionJob, room_id: str) -> RoomMeshes:
        """The room's mesh build, queued now if this is the first time it is asked for."""
        with self._lock:
            build = job.meshes.get(room_id)
            if build is None:
                build = RoomMeshes(job.items_in(room_id))
                job.meshes[room_id] = build
                self._executor.submit(self._build, job, room_id, build)
            return build

    def _build(self, job: ExtractionJob, room_id: str, build: RoomMeshes) -> None:
        build.state, build.started_at = "running", time.monotonic()
        try:
            self._mesh(job, room_id, build.object_ids, self._data_dir())
        except ExtractionError as exc:
            build.error, build.state = str(exc), "failed"
        except Exception as exc:  # the room still gets its items as sized boxes
            log.exception("mesh build failed for %s %s", job.plan_id, room_id)
            build.error, build.state = f"the 3D models stopped ({type(exc).__name__})", "failed"
        else:
            build.state = "done"

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

    def _build_for(self, scene_id: str) -> tuple[ExtractionJob, str, RoomMeshes | None] | None:
        job = self.for_scene(scene_id)
        if job is None:
            return None
        room_id = scene_id[len(job.plan_id) + 1 :]
        return job, room_id, job.meshes.get(room_id)

    def pending(self, scene_id: str) -> bool:
        """Whether this room's furniture is still being extracted."""
        found = self._build_for(scene_id)
        if found is None:
            return False
        job, _, build = found
        if job.state == "running":
            return True
        return job.state == "done" and build is not None and build.state in ("queued", "running")

    def progress(self, scene_id: str) -> dict[str, object] | None:
        """Where the extraction of this room's furniture is, or None when it is not running."""
        found = self._build_for(scene_id)
        if found is None:
            return None
        job, room_id, build = found
        if job.state == "running":
            step, stage, since = job.step, job.stage, job.started_at
        elif job.state == "done" and build is not None and build.state in ("queued", "running"):
            count, name = len(build.object_ids), job.room_name(room_id)
            verb = "building" if build.state == "running" else "waiting to build"
            step, stage, since = 4, f"{verb} 3D models of {count} items in {name}", job.started_at
        else:
            return None
        return {
            "step": step,
            "steps": STEPS,
            "stage": stage,
            "elapsed_s": round(time.monotonic() - since),
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


NOTHING_SEEN = "No furniture from your videos was matched to this room."


def unmatched(names: Sequence[str]) -> str:
    return f"Seen in your videos but not matched to a room: {', '.join(names)}."


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
        room_id = room.scene_id[len(job.plan_id) + 1 :]
        notes = [unmatched(job.unassigned())] if job.unassigned() else []
        if not job.items_in(room_id):
            return SceneFurniture(assets=[], warnings=[NOTHING_SEEN, *notes])
        build = self.jobs.mesh_room(job, room_id)
        if build.state in ("queued", "running"):
            stage = self.jobs.progress(room.scene_id) or {"stage": "building 3D models"}
            return SceneFurniture(
                assets=[],
                warnings=[extracting(str(stage["stage"]))],
                complete=False,
                pending=True,
            )
        from services.reconstruction.assets.reconstruction import reconstruct_furniture

        from .observe_vision import FalVisionObserver, selection_frames, selection_masks

        # Offline: reads the meshes the build stored, normalised and checked, or proxies.
        result = reconstruct_furniture(
            job.namespace, data_dir=self.data_dir, object_ids=build.object_ids
        )
        assets = [item.asset or item.proxy for item in result.items]
        warnings = [*job.warnings, *result.warnings, *notes]
        if build.error:
            warnings.append(f"3D models: {build.error}")
        if proxies := [job.names.get(a.id, a.id) for a in assets if a.is_proxy]:
            warnings.append(f"sized boxes, no 3D model: {', '.join(proxies)}")
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
