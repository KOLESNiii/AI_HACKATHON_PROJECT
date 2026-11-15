"""Furniture extracted live from the walkthrough videos uploaded with a plan (fal.ai).

`POST /floor-plans` with videos starts one `ExtractionJob` per plan, in the background. The
videos are cut up by room so that most of the work runs in parallel:

1. every video is sampled (FFmpeg), one thread per video;
2. every sampled frame is matched to a plan room (`room_frames.py`), all chunks at once;
3. each room's frames are searched for furniture (`assets/selection.discover_frames`, read
   leniently) and its items cut out (SAM 3 masks), all rooms at once. Batches within a room
   stay in order, so the same sofa seen twice is one item; different rooms hold different
   objects, so rooms cannot duplicate each other. Each room has its own registry namespace;
4. a room's SAM 3D meshes are built when it is first opened, as soon as that room has
   finished step 3. Only rooms the user opens cost mesh time.

Until a room's furniture is ready it is served without furniture, with a warning, the
`X-Furniture-Pending` header and `complete = False` (so the assembly is not kept and the next
`GET /scenes` asks again). Then the room's items are placed by the fal vision observer
(`observe_vision.py`) from their evidence frames, flagged for correction where it cannot tell.
A failed job or room says why, and the room falls back to the usual source (reviewed
bindings, demo cache).

AI proposals are not reviewed here (the CLI's review step is skipped): the editor is where the
user corrects them. Provider requests are capped per room; every stage caches its paid results
in the furniture data directory, so re-uploading the same videos is free.
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
    Frame,
    SegmentationResult,
    SelectedObject,
    SelectionResult,
    SourceVideo,
)

from .assemble import FurnitureSource, SceneFurniture

log = logging.getLogger(__name__)

PENDING_HEADER = "X-Furniture-Pending"
PROGRESS_HEADER = "X-Furniture-Progress"
"""JSON `{step, steps, stage, elapsed_s}` while a room's furniture is being extracted."""
STEPS = 4

FRAMES_PER_VIDEO = 32
"""Whole-home walkthroughs visit many rooms: sample densely enough to see each."""
ROOM_FRAMES_MAX = 16
"""Frames searched per room (spread over its share of each video): at most 4 batches in a row."""
BATCH_SIZE = 4
"""Frames per discovery request: the reviewed CLI's default; larger batches fail more often."""
DISCOVERY_TIMEOUT_S = 300
VISION_PARALLEL = 8
"""Room-matching requests in flight at once."""
ROOM_PARALLEL = 6
"""Rooms searched (and cut out) at once."""
MESH_WORKERS = 2
"""Rooms whose 3D models are built at once (each builds MESH_CONCURRENCY items at a time)."""
MASK_REQUESTS_PER_ROOM = 24
MESH_REQUESTS_PER_ROOM = 8
MESH_CONCURRENCY = 4
FULL_FRAME_AREA = 0.85
"""An item boxed this large in every sighting is the whole view, not an object."""

PIPELINE_VERSION = 3
"""Part of the registry namespace: items registered by an older pipeline (which kept lights
and railings, or registered a whole home in one namespace) are never mixed into a newer
one's results."""

State = Literal["running", "done", "failed"]
RoomState = Literal["waiting", "finding", "ready", "failed"]
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
class RoomWork:
    """One room's share of the videos and what was found in it."""

    room_id: str
    name: str
    namespace: str
    """The room's own furniture registry namespace."""
    frames: list[Frame]
    state: RoomState = "waiting"
    objects: list[str] = field(default_factory=list)
    """IDs of the items found in this room (whole-view boxes left out)."""
    names: dict[str, str] = field(default_factory=dict)
    segmentation: SegmentationResult | None = None
    """Kept for the placement observer's evidence frames."""
    warnings: list[str] = field(default_factory=list)
    error: str | None = None
    meshes: RoomMeshes | None = None
    """Its 3D model build, started when the room is first opened."""


@dataclass
class ExtractionJob:
    plan_id: str
    namespace: str
    """Base of every room's registry namespace for these videos."""
    videos: list[Path]
    plan: ParsedFloorPlan | None = None
    """The plan the videos were uploaded with: its rooms are what frames are matched to."""
    state: State = "running"
    stage: str = "starting"
    step: int = 0
    """1..STEPS once a stage has started."""
    started_at: float = field(default_factory=time.monotonic)
    warnings: list[str] = field(default_factory=list)
    error: str | None = None
    sources: list[SourceVideo] = field(default_factory=list)
    rooms: dict[str, RoomWork] = field(default_factory=dict)
    """Room ID -> its work. Rooms no frame was matched to are absent."""
    rooms_known: bool = False
    """Steps 1-2 are done: `rooms` is complete."""

    def settled(self) -> int:
        return sum(w.state in ("ready", "failed") for w in self.rooms.values())


