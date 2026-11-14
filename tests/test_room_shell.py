"""Room shell `.glb` generator (Dev 1, issue #7): shell rules from contracts/schema.py, openings,
mitred corners on non-rectangular rooms, the parsed example plans, and the shell route."""

from __future__ import annotations

import math
import os
import subprocess
import sys
import textwrap
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
from services.reconstruction.room.shell import (  # noqa: E402
    SLAB_M,
    build_shell,
    shell_glb,
    wall_ends,
    wall_sections,
)
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


RAY = np.array([1.0, 0.0137, 0.0071])  # skewed so it never runs exactly along an edge or face
RAY /= np.linalg.norm(RAY)


def _inside(mesh: trimesh.Trimesh, p: np.ndarray) -> bool:
    """Ray parity in plain numpy (Moller-Trumbore), so the probes need no SciPy or rtree. Wall
    pieces touch but never overlap, so parity over a whole wall node is exact."""
    tri = mesh.triangles
    v0, e1, e2 = tri[:, 0], tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]
    h = np.cross(RAY, e2)
    a = np.einsum("ij,ij->i", e1, h)
    ok = np.abs(a) > 1e-12
    f = np.zeros_like(a)
    f[ok] = 1.0 / a[ok]
    s = p - v0
    u = f * np.einsum("ij,ij->i", s, h)
    q = np.cross(s, e1)
    v = f * (q @ RAY)
    t = f * np.einsum("ij,ij->i", e2, q)
    hits = ok & (u >= 0) & (u <= 1) & (v >= 0) & (u + v <= 1) & (t > 1e-9)
    return int(hits.sum()) % 2 == 1


def solid(shell: trimesh.Scene, x: float, y: float, z: float) -> bool:
    """True when (x, y, z) lies inside any wall node of the exported shell meshes."""
    p = np.array([x, y, z], dtype=np.float64)
    return any(
        _inside(shell.geometry[shell.graph[node][1]], p)
        for node in shell.graph.nodes_geometry
        if node.startswith("wall_")
    )


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


# --- review on #41 ----------------------------------------------------------------------------


def invalid_footprints(scene: RoomScene) -> list[str]:
    """Every wall section's footprint must be a simple, convex polygon with positive area."""
    bad = []
    for frame, o_start, o_end in wall_ends(scene):
        for sec in wall_sections(scene, frame, o_start, o_end):
            q = sec.poly
            n = len(q)
            turns = [
                (q[(i + 1) % n][0] - q[i][0]) * (q[(i + 2) % n][1] - q[(i + 1) % n][1])
                - (q[(i + 1) % n][1] - q[i][1]) * (q[(i + 2) % n][0] - q[(i + 1) % n][0])
                for i in range(n)
            ]
            convex = all(t > -1e-12 for t in turns) or all(t < 1e-12 for t in turns)
            area = abs(sum(q[i - 1][0] * q[i][1] - q[i][0] * q[i - 1][1] for i in range(n))) / 2
            if n < 3 or not convex or area <= 1e-8 or sec.y1 <= sec.y0:
                bad.append(f"{frame.wall.id}: {q.round(3).tolist()} y {sec.y0}..{sec.y1}")
    return bad


def test_short_section_at_reflex_corner_is_a_valid_footprint() -> None:
    """Reviewer's case: a door on w3 starting 0.1 m from the L's reflex corner, shorter than the
    0.2 m miter offset there, used to produce a crossed quad."""
    scene = make_scene(
        [(0, 0), (4, 0), (4, 2), (2, 2), (2, 4), (0, 4)],
        doors=[
            {
                "id": "d0",
                "wall_id": "w3",
                "hinge_pos": {"x": 2.0, "z": 2.1},
                "width_m": 0.8,
                "swing_clockwise": True,
                "swings_into_room": True,
            }
        ],
    )
    assert invalid_footprints(scene) == []
    shell = build_shell(scene)
    assert not solid(shell, 2.1, 1.0, 2.5)  # through the door (w3 spans t 0.1..0.9)
    assert solid(shell, 2.1, 2.3, 2.5)  # lintel
    assert not solid(shell, 1.97, 1.0, 2.05)  # nothing inside the reflex corner
    assert solid(shell, 2.15, 1.0, 2.05)  # the corner block outside the room is closed


