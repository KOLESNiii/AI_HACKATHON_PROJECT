"""The agent loop with scripted model replies, and the SDK adapter over a mock transport."""

import json
from collections.abc import Callable
from typing import Any

import anthropic
import httpx2
import pytest
from fastapi.testclient import TestClient

from contracts.schema import (
    BBoxM,
    FurnitureItem,
    LayoutProposal,
    OptimiseRequest,
    Pose2D,
    RoomScene,
    Vec2,
    WallSegment,
)
from services.spatial_engine.agent import (
    AgentLimits,
    AnthropicLayoutModel,
    ModelReply,
    ProviderError,
    ToolCall,
    propose_layout,
)
from services.spatial_engine.main import app, get_layout_model
from services.spatial_engine.report import audit_scene

Step = ModelReply | Exception | Callable[[list[dict[str, Any]]], ModelReply]


def item(item_id: str, x: float, z: float, *, clearance: float = 0, fixed: bool = False):
    return FurnitureItem(
        id=item_id,
        name=item_id.title(),
        category="wardrobe",
        source="extracted_video",
        glb_url="/mesh.glb",
        bbox_m=BBoxM(width=1, height=2, depth=1),
        pose=Pose2D(x=x, z=z),
        requires_front_clear_m=clearance,
        is_fixed=fixed,
    )


def scene() -> RoomScene:
    """The wardrobe's front access is blocked by the box; the radiator is fixed."""
    return RoomScene(
        scene_id="room",
        revision=4,
        shell_glb_url="/shell.glb",
        floor_polygon=[Vec2(x=x, z=z) for x, z in [(0, 0), (8, 0), (8, 8), (0, 8)]],
        walls=[WallSegment(id="north", start=Vec2(x=0, z=0), end=Vec2(x=8, z=0))],
        doors=[],
        windows=[],
        furniture=[
            item("wardrobe", 2, 4, clearance=1),
            item("box", 2, 5.5),
            item("radiator", 7.5, 4, fixed=True),
        ],
    )


class Scripted:
    def __init__(self, *steps: Step) -> None:
        self.steps = list(steps)
        self.requests: list[dict[str, Any]] = []

    def complete(self, *, system: str, messages: Any, tools: Any, timeout_s: float) -> ModelReply:
        self.requests.append({"messages": json.loads(json.dumps(messages)), "tools": tools})
        step = self.steps.pop(0) if self.steps else END
        if isinstance(step, Exception):
            raise step
        return step(messages) if callable(step) else step


END = ModelReply("end_turn", [{"type": "text", "text": "Done."}], (), 50)


def interpret(goal: str, locked: list[str], near: list[str], unsupported: list[str]) -> ModelReply:
    arguments = {
        "goal": goal,
        "locked_item_ids": locked,
        "near_window_item_ids": near,
        "unsupported": unsupported,
    }
    return ModelReply("tool_use", [], (ToolCall("tu_i", "record_request", arguments),), 80)


def move(item_id: str, x: float, z: float, *, stop_reason: str = "tool_use") -> Step:
    def reply(messages: list[dict[str, Any]]) -> ModelReply:
        arguments = {
            "base_draft_id": json.loads(messages[0]["content"])["draft_id"],
            "moves": [{"item_id": item_id, "x": x, "z": z, "yaw_deg": 0}],
        }
        block = {"type": "tool_use", "id": "tu_1", "name": "evaluate_moves", "input": arguments}
        return ModelReply(stop_reason, [block], (ToolCall("tu_1", "evaluate_moves", arguments),), 9)

    return reply


GOOD = move("box", 5, 5.5)
FULL = AgentLimits(stop_at_first_valid_draft=False)
"""Full exploration: the model keeps going until it says it is done."""