Prepare = Callable[[ExtractionJob, Path], None]
"""Steps 1-2: fill `job.sources` and `job.rooms`."""
FindRoom = Callable[[ExtractionJob, RoomWork, Path], None]
"""Step 3 for one room: fill `objects`, `names`, `segmentation`."""
MeshRoom = Callable[[ExtractionJob, RoomWork, Path], None]
"""Step 4 for one room: build its items' meshes."""


def namespace_for(plan_id: str, videos: Sequence[Path]) -> str:
    """Same plan, same videos (content-addressed names) and same pipeline -> same registry
    namespaces, so re-uploading reuses every cached result."""
    digest = hashlib.sha256("\n".join(sorted(v.name for v in videos)).encode()).hexdigest()
    return f"upload-v{PIPELINE_VERSION}-{plan_id}-{digest[:12]}"


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


def _key() -> str:
    key = os.environ.get("FAL_KEY", "")
    if not key:
        raise ExtractionError("FAL_KEY is not set on the reconstruction service")
    return key


def prepare_live(job: ExtractionJob, data_dir: Path) -> None:
    """Steps 1-2: sample every video at once, then match every frame to a room."""
    _key()
    if job.plan is None:
        raise ExtractionError("the plan of these videos is unknown; upload them with the plan")
    from services.reconstruction.assets.selection import sample_sources
    from services.reconstruction.assets.selection_models import SelectionOptions

    from .room_frames import FalRoomClassifier, plan_rooms, spread

    job.step, job.stage = 1, f"reading {len(job.videos)} videos"
    options = SelectionOptions(max_frames_per_video=FRAMES_PER_VIDEO, batch_size=BATCH_SIZE)
    with ThreadPoolExecutor(len(job.videos) or 1, thread_name_prefix="sample") as pool:
        sampled = list(pool.map(lambda v: sample_sources([v], data_dir, options), job.videos))
    frames: list[Frame] = []
    for sources, video_frames, _ in sampled:
        for source in sources:
            if source.source_id not in {s.source_id for s in job.sources}:
                job.sources.append(source)
                frames += [f for f in video_frames if f.source_id == source.source_id]
    if not frames:
        raise ExtractionError("no frames could be read from the videos")

    job.step, job.stage = 2, f"matching {len(frames)} frames to the plan's rooms"
    classifier = FalRoomClassifier(parallel=VISION_PARALLEL)
    frame_rooms, warnings = classifier.assign_frames(job.plan, frames, data_dir)
    job.warnings += warnings
    if unmatched := sum(frame_rooms.get(f.key) is None for f in frames):
        job.warnings.append(
            f"{unmatched} of {len(frames)} frames could not be matched to a room and were skipped"
        )
    by_room: dict[str, list[Frame]] = {}
    for frame in frames:
        if (room := frame_rooms.get(frame.key)) is not None:
            by_room.setdefault(room, []).append(frame)
    if not by_room:
        raise ExtractionError("no frame of the videos could be matched to a room of the plan")
    names = {r.room_id: r.name for r in plan_rooms(job.plan)}
    job.rooms = {
        room_id: RoomWork(
            room_id,
            names.get(room_id, room_id),
            f"{job.namespace}-{room_id}",
            spread(room_frames, ROOM_FRAMES_MAX),
        )
        for room_id, room_frames in by_room.items()
    }


