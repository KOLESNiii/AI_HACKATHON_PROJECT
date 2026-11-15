"""The published scene cache (Dev 1.8, #12): a service that just started serves the real-input
demo room with no upload, key or network, the room stays editable and auditable, and the
committed cache is what the committed inputs reproduce."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest

pytest.importorskip("cv2")
pytest.importorskip("shapely")
pytest.importorskip("trimesh")

from fastapi.testclient import TestClient  # noqa: E402

from contracts.schema import ParsedFloorPlan, Pose2D, RoomScene  # noqa: E402
from services.reconstruction import scenes  # noqa: E402
from services.reconstruction.config import (  # noqa: E402
    REPO_ROOT,
    SCENE_DEMO_CACHE_DIR_ENV,
    furniture_data_dir,
)
from services.reconstruction.main import app  # noqa: E402
from services.reconstruction.room import routes  # noqa: E402
from services.reconstruction.room.annotate import AnnotationResult, FixedAnnotator  # noqa: E402
from services.reconstruction.room.assemble import NO_FURNITURE_YET  # noqa: E402
from services.reconstruction.room.routes import get_annotator  # noqa: E402
from services.reconstruction.room.scene_cache import (  # noqa: E402
    FROM_SCENE_CACHE,
    cache_path,
    differences,
    main,
    read_scene_cache,
    restore_published,
    verify_scene_cache,
)
from services.reconstruction.room.video_furniture import (  # noqa: E402
    RealRoomFurniture,
    from_demo_cache,
    load_bindings,
)
from services.spatial_engine.main import app as spatial_app  # noqa: E402

COMMITTED = REPO_ROOT / "services/reconstruction/room/fixtures/scene_cache"
FURNITURE = REPO_ROOT / "services/reconstruction/assets/fixtures/demo_cache"
ANNOTATIONS = REPO_ROOT / "services/reconstruction/room/fixtures/three_floor.annotations.json"
PROXY_PREFIX = "/api/reconstruction"
(BINDING,) = load_bindings().values()
PLAN = REPO_ROOT / BINDING.plan
SCENE_ID = BINDING.scene_id
PLAN_ID = SCENE_ID.removesuffix(f"-{BINDING.room_id}")
SOFA, OTHER_SOFA, TABLE, CHAIR = (hint.asset_id for hint in BINDING.hints)

pytestmark = pytest.mark.skipif(not PLAN.exists(), reason="example plan missing")


class Unreachable:
    """The label provider, for a service that must not need it."""

    def annotate(self, image: bytes, content_type: str) -> AnnotationResult:
        raise AssertionError("the label provider was called")


@pytest.fixture()
def offline(monkeypatch: pytest.MonkeyPatch) -> None:
    """No key, and any attempt to resolve or connect fails the test."""

    def refuse(*args: object, **kwargs: object) -> None:
        raise AssertionError("network access attempted")

    monkeypatch.delenv("FAL_KEY", raising=False)
    monkeypatch.setattr(socket.socket, "connect", refuse)
    monkeypatch.setattr(socket, "getaddrinfo", refuse)
    monkeypatch.setattr(socket, "create_connection", refuse)


@pytest.fixture()
def data_dir() -> Iterator[Path]:
    """The app's furniture data directory (a throwaway one, tests/conftest.py), empty: a fresh
    checkout that never ran the pipeline."""
    path = furniture_data_dir()
    shutil.rmtree(path, ignore_errors=True)
    path.mkdir(parents=True)
    yield path
    shutil.rmtree(path, ignore_errors=True)
    path.mkdir(parents=True)


@contextmanager
def started(cache_dir: Path) -> Iterator[tuple[TestClient, list[str]]]:
    """The service as it is just after starting with `cache_dir` as its scene cache: nothing
    uploaded, nothing assembled. Yields the client and what the restore reported. Whatever
    another test module had parsed is put back afterwards."""
    held = (routes._plans.pop(PLAN_ID, None), routes._originals.pop(PLAN_ID, None))
    app.dependency_overrides[get_annotator] = Unreachable
    app.dependency_overrides[scenes.get_furniture_source] = lambda: RealRoomFurniture(
        load_bindings(), furniture_data_dir(), FURNITURE
    )
    scenes.clear_cache()
    try:
        problems = restore_published(cache_dir)  # what main.py does at import
        with TestClient(app) as client:
            yield client, problems
    finally:
        app.dependency_overrides.clear()
        scenes.clear_cache()
        routes.clear_corrections()
        routes._plans.pop(PLAN_ID, None)
        routes._originals.pop(PLAN_ID, None)
        if held[0] is not None and held[1] is not None:
            routes._plans[PLAN_ID], routes._originals[PLAN_ID] = held


@pytest.fixture()
def client(data_dir: Path, offline: None) -> Iterator[TestClient]:
    """A just-started service with the committed scene and furniture caches, offline."""
    with started(COMMITTED) as (client, problems):
        assert problems == []
        yield client


@pytest.fixture(scope="module")
def auditor() -> TestClient:
    return TestClient(spatial_app)


@pytest.fixture(scope="module")
def published() -> RoomScene:
    """The assembled demo scene as committed."""
    (cached,) = read_scene_cache(cache_path(COMMITTED, PLAN_ID)).scenes
    return cached.scene


def _scene(client: TestClient, scene_id: str = SCENE_ID) -> tuple[RoomScene, list[str]]:
    res = client.get(f"/scenes/{scene_id}")
    assert res.status_code == 200, res.text
    return RoomScene.model_validate(res.json()), json.loads(res.headers[scenes.WARNINGS_HEADER])


def _audit(auditor: TestClient, scene: RoomScene) -> dict[str, object]:
    res = auditor.post("/audit", json=scene.model_dump(mode="json"))
    assert res.status_code == 200, res.text
    report: dict[str, object] = res.json()
    assert (report["scene_id"], report["scene_revision"]) == (scene.scene_id, scene.revision)
    return report


def _blockers(report: dict[str, object]) -> list[tuple[str, str]]:
    blocked = report["blocked_doors"]
    assert isinstance(blocked, list)
    return sorted((issue["door_id"], issue["blocked_by_item_id"]) for issue in blocked)


def _moved(scene: RoomScene, item_id: str, x: float, z: float) -> RoomScene:
    """What the editor sends after a drag: one pose changed, the next revision."""
    furniture = [
        item.model_copy(update={"pose": Pose2D(x=x, z=z, yaw_deg=item.pose.yaw_deg)})
        if item.id == item_id
        else item
        for item in scene.furniture
    ]
    return scene.model_copy(update={"furniture": furniture, "revision": scene.revision + 1})


def _same(published: RoomScene | ParsedFloorPlan, found: RoomScene | ParsedFloorPlan) -> list[str]:
    return differences(published.model_dump(mode="json"), found.model_dump(mode="json"))


def _fetch(client: TestClient, url: str) -> bytes:
    res = client.get(url.removeprefix(PROXY_PREFIX))
    assert res.status_code == 200, (url, res.text)
    return res.content


# --- The demo room without upload, key or network ---------------------------------------------


def test_a_just_started_service_serves_the_published_room(
    client: TestClient, auditor: TestClient, published: RoomScene
) -> None:
    scene, warnings = _scene(client)
    assert _same(published, scene) == []  # exactly the published scene
    assert warnings == [from_demo_cache(BINDING.furniture_scene_id)]
    assert sorted(item.id for item in scene.furniture) == sorted(h.asset_id for h in BINDING.hints)
    assert not any(item.is_proxy for item in scene.furniture)  # the four meshes, not boxes
    assert len(scene.walls) == len(BINDING.walls_m)  # the labelled room, not the unlabelled one

    assert _fetch(client, scene.shell_glb_url)[:4] == b"glTF"
    for item in scene.furniture:
        glb = _fetch(client, item.glb_url)
        assert f"{hashlib.sha256(glb).hexdigest()}.glb" == item.glb_url.rsplit("/", 1)[1]

    # The documented first audit (docs/architecture.md): estimates to correct, nothing invalid.
    report = _audit(auditor, scene)
    assert report["collisions"] == [] and report["out_of_bounds_item_ids"] == []
    assert _blockers(report) == [("door0", OTHER_SOFA), ("door0", CHAIR)]
    assert SCENE_ID in scenes._scenes  # settled: kept like any complete assembly


def test_the_published_room_stays_editable_and_auditable(
    client: TestClient, auditor: TestClient
) -> None:
    scene, _ = _scene(client)
    edited = _moved(scene, CHAIR, 3.9, 8.6)  # out of the doorway, against the east wall
    res = client.put(f"/scenes/{SCENE_ID}", json=edited.model_dump(mode="json"))
    assert res.status_code == 200, res.text
    saved, _ = _scene(client)
    assert saved == RoomScene.model_validate(res.json()) and saved.revision == 1
    chair = next(item for item in saved.furniture if item.id == CHAIR)
    assert (chair.pose.x, chair.pose.z) == (3.9, 8.6)
    assert "placement" not in chair.correction_needed  # the user put it there
    report = _audit(auditor, saved)
    assert _blockers(report) == [("door0", OTHER_SOFA)]  # the audit follows the move
    assert report["collisions"] == [] and report["out_of_bounds_item_ids"] == []

    # A scale correction needs the original parse of the whole floor: restored with the plan.
    length = BINDING.walls_m["w16"] * 1.1
    res = client.post(
        f"/scenes/{SCENE_ID}/scale",
        params={"wall_id": "w16", "length_m": length, "revision": saved.revision},
    )
    assert res.status_code == 200, res.text
    corrected = RoomScene.model_validate(res.json())
    assert corrected.revision == 2 and corrected.shell_glb_url != saved.shell_glb_url
    assert _fetch(client, corrected.shell_glb_url)[:4] == b"glTF"
    assert client.get(saved.shell_glb_url.removeprefix(PROXY_PREFIX)).status_code == 404
    assert [item.id for item in corrected.furniture] == [item.id for item in saved.furniture]
    assert _audit(auditor, corrected)["out_of_bounds_item_ids"] == []


def test_a_restart_returns_to_the_published_scene(
    data_dir: Path, offline: None, published: RoomScene
) -> None:
    """Corrections are kept in memory only; the cache restores the published starting point."""
    with started(COMMITTED) as (client, _):
        scene, _ = _scene(client)
        edited = _moved(scene, CHAIR, 3.9, 8.6)
        assert client.put(f"/scenes/{SCENE_ID}", json=edited.model_dump(mode="json")).is_success
        assert _scene(client)[0].revision == 1
    with started(COMMITTED) as (client, _):
        scene, _ = _scene(client)
        assert scene.revision == 0 and _same(published, scene) == []


def test_uploading_the_published_plan_never_asks_the_label_provider(client: TestClient) -> None:
    """A plan ID is the hash of the image bytes, so the restored plan answers the upload.
    The `client`'s annotator fails the test if it is called."""
    files = [("files", (PLAN.name, PLAN.read_bytes(), "image/png"))]
    res = client.post("/floor-plans", files=files)
    assert res.status_code == 200, res.text
    plan = ParsedFloorPlan.model_validate(res.json())
    cached = read_scene_cache(cache_path(COMMITTED, PLAN_ID)).plan
    assert plan.plan_id == PLAN_ID and plan.warnings == [*cached.warnings, FROM_SCENE_CACHE]
    assert plan.floors == cached.floors
    assert ParsedFloorPlan.model_validate(client.get(f"/floor-plans/{PLAN_ID}").json()) == plan
    room = client.get(f"/floor-plans/{PLAN_ID}/rooms/{BINDING.room_id}")
    assert len(RoomScene.model_validate(room.json()).walls) == len(BINDING.walls_m)
    assert len(_scene(client)[0].furniture) == len(BINDING.hints)  # and still furnished


