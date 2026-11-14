"""Room shell `.glb` generator (Dev 1, issue #7): shell rules from contracts/schema.py, openings,
mitred corners on non-rectangular rooms, the parsed example plans, and the shell route."""

from __future__ import annotations

import math
from collections.abc import Iterator
from pathlib import Path

import pytest

trimesh = pytest.importorskip("trimesh")
cv2 = pytest.importorskip("cv2")
np = pytest.importorskip("numpy")

from fastapi.testclient import TestClient  # noqa: E402

from contracts.schema import ParsedFloorPlan, RoomScene  # noqa: E402
from services.reconstruction.main import app  # noqa: E402
from services.reconstruction.room.annotate import FixedAnnotator, PlanAnnotations  # noqa: E402
from services.reconstruction.room.parse import parse_floor_plan  # noqa: E402
from services.reconstruction.room.routes import get_annotator  # noqa: E402
from services.reconstruction.room.shell import SLAB_M, build_shell, shell_glb  # noqa: E402
from tests.test_room_parse import _label, _png, single_room  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
H = 2.6


def make_scene(
    pts: list[tuple[float, float]],
    thickness: float | list[float] = 0.2,
    windows: list[dict[str, object]] | None = None,
    doors: list[dict[str, object]] | None = None,
) -> RoomScene:
    n = len(pts)
    th = thickness if isinstance(thickness, list) else [thickness] * n
    walls = [
        {
            "id": f"w{i}",
            "start": {"x": pts[i][0], "z": pts[i][1]},
            "end": {"x": pts[(i + 1) % n][0], "z": pts[(i + 1) % n][1]},
            "height_m": H,
            "thickness_m": th[i],
        }
        for i in range(n)
    ]
    return RoomScene.model_validate(
        {
            "scene_id": "t",
            "shell_glb_url": "/t.glb",
            "floor_polygon": [{"x": x, "z": z} for x, z in pts],
            "walls": walls,
            "windows": windows or [],
            "doors": doors or [],
            "furniture": [],
        }
    )


def _bodies(shell: trimesh.Scene) -> list[trimesh.Trimesh]:
    out = []
    for node in shell.graph.nodes_geometry:
        if node.startswith("wall_"):
            out += shell.geometry[shell.graph[node][1]].split(only_watertight=False)
    return out


def solid(shell: trimesh.Scene, x: float, y: float, z: float) -> bool:
    """True when (x, y, z) lies inside a wall. Every wall piece is a vertical prism, so test its
    height range and its plan footprint (convex hull of its vertices)."""
    for body in _bodies(shell):
        lo, hi = body.bounds
        if not lo[1] - 1e-6 <= y <= hi[1] + 1e-6:
            continue
        hull = cv2.convexHull(body.vertices[:, [0, 2]].astype(np.float32))
        if cv2.pointPolygonTest(hull, (float(x), float(z)), True) >= -1e-4:
            return True
    return False


def corner_probes(scene: RoomScene, y: float = 1.0) -> list[tuple[str, bool]]:
    """Per vertex: just outside along the outward bisector must be wall; just inside must not."""
    pts = [(p.x, p.z) for p in scene.floor_polygon]
    th = {(w.start.x, w.start.z): w.thickness_m for w in scene.walls}
    shell = build_shell(scene)
    out = []
    n = len(pts)
    for i in range(n):
        prev, v, nxt = np.array(pts[i - 1]), np.array(pts[i]), np.array(pts[(i + 1) % n])
        normals = []
        for a, b in ((prev, v), (v, nxt)):
            d = (b - a) / np.linalg.norm(b - a)
            normals.append(np.array([d[1], -d[0]]))
        bis = normals[0] + normals[1]
        bis /= np.linalg.norm(bis)
        t = min(th[tuple(prev)], th[tuple(v)])
        o = v + bis * t * 0.5
        inside = v - bis * 0.03
        out.append((f"outside {v}", solid(shell, o[0], y, o[1])))
        out.append((f"inside {v}", not solid(shell, inside[0], y, inside[1])))
    return out


# --- rules ------------------------------------------------------------------------------------


@pytest.fixture(scope="module")
def rect() -> RoomScene:
    """4 x 3 m. Door on w0 (z = 0): hinge (1.0, 0), clockwise into the room, so the closed leaf
    runs +X and the gap is x 1.0..1.8. Window on w2 (z = 3, runs 4 -> 0): offset 1.0, width
    1.5, so x 3.0..1.5, sill 0.9, head 2.1."""
    return make_scene(
        [(0, 0), (4, 0), (4, 3), (0, 3)],
        windows=[
            {
                "id": "win0",
                "wall_id": "w2",
                "offset_along_wall_m": 1.0,
                "width_m": 1.5,
                "plan_normal_deg": 180.0,
            }
        ],
        doors=[
            {
                "id": "d0",
                "wall_id": "w0",
                "hinge_pos": {"x": 1.0, "z": 0.0},
                "width_m": 0.8,
                "swing_clockwise": True,
                "swings_into_room": True,
            }
        ],
    )


def test_nodes_frame_and_bounds(rect: RoomScene) -> None:
    shell = build_shell(rect)
    walls = {f"wall_w{i}" for i in range(4)}
    assert set(shell.graph.nodes_geometry) == {"floor", "ceiling"} | walls
    for node in shell.graph.nodes_geometry:
        transform, _ = shell.graph[node]
        assert np.allclose(transform, np.eye(4))
    assert np.allclose(shell.bounds, [[-0.2, -SLAB_M, -0.2], [4.2, H + SLAB_M, 3.2]], atol=1e-6)
    floor = shell.geometry[shell.graph["floor"][1]]
    assert math.isclose(floor.bounds[1][1], 0.0, abs_tol=1e-9)  # floor top at Y = 0
    ceiling = shell.geometry[shell.graph["ceiling"][1]]
    assert math.isclose(ceiling.bounds[0][1], H, abs_tol=1e-9)


