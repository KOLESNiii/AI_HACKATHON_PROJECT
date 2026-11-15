"""HTTP integration for the audit contract and shared frontend handoff cases."""

import json
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from contracts.schema import AuditReport, RoomScene
from services.spatial_engine.main import app
from services.spatial_engine.reachability import calculate_reachable_floor_ratio
from services.spatial_engine.report import audit_scene

ROOT = Path(__file__).resolve().parents[2]
PACK = json.loads((ROOT / "services/spatial_engine/fixtures/audit_cases.json").read_text("utf-8"))


def payload() -> dict[str, Any]:
    return json.loads((ROOT / PACK["base_scene"]).read_text("utf-8"))


@pytest.mark.parametrize("case", PACK["cases"], ids=lambda case: case["id"])
def test_shared_cases_through_http(case: dict[str, Any]) -> None:
    body = payload()
    for item in body["furniture"]:
        if item["id"] in case["pose_overrides"]:
            item["pose"] = case["pose_overrides"][item["id"]]
    body["revision"] = case["revision"]
    with TestClient(app) as client:
        response = client.post("/audit", json=body, headers={"Origin": "http://localhost:5173"})
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "*"
    report = AuditReport.model_validate(response.json())
    assert report.scene_id == body["scene_id"]
    assert report.scene_revision == body["revision"]
    assert report.out_of_bounds_item_ids == case["expected"]["out_of_bounds_item_ids"]
    assert [issue.model_dump() for issue in report.blocked_doors] == case["expected"][
        "blocked_doors"
    ]
    expected = case["expected"]["collisions"]
    assert [(issue.item_a, issue.item_b) for issue in report.collisions] == [
        (issue["item_a"], issue["item_b"]) for issue in expected
    ]
    assert [issue.overlap_area_m2 for issue in report.collisions] == pytest.approx(
        [issue["overlap_area_m2"] for issue in expected], abs=1e-9
    )
    assert report.walkable_floor_ratio == pytest.approx(
        calculate_reachable_floor_ratio(RoomScene.model_validate(body))
    )


@pytest.mark.parametrize("compass", [None, 0, 45, 270])
def test_unassessed_checks_stay_null_and_feng_shui_ignores_the_compass(
    compass: float | None,
) -> None:
    body = payload()
    body["north_compass_deg"] = compass
    with TestClient(app) as client:
        response = client.post("/audit", json=body)
    assert response.status_code == 200
    report = response.json()
    assert report["overall_score"] is None
    # Feng shui is judged from door and furniture geometry only, so north does not matter.
    assert report["feng_shui"]["score"] == 100
    assert {x["status"] for x in report["feng_shui"]["sightlines"]} == {"command_position"}
    assert report["glare_alerts"] is None
    assert report["glare_orientation_grounded"] is None


def test_report_contains_clearance_findings_and_does_not_mutate_input() -> None:
    scene = RoomScene.model_validate(payload())
    before = scene.model_dump()
    report = audit_scene(scene)
    assert scene.model_dump() == before
    assert [(issue.item_id, issue.blocked_by_item_id) for issue in report.clearance_issues] == [
        ("item_bed", "item_wardrobe")
    ]
    assert report.clearance_issues[0].actual_m == pytest.approx(0.25)
    assert AuditReport.model_validate_json(report.model_dump_json()) == report


@pytest.mark.parametrize(
    "case",
    [
        "negative_width",
        "invalid_height",
        "duplicate_item",
        "unknown_wall",
        "bad_door",
        "negative_clearance",
        "self_intersection",
        "invalid_parts",
        "missing_field",
    ],
)
def test_invalid_scenes_return_actionable_422(case: str) -> None:
    body = payload()
    if case == "negative_width":
        body["furniture"][0]["bbox_m"]["width"] = -1
    elif case == "invalid_height":
        body["furniture"][0]["bbox_m"]["height"] = 0
    elif case == "duplicate_item":
        body["furniture"].append(body["furniture"][0])
    elif case == "unknown_wall":
        body["doors"][0]["wall_id"] = "missing"
    elif case == "bad_door":
        body["doors"][0]["width_m"] = 0
    elif case == "negative_clearance":
        body["furniture"][0]["requires_front_clear_m"] = -1
    elif case == "self_intersection":
        body["walls"] = []
        body["floor_polygon"] = [{"x": x, "z": z} for x, z in [(0, 0), (4, 4), (0, 4), (3, 0)]]
    elif case == "invalid_parts":
        body["furniture"][1]["collision_parts"][0]["width"] = -1
    else:
        del body["scene_id"]
    with TestClient(app) as client:
        response = client.post("/audit", json=body)
    assert response.status_code == 422
    for error in response.json()["detail"]:
        assert error["loc"][0] == "body"
        assert isinstance(error["msg"], str) and error["msg"]
        assert "input" not in error and "ctx" not in error


