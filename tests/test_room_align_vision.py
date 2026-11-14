"""The vision placement observer and the alignment debug CLI, offline (no provider calls)."""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path

import pytest

pytest.importorskip("cv2")

import cv2  # noqa: E402
import numpy as np  # noqa: E402

from contracts.schema import RoomScene  # noqa: E402
from services.reconstruction.assets.models import EvidenceFrame, FurnitureAsset  # noqa: E402
from services.reconstruction.assets.selection_models import (  # noqa: E402
    SegmentationResult,
    SelectionResult,
)
from services.reconstruction.room import observe_vision as ov  # noqa: E402
from services.reconstruction.room.align import HIGH_CONFIDENCE, align_assets  # noqa: E402
from services.reconstruction.room.align_debug import main as align_main  # noqa: E402
from services.reconstruction.room.plan_view import render_room, wall_letters  # noqa: E402
from tests.test_room_align import MOCKS, ROOT, _box, _room  # noqa: E402

FIXTURES = ROOT / "services/reconstruction/room/fixtures"


def _jpeg(shade: int, size: tuple[int, int] = (120, 160)) -> bytes:
    image = np.full((size[1], size[0], 3), shade, np.uint8)
    return bytes(cv2.imencode(".jpg", image)[1].tobytes())


def _seen(asset_id: str, frames: Sequence[int], primary: int, **fields: object) -> FurnitureAsset:
    evidence = {
        "frames": [
            {
                "frame_index": i,
                "timestamp_s": i / 30,
                "image_size_px": [120, 160],
                "bbox_px": [10.0, 20.0, 50.0, 60.0],
            }
            for i in frames
        ],
        "primary_frame_index": primary,
    }
    return _box(asset_id, evidence=evidence, **fields)


def _by_index(asset_id: str, frame: EvidenceFrame) -> bytes | None:
    return _jpeg(40 + frame.frame_index)


class _Stub(ov.FalVisionObserver):
    """The observer with the provider call replaced by canned answers."""

    def __init__(self, answers: Sequence[str | None | Exception]) -> None:
        super().__init__(retries=1)
        self.answers = list(answers)
        self.requests: list[tuple[str, list[bytes]]] = []

    def _ask(self, prompt: str, images: Sequence[bytes]) -> str | None:
        self.requests.append((prompt, list(images)))
        answer = self.answers.pop(0)
        if isinstance(answer, Exception):
            raise answer
        return answer


def _fractions(room: RoomScene, x: float, z: float) -> tuple[float, float]:
    """Where a room point falls on the plan image the model is shown."""
    view = render_room(room, label_names=True)
    height, width = view.image.shape[:2]
    return (
        (x - view.origin[0]) * view.px_per_m / width,
        (z - view.origin[1]) * view.px_per_m / height,
    )


def _reply(room: RoomScene, *items: dict[str, object]) -> str:
    entries = []
    for item in items:
        x, y = _fractions(room, *item.pop("at"))  # type: ignore[misc]
        entries.append({"x": x, "y": y, **item})
    return "```json\n" + json.dumps({"camera": "in the doorway", "items": entries}) + "\n```"


# --- the plan the model reads -----------------------------------------------------------------


def test_plan_view_maps_between_pixels_and_room() -> None:
    room = _room()
    view = render_room(room)
    assert wall_letters(room) == {"n": "A", "e": "B", "s": "C", "w": "D"}
    height, width = view.image.shape[:2]
    px, py = view.to_pixel((4.0, 3.0))
    assert view.to_room(px / width, py / height) == pytest.approx((4.0, 3.0), abs=0.01)
    assert view.image[view.to_pixel((2.0, 1.5))[::-1]].tolist() != [255, 255, 255]  # floor fill


def test_prompt_lists_walls_and_numbered_objects() -> None:
    prompt = ov.build_prompt(_room(), [_box("a", width=1.2), _box("b", category="chair")])
    assert "- A: 4.0 m" in prompt and "- B: 3.0 m" in prompt
    assert "- 1: a (storage), 1.20 x 0.50 x 0.80" in prompt
    assert "- 2: b (chair)" in prompt


# --- answer -> hints --------------------------------------------------------------------------


