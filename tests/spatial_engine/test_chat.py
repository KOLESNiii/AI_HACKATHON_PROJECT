"""Offline add-item flow: tool retries, HTTP result and immutable source scene."""

import json
import struct
from types import SimpleNamespace
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


def blocker(*, is_fixed: bool) -> FurnitureItem:
    """Stands in the door swing: a problem the room has before any request."""
    return FurnitureItem(
        id="blocker",
        name="Shoe cabinet",
        category="fixture" if is_fixed else "storage",
        is_fixed=is_fixed,
        source="extracted_video",
        glb_url="/cabinet.glb",
        bbox_m=BBoxM(width=0.5, depth=0.5, height=1),
        pose=Pose2D(x=1.5, z=0.5),
    )


def move(**changes: Any) -> dict[str, Any]:
    return {"item_id": "blocker", "x": 5.0, "z": 2.0, "yaw_deg": 0.0, **changes}


class Scripted:
    """Each step is add_item arguments, the model's closing words, a whole turn or a failure."""

    def __init__(self, *steps: dict[str, Any] | str | ModelReply | Exception):
        self.steps = list(steps)
        self.requests: list[dict[str, Any]] = []

    def complete(self, **request: Any) -> ModelReply:
        self.requests.append(request)
        step = self.steps.pop(0)
        if isinstance(step, Exception):
            raise step
        if isinstance(step, ModelReply):
            return step
        if isinstance(step, str):
            return ModelReply("end_turn", [{"type": "text", "text": step}], (), 50)
        block = {"type": "tool_use", "id": "tool-1", "name": "add_item", "input": step}
        return ModelReply("tool_use", [block], (ToolCall("tool-1", "add_item", step),), 50)


def tool_error(model: Scripted, request_index: int = 1) -> str:
    """The tool result the model was sent before its next turn."""
    result = model.requests[request_index]["messages"][-1]["content"][0]
    assert result["is_error"]
    return str(result["content"])


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


@pytest.mark.parametrize("is_fixed", [True, False])
def test_a_problem_the_room_already_has_never_blocks_an_addition(
    room: RoomScene, is_fixed: bool
) -> None:
    """The reported failure: a door already blocked (here by an item that may be fixed, so
    no move can clear it) made every addition fail, however clear its own placement."""
    room.furniture.append(blocker(is_fixed=is_fixed))
    assert [issue.blocked_by_item_id for issue in audit_scene(room).blocked_doors] == ["blocker"]
    reply = add_item(room, arguments())
    assert len(reply.additions) == 1 and not reply.poses
    assert reply.report is not None
    assert [issue.blocked_by_item_id for issue in reply.report.blocked_doors] == ["blocker"]
    assert "1 problem(s) the room already had are unchanged" in reply.text


def test_the_new_item_and_moved_items_must_be_clean(room: RoomScene) -> None:
    room.furniture.append(blocker(is_fixed=False))
    for changes, finding in [
        ({"x": 1.5, "z": 0.5}, "the new item overlaps blocker"),
        ({"x": 2.2, "z": 0.5}, "the new item is in the swing of door door"),
        ({"x": -1.0}, "the new item is outside the floor or crosses a wall"),
        ({"moves": [move(x=1.4, z=0.5)]}, "blocker is in the swing of door door"),
        ({"moves": [move(x=6.8, z=6.8)]}, "blocker overlaps fixed"),
    ]:
        with pytest.raises(SpatialInputError, match=finding):
            add_item(room, arguments(**changes))


def test_moves_are_reported_and_restated_poses_are_not_moves(room: RoomScene) -> None:
    room.furniture.append(blocker(is_fixed=False))
    moved = add_item(room, arguments(moves=[move()]))
    assert moved.poses == {"blocker": Pose2D(x=5, z=2)}
    assert "Also moves 1 item(s) to make room: Shoe cabinet." in moved.text
    assert moved.report is not None and not moved.report.blocked_doors
    assert "already had" not in moved.text

    restated = add_item(room, arguments(moves=[move(x=1.5, z=0.5)]))
    assert not restated.poses and "Also moves" not in restated.text
    assert room.furniture[-1].pose == Pose2D(x=1.5, z=0.5)