@pytest.mark.parametrize(
    "image,fixture", [("one_floor.jpg", "one_floor"), ("three_floor.png", "three_floor")]
)
def test_example_plans_have_no_invalid_footprints(image: str, fixture: str) -> None:
    path = ROOT / "examples" / image
    if not path.exists():
        pytest.skip("example plan missing")
    ann = PlanAnnotations.model_validate_json(
        (ROOT / f"services/reconstruction/room/fixtures/{fixture}.annotations.json").read_text()
    )
    plan = parse_floor_plan([(path.read_bytes(), "image/png")], FixedAnnotator(ann))
    bad = [
        f"{room.room_id} {b}"
        for f in plan.floors
        for room in f.rooms
        for b in invalid_footprints(room.scene)
    ]
    assert bad == []


def _window(wall: str, offset: float, width: float, sill: float) -> dict[str, object]:
    return {
        "id": f"win{offset}",
        "wall_id": wall,
        "offset_along_wall_m": offset,
        "width_m": width,
        "sill_height_m": sill,
        "head_height_m": 2.1,
        "plan_normal_deg": 0.0,
    }


def test_adjacent_openings_keep_their_own_heights() -> None:
    """Windows at t 1..2 (sill 0.9) and t 2..3 (sill 1.4) on w0 (z = 0, running +X)."""
    scene = make_scene(
        [(0, 0), (4, 0), (4, 3), (0, 3)],
        windows=[_window("w0", 1.0, 1.0, 0.9), _window("w0", 2.0, 1.0, 1.4)],
    )
    shell = build_shell(scene)
    assert solid(shell, 2.5, 1.1, -0.1)  # under the higher window: still wall
    assert not solid(shell, 1.5, 1.1, -0.1)  # the lower window
    assert not solid(shell, 2.5, 1.6, -0.1)  # the higher window
    assert solid(shell, 1.5, 0.5, -0.1) and solid(shell, 2.5, 2.3, -0.1)
    assert invalid_footprints(scene) == []


def test_door_next_to_window_keeps_the_wall_under_the_window() -> None:
    """Door gap t 1.0..1.8 (hinge (1, 0), clockwise into the room), window t 1.8..2.8."""
    scene = make_scene(
        [(0, 0), (4, 0), (4, 3), (0, 3)],
        windows=[_window("w0", 1.8, 1.0, 0.9)],
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
    shell = build_shell(scene)
    assert solid(shell, 2.3, 0.5, -0.1)  # under the window
    assert not solid(shell, 2.3, 1.5, -0.1)  # the window
    assert not solid(shell, 1.4, 0.05, -0.1) and not solid(shell, 1.4, 1.5, -0.1)  # the door
    assert solid(shell, 1.4, 2.3, -0.1)  # door lintel


def test_every_node_is_closed_and_outward_facing(rect: RoomScene) -> None:
    shell = build_shell(rect)
    for node in shell.graph.nodes_geometry:
        mesh = shell.geometry[shell.graph[node][1]]
        assert mesh.is_winding_consistent, node
        assert mesh.volume > 0, node


def test_shell_build_needs_no_optional_geometry_packages() -> None:
    """The reconstruction extra has no SciPy, networkx, rtree or shapely; shell generation must
    work without them (review on #41)."""
    script = textwrap.dedent(
        """
        import importlib.abc, sys

        class Block(importlib.abc.MetaPathFinder):
            def find_spec(self, name, path=None, target=None):
                if name.split(".")[0] in {"scipy", "networkx", "rtree", "shapely"}:
                    raise ImportError("blocked " + name)
                return None

        sys.meta_path.insert(0, Block())
        from tests.test_room_shell import make_scene
        from services.reconstruction.room.shell import shell_glb

        for pts in ([(0, 0), (4, 0), (4, 3), (0, 3)],
                    [(0, 0), (4, 0), (4, 2), (2, 2), (2, 4), (0, 4)]):
            assert shell_glb(make_scene(pts)).startswith(b"glTF")
        print("ok")
        """
    )
    env = {**os.environ, "PYTHONPATH": str(ROOT)}
    res = subprocess.run(
        [sys.executable, "-c", script], cwd=ROOT, env=env, capture_output=True, text=True
    )
    assert res.returncode == 0 and res.stdout.strip().endswith("ok"), res.stderr[-2000:]


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