def test_the_answer_becomes_wall_relative_hints() -> None:
    room = _room()
    assets = [_box("flush"), _box("free", width=1.0, depth=0.6), _box("side"), _box("chair")]
    answer = _reply(
        room,
        {
            "asset": 1,
            "at": (2.0, 0.25),
            "against_wall": "A",
            "back_to_wall": "a",
            "confidence": 0.95,
        },
        {"asset": 2, "at": (2.0, 1.2), "against_wall": None, "back_to_wall": None},
        {"asset": 3, "at": (1.0, 0.5), "against_wall": "A", "back_to_wall": "B"},
        {"asset": 4, "at": (2.0, 1.8), "seated_at": 2, "confidence": 0.4},
        {"asset": 9, "at": (1.0, 1.0)},  # not a numbered object
        {"asset": 1, "at": (3.0, 2.0)},  # a second answer for the same object
    )
    reply = ov._Reply.model_validate(json.loads(ov._extract_json(answer)))
    hints = ov.hints_from_reply(reply, room, assets, render_room(room, label_names=True))
    flush, free, side, chair = hints
    assert (flush.wall_id, flush.facing, flush.offset_m) == ("n", "into_room", 0.0)
    assert flush.along_frac == pytest.approx(0.5, abs=0.01)
    assert flush.confidence == ov.UNREVIEWED_CONFIDENCE < HIGH_CONFIDENCE  # 0.95 is capped
    # Free-standing: nearest wall, with the gap between that wall and the item's near face.
    assert (free.wall_id, free.facing) == ("n", None)
    assert free.offset_m == pytest.approx(1.2 - 0.3, abs=0.02)
    # Back to wall B (east, x = 4): the front points -X, which is wall A's start.
    assert (side.wall_id, side.facing, side.offset_m) == ("n", "wall_start", 0.0)
    assert chair.seated_at == "free" and chair.confidence == 0.4


def test_unknown_wall_letters_fall_back_to_the_nearest_wall() -> None:
    room = _room()
    answer = _reply(room, {"asset": 1, "at": (3.6, 1.5), "against_wall": "Z", "back_to_wall": "Q"})
    reply = ov._Reply.model_validate(json.loads(ov._extract_json(answer)))
    (hint,) = ov.hints_from_reply(reply, room, [_box("a")], render_room(room, label_names=True))
    assert (hint.wall_id, hint.facing) == ("e", None) and hint.offset_m > 0


# --- the observer -----------------------------------------------------------------------------


def test_observer_sends_the_plan_then_boxed_frames_and_places_from_the_answer() -> None:
    room = _room()
    assets = [_seen("sofa", [0, 30], 0, category="sofa"), _seen("table", [0], 0)]
    observer = _Stub(
        [
            _reply(
                room,
                {"asset": 1, "at": (2.0, 0.25), "against_wall": "A", "back_to_wall": "A"},
                {"asset": 2, "at": (2.0, 1.6)},
            )
        ]
    )
    result = align_assets(room, assets, observer, _by_index)

    ((prompt, images),) = observer.requests
    assert "- 1: sofa (sofa)" in prompt
    assert images[0][:8] == b"\x89PNG\r\n\x1a\n" and len(images) == 3  # plan + frames 0 and 30
    assert all(data[:2] == b"\xff\xd8" for data in images[1:])
    boxed = cv2.imdecode(np.frombuffer(images[1], np.uint8), cv2.IMREAD_COLOR)
    assert boxed[20, 35].tolist() != boxed[150, 100].tolist()  # a box was drawn on the frame
    assert observer.camera == "in the doorway"

    sofa, table = result.items
    assert (sofa.pose.x, sofa.pose.z, sofa.pose.yaw_deg) == pytest.approx(
        (2.0, 0.25, 0.0), abs=0.03
    )
    assert result.records["sofa"].method == "hint" and result.records["table"].method == "hint"
    # A model's answer is never taken as settled.
    assert sofa.correction_needed == ["placement", "orientation"]
    assert result.records["sofa"].primary_frame_index == 0


def test_frames_are_chosen_to_show_every_asset() -> None:
    assets = [_seen(f"a{i}", [i, 100], i) for i in range(10)]
    shots = ov._shots(assets, _by_index)
    assert len(shots) == ov.MAX_FRAMES
    assert shots[0].shows == set(range(1, 11))  # the shared wide frame comes first
    one = ov._shots([_seen("a", [1], 1), _seen("b", [1], 1)], lambda *_: _jpeg(9))
    assert len(one) == 1 and len(one[0].marks) == 2  # the same image is sent once


def _decode(data: bytes) -> np.ndarray:
    return cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)