def test_other_rooms_of_the_published_plan_load_without_furniture(client: TestClient) -> None:
    plan = read_scene_cache(cache_path(COMMITTED, PLAN_ID)).plan
    other = plan.floors[1].rooms[0].scene
    scene, warnings = _scene(client, other.scene_id)
    assert scene.furniture == [] and warnings == [NO_FURNITURE_YET]
    assert _fetch(client, scene.shell_glb_url)[:4] == b"glTF"


def test_a_restore_never_replaces_a_plan_the_service_already_has(client: TestClient) -> None:
    served = routes._plans[PLAN_ID]
    assert restore_published(COMMITTED) == []
    assert routes._plans[PLAN_ID] is served
    assert routes.restore_plan(served.model_copy(update={"warnings": []})) is False
    assert routes._plans[PLAN_ID] is served and routes._originals[PLAN_ID] is served


def test_the_service_restores_the_committed_cache_when_it_starts() -> None:
    """The real wiring: a new process with the default settings and no key knows the room."""
    env = {k: v for k, v in os.environ.items() if k not in (SCENE_DEMO_CACHE_DIR_ENV, "FAL_KEY")}
    code = (
        "import services.reconstruction.main\n"
        "from services.reconstruction.room.routes import find_parsed_scene\n"
        f"print(len(find_parsed_scene({SCENE_ID!r}).walls))\n"
    )
    done = subprocess.run(
        [sys.executable, "-c", code], cwd=REPO_ROOT, env=env, capture_output=True, text=True
    )
    assert done.returncode == 0, done.stderr
    assert done.stdout.strip() == str(len(BINDING.walls_m)) and "skipped" not in done.stderr


