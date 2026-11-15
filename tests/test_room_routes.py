"""Floor-plan routes on the reconstruction service, and the ParsedFloorPlan contract."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from pydantic import ValidationError

pytest.importorskip("cv2")

from fastapi.testclient import TestClient  # noqa: E402

from contracts.schema import ParsedFloorPlan, ParsedRoom, RoomScene  # noqa: E402
from services.reconstruction.main import app  # noqa: E402
from services.reconstruction.room.annotate import FixedAnnotator, PlanAnnotations  # noqa: E402
from services.reconstruction.room.routes import get_annotator  # noqa: E402
from tests.test_room_parse import _label, _png, single_room  # noqa: E402


@pytest.fixture()
def client() -> Iterator[TestClient]:
    ann = PlanAnnotations(rooms=[_label("Studio", 400, 350, 4.0, 3.0)])
    app.dependency_overrides[get_annotator] = lambda: FixedAnnotator(ann)
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_upload_then_fetch_plan_and_room(client: TestClient) -> None:
    files = [("files", ("plan.png", _png(single_room()), "image/png"))]
    res = client.post("/floor-plans", files=files)
    assert res.status_code == 200, res.text
    plan = ParsedFloorPlan.model_validate(res.json())
    room = plan.floors[0].rooms[0]
    assert room.name == "Studio"

    again = client.get(f"/floor-plans/{plan.plan_id}")
    assert again.status_code == 200 and again.json() == res.json()

    scene = client.get(f"/floor-plans/{plan.plan_id}/rooms/{room.room_id}")
    assert scene.status_code == 200
    assert RoomScene.model_validate(scene.json()) == room.scene


def test_same_upload_returns_the_same_plan_id(client: TestClient) -> None:
    files = [("files", ("plan.png", _png(single_room()), "image/png"))]
    a = client.post("/floor-plans", files=files).json()["plan_id"]
    b = client.post("/floor-plans", files=files).json()["plan_id"]
    assert a == b


def test_errors(client: TestClient) -> None:
    assert client.get("/floor-plans/plan-unknown").status_code == 404
    bad = client.post("/floor-plans", files=[("files", ("x.png", b"not an image", "image/png"))])
    assert bad.status_code == 422
    empty = client.post("/floor-plans", files=[("files", ("x.png", b"", "image/png"))])
    assert empty.status_code == 422
    many = [("files", (f"{i}.png", b"x", "image/png")) for i in range(6)]
    assert client.post("/floor-plans", files=many).status_code == 422


def test_parsed_room_contract() -> None:
    scene = RoomScene.model_validate(
        {
            "scene_id": "p-r",
            "shell_glb_url": "/api/reconstruction/shells/p-r.glb",
            "floor_polygon": [{"x": 0, "z": 0}, {"x": 1, "z": 0}, {"x": 1, "z": 1}],
            "walls": [],
            "windows": [],
            "doors": [],
            "furniture": [],
        }
    )
    room = ParsedRoom(
        room_id="floor-0-room-0",
        name="Hall",
        area_m2=0.5,
        dimension_source="estimated",
        correction_needed=["dimensions", "openings", "orientation"],
        scene=scene,
    )
    assert room.labelled_width_m is None
    with pytest.raises(ValidationError):
        ParsedRoom(
            room_id="Floor 0", name="x", area_m2=1, dimension_source="estimated", scene=scene
        )
    with pytest.raises(ValidationError):
        ParsedRoom(
            room_id="r",
            name="x",
            area_m2=1,
            dimension_source="catalog",  # type: ignore[arg-type]
            scene=scene,
        )


# --- walkthrough videos uploaded with the plan ---------------------------------------------------


@pytest.fixture()
def uploads(tmp_path, monkeypatch):
    """Uploads in tmp_path; extraction jobs recorded, never run against fal."""
    from services.reconstruction.room import video_jobs
    from services.reconstruction.room.routes import get_upload_dir

    started: list[video_jobs.ExtractionJob] = []
    jobs = video_jobs.Extractions(lambda: tmp_path / "furniture", run=started.append)
    monkeypatch.setattr(video_jobs, "EXTRACTIONS", jobs)
    app.dependency_overrides[get_upload_dir] = lambda: tmp_path / "uploads"
    yield tmp_path / "uploads"
    app.dependency_overrides.pop(get_upload_dir, None)


def _plan_file() -> tuple[str, tuple[str, bytes, str]]:
    return ("files", ("plan.png", _png(single_room()), "image/png"))


def test_videos_are_kept_under_the_plan_and_noted(client: TestClient, uploads) -> None:
    videos = [
        ("videos", ("a.mp4", b"first video", "video/mp4")),
        ("videos", ("b.mov", b"second video", "video/quicktime")),
    ]
    res = client.post("/floor-plans", files=[_plan_file(), *videos])
    assert res.status_code == 200, res.text
    plan = ParsedFloorPlan.model_validate(res.json())
    assert any("2 walkthrough videos received" in w for w in plan.warnings)
    kept = sorted(p.suffix for p in (uploads / plan.plan_id / "videos").iterdir())
    assert kept == [".mov", ".mp4"]
    assert not [p for p in uploads.iterdir() if p.name.startswith(".staging-")]
    # The note belongs to that response, not to the stored plan.
    assert client.get(f"/floor-plans/{plan.plan_id}").json()["warnings"] == [
        w for w in plan.warnings if "walkthrough video" not in w
    ]
    # Re-uploading the same video keeps one copy.
    again = client.post("/floor-plans", files=[_plan_file(), videos[0]])
    assert again.status_code == 200
    assert len(list((uploads / plan.plan_id / "videos").iterdir())) == 2


def test_plan_without_videos_has_no_note(client: TestClient, uploads) -> None:
    res = client.post("/floor-plans", files=[_plan_file()])
    assert res.status_code == 200
    assert not any("walkthrough video" in w for w in res.json()["warnings"])
    assert not uploads.exists() or list(uploads.iterdir()) == []


def test_rejected_videos_leave_nothing(client: TestClient, uploads) -> None:
    not_video = client.post(
        "/floor-plans", files=[_plan_file(), ("videos", ("notes.txt", b"hello", "text/plain"))]
    )
    assert not_video.status_code == 415
    empty = client.post(
        "/floor-plans", files=[_plan_file(), ("videos", ("a.mp4", b"", "video/mp4"))]
    )
    assert empty.status_code == 422
    many = [("videos", (f"{i}.mp4", b"x", "video/mp4")) for i in range(6)]
    assert client.post("/floor-plans", files=[_plan_file(), *many]).status_code == 422
    assert [p for p in uploads.iterdir() if any(p.iterdir())] == []
    from services.reconstruction.room import video_jobs

    assert video_jobs.extractions().for_scene("plan-x-room") is None


def test_oversized_video_is_rejected(tmp_path) -> None:
    import io

    from services.reconstruction.room.videos import VideoRejected, stage_video

    with pytest.raises(VideoRejected) as exc:
        stage_video(io.BytesIO(b"x" * 11), "big.mp4", "video/mp4", tmp_path, max_bytes=10)
    assert exc.value.status_code == 413
