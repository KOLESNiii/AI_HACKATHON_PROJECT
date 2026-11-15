"""SSE progress is observable while the harness is blocked in a provider call."""

import asyncio
import json
import threading
from typing import Any

import pytest
from fastapi.testclient import TestClient

from contracts.schema import LayoutProposal, OptimiseRequest
from services.spatial_engine.agent import ProviderError, prepare_layout, propose_layout
from services.spatial_engine.main import app, get_interpreter_model, get_layout_model
from services.spatial_engine.streaming import solve_events
from tests.spatial_engine.test_agent import END, Scripted, interpret, move, scene


def event(frame: str) -> tuple[str, Any]:
    lines = frame.splitlines()
    return lines[0].removeprefix("event: "), json.loads(lines[1].removeprefix("data: "))


@pytest.fixture(autouse=True)
def restore_dependencies():
    before = app.dependency_overrides.copy()
    yield
    app.dependency_overrides = before


def post(request: OptimiseRequest, model: Scripted | None):
    app.dependency_overrides[get_layout_model] = lambda: model
    app.dependency_overrides[get_interpreter_model] = lambda: None
    with TestClient(app) as client:
        return client.post("/solve/stream", json=request.model_dump(mode="json"))


def test_streamed_result_matches_the_existing_solver():
    request = OptimiseRequest(scene=scene())
    result = post(request, Scripted(move("box", 4, 5.5)))
    assert result.status_code == 200
    assert result.headers["content-type"].startswith("text/event-stream")
    assert result.headers["x-accel-buffering"] == "no"
    assert "no-cache" in result.headers["cache-control"]
    frames = [event(frame) for frame in result.text.strip().split("\n\n")]
    assert [data["stage"] for kind, data in frames if kind == "progress"] == [
        "validating",
        "exploring",
        "exploring",
        "evaluating",
        "evaluating",
        "verifying",
    ]
    assert [kind for kind, _ in frames].count("result") == 1
    streamed = LayoutProposal.model_validate(frames[-1][1])
    normal = propose_layout(request, Scripted(move("box", 4, 5.5)))
    assert streamed.model_dump(exclude={"proposal_id"}) == normal.model_dump(
        exclude={"proposal_id"}
    )


def test_validation_errors_still_use_http_422_before_stream_headers():
    request = OptimiseRequest(scene=scene(), locked_item_ids=["missing"])
    result = post(request, Scripted())
    assert result.status_code == 422
    assert result.headers["content-type"].startswith("application/json")
    assert "input" not in result.json()["detail"][0]


@pytest.mark.parametrize(
    "model", [None, Scripted(END), Scripted(ProviderError("auth", retryable=False))]
)
def test_no_proposal_and_provider_failures_are_normal_terminal_results(model):
    result = post(OptimiseRequest(scene=scene()), model)
    frames = [event(frame) for frame in result.text.strip().split("\n\n")]
    assert frames[-1][0] == "result"
    assert not frames[-1][1]["improved"]
    assert not frames[-1][1]["poses"]


def test_interpretation_retry_and_rejected_placement_report_actual_activity():
    model = Scripted(
        ProviderError("timeout", retryable=True),
        interpret("balanced", [], [], []),
        move("box", -1, 5.5),
        move("box", 4, 5.5),
    )
    result = post(OptimiseRequest(scene=scene(), instruction="Clear access"), model)
    frames = [event(frame) for frame in result.text.strip().split("\n\n")]
    updates = [data for kind, data in frames if kind == "progress"]
    assert any(data["stage"] == "retrying" for data in updates)
    assert any("1 outside-room item" in data["message"] for data in updates)
    assert frames[-1][1]["improved"]