# --- The cache is what the committed inputs give ----------------------------------------------


def test_the_committed_cache_is_reproduced_from_the_committed_inputs(offline: None) -> None:
    """The plan image parsed with its recorded labels, and the room assembled from the furniture
    cache, give the committed plan and scene. A change to the parser, the aligner, the hints or
    the furniture cache that moves the demo scene fails here until the cache is republished."""
    problems = verify_scene_cache(
        cache_path(COMMITTED, PLAN_ID),
        furniture_cache_dir=FURNITURE,
        bindings=load_bindings(),
        images=[(PLAN.read_bytes(), "image/png")],
        annotator=FixedAnnotator.from_file(ANNOTATIONS),
    )
    assert problems == []


def test_publish_and_verify_round_trip(
    tmp_path: Path, offline: None, capsys: pytest.CaptureFixture[str]
) -> None:
    cache_dir, no_furniture = tmp_path / "cache", tmp_path / "no-furniture"
    no_furniture.mkdir()
    publish = ["publish", str(PLAN), "--annotations", str(ANNOTATIONS), "--cache-dir"]
    verify = ["verify", "--plan-id", PLAN_ID, "--furniture-cache-dir", str(FURNITURE)]
    assert main([*verify, "--cache-dir", str(cache_dir)]) == 2  # nothing published yet
    assert "no cache published" in capsys.readouterr().out

    assert main([*publish, str(cache_dir), "--furniture-cache-dir", str(FURNITURE)]) == 0
    path = cache_path(cache_dir, PLAN_ID)
    committed = json.loads(cache_path(COMMITTED, PLAN_ID).read_text())
    assert differences(committed, json.loads(path.read_text())) == []  # same as the committed one
    assert main([*verify, "--cache-dir", str(cache_dir)]) == 0

    # A published pose that the assembly no longer gives is found and named.
    document = json.loads(path.read_text())
    chair = next(i for i in document["scenes"][0]["scene"]["furniture"] if i["id"] == CHAIR)
    chair["pose"]["x"] += 0.2
    path.write_text(json.dumps(document))
    capsys.readouterr()
    assert main([*verify, "--cache-dir", str(cache_dir)]) == 2
    assert f"furniture[{CHAIR}].pose.x" in capsys.readouterr().out

    # A refused publish (no furniture to place) leaves the earlier cache as it was.
    before = path.read_bytes()
    assert main([*publish, str(cache_dir), "--furniture-cache-dir", str(no_furniture)]) == 2
    out = capsys.readouterr().out
    assert "not placed" in out and str(tmp_path) not in out
    assert path.read_bytes() == before