def test_long_lists_of_moves_are_counted_not_spelled_out(room: RoomScene) -> None:
    rows = [1.5 + 0.8 * index for index in range(8)]
    for index, z in enumerate(rows):
        stool = blocker(is_fixed=False).model_copy(
            update={"id": f"stool-{index}", "name": f"Stool {index}", "pose": Pose2D(x=3, z=z)}
        )
        room.furniture.append(stool)
    moves = [move(item_id=f"stool-{index}", x=4.0, z=z) for index, z in enumerate(rows)]
    reply = add_item(room, arguments(x=6.0, z=2.0, moves=moves))
    assert len(reply.poses) == 8
    assert "Also moves 8 item(s) to make room: Stool 0, " in reply.text
    assert "Stool 5 and 2 more." in reply.text and "Stool 6" not in reply.text


def test_moves_may_be_omitted_and_unhandled_wishes_are_reported(room: RoomScene) -> None:
    wanted = arguments(not_handled=["a rug", "x" * 500])
    del wanted["moves"]
    reply = add_item(room, wanted)
    assert len(reply.additions) == 1
    assert "Not handled: a rug." in reply.text and "x" * 121 not in reply.text


def test_an_addition_may_not_seal_the_room(room: RoomScene) -> None:
    """An outward door has no swing inside the room, so only the entry check sees this."""
    room.doors[0].swings_into_room = False
    chest = arguments(width_m=1.6, depth_m=0.4, x=0.85, z=0.2)
    with pytest.raises(SpatialInputError, match="no floor can be reached from the doors"):
        add_item(room, chest)
    reply = add_item(room, {**chest, "z": 4.0})
    assert reply.report is not None and reply.report.walkable_floor_ratio


def test_agent_corrects_a_collision(room: RoomScene) -> None:
    model = Scripted(arguments(x=7.0, z=7.0), arguments())
    reply = chat(ChatRequest(scene=room, instruction="Add a table"), model)
    assert len(reply.additions) == 1 and len(model.requests) == 2
    assert tool_error(model) == "Placement rejected: the new item overlaps fixed by 0.25 m2"
    assert {tool["name"] for tool in model.requests[0]["tools"]} == {"add_item", "rearrange_room"}


def test_the_model_is_told_what_is_already_wrong_and_why_arguments_failed(
    room: RoomScene,
) -> None:
    room.furniture.append(blocker(is_fixed=True))
    model = Scripted(arguments(width_m=-1), arguments())
    reply = chat(ChatRequest(scene=room, instruction="Add a table"), model)
    assert len(reply.additions) == 1
    sent = json.loads(model.requests[0]["messages"][0]["content"])
    assert sent["instruction"] == "Add a table" and sent["scene"]["scene_id"] == "chat-room"
    assert sent["existing_problems"] == {
        "collisions": [],
        "out_of_bounds_item_ids": [],
        "blocked_doors": [{"door_id": "door", "blocked_by_item_id": "blocker"}],
    }
    assert tool_error(model).startswith("Invalid tool arguments: width_m: ")


def test_the_models_own_answer_is_returned_when_it_proposes_nothing(room: RoomScene) -> None:
    request = ChatRequest(scene=room, instruction="Add a 9 m sofa")
    explained = chat(request, Scripted(arguments(x=-1.0), "It is wider\n\n- than the room."))
    assert explained.text == "It is wider - than the room."
    assert not explained.additions and not explained.poses and explained.report is None

    sdk_blocks = [
        SimpleNamespace(type="thinking"),
        SimpleNamespace(type="text", text="One radiator."),
    ]
    assert (
        chat(request, Scripted(ModelReply("end_turn", sdk_blocks, (), 5))).text == "One radiator."
    )
    assert len(chat(request, Scripted("word " * 400)).text) == 900
    assert chat(request, Scripted("  ")).text.startswith("No verified proposal")


def test_a_truncated_turn_never_runs_its_tool_call(room: RoomScene) -> None:
    call = ToolCall("tool-1", "add_item", arguments())
    block = {"type": "tool_use", "id": "tool-1", "name": "add_item", "input": arguments()}
    model = Scripted(ModelReply("max_tokens", [block], (call,), 50))
    reply = chat(ChatRequest(scene=room, instruction="Add a table"), model)
    assert not reply.additions and reply.text.startswith("No verified proposal")


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
