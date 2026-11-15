"""Live furniture extraction from uploaded videos (`room/video_jobs.py`), with fake runners:
no test here calls fal."""

from __future__ import annotations

import json
import threading
import time
from collections.abc import Callable, Iterator
from pathlib import Path
from types import SimpleNamespace

import pytest

pytest.importorskip("cv2")

from fastapi.testclient import TestClient  # noqa: E402

from contracts.schema import RoomScene  # noqa: E402
from services.reconstruction.main import app  # noqa: E402
from services.reconstruction.room import video_jobs  # noqa: E402
from services.reconstruction.room.annotate import FixedAnnotator, PlanAnnotations  # noqa: E402
from services.reconstruction.room.assemble import NoFurniture, SceneFurniture, assets_of  # noqa: E402
from services.reconstruction.room.routes import get_annotator, get_upload_dir  # noqa: E402
from services.reconstruction.room.video_jobs import (  # noqa: E402
    PENDING_HEADER,
    PROGRESS_HEADER,
    ExtractionError,
    ExtractionJob,
    Extractions,
    RoomWork,
    VideoFurniture,
)
from services.reconstruction.scenes import clear_cache  # noqa: E402
from tests.test_room_parse import _label, _png, single_room  # noqa: E402

MOCK_SCENE = Path(__file__).parents[1] / "contracts" / "mock_room" / "mock_scene.json"


def _wait(job: ExtractionJob, timeout: float = 5) -> None:
    deadline = time.monotonic() + timeout
    while job.state == "running" and time.monotonic() < deadline:
        time.sleep(0.01)
    assert job.state != "running", "job did not finish"


def test_jobs_run_once_per_plan_and_videos_and_retry_after_failure(tmp_path: Path) -> None:
    runs: list[str] = []
    fail = True

    def prepare(job: ExtractionJob, data_dir: Path) -> None:
        runs.append(job.namespace)
        if fail:
            raise ExtractionError("no furniture was found in the videos")

    jobs = Extractions(lambda: tmp_path, prepare=prepare)
    a = [tmp_path / "aaaa.mp4"]
    assert jobs.start("plan-1", a)
    job = jobs.for_scene("plan-1-floor-0-room-0")
    assert job is not None
    _wait(job)
    assert job.state == "failed" and job.error == "no furniture was found in the videos"
    assert jobs.for_scene("plan-10-room") is None  # another plan, not a prefix match

    fail = False
    assert jobs.start("plan-1", a)  # a failed job is started again
    job = jobs.for_scene("plan-1-x")
    assert job is not None
    _wait(job)
    assert job.state == "done"
    assert not jobs.start("plan-1", a)  # same videos: nothing new to do
    assert jobs.start("plan-1", [tmp_path / "bbbb.mp4"])  # new videos: a new job
    job = jobs.for_scene("plan-1-x")
    assert job is not None
    _wait(job)
    assert len(set(runs)) == 2


def test_unexpected_errors_are_reported_without_details(tmp_path: Path) -> None:
    def prepare(job: ExtractionJob, data_dir: Path) -> None:
        raise OSError("/secret/path")

    jobs = Extractions(lambda: tmp_path, prepare=prepare)
    jobs.start("plan-1", [tmp_path / "a.mp4"])
    job = jobs.for_scene("plan-1-r")
    assert job is not None
    _wait(job)
    assert job.error == "the extraction stopped (OSError)"