@pytest.mark.parametrize("case", ["pose", "part"])
def test_nonfinite_values_do_not_break_error_serialization(case: str) -> None:
    body = payload()
    if case == "pose":
        body["furniture"][0]["pose"]["x"] = float("inf")
    else:
        body["furniture"][1]["collision_parts"][0]["x"] = float("nan")
    # Exercise malicious/non-standard JSON that Python's parser accepts; httpx's
    # json= encoder correctly rejects these values before making a request.
    with TestClient(app) as client:
        response = client.post(
            "/audit", content=json.dumps(body), headers={"Content-Type": "application/json"}
        )
    assert response.status_code == 422
    assert isinstance(response.json()["detail"], list)


def test_bad_json_and_missing_body_are_422() -> None:
    with TestClient(app) as client:
        for response in (client.post("/audit"), client.post("/audit", content="{")):
            assert response.status_code == 422


def test_revision_echo_does_not_reuse_previous_report() -> None:
    body = payload()
    with TestClient(app) as client:
        first = client.post("/audit", json=body).json()
        body["revision"] = 7
        body["scene_id"] = "another-room"
        second = client.post("/audit", json=body).json()
    assert first["scene_revision"] == 0
    assert second["scene_revision"] == 7 and second["scene_id"] == "another-room"


def test_openapi_exposes_shared_models_and_nullable_scores() -> None:
    with TestClient(app) as client:
        document = client.get("/openapi.json").json()
    operation = document["paths"]["/audit"]["post"]
    assert operation["requestBody"]["content"]["application/json"]["schema"]["$ref"].endswith(
        "/RoomScene"
    )
    assert operation["responses"]["200"]["content"]["application/json"]["schema"]["$ref"].endswith(
        "/AuditReport"
    )
    properties = document["components"]["schemas"]["AuditReport"]["properties"]
    for field in (
        "overall_score",
        "feng_shui",
        "glare_alerts",
        "walkable_floor_ratio",
        "glare_orientation_grounded",
    ):
        assert {"type": "null"} in properties[field]["anyOf"]


@pytest.mark.parametrize("error_type", [RuntimeError, TypeError, IndexError, ValueError])
def test_unexpected_errors_are_failures_not_clean_reports(
    monkeypatch: pytest.MonkeyPatch, error_type: type[Exception]
) -> None:
    def fail(_scene: RoomScene) -> AuditReport:
        raise error_type("private internal error")

    monkeypatch.setattr("services.spatial_engine.main.audit_scene", fail)
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.post("/audit", json=payload())
    assert response.status_code == 500
    assert "private internal error" not in response.text
    assert response.json()["detail"][0]["type"] == "internal_error"


def test_no_doors_keeps_independent_findings_available() -> None:
    body = payload()
    body["doors"] = []
    body["furniture"][0]["pose"]["x"] = -1
    wardrobe = next(item for item in body["furniture"] if item["id"] == "item_wardrobe")
    wardrobe["pose"] = {"x": 2.1, "z": 2.5, "yaw_deg": 0}
    with TestClient(app) as client:
        response = client.post("/audit", json=body)
    assert response.status_code == 200
    report = response.json()
    assert report["walkable_floor_ratio"] is None
    assert report["collisions"]
    assert report["out_of_bounds_item_ids"] == ["item_bed"]
    assert report["clearance_issues"]
    assert report["blocked_doors"] == []
    assert report["scene_id"] == body["scene_id"] and report["scene_revision"] == 0


def test_geometry_library_errors_are_safe_422(monkeypatch: pytest.MonkeyPatch) -> None:
    from shapely.errors import GEOSException

    def fail(_scene: RoomScene) -> AuditReport:
        raise GEOSException("private internal geometry data")

    monkeypatch.setattr("services.spatial_engine.main.audit_scene", fail)
    with TestClient(app) as client:
        response = client.post("/audit", json=payload())
    assert response.status_code == 422
    assert "private internal geometry data" not in response.text
    assert response.json()["detail"][0]["msg"] == "Room geometry could not be processed"


def test_swing_warning_and_walkability_remain_independent_through_api() -> None:
    body = payload()
    body["floor_polygon"] = [{"x": x, "z": z} for x, z in [(0, 0), (6, 0), (6, 6), (0, 6)]]
    body["walls"] = [{"id": "north", "start": {"x": 0, "z": 0}, "end": {"x": 6, "z": 0}}]
    body["doors"] = [
        {"id": "entry", "wall_id": "north", "hinge_pos": {"x": 1, "z": 0}, "width_m": 0.9}
    ]
    body["windows"] = []
    body["furniture"] = [
        {
            "id": "plant",
            "name": "Plant",
            "category": "other",
            "source": "extracted_video",
            "glb_url": "/plant.glb",
            "bbox_m": {"width": 0.2, "height": 0.8, "depth": 0.2},
            "pose": {"x": 1.65, "z": 0.65, "yaw_deg": 0},
        }
    ]
    with TestClient(app) as client:
        result = client.post("/audit", json=body)
    assert result.status_code == 200
    report = result.json()
    assert report["blocked_doors"] == [{"door_id": "entry", "blocked_by_item_id": "plant"}]
    assert report["walkable_floor_ratio"] > 0.98