# --- Unusable caches --------------------------------------------------------------------------


def _not_json(document: dict[str, object]) -> str:
    return "{"


def _another_plans_scene(document: dict[str, object]) -> str:
    document["scenes"][0]["scene"]["scene_id"] = "plan-000000000000-floor-0-room-3"  # type: ignore[index]
    return json.dumps(document)


def _other_geometry(document: dict[str, object]) -> str:
    document["scenes"][0]["scene"]["walls"][0]["height_m"] += 0.1  # type: ignore[index]
    return json.dumps(document)


def _edited_scene(document: dict[str, object]) -> str:
    document["scenes"][0]["scene"]["revision"] = 3  # type: ignore[index]
    return json.dumps(document)


def _unknown_field(document: dict[str, object]) -> str:
    return json.dumps(document | {"poses": {}})


@pytest.mark.parametrize(
    ("damage", "name", "reason"),
    [
        (_not_json, f"{PLAN_ID}.json", "not a scene cache"),
        (_unknown_field, f"{PLAN_ID}.json", "not a scene cache"),
        (json.dumps, "plan-000000000000.json", "not the file's name"),
        (_another_plans_scene, f"{PLAN_ID}.json", "is not a room of"),
        (_other_geometry, f"{PLAN_ID}.json", "walls differ"),
        (_edited_scene, f"{PLAN_ID}.json", "revision 3"),
    ],
)
def test_an_unusable_cache_is_skipped_and_said_so(
    damage: Callable[[dict[str, object]], str],
    name: str,
    reason: str,
    tmp_path: Path,
    data_dir: Path,
    offline: None,
) -> None:
    document = json.loads(cache_path(COMMITTED, PLAN_ID).read_text())
    (tmp_path / name).write_text(damage(document))
    with started(tmp_path) as (client, problems):
        assert len(problems) == 1 and problems[0].startswith(f"{name}: ") and reason in problems[0]
        assert str(tmp_path) not in problems[0]  # no server paths
        assert PLAN_ID not in routes._plans
        assert client.get(f"/scenes/{SCENE_ID}").status_code == 404  # unknown, as before #12