def find_live(job: ExtractionJob, work: RoomWork, data_dir: Path) -> None:
    """Step 3 for one room: discover its furniture in its frames, then cut the items out."""
    key = _key()
    from services.reconstruction.assets.mask_providers import FalSamProvider
    from services.reconstruction.assets.providers import FalVisionProvider
    from services.reconstruction.assets.segmentation import segment_furniture
    from services.reconstruction.assets.selection import discover_frames
    from services.reconstruction.assets.selection_models import SelectionOptions

    # One provider per room thread: each holds its own fal client.
    provider = FalVisionProvider(
        key=key,
        endpoint=os.environ.get("FAL_VISION_ENDPOINT", "fal-ai/any-llm/vision"),
        model=os.environ.get("FAL_VISION_MODEL", "google/gemini-2.5-flash"),
        timeout_s=DISCOVERY_TIMEOUT_S,
        lenient=True,
    )
    options = SelectionOptions(
        batch_size=BATCH_SIZE,
        max_requests=-(-len(work.frames) // BATCH_SIZE) + 2,
        # Videos of the same room may show the same item: match across them, in this room.
        room_key=f"{job.plan_id}:{work.room_id}",
    )

    def discover() -> SelectionResult:
        return discover_frames(
            work.namespace,
            job.sources,
            work.frames,
            data_dir=data_dir,
            provider=provider,
            options=options,
        )

    selection = discover()
    if batch_failures(selection)[0]:
        # Free: cached answers are re-read and requests still running remotely are collected.
        selection = discover()
    failed, total = batch_failures(selection)
    if total and failed == total:
        raise ExtractionError("the vision model could not read this room's frames")
    if failed:
        work.warnings.append(
            f"{failed} of {total} frame batches of this room could not be read; "
            "some furniture may be missing"
        )
    objects = [o for o in selection.objects if not whole_view(o)]
    if dropped := len(selection.objects) - len(objects):
        work.warnings.append(f"{dropped} item(s) boxed as the whole view were left out")
    work.names = {o.id: o.name for o in objects}
    work.objects = [o.id for o in objects]
    if work.objects:
        work.segmentation = segment_furniture(
            work.namespace,
            data_dir=data_dir,
            provider=FalSamProvider(key=key),
            object_ids=work.objects,
            max_requests=MASK_REQUESTS_PER_ROOM,
        )


def mesh_live(job: ExtractionJob, work: RoomWork, data_dir: Path) -> None:
    """Step 4 for one room: its items' meshes."""
    key = _key()
    from services.reconstruction.assets.mesh_providers import FalSam3dProvider
    from services.reconstruction.assets.reconstruction import reconstruct_furniture

    result = reconstruct_furniture(
        work.namespace,
        data_dir=data_dir,
        provider=FalSam3dProvider(key=key),
        object_ids=work.objects,
        max_requests=MESH_REQUESTS_PER_ROOM,
        concurrency=MESH_CONCURRENCY,
    )
    if failed := [i.object_id for i in result.items if i.failure is not None]:
        names = ", ".join(work.names.get(o, o) for o in failed)
        work.warnings.append(f"no 3D model for {names}: shown as sized boxes")


class Extractions:
    """The latest extraction job of each plan.

    Jobs run one at a time (steps 1-2, then their rooms' step 3 on a pool of ROOM_PARALLEL).
    Room mesh builds have their own MESH_WORKERS, so a room can be built while other rooms of
    the same job are still being searched."""

    def __init__(
        self,
        data_dir: Callable[[], Path],
        prepare: Prepare = prepare_live,
        find: FindRoom = find_live,
        mesh: MeshRoom = mesh_live,
        room_parallel: int = ROOM_PARALLEL,
    ) -> None:
        self._data_dir = data_dir
        self._prepare = prepare
        self._find = find
        self._mesh = mesh
        self._room_parallel = max(1, room_parallel)
        self._jobs: dict[str, ExtractionJob] = {}
        self._generations: dict[str, int] = {}
        """Per plan, bumped whenever a job starts: the plan's furniture source changed."""
        self._lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="extract")
        self._meshers = ThreadPoolExecutor(MESH_WORKERS, thread_name_prefix="mesh")

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
        data_dir = self._data_dir()
        try:
            self._prepare(job, data_dir)
        except ExtractionError as exc:
            job.error, job.state = str(exc), "failed"
            return
        except Exception as exc:  # a provider or media failure must not kill the worker
            log.exception("furniture extraction failed for %s", job.plan_id)
            job.error, job.state = f"the extraction stopped ({type(exc).__name__})", "failed"
            return
        job.step, job.stage = 3, f"finding furniture in {len(job.rooms)} rooms"
        job.rooms_known = True
        with ThreadPoolExecutor(self._room_parallel, thread_name_prefix="room") as pool:
            for work in job.rooms.values():
                pool.submit(self._find_room, job, work, data_dir)
        if job.rooms and all(w.state == "failed" for w in job.rooms.values()):
            first = next(iter(job.rooms.values())).error or "unknown reason"
            job.error, job.state = f"no room could be searched ({first})", "failed"
        else:
            job.state = "done"
        log.info("furniture extraction for %s: %s", job.plan_id, job.state)

    def _find_room(self, job: ExtractionJob, work: RoomWork, data_dir: Path) -> None:
        work.state = "finding"
        try:
            self._find(job, work, data_dir)
        except ExtractionError as exc:
            work.error, work.state = str(exc), "failed"
        except Exception as exc:  # one room's failure must not stop the others
            log.exception("furniture search failed for %s %s", job.plan_id, work.room_id)
            work.error, work.state = f"the search stopped ({type(exc).__name__})", "failed"
        else:
            work.state = "ready"

    def mesh_room(self, job: ExtractionJob, work: RoomWork) -> RoomMeshes:
        """The room's mesh build, queued now if this is the first time it is asked for."""
        with self._lock:
            if work.meshes is None:
                work.meshes = RoomMeshes(list(work.objects))
                self._meshers.submit(self._build, job, work, work.meshes)
            return work.meshes

    def _build(self, job: ExtractionJob, work: RoomWork, build: RoomMeshes) -> None:
        build.state, build.started_at = "running", time.monotonic()
        try:
            self._mesh(job, work, self._data_dir())
        except ExtractionError as exc:
            build.error, build.state = str(exc), "failed"
        except Exception as exc:  # the room still gets its items as sized boxes
            log.exception("mesh build failed for %s %s", job.plan_id, work.room_id)
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

    def _room(self, scene_id: str) -> tuple[ExtractionJob, RoomWork | None] | None:
        job = self.for_scene(scene_id)
        if job is None:
            return None
        return job, job.rooms.get(scene_id[len(job.plan_id) + 1 :])

    def pending(self, scene_id: str) -> bool:
        """Whether this room's furniture is still being extracted."""
        found = self._room(scene_id)
        if found is None:
            return False
        job, work = found
        if job.state == "failed":
            return False
        if not job.rooms_known:
            return True
        if work is None:
            return False
        if work.state in ("waiting", "finding"):
            return True
        return (
            work.state == "ready"
            and work.meshes is not None
            and work.meshes.state
            in (
                "queued",
                "running",
            )
        )

    def progress(self, scene_id: str) -> dict[str, object] | None:
        """Where the extraction of this room's furniture is, or None when it is not running."""
        if not self.pending(scene_id):
            return None
        found = self._room(scene_id)
        assert found is not None
        job, work = found
        if not job.rooms_known or work is None:
            step, stage = job.step, job.stage
        elif work.state in ("waiting", "finding"):
            step = 3
            stage = (
                f"finding furniture in {work.name} ({job.settled()} of {len(job.rooms)} rooms done)"
            )
        else:
            assert work.meshes is not None
            verb = "building" if work.meshes.state == "running" else "waiting to build"
            step = 4
            stage = f"{verb} 3D models of {len(work.meshes.object_ids)} items in {work.name}"
        return {
            "step": step,
            "steps": STEPS,
            "stage": stage,
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


NOTHING_SEEN = "No furniture from your videos was matched to this room."


class VideoFurniture:
    """Furniture for rooms of plans uploaded with videos; every other room uses `fallback`."""

    def __init__(self, jobs: Extractions, data_dir: Path, fallback: FurnitureSource) -> None:
        self.jobs = jobs
        self.data_dir = data_dir
        self.fallback = fallback

    def _waiting(self, room: RoomScene, job: ExtractionJob) -> SceneFurniture:
        progress = self.jobs.progress(room.scene_id)
        stage = str(progress["stage"]) if progress else job.stage
        return SceneFurniture(assets=[], warnings=[extracting(stage)], complete=False, pending=True)

    def _fallback(self, room: RoomScene, reason: str) -> SceneFurniture:
        furniture = self.fallback.furniture_for(room)
        furniture.warnings.insert(0, extraction_failed(reason))
        return furniture

    def furniture_for(self, room: RoomScene) -> SceneFurniture:
        job = self.jobs.for_scene(room.scene_id)
        if job is None:
            return self.fallback.furniture_for(room)
        if job.state == "failed":
            return self._fallback(room, job.error or "unknown reason")
        if not job.rooms_known:
            return self._waiting(room, job)
        work = job.rooms.get(room.scene_id[len(job.plan_id) + 1 :])
        if work is None:
            return SceneFurniture(assets=[], warnings=[NOTHING_SEEN, *job.warnings])
        if work.state in ("waiting", "finding"):
            return self._waiting(room, job)
        if work.state == "failed":
            return self._fallback(room, work.error or "unknown reason")
        if not work.objects:
            return SceneFurniture(assets=[], warnings=[NOTHING_SEEN, *work.warnings])
        build = self.jobs.mesh_room(job, work)
        if build.state in ("queued", "running"):
            return self._waiting(room, job)
        from services.reconstruction.assets.reconstruction import reconstruct_furniture

        from .observe_vision import FalVisionObserver, selection_frames, selection_masks

        # Offline: reads the meshes the build stored, normalised and checked, or proxies.
        result = reconstruct_furniture(
            work.namespace, data_dir=self.data_dir, object_ids=build.object_ids
        )
        assets = [item.asset or item.proxy for item in result.items]
        warnings = [*job.warnings, *work.warnings, *result.warnings]
        if build.error:
            warnings.append(f"3D models: {build.error}")
        if proxies := [work.names.get(a.id, a.id) for a in assets if a.is_proxy]:
            warnings.append(f"sized boxes, no 3D model: {', '.join(proxies)}")
        return SceneFurniture(
            assets=assets,
            observer=FalVisionObserver(masks=selection_masks(self.data_dir)),
            frames=(
                selection_frames(work.segmentation, self.data_dir)
                if work.segmentation is not None
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
