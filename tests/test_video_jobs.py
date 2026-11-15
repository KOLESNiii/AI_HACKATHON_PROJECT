"""Live furniture extraction from uploaded videos (`room/video_jobs.py`), with fake runners:
no test here calls fal."""

from __future__ import annotations

import json
import threading
import time
from collections.abc import Iterator
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

    def run(job: ExtractionJob, data_dir: Path) -> None:
        runs.append(job.namespace)
        if fail:
            raise ExtractionError("no furniture was found in the videos")

    jobs = Extractions(lambda: tmp_path, run=run)
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
    def run(job: ExtractionJob, data_dir: Path) -> None:
        raise OSError("/secret/path")

    jobs = Extractions(lambda: tmp_path, run=run)
    jobs.start("plan-1", [tmp_path / "a.mp4"])
    job = jobs.for_scene("plan-1-r")
    assert job is not None
    _wait(job)
    assert job.error == "the extraction stopped (OSError)"


def test_live_run_needs_a_key(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FAL_KEY", raising=False)
    job = ExtractionJob("plan-1", "upload-plan-1-x", [tmp_path / "a.mp4"])
    with pytest.raises(ExtractionError, match="FAL_KEY"):
        video_jobs.run_live(job, tmp_path)


class _Fallback:
    def furniture_for(self, room: RoomScene) -> SceneFurniture:
        return SceneFurniture(assets=[], warnings=["fallback"])


def _room(scene_id: str = "plan-1-floor-0-room-0") -> RoomScene:
    return RoomScene.model_validate_json(MOCK_SCENE.read_text()).model_copy(
        update={"scene_id": scene_id, "furniture": []}
    )


def test_video_furniture_by_job_state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    jobs = Extractions(lambda: tmp_path, run=lambda job, d: None)
    source = VideoFurniture(jobs, tmp_path, _Fallback())
    assert source.furniture_for(_room()).warnings == ["fallback"]  # no videos for this plan

    job = ExtractionJob("plan-1", "upload-plan-1-x", [])
    jobs._jobs["plan-1"] = job
    running = source.furniture_for(_room())
    assert running.assets == [] and not running.complete
    assert "Extracting furniture" in running.warnings[0]

    job.state, job.error = "failed", "FAL_KEY is not set on the reconstruction service"
    failed = source.furniture_for(_room())
    assert failed.warnings[0].startswith("Furniture could not be extracted")
    assert failed.warnings[1:] == ["fallback"]

    furnished = RoomScene.model_validate_json(MOCK_SCENE.read_text())
    assets = assets_of(furnished)
    items = [SimpleNamespace(asset=a, proxy=a) for a in assets]
    monkeypatch.setattr(
        "services.reconstruction.assets.reconstruction.reconstruct_furniture",
        lambda scene_id, data_dir: SimpleNamespace(items=items, warnings=[]),
    )
    job.state = "done"
    done = source.furniture_for(_room())
    assert [a.id for a in done.assets] == [a.id for a in assets]
    assert done.complete
    assert type(done.observer).__name__ == "FalVisionObserver"


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    release = threading.Event()
    jobs = Extractions(lambda: tmp_path / "furniture", run=lambda job, d: release.wait(5))
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
    assert progress["steps"] == 3 and progress["elapsed_s"] >= 0
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