def test_instruction_is_interpreted_explored_and_reaudited() -> None:
    room = scene()
    snapshot = room.model_dump()
    model = Scripted(interpret("balanced", [], [], ["more storage"]), GOOD, END)
    request = OptimiseRequest(scene=room, instruction="tidy up")
    proposal = propose_layout(request, model, limits=FULL)

    assert proposal.improved and proposal.outcome == "completed" and proposal.goal == "balanced"
    assert proposal.poses == {"box": Pose2D(x=5, z=5.5)}
    assert proposal.report.scene_id == "room" and proposal.report.scene_revision == 4
    assert proposal.report.clearance_issues == []
    assert "Moved 1 item(s): Box." in proposal.explanation
    assert "Not handled: more storage." in proposal.explanation
    assert room.model_dump() == snapshot

    assert [tool["name"] for tool in model.requests[0]["tools"]] == ["record_request"]
    assistant, results = model.requests[2]["messages"][1:]
    assert assistant["role"] == "assistant" and assistant["content"][0]["id"] == "tu_1"
    assert results["role"] == "user" and len(results["content"]) == 1
    result = results["content"][0]
    assert (result["type"], result["tool_use_id"], result["is_error"]) == (
        "tool_result",
        "tu_1",
        False,
    )
    assert json.loads(result["content"])["is_best"]


def test_explicit_goal_wins_and_model_can_add_locks_but_not_move_them() -> None:
    model = Scripted(interpret("brighter", ["box", "ghost"], ["radiator"], []), GOOD, END)
    request = OptimiseRequest(scene=scene(), instruction="keep the box", goal="roomier")
    proposal = propose_layout(request, model)

    assert proposal.goal == "roomier" and not proposal.improved and proposal.poses == {}
    assert proposal.outcome == "completed"
    assert proposal.report == audit_scene(scene())
    assert "No valid layout was found" in proposal.explanation
    assert "fixed or locked" in proposal.explanation
    result = model.requests[2]["messages"][2]["content"][0]
    assert result["is_error"] and json.loads(result["content"])["error"]["code"] == "locked_item"


def test_default_stops_at_the_first_valid_draft_and_a_separate_model_interprets() -> None:
    reader = Scripted(interpret("balanced", [], [], []))
    explorer = Scripted(move("box", 7.5, 4.5), GOOD, GOOD)
    request = OptimiseRequest(scene=scene(), instruction="tidy up")
    proposal = propose_layout(request, explorer, interpreter=reader)

    # The collision in the first attempt does not stop the loop; the first valid draft does.
    assert len(reader.requests) == 1 and len(explorer.requests) == 2
    assert proposal.improved and proposal.outcome == "completed"
    assert proposal.poses == {"box": Pose2D(x=5, z=5.5)}


def test_no_configured_model_is_reported_as_unavailable_not_as_a_clean_result() -> None:
    proposal = propose_layout(OptimiseRequest(scene=scene()), None)
    assert (proposal.improved, proposal.outcome, proposal.poses) == (
        False,
        "assistant_unavailable",
        {},
    )
    assert proposal.report == audit_scene(scene())
    assert "could not be used" in proposal.explanation


def test_authentication_failure_is_not_retried() -> None:
    model = Scripted(ProviderError("authentication", retryable=False), GOOD)
    proposal = propose_layout(OptimiseRequest(scene=scene()), model)
    assert proposal.outcome == "assistant_unavailable" and not proposal.improved
    assert len(model.requests) == 1


def test_one_retry_then_a_later_failure_keeps_the_verified_draft() -> None:
    busy = ProviderError("rate_limited", retryable=True)
    model = Scripted(busy, GOOD, ProviderError("server_error", retryable=True), GOOD)
    proposal = propose_layout(OptimiseRequest(scene=scene()), model, limits=FULL)
    assert proposal.improved and proposal.outcome == "stopped_early"
    assert proposal.poses == {"box": Pose2D(x=5, z=5.5)} and len(model.requests) == 3
    assert "stopped early" in proposal.explanation


def test_model_call_budget_is_shared_and_ends_the_loop() -> None:
    model = Scripted(*[GOOD] * 20)
    limits = AgentLimits(max_model_calls=3, stop_at_first_valid_draft=False)
    proposal = propose_layout(OptimiseRequest(scene=scene()), model, limits=limits)
    assert len(model.requests) == 3
    assert proposal.improved and proposal.outcome == "stopped_early"


def test_time_limit_ends_the_loop() -> None:
    ticks = iter(range(0, 10_000, 100))
    model = Scripted(*[GOOD] * 20)
    proposal = propose_layout(OptimiseRequest(scene=scene()), model, clock=lambda: next(ticks))
    assert len(model.requests) == 0 and proposal.outcome == "stopped_early"
    assert not proposal.improved


