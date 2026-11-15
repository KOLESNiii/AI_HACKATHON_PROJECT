"""Matching walkthrough frames and items to plan rooms (`room/room_frames.py`), lenient live
discovery (`assets/providers.py`) and the extraction job's checks. No test calls fal."""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path

import pytest

cv2 = pytest.importorskip("cv2")

import numpy as np  # noqa: E402

from contracts.schema import ParsedFloorPlan  # noqa: E402
from services.reconstruction.assets.providers import DiscoveryError, parse_discovery  # noqa: E402
from services.reconstruction.assets.selection_models import (  # noqa: E402
    Box,
    Frame,
    SelectedObject,
    Sighting,
)
from services.reconstruction.room.plan_view import render_floor  # noqa: E402
from services.reconstruction.room.room_frames import (  # noqa: E402
    FalRoomClassifier,
    adjacency,
    assign_items,
    parse_reply,
    plan_rooms,
    smooth,
)
from services.reconstruction.room.video_jobs import whole_view  # noqa: E402

CACHED = (
    Path(__file__).parents[1]
    / "services/reconstruction/room/fixtures/scene_cache/plan-83a12322e933.json"
)
PLAN = ParsedFloorPlan.model_validate(json.loads(CACHED.read_text())["plan"])
SOURCE = "a" * 64


def _frame(index: int, source: str = SOURCE) -> Frame:
    return Frame(
        key=f"{source}:0:{index}",
        source_id=source,
        frame_index=index,
        pts=index,
        timestamp_s=float(index),
        image_size_px=(64, 48),
        image_path=f"{index}.png",
        quality=0.8,
    )


def _object(obj_id: str, frames: Sequence[Frame], area: float = 0.2) -> SelectedObject:
    side = area**0.5
    return SelectedObject(
        id=obj_id,
        name=obj_id,
        category="sofa",
        appearance="brown",
        sightings=[
            Sighting(frame_key=f.key, box=Box(x=0, y=0, width=side, height=side)) for f in frames
        ],
    )


# --- the plan -------------------------------------------------------------------------------


def test_rooms_are_numbered_across_floors() -> None:
    rooms = plan_rooms(PLAN)
    assert [r.number for r in rooms] == list(range(1, len(rooms) + 1))
    assert len(rooms) == sum(len(f.rooms) for f in PLAN.floors)
    assert {r.floor_id for r in rooms} == {f.floor_id for f in PLAN.floors}


def test_door_adjacency_is_symmetric_and_stays_on_one_floor() -> None:
    rooms = plan_rooms(PLAN)
    near = adjacency(rooms)
    floor_of = {r.room_id: r.floor_id for r in rooms}
    assert any(near.values()), "the demo plan's rooms share doors"
    for room, others in near.items():
        assert room not in others
        for other in others:
            assert room in near[other]
            assert floor_of[room] == floor_of[other]


def test_each_floor_renders_with_its_rooms() -> None:
    rooms = plan_rooms(PLAN)
    for floor in PLAN.floors:
        image = render_floor([(r.number, r.scene) for r in rooms if r.floor_id == floor.floor_id])
        assert image.ndim == 3 and max(image.shape[:2]) <= 1400
        assert (image != 255).any()


# --- walkthrough continuity -----------------------------------------------------------------


NEAR = {"hall": {"kitchen", "bed"}, "kitchen": {"hall"}, "bed": {"hall"}}


def test_a_lone_frame_between_two_of_one_room_joins_it() -> None:
    assert smooth(["kitchen", "bed", "kitchen"], NEAR) == ["kitchen"] * 3


def test_a_lone_jump_to_a_room_without_a_shared_door_is_undone() -> None:
    labels = ["kitchen", "kitchen", "bed", "hall", "hall"]
    assert smooth(labels, NEAR) == ["kitchen", "kitchen", "kitchen", "hall", "hall"]


def test_walking_through_a_door_is_kept() -> None:
    labels = ["kitchen", "kitchen", "hall", "hall", "bed", "bed"]
    assert smooth(labels, NEAR) == labels
    assert smooth(["kitchen", "kitchen", "hall"], NEAR) == ["kitchen", "kitchen", "hall"]


def test_unassigned_frames_stay_unassigned_but_keep_continuity() -> None:
    assert smooth(["kitchen", None, "bed", "kitchen"], NEAR) == [
        "kitchen",
        None,
        "kitchen",
        "kitchen",
    ]
    assert smooth([None, None], NEAR) == [None, None]


def test_items_go_to_the_room_most_of_their_sightings_show() -> None:
    f = [_frame(i) for i in range(5)]
    rooms = {f[0].key: "kitchen", f[1].key: "kitchen", f[2].key: "bed", f[3].key: None}
    objects = [
        _object("vid-000001", f[:3]),  # 2 kitchen, 1 bed
        _object("vid-000002", [f[1], f[2]]),  # tie
        _object("vid-000003", [f[3], f[4]]),  # no room seen
    ]
    assert assign_items(objects, rooms) == {
        "vid-000001": "kitchen",
        "vid-000002": None,
        "vid-000003": None,
    }