def test_a_mask_is_traced_and_a_missing_one_falls_back_to_the_box() -> None:
    mask = np.zeros((160, 120), bool)
    mask[60:120, 30:90] = True  # the item, away from its evidence box (10, 20, 50, 60)
    assets = [_seen("masked", [0], 0), _seen("boxed", [0], 0)]

    def masks(asset_id: str, frame: EvidenceFrame) -> np.ndarray | None:
        return mask if asset_id == "masked" else None

    (shot,) = ov._shots(assets, _by_index, masks)
    image = ov._draw_marks(shot)
    plain = _decode(_by_index("x", EvidenceFrame(frame_index=0, timestamp_s=0.0)))
    assert image is not None
    assert image[90, 60].tolist() != plain[90, 60].tolist()  # inside the mask: tinted
    assert image[150, 110].tolist() == pytest.approx(plain[150, 110].tolist(), abs=3)  # untouched
    # Item 2 has no mask: its box is drawn at its evidence bbox.
    assert image[50, 10].tolist() != pytest.approx(plain[50, 10].tolist(), abs=3)

    # A mask of another frame's size cannot be traced: fall back to the box.
    (shot,) = ov._shots(assets[:1], _by_index, lambda *_: np.ones((10, 10), bool))
    boxed = ov._draw_marks(shot)
    assert boxed is not None
    assert boxed[50, 10].tolist() != pytest.approx(plain[50, 10].tolist(), abs=3)
    assert boxed[90, 60].tolist() == pytest.approx(plain[90, 60].tolist(), abs=3)


def test_selection_masks_read_mask_urls_under_the_data_directory(tmp_path: Path) -> None:
    pixels = np.zeros((16, 12), np.uint8)
    pixels[4:8, 2:6] = 255
    (tmp_path / "masks").mkdir()
    cv2.imwrite(str(tmp_path / "masks/m.png"), pixels)
    outside = tmp_path.parent / f"{tmp_path.name}-outside.png"
    cv2.imwrite(str(outside), pixels)
    source = ov.selection_masks(tmp_path)

    def frame(mask_url: str | None) -> EvidenceFrame:
        return EvidenceFrame(frame_index=0, timestamp_s=0.0, mask_url=mask_url)

    mask = source("a", frame("masks/m.png"))
    assert mask is not None and mask.dtype == bool and int(mask.sum()) == 16
    assert source("a", frame(None)) is None
    assert source("a", frame("masks/missing.png")) is None
    assert source("a", frame(f"../{outside.name}")) is None  # refused, not read


def test_the_observer_traces_masks_it_is_given() -> None:
    room = _room()
    mask = np.zeros((160, 120), bool)
    mask[60:120, 30:90] = True
    observer = _Stub([_reply(room, {"asset": 1, "at": (2.0, 0.25), "against_wall": "A"})])
    observer.masks = lambda *_: mask
    assert len(observer.observe(room, [_seen("a", [0], 0)], _by_index)) == 1
    ((prompt, images),) = observer.requests
    assert "box or a traced outline" in prompt
    sent = _decode(images[1])
    plain = _decode(_by_index("a", EvidenceFrame(frame_index=0, timestamp_s=0.0)))
    assert np.abs(sent[90, 60].astype(int) - plain[90, 60].astype(int)).max() > 10


@pytest.mark.parametrize(
    "answers, requests",
    [
        (["no json here", "still {not json"], 2),  # unreadable twice: give up
        ([RuntimeError("provider down")], 1),
        ([None], 1),  # provider unavailable (no key or client)
    ],
)
def test_observer_failures_mean_no_hints(
    answers: list[str | None | Exception], requests: int
) -> None:
    observer = _Stub(answers)
    result = align_assets(_room(), [_seen("a", [0], 0)], observer, _by_index)
    assert len(observer.requests) == requests
    assert result.records["a"].method == "default"
    assert result.items[0].correction_needed == ["placement", "orientation"]


def test_observer_retries_an_unreadable_answer() -> None:
    room = _room()
    good = _reply(room, {"asset": 1, "at": (2.0, 0.25), "against_wall": "A"})
    observer = _Stub(["garbage", good])
    assert len(observer.observe(room, [_seen("a", [0], 0)], _by_index)) == 1
    assert observer.warnings == ["unreadable placement answer (ValueError)"]


def test_observer_without_frames_or_key_asks_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    observer = _Stub([])
    assert observer.observe(_room(), [_seen("a", [0], 0)], lambda *_: None) == []
    assert observer.requests == [] and "no evidence frames" in observer.warnings[0]

    monkeypatch.delenv("FAL_KEY", raising=False)
    real = ov.FalVisionObserver()
    assert real.observe(_room(), [_seen("a", [0], 0)], _by_index) == []
    assert real.warnings == ["FAL_KEY is not set; placement hints were not requested"]


# --- frame sources ----------------------------------------------------------------------------


def test_directory_frames(tmp_path: Path) -> None:
    (tmp_path / "30.jpg").write_bytes(b"thirty")
    source = ov.directory_frames(tmp_path)
    assert source("any", EvidenceFrame(frame_index=30, timestamp_s=1.0)) == b"thirty"
    assert source("any", EvidenceFrame(frame_index=31, timestamp_s=1.0)) is None