def test_door_opening(rect: RoomScene) -> None:
    shell = build_shell(rect)
    assert not solid(shell, 1.4, 1.0, -0.1)  # through the door
    assert not solid(shell, 1.4, 0.01, -0.1)  # down to the floor
    assert solid(shell, 1.4, 2.3, -0.1)  # lintel above head height 2.05
    assert solid(shell, 0.5, 1.0, -0.1) and solid(shell, 2.2, 1.0, -0.1)  # either side


def test_window_opening(rect: RoomScene) -> None:
    shell = build_shell(rect)
    assert solid(shell, 2.25, 0.5, 3.1)  # below the sill
    assert not solid(shell, 2.25, 1.5, 3.1)  # the glazing gap
    assert solid(shell, 2.25, 2.4, 3.1)  # above the head
    assert solid(shell, 1.0, 1.5, 3.1) and solid(shell, 3.5, 1.5, 3.1)  # either side


def test_glb_round_trip_keeps_nodes(rect: RoomScene) -> None:
    loaded = trimesh.load(trimesh.util.wrap_as_stream(shell_glb(rect)), file_type="glb")
    assert set(loaded.graph.nodes_geometry) == {"floor", "ceiling"} | {
        f"wall_w{i}" for i in range(4)
    }


# --- corners ----------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "pts,thickness",
    [
        ([(0, 0), (4, 0), (4, 3), (0, 3)], 0.2),
        ([(0, 0), (4, 0), (4, 2), (2, 2), (2, 4), (0, 4)], 0.15),  # reflex corner at (2, 2)
        ([(0, 0), (4, 0), (4, 2), (3, 3), (0, 3)], 0.2),  # 45-degree bay
        ([(0, 0), (4, 0), (4, 3), (0, 3)], [0.3, 0.1, 0.2, 0.1]),  # mixed thickness
    ],
    ids=["rectangle", "l-shape", "bay", "mixed-thickness"],
)
def test_corners_closed_outside_and_clear_inside(
    pts: list[tuple[float, float]], thickness: float | list[float]
) -> None:
    failures = [name for name, ok in corner_probes(make_scene(pts, thickness)) if not ok]
    assert not failures, failures


def test_l_shape_reflex_corner_matches_mock_rule() -> None:
    shell = build_shell(make_scene([(0, 0), (4, 0), (4, 2), (2, 2), (2, 4), (0, 4)], 0.15))
    assert not solid(shell, 1.95, 1.0, 2.05)  # just inside the reflex corner
    assert solid(shell, 2.07, 1.0, 2.07)  # the reflex corner is closed outside the room


# --- parsed plans and route -------------------------------------------------------------------


@pytest.mark.parametrize(
    "image,fixture",
    [("one_floor.jpg", "one_floor"), ("three_floor.png", "three_floor")],
)
def test_every_parsed_room_gets_a_valid_shell(image: str, fixture: str) -> None:
    path = ROOT / "examples" / image
    if not path.exists():
        pytest.skip("example plan missing")
    ann = PlanAnnotations.model_validate_json(
        (ROOT / f"services/reconstruction/room/fixtures/{fixture}.annotations.json").read_text()
    )
    plan = parse_floor_plan([(path.read_bytes(), "image/png")], FixedAnnotator(ann))
    for floor in plan.floors:
        for room in floor.rooms:
            sc = room.scene
            loaded = trimesh.load(trimesh.util.wrap_as_stream(shell_glb(sc)), file_type="glb")
            assert set(loaded.graph.nodes_geometry) == {"floor", "ceiling"} | {
                f"wall_{w.id}" for w in sc.walls
            }
            lo, hi = loaded.bounds
            xs, zs = [p.x for p in sc.floor_polygon], [p.z for p in sc.floor_polygon]
            assert lo[0] <= min(xs) and hi[0] >= max(xs) and lo[2] <= min(zs) and hi[2] >= max(zs)
            assert math.isclose(lo[1], -SLAB_M, abs_tol=1e-6)


@pytest.fixture()
def client() -> Iterator[TestClient]:
    ann = PlanAnnotations(rooms=[_label("Studio", 400, 350, 4.0, 3.0)])
    app.dependency_overrides[get_annotator] = lambda: FixedAnnotator(ann)
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_shell_route_serves_the_scene_url(client: TestClient) -> None:
    files = [("files", ("plan.png", _png(single_room()), "image/png"))]
    plan = ParsedFloorPlan.model_validate(client.post("/floor-plans", files=files).json())
    scene = plan.floors[0].rooms[0].scene
    # The editor fetches shell_glb_url; Vite strips /api/reconstruction before the service.
    assert scene.shell_glb_url.startswith("/api/reconstruction/shells/")
    res = client.get(scene.shell_glb_url.removeprefix("/api/reconstruction"))
    assert res.status_code == 200
    assert res.headers["content-type"] == "model/gltf-binary"
    assert "immutable" in res.headers["cache-control"]
    loaded = trimesh.load(trimesh.util.wrap_as_stream(res.content), file_type="glb")
    assert "wall_w0" in loaded.graph.nodes_geometry
    again = client.get(scene.shell_glb_url.removeprefix("/api/reconstruction"))
    assert again.content == res.content
    assert client.get("/shells/plan-unknown-floor-0-room-0.glb").status_code == 404