@pytest.mark.parametrize("stop_reason", ["max_tokens", "refusal", "pause_turn", None])
def test_truncated_or_declined_turns_never_run_their_tool_calls(stop_reason: str | None) -> None:
    model = Scripted(move("box", 5, 5.5, stop_reason=stop_reason))  # type: ignore[arg-type]
    proposal = propose_layout(OptimiseRequest(scene=scene()), model)
    assert not proposal.improved and proposal.outcome == "stopped_early"
    assert proposal.poses == {}


def test_an_invalid_draft_is_never_returned_even_if_the_model_stops_happy() -> None:
    model = Scripted(move("box", 7.5, 4.5), END)
    proposal = propose_layout(OptimiseRequest(scene=scene()), model)
    assert not proposal.improved and proposal.outcome == "completed"
    assert proposal.report.collisions == [] and proposal.poses == {}


def test_request_limits_and_bad_input_fail_before_any_model_call() -> None:
    model = Scripted(GOOD)
    capped = propose_layout(OptimiseRequest(scene=scene(), max_candidates=1), model)
    assert capped.improved
    with pytest.raises(ValueError, match="not known"):
        propose_layout(
            OptimiseRequest(scene=scene(), locked_item_ids=["sofa"], instruction="x"), model
        )
    crowded = scene()
    crowded.furniture = [item(f"i{n}", 1, 1) for n in range(61)]
    with pytest.raises(ValueError, match="at most 60"):
        propose_layout(OptimiseRequest(scene=crowded), model)
    assert len(model.requests) == 1  # only the first, valid request called the model


def test_solve_endpoint_returns_the_contract_and_honest_outcomes() -> None:
    client = TestClient(app)
    body = OptimiseRequest(scene=scene()).model_dump(mode="json")
    try:
        app.dependency_overrides[get_layout_model] = lambda: Scripted(GOOD, END)
        response = client.post("/solve", json=body)
        proposal = LayoutProposal.model_validate(response.json())
        assert response.status_code == 200 and proposal.improved
        assert proposal.outcome == "completed" and proposal.report.scene_revision == 4

        app.dependency_overrides[get_layout_model] = lambda: None
        unavailable = client.post("/solve", json=body).json()
        assert unavailable["outcome"] == "assistant_unavailable" and not unavailable["improved"]

        rejected = client.post("/solve", json={**body, "locked_item_ids": ["sofa"]})
        assert rejected.status_code == 422
        assert client.post("/solve", json={**body, "instruction": "x" * 501}).status_code == 422
    finally:
        app.dependency_overrides.clear()


def test_missing_api_key_means_no_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert get_layout_model() is None
    monkeypatch.setenv("ANTHROPIC_API_KEY", "  ")
    assert get_layout_model() is None


def sdk_model(handler: Callable[[httpx2.Request], httpx2.Response]) -> AnthropicLayoutModel:
    model = AnthropicLayoutModel("sk-secret")
    model._client = anthropic.Anthropic(
        api_key="sk-secret",
        max_retries=0,
        http_client=anthropic.DefaultHttpxClient(transport=httpx2.MockTransport(handler)),
    )
    return model


def test_sdk_adapter_sends_the_expected_request_and_parses_tool_calls() -> None:
    seen: dict[str, Any] = {}

    def handler(request: httpx2.Request) -> httpx2.Response:
        seen.update(
            path=request.url.path, headers=request.headers, body=json.loads(request.content)
        )
        message = {
            "id": "msg_1",
            "type": "message",
            "role": "assistant",
            "model": "claude-sonnet-5-5",
            "content": [
                {"type": "text", "text": "Trying a move."},
                {"type": "tool_use", "id": "toolu_1", "name": "evaluate_moves", "input": {"a": 1}},
            ],
            "stop_reason": "tool_use",
            "stop_sequence": None,
            "usage": {"input_tokens": 120, "output_tokens": 30},
        }
        return httpx2.Response(200, json=message)

    tools = [{"name": "t", "description": "d", "input_schema": {"type": "object"}}]
    messages = [{"role": "user", "content": "hello"}]
    reply = sdk_model(handler).complete(system="s", messages=messages, tools=tools, timeout_s=5)

    assert reply.stop_reason == "tool_use" and reply.tokens == 150
    assert reply.tool_calls == (ToolCall("toolu_1", "evaluate_moves", {"a": 1}),)
    credentials = seen["headers"].get("x-api-key") or seen["headers"]["authorization"]
    assert seen["path"] == "/v1/messages" and "sk-secret" in credentials
    assert "server-side-fallback-2026-07-01" in seen["headers"]["anthropic-beta"]
    body = seen["body"]
    assert (body["model"], body["fallbacks"]) == ("claude-sonnet-5-5", "default")
    assert body["output_config"] == {"effort": "medium"} and body["system"] == "s"
    assert not {"temperature", "tool_choice", "thinking"} & set(body)


