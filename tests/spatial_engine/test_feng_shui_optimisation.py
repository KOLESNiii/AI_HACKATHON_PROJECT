"""Feng Shui optimisation uses the runtime skill and the same full score as Stats."""

import json

import pytest
from fastapi.testclient import TestClient

from contracts.schema import OptimiseRequest, Pose2D
from services.spatial_engine import feng_shui_skill
from services.spatial_engine.agent import ModelReply, ToolCall, propose_layout
from services.spatial_engine.chat import ChatRequest, chat
from services.spatial_engine.feng_shui_inputs import FengShuiRequest
from services.spatial_engine.feng_shui_score import score_feng_shui
from services.spatial_engine.layout_tools import LayoutPreferences, LayoutToolbox
from services.spatial_engine.main import app, get_layout_model
from services.spatial_engine.objective import compare_evaluations, compare_layouts, evaluate_layout
from tests.spatial_engine.test_agent import END, Scripted, interpret, move, scene
from tests.spatial_engine.test_feng_shui import RecordedModel
from tests.spatial_engine.test_feng_shui_score import bed, room


class RecordingModel(Scripted):
    def __init__(self, *steps):
        super().__init__(*steps)
        self.systems = []

    def complete(self, **kwargs):
        self.systems.append(kwargs["system"])
        return super().complete(**kwargs)


def shift_bed(x=2.6, z=3.0):
    def reply(messages):
        arguments = {
            "base_draft_id": json.loads(messages[0]["content"])["draft_id"],
            "moves": [{"item_id": "bed", "x": x, "z": z, "yaw_deg": 180}],
        }
        block = {"type": "tool_use", "id": "move-bed", "name": "evaluate_moves", "input": arguments}
        return ModelReply(
            "tool_use", [block], (ToolCall("move-bed", "evaluate_moves", arguments),), 30
        )

    return reply


def original_room():
    return room(bed(x=0.925))


def test_direct_feng_shui_request_uses_the_shared_skill_and_measured_rule_feedback():
    original = original_room()
    snapshot = original.model_dump()
    model = RecordingModel(shift_bed())
    progress = []
    proposal = propose_layout(
        OptimiseRequest(scene=original, goal="feng_shui"), model, progress=progress.append
    )
    assert proposal.improved and proposal.goal == "feng_shui"
    assert "Mode: layout_optimisation" in model.systems[0]
    assert "Use Form School spatial principles" in model.systems[0]
    assert "lowest-scoring, highest-weight" in model.systems[0]
    assert "call record_assessment exactly once" not in model.systems[0]
    assert {tool["name"] for tool in model.requests[0]["tools"]} == {
        "inspect_layout",
        "evaluate_moves",
        "compare_layouts",
    }
    payload = json.loads(model.requests[0]["messages"][0]["content"])
    baseline = score_feng_shui(FengShuiRequest(scene=original))
    assert payload["feng_shui"] == baseline.model_dump(mode="json")
    assert payload["metrics"]["feng_shui_score"] == baseline.score
    assert any("no mirror inventory" in note for note in payload["feng_shui"]["unassessed"])
    assert any("Feng Shui skill" in update.message for update in progress)
    candidate = original.model_copy(deep=True)
    candidate.furniture[0].pose = proposal.poses["bed"]
    final = score_feng_shui(FengShuiRequest(scene=candidate))
    assert final.score > baseline.score
    assert f"{baseline.score} before, {final.score} now" in proposal.explanation
    assert "coverage" in proposal.explanation
    assert original.model_dump() == snapshot


def test_exact_chat_request_routes_through_the_skill_and_preserves_the_users_words():
    route = ModelReply("tool_use", [], (ToolCall("route", "rearrange_room", {}),), 10)
    model = RecordingModel(route, interpret("feng_shui", [], [], []), shift_bed())
    instruction = "optimise the feng shui"
    result = chat(ChatRequest(scene=original_room(), instruction=instruction), model)
    assert result.proposal is not None and result.proposal.improved
    assert result.proposal.goal == "feng_shui"
    assert not result.additions
    assert "Feng Shui request call rearrange_room" in model.systems[0]
    assert "Mode: layout_optimisation" in model.systems[-1]
    payload = json.loads(model.requests[-1]["messages"][0]["content"])
    assert payload["person_request"] == instruction


def test_each_candidate_exposes_the_full_score_and_coverage_and_cannot_move_locked_items():
    original = original_room()
    tools = LayoutToolbox(original, preferences=LayoutPreferences(goal="feng_shui"))
    first = tools.call("inspect_layout", {"draft_id": tools.session.original_draft_id})
    result = tools.call(
        "evaluate_moves",
        {
            "base_draft_id": first["draft_id"],
            "moves": [{"item_id": "bed", "x": 2.6, "z": 3.0, "yaw_deg": 180}],
        },
    )
    candidate = original.model_copy(deep=True)
    candidate.furniture[0].pose = Pose2D(x=2.6, z=3, yaw_deg=180)
    assert result["feng_shui"] == score_feng_shui(FengShuiRequest(scene=candidate)).model_dump(
        mode="json"
    )
    assert result["is_best"]
    locked = RecordingModel(shift_bed())
    proposal = propose_layout(
        OptimiseRequest(scene=original, goal="feng_shui", locked_item_ids=["bed"]), locked
    )
    assert not proposal.improved and not proposal.poses and not locked.requests
    invalid = propose_layout(
        OptimiseRequest(scene=original, goal="feng_shui"), RecordingModel(shift_bed(x=-5), END)
    )
    assert not invalid.improved and not invalid.poses