def test_selection_frames_reads_the_selector_output(tmp_path: Path) -> None:
    source_id = "a" * 64
    (tmp_path / "frames").mkdir()
    (tmp_path / "frames/f30.png").write_bytes(b"png-30")
    result = SelectionResult.model_validate(
        {
            "scene_id": "s",
            "registry_revision": 1,
            "sources": [],
            "frames": [
                {
                    "key": f"{source_id}:0:30",
                    "source_id": source_id,
                    "frame_index": 30,
                    "pts": 30,
                    "timestamp_s": 1.0,
                    "image_size_px": [120, 160],
                    "image_path": "frames/f30.png",
                    "quality": 0.9,
                },
                {
                    "key": f"{source_id}:0:60",
                    "source_id": source_id,
                    "frame_index": 60,
                    "pts": 60,
                    "timestamp_s": 2.0,
                    "image_size_px": [120, 160],
                    "image_path": "../outside.png",
                    "quality": 0.9,
                },
            ],
            "objects": [
                {
                    "id": "vid-sofa-01",
                    "name": "Sofa",
                    "category": "sofa",
                    "appearance": "brown",
                    "sightings": [
                        {
                            "frame_key": f"{source_id}:0:30",
                            "box": {"x": 0.1, "y": 0.1, "width": 0.5, "height": 0.5},
                        },
                        {
                            "frame_key": f"{source_id}:0:60",
                            "box": {"x": 0.1, "y": 0.1, "width": 0.5, "height": 0.5},
                        },
                    ],
                }
            ],
            "geometry_frame_keys": [],
            "unresolved": [],
            "warnings": [],
            "complete": True,
        }
    )
    segmented = SegmentationResult.model_validate(
        {
            **result.model_dump(include={"scene_id", "registry_revision", "frames", "objects"}),
            "missing": [],
            "warnings": [],
            "complete": True,
        }
    )
    for given in (result, segmented):  # #14 selection or #15 segmentation output
        source = ov.selection_frames(given, tmp_path)
        assert source("vid-sofa-01", EvidenceFrame(frame_index=30, timestamp_s=1.0)) == b"png-30"
        escape = EvidenceFrame(frame_index=60, timestamp_s=2.0)
        assert source("vid-sofa-01", escape) is None
        assert source("other", EvidenceFrame(frame_index=30, timestamp_s=1.0)) is None


# --- debug CLI --------------------------------------------------------------------------------


def test_cli_places_the_reception_assets_from_recorded_hints(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code = align_main(
        [
            "--demo",
            "g-reception",
            "--out",
            str(tmp_path),
            "--assets",
            str(FIXTURES / "reception.assets.json"),
            "--hints",
            str(FIXTURES / "reception.hints.json"),
            "--save-hints",
            str(tmp_path / "hints.json"),
        ]
    )
    assert code == 0
    out = capsys.readouterr().out
    assert "g-reception-o01" in out and "vs reference" in out
    aligned = RoomScene.model_validate_json((tmp_path / "g-reception.json").read_text())
    assert aligned.scene_id == "g-reception"  # the room ID the editor opens
    assert len(aligned.furniture) == 7  # the room's three fixed items plus the four assets
    records = json.loads((tmp_path / "records.json").read_text())
    assert {r["method"] for r in records.values()} == {"hint"}
    assert json.loads((tmp_path / "hints.json").read_text()) == json.loads(
        (FIXTURES / "reception.hints.json").read_text()
    )
    assert (tmp_path / "g-reception.png").stat().st_size > 1000


def test_cli_default_layout_for_a_floor(tmp_path: Path) -> None:
    assert align_main(["--demo", "second", "--out", str(tmp_path)]) == 0
    scene = RoomScene.model_validate_json((MOCKS / "three_floor_second_scene.json").read_text())
    placed = [
        item
        for path in sorted(tmp_path.glob("s-*.json"))
        for item in RoomScene.model_validate_json(path.read_text()).furniture
    ]
    assert sorted(f.id for f in placed) == sorted(f.id for f in scene.furniture)
    assert sorted(p.stem for p in tmp_path.glob("*.png")) == ["s-bath", "s-bed7", "s-bed8"]


def test_cli_takes_a_single_room_scene_and_rejects_unknown_rooms(tmp_path: Path) -> None:
    assert align_main(["--scene", str(MOCKS / "mock_scene.json"), "--out", str(tmp_path)]) == 0
    assert (tmp_path / "demo_studio_01.json").is_file()
    assert align_main(["--demo", "no-such-room", "--out", str(tmp_path)]) == 1
    two = ["--demo", "g-master", "g-kitchen", "--assets", str(FIXTURES / "reception.assets.json")]
    assert align_main([*two, "--out", str(tmp_path)]) == 1  # --assets needs one room