@pytest.mark.parametrize(
    ("status", "kind", "retryable"),
    [
        (401, "authentication", False),
        (403, "authentication", False),
        (400, "request_rejected", False),
        (429, "rate_limited", True),
        (500, "server_error", True),
        (529, "server_error", True),
    ],
)
def test_sdk_adapter_maps_http_failures_without_leaking_the_key(
    status: int, kind: str, retryable: bool
) -> None:
    error = {"type": "error", "error": {"type": "x", "message": "sk-secret echoed"}}
    model = sdk_model(lambda request: httpx2.Response(status, json=error))
    with pytest.raises(ProviderError) as caught:
        model.complete(
            system="s", messages=[{"role": "user", "content": "x"}], tools=[], timeout_s=5
        )
    assert (caught.value.kind, caught.value.retryable) == (kind, retryable)
    assert "sk-secret" not in str(caught.value)


def test_sdk_adapter_maps_timeouts() -> None:
    def handler(request: httpx2.Request) -> httpx2.Response:
        raise httpx2.ReadTimeout("slow", request=request)

    with pytest.raises(ProviderError) as caught:
        sdk_model(handler).complete(
            system="s", messages=[{"role": "user", "content": "x"}], tools=[], timeout_s=5
        )
    assert (caught.value.kind, caught.value.retryable) == ("timeout", True)


def test_accepting_a_proposal_then_reauditing_reproduces_its_report() -> None:
    """The editor's accept path: copy poses by ID, bump the revision, call /audit."""
    room = scene()
    proposal = propose_layout(OptimiseRequest(scene=room), Scripted(GOOD, END))
    assert proposal.report.scene_revision == room.revision  # still current, so not stale

    accepted = room.model_copy(deep=True)
    for furniture in accepted.furniture:
        if furniture.id in proposal.poses:
            furniture.pose = proposal.poses[furniture.id]
    accepted.revision += 1

    response = TestClient(app).post("/audit", json=accepted.model_dump(mode="json"))
    reaudit = response.json()
    assert response.status_code == 200 and reaudit["scene_revision"] == room.revision + 1
    expected = proposal.report.model_dump(mode="json")
    assert {**reaudit, "scene_revision": room.revision} == expected


@pytest.mark.parametrize("retryable", [True, False])
def test_interpreter_failure_keeps_explorer_available(retryable: bool) -> None:
    error = ProviderError("request_rejected", retryable=retryable)
    reader = Scripted(error, error)
    explorer = Scripted(GOOD)
    result = propose_layout(
        OptimiseRequest(scene=scene(), instruction="Keep the box still"),
        explorer,
        interpreter=reader,
    )
    assert result.improved
    assert "not applied" in result.explanation
    assert len(reader.requests) == (2 if retryable else 1)


def test_interpreter_retry_preserves_locks_and_tolerates_extra_output() -> None:
    reading = interpret("balanced", ["box"], [], ["extra"] * 9)
    reading.tool_calls[0].arguments["extra_key"] = True
    reader = Scripted(ProviderError("timeout", retryable=True), reading)
    explorer = Scripted(GOOD)
    result = propose_layout(
        OptimiseRequest(scene=scene(), instruction="Keep the box still"),
        explorer,
        interpreter=reader,
    )
    assert not result.improved
    assert len(reader.requests) == 2
    assert "not applied" not in result.explanation


@pytest.mark.parametrize("goal", ["balanced", "roomier", "minimal_changes"])
def test_non_brightness_goals_accept_audit_valid_windows(goal: str) -> None:
    from contracts.schema import WindowOpening

    original = scene()
    original.windows = [
        WindowOpening(
            id="w",
            wall_id="north",
            offset_along_wall_m=7,
            width_m=2,
            sill_height_m=1,
            head_height_m=2,
            plan_normal_deg=0,
        )
    ]
    audit_scene(original)
    result = propose_layout(OptimiseRequest(scene=original, goal=goal), Scripted(GOOD))
    assert result.improved