def test_full_scoring_is_opt_in_and_the_comparator_requires_it():
    original = original_room()
    plain = evaluate_layout(original, original)
    assert plain.feng_shui is None and plain.metrics.feng_shui_score is None
    with pytest.raises(ValueError, match="measured full-rule"):
        compare_evaluations(plain, plain, "feng_shui")
    candidate = original.model_copy(deep=True)
    candidate.furniture[0].pose = Pose2D(x=2.6, z=3, yaw_deg=180)
    assert compare_layouts(original, candidate, goal="feng_shui").outcome == "better"


def test_full_goal_improves_backing_even_when_the_door_placement_score_is_unchanged():
    original = room(bed(z=2.1))
    candidate = original.model_copy(deep=True)
    candidate.furniture[0].pose = Pose2D(x=2.6, z=3, yaw_deg=180)
    comparison = compare_layouts(original, candidate, goal="feng_shui")
    assert comparison.baseline.report.feng_shui.score == comparison.candidate.report.feng_shui.score
    assert (
        comparison.candidate.metrics.feng_shui_score > comparison.baseline.metrics.feng_shui_score
    )
    assert comparison.outcome == "better" and comparison.deciding_metric == "feng_shui_score"


def test_unassessable_full_score_remains_unknown_in_the_tool_payload_and_reply():
    model = RecordingModel(END)
    proposal = propose_layout(OptimiseRequest(scene=scene(), goal="feng_shui"), model)
    payload = json.loads(model.requests[0]["messages"][0]["content"])
    assert payload["feng_shui"]["score"] is None
    assert payload["feng_shui"]["unassessed"]
    assert "not assessable" in proposal.explanation
    assert not proposal.improved


def test_missing_skill_is_a_configuration_error_without_breaking_other_goals(monkeypatch, tmp_path):
    monkeypatch.setattr(feng_shui_skill, "SKILL_PATH", tmp_path / "missing-skill.md")
    model = RecordingModel(shift_bed())
    with pytest.raises(feng_shui_skill.FengShuiSkillUnavailable):
        propose_layout(OptimiseRequest(scene=original_room(), goal="feng_shui"), model)
    assert not model.requests
    previous = app.dependency_overrides.copy()
    app.dependency_overrides[get_layout_model] = lambda: RecordingModel(shift_bed())
    try:
        with TestClient(app) as client:
            response = client.post(
                "/solve",
                json=OptimiseRequest(scene=original_room(), goal="feng_shui").model_dump(
                    mode="json"
                ),
            )
    finally:
        app.dependency_overrides = previous
    assert response.status_code == 503
    assert "not configured" in response.json()["detail"][0]["msg"]
    other = propose_layout(OptimiseRequest(scene=scene()), RecordingModel(move("box", 4, 5.5)))
    assert other.improved


def test_advice_keeps_its_read_only_assessment_protocol():
    from services.spatial_engine.feng_shui import assess_feng_shui

    model = RecordedModel()
    assert assess_feng_shui(FengShuiRequest(scene=scene()), model).outcome == "completed"
    assert "Mode: assessment" in model.request["system"]
    assert "lowest-scoring, highest-weight" not in model.request["system"]
    assert [tool["name"] for tool in model.request["tools"]] == ["record_assessment"]


def test_streamed_chat_uses_the_skill_and_returns_the_stats_score_in_its_explanation():
    route = ModelReply("tool_use", [], (ToolCall("route", "rearrange_room", {}),), 10)
    model = RecordingModel(route, interpret("feng_shui", [], [], []), shift_bed())
    previous = app.dependency_overrides.copy()
    app.dependency_overrides[get_layout_model] = lambda: model
    try:
        with TestClient(app) as client:
            result = client.post(
                "/chat/stream",
                json={
                    "scene": original_room().model_dump(),
                    "instruction": "optimise the feng shui",
                },
            )
            frames = result.text.strip().split("\n\n")
            assert "Using the Feng Shui skill" in result.text
            reply = json.loads(frames[-1].split("data: ", 1)[1])
            proposal = reply["proposal"]
            assert proposal["goal"] == "feng_shui" and proposal["improved"]
            candidate = original_room()
            candidate.furniture[0].pose = Pose2D.model_validate(proposal["poses"]["bed"])
            score = client.post("/feng-shui/score", json={"scene": candidate.model_dump()}).json()
            assert f"{score['score']} now" in proposal["explanation"]
    finally:
        app.dependency_overrides = previous


def test_feng_shui_optimisation_accepts_ids_shared_across_object_types():
    """The audit only needs IDs unique per type; the optimiser must accept what /audit accepts."""
    original = original_room()
    original.doors = [original.doors[0].model_copy(update={"id": original.walls[0].id})]
    with TestClient(app) as client:
        assert client.post("/audit", json=original.model_dump(mode="json")).status_code == 200
    proposal = propose_layout(
        OptimiseRequest(scene=original, goal="feng_shui"), RecordingModel(shift_bed())
    )
    assert proposal.goal == "feng_shui"
    assert proposal.outcome == "completed"
