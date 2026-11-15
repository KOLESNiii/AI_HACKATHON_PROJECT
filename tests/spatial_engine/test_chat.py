"""Offline add-item flow: tool retries, HTTP result and immutable source scene."""

import json
import struct
from typing import Any

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from contracts.schema import BBoxM, DoorOpening, FurnitureItem, Pose2D, RoomScene, Vec2, WallSegment
from services.spatial_engine.agent import ModelReply, ProviderError, ToolCall
from services.spatial_engine.chat import ChatRequest, add_item, chat
from services.spatial_engine.geometry import SpatialInputError
from services.spatial_engine.main import app, get_layout_model
from services.spatial_engine.proxy import proxy_glb
from services.spatial_engine.report import audit_scene


@pytest.fixture
def room() -> RoomScene:
    return RoomScene(
        scene_id="chat-room",
        revision=3,
        shell_glb_url="/shell.glb",
        floor_polygon=[Vec2(x=x, z=z) for x, z in [(0, 0), (8, 0), (8, 8), (0, 8)]],
        walls=[WallSegment(id="wall", start=Vec2(x=0, z=0), end=Vec2(x=8, z=0))],
        doors=[DoorOpening(id="door", wall_id="wall", hinge_pos=Vec2(x=1, z=0), width_m=1)],
        windows=[],
        furniture=[
            FurnitureItem(
                id="fixed",
                name="Radiator",
                category="fixture",
                is_fixed=True,
                source="extracted_video",
                glb_url="/fixture.glb",
                bbox_m=BBoxM(width=1, depth=1, height=1),
                pose=Pose2D(x=7, z=7),
            )
        ],
    )


def arguments(**changes: Any) -> dict[str, Any]:
    return {
        "name": "Side table",
        "category": "table",
        "width_m": 0.5,
        "depth_m": 0.5,
        "height_m": 0.6,
        "x": 4.0,
        "z": 4.0,
        "yaw_deg": 0.0,
        "moves": [],
        **changes,
    }


class Scripted:
    def __init__(self, *steps: dict[str, Any] | Exception):
        self.steps = list(steps)
        self.requests: list[dict[str, Any]] = []

    def complete(self, **request: Any) -> ModelReply:
        self.requests.append(request)
        step = self.steps.pop(0)
        if isinstance(step, Exception):
            raise step
        block = {"type": "tool_use", "id": "tool-1", "name": "add_item", "input": step}
        return ModelReply("tool_use", [block], (ToolCall("tool-1", "add_item", step),), 50)


def test_addition_is_audited_without_mutation(room: RoomScene) -> None:
    before = room.model_dump()
    reply = add_item(room, arguments())
    assert room.model_dump() == before
    assert len(reply.additions) == 1 and not reply.poses
    item = reply.additions[0]
    assert item.is_proxy and item.dimension_source == "estimated"
    assert item.correction_needed == ["dimensions"]
    candidate = room.model_copy(deep=True)
    candidate.furniture.extend(reply.additions)
    assert audit_scene(candidate) == reply.report
    assert not reply.report.collisions and not reply.report.blocked_doors  # type: ignore[union-attr]


@pytest.mark.parametrize(
    "changes",
    [
        {"x": 7.0, "z": 7.0},
        {"x": -1.0},
        {"x": 1.5, "z": 0.5},
        {"moves": [{"item_id": "fixed", "x": 5.0, "z": 5.0, "yaw_deg": 0.0}]},
        {"moves": [{"item_id": "missing", "x": 5.0, "z": 5.0, "yaw_deg": 0.0}]},
    ],
)
def test_invalid_placement_and_moves_are_rejected(room: RoomScene, changes: dict[str, Any]) -> None:
    snapshot = room.model_dump()
    with pytest.raises(SpatialInputError):
        add_item(room, arguments(**changes))
    assert room.model_dump() == snapshot


@pytest.mark.parametrize(
    "changes",
    [
        {"width_m": -1},
        {"depth_m": float("nan")},
        {"height_m": 30},
        {"category": "fixture"},
        {"extra": True},
    ],
)
def test_untrusted_arguments(room: RoomScene, changes: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        add_item(room, arguments(**changes))


def test_agent_corrects_a_collision(room: RoomScene) -> None:
    model = Scripted(arguments(x=7.0, z=7.0), arguments())
    reply = chat(ChatRequest(scene=room, instruction="Add a table"), model)
    assert len(reply.additions) == 1 and len(model.requests) == 2
    error = model.requests[1]["messages"][2]["content"][0]
    assert error["is_error"] and "collisions" in error["content"]
    assert {tool["name"] for tool in model.requests[0]["tools"]} == {"add_item", "rearrange_room"}


def test_missing_key_and_provider_failure_never_add(room: RoomScene) -> None:
    request = ChatRequest(scene=room, instruction="Add a table")
    assert not chat(request, None).additions
    assert not chat(request, Scripted(ProviderError("timeout", retryable=True))).additions


def test_chat_route_and_proxy(room: RoomScene) -> None:
    app.dependency_overrides[get_layout_model] = lambda: Scripted(arguments())
    try:
        with TestClient(app) as client:
            response = client.post(
                "/chat", json={"scene": room.model_dump(), "instruction": "Add a table"}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["additions"][0]["is_proxy"] and data["report"]["scene_revision"] == 3
            path = data["additions"][0]["glb_url"].removeprefix("/api/spatial_engine")
            proxy = client.get(path)
            assert proxy.status_code == 200 and proxy.content[:4] == b"glTF"
            assert client.get("/proxies/nan/1/1.glb").status_code == 422
            assert (
                client.post(
                    "/chat", json={"scene": room.model_dump(), "instruction": "x" * 501}
                ).status_code
                == 422
            )
    finally:
        app.dependency_overrides.clear()


def test_proxy_has_metric_bottom_centred_bounds() -> None:
    data = proxy_glb(1.2, 0.8, 0.6)
    assert struct.unpack_from("<I", data, 8)[0] == len(data)
    size = struct.unpack_from("<I", data, 12)[0]
    doc = json.loads(data[20 : 20 + size])
    assert doc["accessors"][0]["min"] == [-0.6, 0, -0.3]
    assert doc["accessors"][0]["max"] == [0.6, 0.8, 0.3]
