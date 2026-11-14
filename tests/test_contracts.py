import importlib.util
import json
import math
from pathlib import Path

import pytest
from pydantic import ValidationError

from contracts.schema import (
    GLB_BBOX_TOLERANCE_M,
    AuditReport,
    FengShuiReport,
    LayoutProposal,
    Pose2D,
    RoomScene,
)

ROOT = Path(__file__).resolve().parent.parent
MOCK_SCENE = ROOT / "contracts" / "mock_room" / "mock_scene.json"
MOCK_ASSETS = ROOT / "frontend" / "public" / "mock_room"


def load_mock() -> RoomScene:
    return RoomScene.model_validate(json.loads(MOCK_SCENE.read_text()))


def test_unassessed_audit_fields_round_trip_as_null() -> None:
    report = AuditReport(scene_id="room", scene_revision=3, collisions=[], blocked_doors=[])
    raw = report.model_dump()
    for field in (
        "overall_score",
        "walkable_floor_ratio",
        "glare_alerts",
        "feng_shui",
        "glare_orientation_grounded",
    ):
        assert field in raw and raw[field] is None
    assert AuditReport.model_validate_json(report.model_dump_json()) == report


@pytest.mark.parametrize("grounded", [True, False])
def test_assessed_audit_fields_remain_backwards_compatible(grounded: bool) -> None:
    report = AuditReport(
        scene_id="room",
        scene_revision=0,
        collisions=[],
        blocked_doors=[],
        overall_score=80,
        walkable_floor_ratio=0.7,
        glare_orientation_grounded=grounded,
        glare_alerts=[],
        feng_shui=FengShuiReport(score=60, sightlines=[]),
    )
    restored = AuditReport.model_validate_json(report.model_dump_json())
    assert restored == report
    assert restored.glare_orientation_grounded is grounded


def test_mock_scene_validates_with_defaults() -> None:
    scene = load_mock()
    assert scene.revision == 0
    assert len({item.id for item in scene.furniture}) == len(scene.furniture)
    proxies = {item.id for item in scene.furniture if item.is_proxy}
    assert proxies == {"vid-desk-01", "vid-chair-01", "vid-table-01", "fix-radiator-01"}
    for item in scene.furniture:
        assert item.dimension_source == "estimated"
        assert item.correction_needed == []
    assert all(door.swings_into_room for door in scene.doors)


def test_mock_scene_lists_every_field() -> None:
    """schema.ts treats every non-nullable field as present, so the fixture must include them."""

    def missing(raw: object, dumped: object, path: str = "") -> list[str]:
        if isinstance(dumped, dict) and isinstance(raw, dict):
            out = []
            for key, value in dumped.items():
                if key not in raw:
                    if value is not None:
                        out.append(f"{path}.{key}")
                else:
                    out += missing(raw[key], value, f"{path}.{key}")
            return out
        if isinstance(dumped, list) and isinstance(raw, list):
            return [
                m
                for i, (r, d) in enumerate(zip(raw, dumped))
                for m in missing(r, d, f"{path}[{i}]")
            ]
        return []

    raw = json.loads(MOCK_SCENE.read_text())
    assert missing(raw, load_mock().model_dump()) == []


def test_scene_rules_are_validated() -> None:
    raw = json.loads(MOCK_SCENE.read_text())
    with pytest.raises(ValidationError, match="clockwise"):
        RoomScene.model_validate({**raw, "floor_polygon": raw["floor_polygon"][::-1]})
    flipped = [{**w, "start": w["end"], "end": w["start"]} for w in raw["walls"]]
    with pytest.raises(ValidationError, match="side"):
        RoomScene.model_validate({**raw, "walls": flipped})

    item = raw["furniture"][0]
    with pytest.raises(ValidationError):  # repo-relative paths are not fetchable URLs
        RoomScene.model_validate(
            {**raw, "furniture": [{**item, "glb_url": "services/reconstruction/x.glb"}]}
        )
    scene = RoomScene.model_validate(
        {**raw, "furniture": [{**item, "dimension_source": "catalog"}]}
    )
    assert scene.furniture[0].dimension_source == "catalog"


def test_mock_window_bearing_matches_its_wall() -> None:
    """plan_normal_deg is derived from the wall's outward normal (dz, -dx)."""
    scene = load_mock()
    walls = {w.id: w for w in scene.walls}
    for window in scene.windows:
        w = walls[window.wall_id]
        dx, dz = w.end.x - w.start.x, w.end.z - w.start.z
        # Bearing of direction (x, z) is atan2(x, -z), clockwise from -Z.
        bearing = math.degrees(math.atan2(dz, dx)) % 360
        diff = (window.plan_normal_deg - bearing + 180) % 360 - 180
        assert math.isclose(diff, 0, abs_tol=1e-6)
        assert window.compass_azimuth_deg is None  # no compass in the mock


def test_audit_report_must_echo_scene() -> None:
    base = {
        "overall_score": 80,
        "walkable_floor_ratio": 0.6,
        "glare_orientation_grounded": False,
        "collisions": [],
        "blocked_doors": [],
        "glare_alerts": [],
        "feng_shui": {"score": 50, "sightlines": []},
    }
    with pytest.raises(ValidationError):
        AuditReport.model_validate(base)
    report = AuditReport.model_validate({**base, "scene_id": "s", "scene_revision": 4})
    assert report.clearance_issues == []
    assert report.out_of_bounds_item_ids == []