def test_live_run_needs_a_key(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FAL_KEY", raising=False)
    job = ExtractionJob("plan-1", "upload-plan-1-x", [tmp_path / "a.mp4"])
    with pytest.raises(ExtractionError, match="FAL_KEY"):
        video_jobs.prepare_live(job, tmp_path)


class _Fallback:
    def furniture_for(self, room: RoomScene) -> SceneFurniture:
        return SceneFurniture(assets=[], warnings=["fallback"])


def _room(scene_id: str = "plan-1-floor-0-room-0") -> RoomScene:
    return RoomScene.model_validate_json(MOCK_SCENE.read_text()).model_copy(
        update={"scene_id": scene_id, "furniture": []}
    )


def _work(room_id: str) -> RoomWork:
    return RoomWork(room_id, f"Room {room_id}", f"ns-{room_id}", [])


def _rooms(*room_ids: str) -> Callable[[ExtractionJob, Path], None]:
    def prepare(job: ExtractionJob, data_dir: Path) -> None:
        job.rooms = {r: _work(r) for r in room_ids}

    return prepare


def _until(check: Callable[[], bool], timeout: float = 5) -> None:
    deadline = time.monotonic() + timeout
    while not check() and time.monotonic() < deadline:
        time.sleep(0.01)
    assert check(), "condition not reached in time"


def test_rooms_are_searched_at_once_and_fail_alone(tmp_path: Path) -> None:
    rooms = ("floor-0-room-0", "floor-0-room-1", "floor-0-room-2")
    together = threading.Barrier(len(rooms), timeout=5)

    def find(job: ExtractionJob, work: RoomWork, data_dir: Path) -> None:
        together.wait()  # breaks (and fails the room) unless every room is searched at once
        if work.room_id == "floor-0-room-2":
            raise ExtractionError("the vision model could not read this room's frames")
        work.objects = [f"vid-{work.room_id[-1]}"]

    jobs = Extractions(lambda: tmp_path, prepare=_rooms(*rooms), find=find)
    jobs.start("plan-1", [tmp_path / "a.mp4"])
    job = jobs.for_scene("plan-1-floor-0-room-0")
    assert job is not None
    _wait(job)
    assert job.state == "done"
    assert [job.rooms[r].state for r in rooms] == ["ready", "ready", "failed"]
    assert job.rooms["floor-0-room-2"].error == "the vision model could not read this room's frames"


def test_every_room_failing_fails_the_job(tmp_path: Path) -> None:
    def find(job: ExtractionJob, work: RoomWork, data_dir: Path) -> None:
        raise ExtractionError("the vision model could not read this room's frames")

    jobs = Extractions(lambda: tmp_path, prepare=_rooms("r0", "r1"), find=find)
    jobs.start("plan-1", [tmp_path / "a.mp4"])
    job = jobs.for_scene("plan-1-r0")
    assert job is not None
    _wait(job)
    assert job.state == "failed" and job.error is not None
    assert job.error.startswith("no room could be searched")


def test_a_room_is_built_while_other_rooms_are_still_searched(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    slow_room = threading.Event()
    built: list[str] = []

    def find(job: ExtractionJob, work: RoomWork, data_dir: Path) -> None:
        if work.room_id == "floor-0-room-1":
            slow_room.wait(5)
        work.objects = ["vid-000001"]

    finish_build = threading.Event()

    def mesh(job: ExtractionJob, work: RoomWork, data_dir: Path) -> None:
        built.append(work.room_id)
        finish_build.wait(5)

    rooms = _rooms("floor-0-room-0", "floor-0-room-1")
    jobs = Extractions(lambda: tmp_path, prepare=rooms, find=find, mesh=mesh)
    source = VideoFurniture(jobs, tmp_path, _Fallback())
    jobs.start("plan-1", [tmp_path / "a.mp4"])
    job = jobs.for_scene("plan-1-floor-0-room-0")
    assert job is not None
    _until(lambda: job.rooms_known and job.rooms["floor-0-room-0"].state == "ready")
    assert job.rooms["floor-0-room-1"].state == "finding"
    progress = jobs.progress("plan-1-floor-0-room-1")
    assert progress is not None and progress["step"] == 3
    assert "finding furniture in Room floor-0-room-1 (1 of 2 rooms done)" == progress["stage"]

    first = source.furniture_for(_room("plan-1-floor-0-room-0"))
    assert first.pending  # its 3D models are now being built
    _until(lambda: built == ["floor-0-room-0"])
    assert job.state == "running" and job.rooms["floor-0-room-1"].state == "finding"
    slow_room.set()
    finish_build.set()
    _wait(job)
    assert job.state == "done"


def test_video_furniture_by_room_state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    release = threading.Event()
    meshed: list[tuple[str, list[str]]] = []

    def mesh(job: ExtractionJob, work: RoomWork, data_dir: Path) -> None:
        release.wait(5)
        meshed.append((work.room_id, list(work.objects)))

    jobs = Extractions(lambda: tmp_path, mesh=mesh)
    source = VideoFurniture(jobs, tmp_path, _Fallback())
    assert source.furniture_for(_room()).warnings == ["fallback"]  # no videos for this plan

    job = ExtractionJob("plan-1", "upload-plan-1-x", [])
    jobs._jobs["plan-1"] = job
    running = source.furniture_for(_room())  # steps 1-2: rooms not known yet
    assert running.assets == [] and not running.complete and running.pending
    assert "Extracting furniture" in running.warnings[0]
    assert jobs.pending("plan-1-floor-0-room-0")

    job.state, job.error = "failed", "FAL_KEY is not set on the reconstruction service"
    failed = source.furniture_for(_room())
    assert failed.warnings[0].startswith("Furniture could not be extracted")
    assert failed.warnings[1:] == ["fallback"]
    assert not jobs.pending("plan-1-floor-0-room-0")

    assets = assets_of(RoomScene.model_validate_json(MOCK_SCENE.read_text()))
    by_id = {a.id: a for a in assets}
    read: list[tuple[str, list[str] | None]] = []

    def reconstruct(scene_id: str, data_dir: Path, object_ids: list[str] | None = None):  # type: ignore[no-untyped-def]
        read.append((scene_id, object_ids))
        items = [SimpleNamespace(asset=by_id[o], proxy=by_id[o]) for o in object_ids or []]
        return SimpleNamespace(items=items, warnings=[])

    monkeypatch.setattr(
        "services.reconstruction.assets.reconstruction.reconstruct_furniture", reconstruct
    )
    mine = assets[0].id
    job.state, job.error, job.rooms_known = "running", None, True
    job.rooms = {
        "floor-0-room-0": _work("floor-0-room-0"),
        "floor-0-room-1": _work("floor-0-room-1"),
        "floor-0-room-2": _work("floor-0-room-2"),
        "floor-0-room-3": _work("floor-0-room-3"),
    }
    job.rooms["floor-0-room-0"].state = "ready"
    job.rooms["floor-0-room-0"].objects = [mine]
    job.rooms["floor-0-room-1"].state = "finding"
    job.rooms["floor-0-room-2"].state, job.rooms["floor-0-room-2"].error = "failed", "no luck"
    job.rooms["floor-0-room-3"].state = "ready"  # searched, nothing found

    unseen = source.furniture_for(_room("plan-1-floor-0-room-7"))  # no frame matched to it
    assert unseen.complete and unseen.warnings[0] == video_jobs.NOTHING_SEEN
    empty = source.furniture_for(_room("plan-1-floor-0-room-3"))
    assert empty.complete and empty.warnings[0] == video_jobs.NOTHING_SEEN
    searching = source.furniture_for(_room("plan-1-floor-0-room-1"))
    assert searching.pending and "finding furniture in" in searching.warnings[0]
    broken = source.furniture_for(_room("plan-1-floor-0-room-2"))
    assert "no luck" in broken.warnings[0] and broken.warnings[1:] == ["fallback"]

    # The first request for a ready room queues its 3D models; pending until they are built.
    queued = source.furniture_for(_room())
    assert queued.pending and not queued.complete and queued.assets == []
    progress = jobs.progress("plan-1-floor-0-room-0")
    assert progress is not None and progress["step"] == 4
    release.set()
    _until(
        lambda: (
            job.rooms["floor-0-room-0"].meshes is not None
            and job.rooms["floor-0-room-0"].meshes.state == "done"
        )
    )
    assert meshed == [("floor-0-room-0", [mine])]

    done = source.furniture_for(_room())
    assert [a.id for a in done.assets] == [mine]  # only this room's items
    assert read == [("ns-floor-0-room-0", [mine])]  # from this room's own namespace
    assert done.complete and not done.pending
    assert type(done.observer).__name__ == "FalVisionObserver"
    assert not jobs.pending("plan-1-floor-0-room-0")


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    release = threading.Event()
    jobs = Extractions(lambda: tmp_path / "furniture", prepare=lambda job, d: release.wait(5))
    monkeypatch.setattr(video_jobs, "EXTRACTIONS", jobs)
    ann = PlanAnnotations(rooms=[_label("Studio", 400, 350, 4.0, 3.0)])
    app.dependency_overrides[get_annotator] = lambda: FixedAnnotator(ann)
    app.dependency_overrides[get_upload_dir] = lambda: tmp_path / "uploads"
    clear_cache()
    with TestClient(app) as c:
        c.release = release  # type: ignore[attr-defined]
        yield c
    release.set()
    app.dependency_overrides.clear()
    clear_cache()


def test_rooms_of_a_plan_with_videos_wait_for_extraction(client: TestClient) -> None:
    files = [
        ("files", ("plan.png", _png(single_room()), "image/png")),
        ("videos", ("a.mp4", b"a video", "video/mp4")),
    ]
    plan = client.post("/floor-plans", files=files).json()
    assert any("extracting their furniture" in w for w in plan["warnings"])
    scene_id = plan["floors"][0]["rooms"][0]["scene"]["scene_id"]

    pending = client.get(f"/scenes/{scene_id}")
    assert pending.status_code == 200
    assert pending.headers.get(PENDING_HEADER) == "true"
    progress = json.loads(pending.headers[PROGRESS_HEADER])
    assert progress["steps"] == 4 and progress["elapsed_s"] >= 0
    assert isinstance(progress["stage"], str)
    assert "Extracting furniture" in json.loads(pending.headers["X-Reconstruction-Warnings"])[0]
    assert pending.json()["furniture"] == []

    client.release.set()  # type: ignore[attr-defined]
    job = video_jobs.extractions().for_scene(scene_id)
    assert job is not None
    _wait(job)
    settled = client.get(f"/scenes/{scene_id}")
    assert settled.status_code == 200
    assert PENDING_HEADER not in settled.headers
    assert PROGRESS_HEADER not in settled.headers


def test_rooms_without_videos_are_never_pending(client: TestClient) -> None:
    files = [("files", ("plan.png", _png(single_room()), "image/png"))]
    plan = client.post("/floor-plans", files=files).json()
    scene_id = plan["floors"][0]["rooms"][0]["scene"]["scene_id"]
    res = client.get(f"/scenes/{scene_id}")
    assert res.status_code == 200 and PENDING_HEADER not in res.headers
    assert NoFurniture  # the default source for unbound rooms


# --- races between extraction jobs and scene assembly (PR #70 review) ----------------------------


class _ScriptedSource:
    """Answers `furniture_for` from a script, one entry per call (the last one repeats)."""

    def __init__(self, *answers: Callable[[], SceneFurniture]) -> None:
        self.answers = list(answers)
        self.calls = 0

    def furniture_for(self, room: RoomScene) -> SceneFurniture:
        answer = self.answers[min(self.calls, len(self.answers) - 1)]
        self.calls += 1
        return answer()


@pytest.fixture()
def plan_room(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[tuple[TestClient, str]]:
    """A parsed room and a client; extraction jobs run a no-op, never fal."""
    monkeypatch.setattr(
        video_jobs, "EXTRACTIONS", Extractions(lambda: tmp_path, prepare=lambda job, d: None)
    )
    ann = PlanAnnotations(rooms=[_label("Studio", 400, 350, 4.0, 3.0)])
    app.dependency_overrides[get_annotator] = lambda: FixedAnnotator(ann)
    clear_cache()
    with TestClient(app) as c:
        files = [("files", ("plan.png", _png(single_room()), "image/png"))]
        plan = c.post("/floor-plans", files=files).json()
        yield c, plan["floors"][0]["rooms"][0]["scene"]["scene_id"]
    app.dependency_overrides.clear()
    clear_cache()


def _use(source: _ScriptedSource) -> None:
    from services.reconstruction.scenes import get_furniture_source

    app.dependency_overrides[get_furniture_source] = lambda: source


def test_extraction_finishing_mid_assembly_is_assembled_again(
    plan_room: tuple[TestClient, str],
) -> None:
    """The job finished after `furniture_for` answered "still extracting" (no job is running
    any more): the empty room must not be the final answer."""
    client, scene_id = plan_room
    source = _ScriptedSource(
        lambda: SceneFurniture(assets=[], warnings=["extracting"], complete=False, pending=True),
        lambda: SceneFurniture(assets=[], warnings=["extracted"]),
    )
    _use(source)
    res = client.get(f"/scenes/{scene_id}")
    assert res.status_code == 200
    assert source.calls == 2
    assert json.loads(res.headers["X-Reconstruction-Warnings"])[-1] == "extracted"
    assert PENDING_HEADER not in res.headers
    assert client.get(f"/scenes/{scene_id}").status_code == 200
    assert source.calls == 2  # the finished room is kept


def test_a_pending_room_always_tells_the_client_to_ask_again(
    plan_room: tuple[TestClient, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Even when the job's progress is gone by the time the response is written."""
    client, scene_id = plan_room
    jobs = video_jobs.extractions()
    monkeypatch.setattr(jobs, "pending", lambda scene_id: True)
    monkeypatch.setattr(jobs, "progress", lambda scene_id: None)
    _use(
        _ScriptedSource(
            lambda: SceneFurniture(assets=[], warnings=[], complete=False, pending=True)
        )
    )
    res = client.get(f"/scenes/{scene_id}")
    assert res.status_code == 200
    assert res.headers.get(PENDING_HEADER) == "true"
    assert PROGRESS_HEADER not in res.headers


def test_a_room_assembled_from_a_replaced_source_is_not_kept(
    plan_room: tuple[TestClient, str], tmp_path: Path
) -> None:
    """New videos start a job while a request is assembling from the old furniture source:
    that assembly must not be kept after `forget_plan` cleared the cache."""
    client, scene_id = plan_room
    plan_id = scene_id.rsplit("-floor-", 1)[0]

    def old_source_then_videos_arrive() -> SceneFurniture:
        assert video_jobs.extractions().start(plan_id, [tmp_path / "new.mp4"])
        return SceneFurniture(assets=[], warnings=["old source"])

    source = _ScriptedSource(
        old_source_then_videos_arrive,
        lambda: SceneFurniture(assets=[], warnings=["new source"]),
    )
    _use(source)
    res = client.get(f"/scenes/{scene_id}")
    assert res.status_code == 200
    assert source.calls == 2
    assert json.loads(res.headers["X-Reconstruction-Warnings"])[-1] == "new source"
    from services.reconstruction import scenes

    assert scenes._scenes[scene_id].warnings[-1] == "new source"
