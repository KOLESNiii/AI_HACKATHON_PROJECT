import json
import math
from pathlib import Path

import pytest
from pydantic import ValidationError

from contracts.schema import AuditReport, FengShuiReport, LayoutProposal, Pose2D, RoomScene

MOCK_SCENE = Path(__file__).resolve().parent.parent / "contracts" / "mock_room" / "mock_scene.json"


def load_mock() -> RoomScene:
    return RoomScene.model_validate(json.loads(MOCK_SCENE.read_text()))


def test_mock_scene_validates_with_defaults() -> None:
    scene = load_mock()
    assert scene.revision == 0
    assert len({item.id for item in scene.furniture}) == len(scene.furniture)
    for item in scene.furniture:
        assert item.is_proxy is False
        assert item.dimension_source == "estimated"
        assert item.needs_correction is False
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


def test_mock_shell_door_gap_follows_swing_rule() -> None:
    trimesh = pytest.importorskip("trimesh")
    import numpy as np

    shell = Path(__file__).resolve().parent.parent / "frontend/public/mock_room/shell.glb"
    if not shell.exists():
        pytest.skip("run scripts/generate_mock_glbs.py first")
    parts = [p.bounds for p in trimesh.load(shell, force="mesh").split(only_watertight=False)]

    def solid(x: float, y: float, z: float) -> bool:
        p = np.array([x, y, z])
        return any(np.all(p >= lo - 1e-6) and np.all(p <= hi + 1e-6) for lo, hi in parts)

    # door_1: hinge (0.4, 0) on w_north, clockwise into the room => opening spans x 0.4..1.25.
    assert not solid(0.8, 1.0, -0.07)
    assert solid(0.2, 1.0, -0.07) and solid(1.3, 1.0, -0.07)