def test_field_docstrings_reach_openapi() -> None:
    props = RoomScene.model_json_schema()["properties"]
    assert "stale responses" in props["revision"]["description"]


def test_yaw_and_plan_bearing_conventions_agree() -> None:
    def yaw_front(yaw: float) -> tuple[float, float]:
        return math.sin(math.radians(yaw)), math.cos(math.radians(yaw))

    def bearing_dir(bearing: float) -> tuple[float, float]:
        return math.sin(math.radians(bearing)), -math.cos(math.radians(bearing))

    for yaw, expected in [(0, (0, 1)), (90, (1, 0)), (180, (0, -1)), (270, (-1, 0))]:
        assert all(math.isclose(a, b, abs_tol=1e-9) for a, b in zip(yaw_front(yaw), expected))
        bearing = (180 - yaw) % 360
        assert all(math.isclose(a, b, abs_tol=1e-9) for a, b in zip(bearing_dir(bearing), expected))

    # The mock south-wall window faces +Z, which is bearing 180 and yaw 0.
    window = load_mock().windows[0]
    assert window.plan_normal_deg == 180.0


def test_layout_proposal_round_trips() -> None:
    scene = load_mock()
    report = AuditReport(
        scene_id=scene.scene_id,
        scene_revision=3,
        overall_score=90,
        walkable_floor_ratio=0.7,
        glare_orientation_grounded=False,
        collisions=[],
        blocked_doors=[],
        glare_alerts=[],
        feng_shui=FengShuiReport(score=60, sightlines=[]),
    )
    proposal = LayoutProposal(
        proposal_id="p1",
        poses={"item_desk": Pose2D(x=1.0, z=2.0, yaw_deg=90)},
        report=report,
        improved=True,
    )
    assert LayoutProposal.model_validate_json(proposal.model_dump_json()) == proposal


def load_generator():
    spec = importlib.util.spec_from_file_location("gen", ROOT / "scripts" / "generate_mock_glbs.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def solid_at(mesh, x: float, y: float, z: float) -> bool:
    """True when the point lies inside one of the mesh's boxes (all mock parts are boxes)."""
    import numpy as np

    p = np.array([x, y, z])
    return any(
        np.all(p >= lo - 1e-6) and np.all(p <= hi + 1e-6)
        for lo, hi in (part.bounds for part in mesh.split(only_watertight=False))
    )


def test_mock_glbs_follow_contract() -> None:
    trimesh = pytest.importorskip("trimesh")
    import numpy as np

    if not (MOCK_ASSETS / "shell.glb").exists():
        pytest.skip("run scripts/generate_mock_glbs.py first")
    scene = load_mock()

    for item in scene.furniture:
        mesh = trimesh.load(MOCK_ASSETS / Path(item.glb_url).name, force="mesh")
        b = item.bbox_m
        expected = [[-b.width / 2, 0, -b.depth / 2], [b.width / 2, b.height, b.depth / 2]]
        assert np.allclose(mesh.bounds, expected, atol=GLB_BBOX_TOLERANCE_M)

    shell = trimesh.load(MOCK_ASSETS / "shell.glb")
    nodes = set(shell.graph.nodes_geometry)
    assert nodes == {"floor", "ceiling"} | {f"wall_{w.id}" for w in scene.walls}
    for node in nodes:
        transform, _ = shell.graph[node]
        assert np.allclose(transform, np.eye(4))

    # door_1: hinge (0.4, 0) on w_north, clockwise into the room => opening spans x 0.4..1.25.
    north = shell.geometry[shell.graph["wall_w_north"][1]]
    assert not solid_at(north, 0.8, 1.0, -0.07)
    assert solid_at(north, 0.2, 1.0, -0.07) and solid_at(north, 1.3, 1.0, -0.07)


def test_mock_shell_supports_l_shaped_rooms() -> None:
    pytest.importorskip("trimesh")
    gen = load_generator()
    pts = [(0, 0), (4, 0), (4, 2), (2, 2), (2, 4), (0, 4)]  # reflex corner at (2, 2)
    walls = [
        {
            "id": f"w{i}",
            "start": {"x": x0, "z": z0},
            "end": {"x": x1, "z": z1},
            "height_m": 2.6,
            "thickness_m": 0.15,
        }
        for i, ((x0, z0), (x1, z1)) in enumerate(zip(pts, pts[1:] + pts[:1]))
    ]
    scene = RoomScene(
        scene_id="l",
        shell_glb_url="/l.glb",
        floor_polygon=[{"x": x, "z": z} for x, z in pts],
        walls=walls,
        windows=[],
        doors=[],
        furniture=[],
    )
    shell = gen.shell_scene(scene.model_dump())
    walls_mesh = [shell.geometry[f"wall_w{i}"] for i in range(len(pts))]

    def solid(x: float, z: float) -> bool:
        return any(solid_at(m, x, 1.0, z) for m in walls_mesh)

    assert not solid(1.95, 2.05)  # just inside the reflex corner: no wall poking into the room
    assert solid(2.07, 2.07)  # the reflex corner is closed outside the room
    assert solid(-0.07, -0.07) and solid(4.07, 2.07)  # convex outer corners are closed