def test_an_empty_or_missing_cache_directory_publishes_nothing(tmp_path: Path) -> None:
    assert restore_published(tmp_path) == [] and restore_published(tmp_path / "absent") == []


def test_a_file_that_cannot_be_read_is_skipped_by_kind_only(tmp_path: Path) -> None:
    (tmp_path / f"{PLAN_ID}.json").mkdir()  # not a file: reading it is an OSError
    assert restore_published(tmp_path) == [f"{PLAN_ID}.json: IsADirectoryError"]


@pytest.mark.parametrize(
    ("published_value", "found", "expected"),
    [
        ({"x": 1.0}, {"x": 1.0009}, []),
        ({"x": 1.0}, {"x": 1.002}, ["x"]),
        ({"a": {"b": [1, 2]}}, {"a": {"b": [1, 3]}}, ["a.b[1]"]),
        (
            {"items": [{"id": "sofa", "w": 1}]},
            {"items": [{"id": "sofa", "w": 2}]},
            ["items[sofa].w"],
        ),
        ({"items": [1]}, {"items": [1, 2]}, ["items (1 published, 2 found)"]),
        ({"x": 1}, {"y": 1}, ["(root) (fields)"]),
        ({"flag": True}, {"flag": 1}, ["flag"]),
        ({"name": "a"}, {"name": "b"}, ["name"]),
        ({"x": None}, {"x": 0.0}, ["x"]),
    ],
)
def test_differences_names_what_differs(
    published_value: object, found: object, expected: list[str]
) -> None:
    assert differences(published_value, found) == expected