# --- the model's answer ---------------------------------------------------------------------


def test_reply_parsing_keeps_confident_known_rooms_only() -> None:
    rooms = plan_rooms(PLAN)
    text = (
        "```json\n"
        + json.dumps(
            {
                "frames": [
                    {"frame": "F0", "room": 1, "confidence": 0.9},
                    {"frame": "F1", "room": 2, "confidence": 0.1},
                    {"frame": "F2", "room": 999, "confidence": 0.9},
                    {"frame": "F3", "room": None},
                    {"frame": "F7", "room": 1},
                    {"frame": "X", "room": 1},
                ]
            }
        )
        + "\n```"
    )
    answer = parse_reply(text, 4, rooms)
    assert [r.number if r else None for r in answer] == [1, None, None, None]
    with pytest.raises(ValueError):
        parse_reply("no json here", 4, rooms)


def _write_frames(data_dir: Path, frames: Sequence[Frame]) -> None:
    for f in frames:
        cv2.imwrite(str(data_dir / f.image_path), np.full((48, 64, 3), 128, np.uint8))


def test_classifier_matches_frames_then_items(tmp_path: Path) -> None:
    rooms = plan_rooms(PLAN)
    near = adjacency(rooms)
    a = next(r for r in rooms if near[r.room_id])
    b = next(r for r in rooms if r.room_id in near[a.room_id])
    frames = [_frame(i) for i in range(10)]
    _write_frames(tmp_path, frames)
    prompts: list[str] = []

    def ask(prompt: str, images: Sequence[bytes]) -> str:
        prompts.append(prompt)
        count = len(images) - len(PLAN.floors)
        start = 0 if len(prompts) == 1 else 8
        rooms_seen = [a.number if start + i < 6 else b.number for i in range(count)]
        return json.dumps(
            {
                "frames": [
                    {"frame": f"F{i}", "room": n, "confidence": 0.9}
                    for i, n in enumerate(rooms_seen)
                ]
            }
        )

    objects = [_object("vid-000001", frames[:3]), _object("vid-000002", frames[7:])]
    result = FalRoomClassifier(ask=ask).assign(PLAN, frames, objects, tmp_path)
    assert len(prompts) == 2  # 10 frames, 8 per request
    assert f"room {b.number}" in prompts[1]  # the previous batch's last room is passed on
    assert result.item_rooms == {"vid-000001": a.room_id, "vid-000002": b.room_id}
    assert result.warnings == []


def test_classifier_failures_leave_frames_unassigned(tmp_path: Path) -> None:
    frames = [_frame(i) for i in range(3)]
    _write_frames(tmp_path, frames)

    def broken(prompt: str, images: Sequence[bytes]) -> str:
        raise TimeoutError

    objects = [_object("vid-000001", frames)]
    result = FalRoomClassifier(ask=broken).assign(PLAN, frames, objects, tmp_path)
    assert result.item_rooms == {"vid-000001": None}
    assert result.warnings == ["1 frame batch(es) could not be matched to rooms"]
    unreadable = FalRoomClassifier(ask=lambda p, i: "sorry").assign(PLAN, frames, objects, tmp_path)
    assert unreadable.item_rooms == {"vid-000001": None}


# --- lenient discovery and the job's checks -------------------------------------------------


def _answer(objects: list[dict[str, object]], empty: list[str] | None = None) -> str:
    return json.dumps({"objects": objects, "empty_frames": empty or [], "warnings": []})


def _obj(category: str, *keys: str, box: dict[str, float] | None = None) -> dict[str, object]:
    box = box or {"x": 0.1, "y": 0.1, "width": 0.3, "height": 0.3}
    return {
        "name": "thing",
        "category": category,
        "appearance": "grey",
        "sightings": [{"frame_key": k, "box": box} for k in keys],
    }


def test_strict_parsing_rejects_what_lenient_parsing_repairs() -> None:
    frames = [_frame(i) for i in range(3)]
    text = _answer(
        [
            _obj("lamp", "F0", "F0"),  # unknown category, repeated frame
            _obj("sofa", "F9"),  # unknown frame only: dropped
            _obj("table", "F1", box={"x": 0.8, "y": 0.5, "width": 0.5, "height": 0.9}),
        ]
    )  # F2 never mentioned
    with pytest.raises(DiscoveryError):
        parse_discovery(text, frames, [])
    found = parse_discovery(text, frames, [], lenient=True)
    assert [o.category for o in found.objects] == ["other", "table"]
    assert [len(o.sightings) for o in found.objects] == [1, 1]
    box = found.objects[1].sightings[0].box
    assert box.x + box.width <= 1 and box.y + box.height <= 1
    assert found.empty_frames == [frames[2].key]
    assert any("not accounted for" in w for w in found.warnings)
    found.validate_frames({f.key for f in frames})  # what selection.py checks next


def test_items_boxed_as_the_whole_view_are_recognised() -> None:
    f = [_frame(0), _frame(1)]
    assert whole_view(_object("vid-000001", f, area=0.95))
    assert not whole_view(_object("vid-000002", f, area=0.3))