def test_progress_and_heartbeats_arrive_before_a_blocked_model_finishes():
    async def run():
        entered, release = threading.Event(), threading.Event()

        def blocked(messages):
            entered.set()
            assert release.wait(3)
            return move("box", 4, 5.5)(messages)

        request = OptimiseRequest(scene=scene())
        stream = solve_events(
            request, Scripted(blocked), None, prepare_layout(request), heartbeat_s=0.01
        )
        try:
            assert event(await anext(stream))[1]["stage"] == "validating"
            assert event(await anext(stream))[1]["stage"] == "exploring"
            assert event(await anext(stream))[1]["stage"] == "exploring"
            assert await asyncio.to_thread(entered.wait, 1)
            assert await asyncio.wait_for(anext(stream), 1) == ": keep-alive\n\n"
            release.set()
            frames = [event(frame) async for frame in stream if frame.startswith("event:")]
            assert frames[-1][0] == "result"
        finally:
            release.set()
            await stream.aclose()

    asyncio.run(run())


def test_disconnect_during_a_call_prevents_its_tools_and_later_calls(monkeypatch):
    async def run():
        entered, release, finished = threading.Event(), threading.Event(), threading.Event()

        def blocked(messages):
            entered.set()
            assert release.wait(3)
            finished.set()
            return move("box", 4, 5.5)(messages)

        model = Scripted(blocked, END)
        request = OptimiseRequest(scene=scene())
        prepared = prepare_layout(request)
        original_call = prepared.call
        moves = []

        def observed(name, arguments):
            if name == "evaluate_moves":
                moves.append(arguments)
            return original_call(name, arguments)

        monkeypatch.setattr(prepared, "call", observed)
        stream = solve_events(request, model, None, prepared)
        try:
            await anext(stream)
            await anext(stream)
            assert await asyncio.to_thread(entered.wait, 1)
            await stream.aclose()
            release.set()
            assert await asyncio.to_thread(finished.wait, 1)
            assert len(model.requests) == 1
            assert not moves
        finally:
            release.set()
            await stream.aclose()

    asyncio.run(run())


def test_unexpected_worker_errors_end_the_stream_without_exposing_exception_text():
    result = post(OptimiseRequest(scene=scene()), Scripted(RuntimeError("private request data")))
    frames = [event(frame) for frame in result.text.strip().split("\n\n")]
    assert frames[-1][0] == "error"
    assert "private request data" not in result.text
    assert sum(kind in {"result", "error"} for kind, _ in frames) == 1


def test_chat_stream_emits_progress_and_audited_additions_without_mutating_the_room():
    from tests.spatial_engine.test_chat import Scripted as ChatModel
    from tests.spatial_engine.test_chat import arguments

    room = scene()
    before = room.model_dump()
    app.dependency_overrides[get_layout_model] = lambda: ChatModel(arguments())
    with TestClient(app) as client:
        response = client.post(
            "/chat/stream", json={"scene": room.model_dump(), "instruction": "Add a table"}
        )
    assert response.status_code == 200
    frames = [event(frame) for frame in response.text.strip().split("\n\n")]
    assert [data["stage"] for kind, data in frames if kind == "progress"] == [
        "validating",
        "exploring",
        "evaluating",
        "verifying",
    ]
    assert frames[-1][0] == "reply"
    result = frames[-1][1]
    assert len(result["additions"]) == 1
    assert not result["additions"][0]["is_proxy"]
    assert result["report"]["scene_revision"] == room.revision
    assert room.model_dump() == before


def test_chat_stream_preserves_delegated_feng_shui_goal_and_outcome():
    from services.spatial_engine.agent import ModelReply, ToolCall

    route = ModelReply("tool_use", [], (ToolCall("route", "rearrange_room", {}),), 10)
    model = Scripted(route, interpret("feng_shui", [], [], []), move("box", 4, 5.5))
    app.dependency_overrides[get_layout_model] = lambda: model
    with TestClient(app) as client:
        response = client.post(
            "/chat/stream", json={"scene": scene().model_dump(), "instruction": "Better feng shui"}
        )
    frames = [event(frame) for frame in response.text.strip().split("\n\n")]
    proposal = frames[-1][1]["proposal"]
    assert proposal["goal"] == "feng_shui"
    assert proposal["improved"]
    assert proposal["outcome"] == "completed"
