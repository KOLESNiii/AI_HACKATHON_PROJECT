"""Matching walkthrough frames and items to plan rooms (`room/room_frames.py`), lenient live
discovery (`assets/providers.py`) and the extraction job's checks. No test calls fal."""

from __future__ import annotations

import json
import threading
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
    parse_reply,
    plan_rooms,
    smooth,
    spread,
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


def test_spread_caps_each_room_evenly_over_every_video() -> None:
    other = "b" * 64
    frames = [_frame(i) for i in range(30)] + [_frame(i, other) for i in range(10)]
    picked = spread(frames, 16)
    assert len(picked) <= 16
    first = [f.timestamp_s for f in picked if f.source_id == SOURCE]
    second = [f.timestamp_s for f in picked if f.source_id == other]
    assert first[0] == 0 and first[-1] == 29  # covers the first video's whole span
    assert second and second[0] == 0 and second[-1] == 9
    assert len(first) > len(second)  # shares follow each video's frames
    few = frames[:5]
    assert spread(few, 16) == few


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


def test_classifier_matches_every_chunk_at_once_then_smooths(tmp_path: Path) -> None:
    rooms = plan_rooms(PLAN)
    near = adjacency(rooms)
    a = next(r for r in rooms if near[r.room_id])
    b = next(r for r in rooms if r.room_id in near[a.room_id])
    other = "b" * 64
    frames = [_frame(i) for i in range(16)] + [_frame(i, other) for i in range(8)]
    _write_frames(tmp_path, frames)
    together = threading.Barrier(3, timeout=5)  # 3 chunks: breaks unless all run at once

    def ask(prompt: str, images: Sequence[bytes]) -> str:
        together.wait()
        count = len(images) - len(PLAN.floors)
        assert "previous" not in prompt  # chunks run at once: no hint from the one before
        answers = [{"frame": f"F{i}", "room": a.number, "confidence": 0.9} for i in range(count)]
        answers[3]["room"] = b.number  # one stray frame, smoothed away
        return json.dumps({"frames": answers})

    frame_rooms, warnings = FalRoomClassifier(ask=ask, parallel=4).assign_frames(
        PLAN, frames, tmp_path
    )
    assert warnings == []
    assert set(frame_rooms) == {f.key for f in frames}
    assert set(frame_rooms.values()) == {a.room_id}


def test_classifier_failures_leave_frames_unassigned(tmp_path: Path) -> None:
    frames = [_frame(i) for i in range(3)]
    _write_frames(tmp_path, frames)

    def broken(prompt: str, images: Sequence[bytes]) -> str:
        raise TimeoutError

    frame_rooms, warnings = FalRoomClassifier(ask=broken).assign_frames(PLAN, frames, tmp_path)
    assert set(frame_rooms.values()) == {None}
    assert warnings == ["1 of 1 frame batches could not be matched to rooms"]
    unreadable, _ = FalRoomClassifier(ask=lambda p, i: "sorry").assign_frames(
        PLAN, frames, tmp_path
    )
    assert set(unreadable.values()) == {None}


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
