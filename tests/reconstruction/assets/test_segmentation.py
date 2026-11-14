from __future__ import annotations

import json
import shutil
from collections.abc import Callable
from pathlib import Path
from unittest.mock import Mock

import cv2
import fal_client
import numpy as np
import pytest
from numpy.typing import NDArray
from pydantic import ValidationError

from services.reconstruction.assets.mask_providers import (
    FalSamProvider,
    GrabCutProvider,
    MaskError,
    Segment,
)
from services.reconstruction.assets.models import AssetEvidence
from services.reconstruction.assets.providers import RecordedProvider, RequestBudget
from services.reconstruction.assets.registry import Registry
from services.reconstruction.assets.segment_items import main
from services.reconstruction.assets.segmentation import read_mask, segment_furniture
from services.reconstruction.assets.selection import object_evidence, select_furniture_frames
from services.reconstruction.assets.selection_models import (
    Box,
    Discovery,
    Frame,
    MaskRecord,
    RegistryState,
    SegmentationResult,
    SelectedObject,
    SelectionOptions,
    Sighting,
)

SOURCE = "a" * 64
W, H = 240, 160
Rect = tuple[int, int, int, int]
"""True object pixels as (x0, y0, x1, y1)."""
RED: Rect = (30, 40, 100, 110)
BLUE: Rect = (140, 30, 210, 90)
Mask = NDArray[np.bool_]


def loose_box(rect: Rect, pad: int = 6) -> Box:
    """A coarse reviewed box: a few pixels larger than the object, like the #14 annotations."""
    x0, y0, x1, y1 = rect
    return Box(
        x=(x0 - pad) / W,
        y=(y0 - pad) / H,
        width=(x1 - x0 + 2 * pad) / W,
        height=(y1 - y0 + 2 * pad) / H,
    )


def rect_mask(rect: Rect) -> Mask:
    mask = np.zeros((H, W), bool)
    mask[rect[1] : rect[3], rect[0] : rect[2]] = True
    return mask


def iou(a: Mask, b: Mask) -> float:
    return float((a & b).sum() / (a | b).sum())


def make_scene(
    data_dir: Path, rects: dict[str, Rect], *, index: int = 0, scene_id: str = "scene"
) -> Frame:
    """One synthetic frame with a flat coloured rectangle per item, registered as #14 would."""
    frame = Frame(
        key=f"{SOURCE}:0:{index}",
        source_id=SOURCE,
        frame_index=index,
        pts=index * 100,
        timestamp_s=float(index),
        image_size_px=(W, H),
        image_path=f"frames/{SOURCE}/{index}.png",
        quality=0.8,
    )
    image = np.random.default_rng(0).integers(110, 140, (H, W, 3)).astype(np.uint8)
    colours = [(40, 40, 220), (220, 60, 40), (40, 200, 60)]
    for colour, (x0, y0, x1, y1) in zip(colours, rects.values(), strict=False):
        image[y0:y1, x0:x1] = colour
    path = data_dir / frame.image_path
    path.parent.mkdir(parents=True, exist_ok=True)
    assert cv2.imwrite(str(path), image)

    def add(state: RegistryState) -> None:
        state.frames[frame.key] = frame
        for object_id, rect in rects.items():
            sighting = Sighting(frame_key=frame.key, box=loose_box(rect), quality=0.8)
            if object_id in state.objects:
                state.objects[object_id].sightings.append(sighting)
                state.objects[object_id].selected_views.append(frame.key)
            else:
                state.objects[object_id] = SelectedObject(
                    id=object_id,
                    name=object_id,
                    category="other",
                    appearance="flat colour",
                    sightings=[sighting],
                    selected_views=[frame.key],
                )

    Registry(data_dir, namespace=scene_id).update(scene_id, add)
    return frame


class FakeProvider:
    """Test double for the provider boundary: replies with whatever `reply` returns."""

    method = "sam3"

    def __init__(self, reply: Callable[[list[Box]], list[Mask | None]] | None = None) -> None:
        self.reply = reply or (lambda boxes: [box_mask(box) for box in boxes])
        self.calls: list[list[Box]] = []
        self.score: float | None = 0.95

    def segment(
        self,
        frame: Frame,
        image: NDArray[np.uint8],
        boxes: list[Box],
        registry: Registry,
        *,
        budget: RequestBudget | None = None,
    ) -> list[Segment | None]:
        self.calls.append(list(boxes))
        return [None if mask is None else Segment(mask, self.score) for mask in self.reply(boxes)]


def box_mask(box: Box) -> Mask:
    mask = np.zeros((H, W), bool)
    mask[round(box.y * H) : round((box.y + box.height) * H), round(box.x * W) :][
        :, : round(box.width * W)
    ] = True
    return mask


def record(frame_key: str, box: Box) -> MaskRecord:
    return MaskRecord(
        frame_key=frame_key,
        box=box,
        method="grabcut",
        mask_path="masks/m.png",
        crop_path="masks/m.crop.png",
        bbox_px=(1, 2, 3, 4),
        area_px=12,
    )


def test_mask_records_must_belong_to_one_sighting_each() -> None:
    box = loose_box(RED)
    base = {
        "id": "vid-000001",
        "name": "Sofa",
        "category": "sofa",
        "appearance": "brown",
        "sightings": [Sighting(frame_key="f:0:0", box=box)],
    }
    obj = SelectedObject.model_validate({**base, "masks": [record("f:0:0", box)]})
    assert obj.mask_for("f:0:0") == obj.masks[0] and obj.mask_for("f:0:1") is None
    with pytest.raises(ValidationError, match="masks"):
        SelectedObject.model_validate({**base, "masks": [record("f:0:9", box)]})
    with pytest.raises(ValidationError, match="masks"):
        SelectedObject.model_validate({**base, "masks": [record("f:0:0", box)] * 2})


def test_mask_is_not_current_after_its_sighting_box_changes() -> None:
    obj = SelectedObject(
        id="vid-000001",
        name="Sofa",
        category="sofa",
        appearance="brown",
        sightings=[Sighting(frame_key="f:0:0", box=loose_box(BLUE))],
        masks=[record("f:0:0", loose_box(RED))],
    )
    assert obj.mask_for("f:0:0") is None


def test_registry_snapshots_written_before_masks_still_load() -> None:
    old = {
        "objects": {
            "vid-000001": {
                "id": "vid-000001",
                "name": "Sofa",
                "category": "sofa",
                "appearance": "brown",
                "sightings": [{"frame_key": "f:0:0", "box": loose_box(RED).model_dump()}],
            }
        },
        "frames": {"f:0:0": make_scene_frame_dict()},
    }
    assert RegistryState.model_validate(old).objects["vid-000001"].masks == []


def make_scene_frame_dict() -> dict[str, object]:
    return {
        "key": "f:0:0",
        "source_id": SOURCE,
        "frame_index": 0,
        "pts": 0,
        "timestamp_s": 0,
        "image_size_px": (W, H),
        "image_path": "0.png",
        "quality": 0.5,
    }


def test_each_item_gets_its_own_mask_and_cutout_linked_to_the_source_frame(tmp_path: Path) -> None:
    frame = make_scene(tmp_path, {"vid-000001": RED, "vid-000002": BLUE})
    result = segment_furniture("scene", data_dir=tmp_path, provider=GrabCutProvider())
    assert result.complete and result.missing == []
    assert [obj.id for obj in result.objects] == ["vid-000001", "vid-000002"]
    assert [f.key for f in result.frames] == [frame.key]
    for obj, rect in zip(result.objects, (RED, BLUE), strict=True):
        (mask,) = obj.masks
        assert mask.frame_key == frame.key and mask.method == "grabcut" and mask.score is None
        assert mask.box == loose_box(rect)
        pixels = read_mask(tmp_path, mask.mask_path)
        assert pixels.shape == (H, W) and iou(pixels, rect_mask(rect)) >= 0.9
        x, y, w, h = mask.bbox_px
        assert mask.area_px == int(pixels.sum()) == int(pixels[y : y + h, x : x + w].sum())
        assert abs(x - rect[0]) <= 2 and abs(y - rect[1]) <= 2
        cutout = cv2.imread(str(tmp_path / mask.crop_path), cv2.IMREAD_UNCHANGED)
        original = cv2.imread(str(tmp_path / frame.image_path))
        assert cutout.shape == (h, w, 4)
        assert np.array_equal(cutout[..., 3] > 0, pixels[y : y + h, x : x + w])
        assert np.array_equal(cutout[..., :3], original[y : y + h, x : x + w])
    stored = Registry(tmp_path, namespace="scene").load("scene")
    assert [obj.masks for obj in stored.objects.values()] == [obj.masks for obj in result.objects]
    assert result.registry_revision == stored.revision
    assert any("GrabCut" in warning for warning in result.warnings)


def test_rerun_reuses_stored_masks_and_replace_segments_again(tmp_path: Path) -> None:
    make_scene(tmp_path, {"vid-000001": RED, "vid-000002": BLUE})
    provider = FakeProvider()
    first = segment_furniture("scene", data_dir=tmp_path, provider=provider)
    second = segment_furniture("scene", data_dir=tmp_path, provider=provider)
    assert len(provider.calls) == 1 and len(provider.calls[0]) == 2
    assert second.complete and second.objects == first.objects
    third = segment_furniture("scene", data_dir=tmp_path, provider=provider, replace=True)
    assert len(provider.calls) == 2 and third.objects == first.objects


def test_changed_box_or_lost_file_is_segmented_again(tmp_path: Path) -> None:
    frame = make_scene(tmp_path, {"vid-000001": RED, "vid-000002": BLUE})
    provider = FakeProvider()
    first = segment_furniture("scene", data_dir=tmp_path, provider=provider)
    moved = loose_box(RED, pad=10)

    def move(state: RegistryState) -> None:
        state.objects["vid-000001"].sightings = [Sighting(frame_key=frame.key, box=moved)]

    Registry(tmp_path, namespace="scene").update("scene", move)
    second = segment_furniture("scene", data_dir=tmp_path, provider=provider)
    assert provider.calls[1] == [moved] and second.complete
    assert second.objects[0].masks[0].box == moved
    assert second.objects[1].masks == first.objects[1].masks
    (tmp_path / second.objects[1].masks[0].mask_path).unlink()
    third = segment_furniture("scene", data_dir=tmp_path, provider=provider)
    assert provider.calls[2] == [loose_box(BLUE)] and third.complete
    assert (tmp_path / third.objects[1].masks[0].mask_path).is_file()


@pytest.mark.parametrize(
    ("reply", "reason"),
    [
        (lambda boxes: [None for _ in boxes], "no mask returned"),
        (lambda boxes: [np.zeros((H, W), bool) for _ in boxes], "empty"),
        (lambda boxes: [np.ones((H // 2, W // 2), bool) for _ in boxes], "size"),
        (lambda boxes: [rect_mask((0, 120, 30, 160)) for _ in boxes], "disagrees"),
        (lambda boxes: [box_mask(boxes[0])], "one mask per box"),
    ],
)
def test_unusable_masks_are_reported_and_never_stored(
    tmp_path: Path, reply: Callable[[list[Box]], list[Mask | None]], reason: str
) -> None:
    frame = make_scene(tmp_path, {"vid-000001": RED, "vid-000002": BLUE})
    result = segment_furniture("scene", data_dir=tmp_path, provider=FakeProvider(reply))
    assert not result.complete
    assert [(m.object_id, m.frame_key) for m in result.missing] == [
        ("vid-000001", frame.key),
        ("vid-000002", frame.key),
    ]
    assert all(reason in m.reason for m in result.missing)
    assert [obj.masks for obj in result.objects] == [[], []]
    assert not (tmp_path / "masks").exists() or not list((tmp_path / "masks").rglob("*.png"))


def test_a_mask_for_the_wrong_item_is_rejected_while_the_right_one_is_kept(tmp_path: Path) -> None:
    make_scene(tmp_path, {"vid-000001": RED, "vid-000002": BLUE})
    swapped = FakeProvider(lambda boxes: [box_mask(boxes[0]), box_mask(boxes[0])])
    result = segment_furniture("scene", data_dir=tmp_path, provider=swapped)
    assert [m.object_id for m in result.missing] == ["vid-000002"]
    assert len(result.objects[0].masks) == 1 and result.objects[1].masks == []


def test_provider_failure_and_missing_frame_image_keep_items_and_other_frames(
    tmp_path: Path,
) -> None:
    first = make_scene(tmp_path, {"vid-000001": RED})
    second = make_scene(tmp_path, {"vid-000001": RED}, index=1)
    (tmp_path / second.image_path).unlink()
    result = segment_furniture("scene", data_dir=tmp_path, provider=FakeProvider())
    assert [m.frame_key for m in result.missing] == [second.key] and not result.complete
    assert "unavailable" in result.missing[0].reason
    assert [m.frame_key for m in result.objects[0].masks] == [first.key]

    def fail(boxes: list[Box]) -> list[Mask | None]:
        raise MaskError("provider unavailable; safe to retry")

    failed = segment_furniture(
        "scene", data_dir=tmp_path, provider=FakeProvider(fail), replace=True
    )
    assert {m.reason for m in failed.missing} >= {"provider unavailable; safe to retry"}
    # A failed replacement never discards the mask that was already stored.
    assert failed.objects[0].masks == result.objects[0].masks


def test_overlapping_masks_of_different_items_are_flagged(tmp_path: Path) -> None:
    frame = make_scene(tmp_path, {"vid-000001": RED, "vid-000002": (60, 50, 130, 120)})
    result = segment_furniture("scene", data_dir=tmp_path, provider=FakeProvider())
    assert result.complete
    (warning,) = [w for w in result.warnings if "overlap" in w]
    assert "vid-000001" in warning and "vid-000002" in warning and str(frame.frame_index) in warning


def test_only_requested_items_are_segmented_and_unknown_inputs_are_rejected(tmp_path: Path) -> None:
    make_scene(tmp_path, {"vid-000001": RED, "vid-000002": BLUE})
    provider = FakeProvider()
    result = segment_furniture(
        "scene", data_dir=tmp_path, provider=provider, object_ids=["vid-000002"]
    )
    assert [obj.id for obj in result.objects] == ["vid-000002"]
    assert provider.calls == [[loose_box(BLUE)]]
    with pytest.raises(ValueError, match="unknown object"):
        segment_furniture("scene", data_dir=tmp_path, provider=provider, object_ids=["vid-9"])
    with pytest.raises(ValueError, match="no selected furniture"):
        segment_furniture("other-scene", data_dir=tmp_path, provider=provider)
    with pytest.raises(ValueError, match="scene_id"):
        segment_furniture(" ", data_dir=tmp_path, provider=provider)
    with pytest.raises(ValueError, match="no furniture registry"):
        segment_furniture("scene", data_dir=tmp_path / "mistyped", provider=provider)
    assert not (tmp_path / "mistyped").exists()


def test_read_mask_refuses_paths_outside_the_data_directory(tmp_path: Path) -> None:
    data = tmp_path / "data"
    data.mkdir()
    assert cv2.imwrite(str(tmp_path / "outside.png"), np.full((4, 4), 255, np.uint8))
    with pytest.raises(ValueError, match="outside"):
        read_mask(data, "../outside.png")
    with pytest.raises(ValueError, match="unavailable"):
        read_mask(data, "masks/absent.png")


def test_evidence_carries_the_mask_reference_and_its_tight_box(tmp_path: Path) -> None:
    frame = make_scene(tmp_path, {"vid-000001": RED})
    other = make_scene(tmp_path, {"vid-000001": RED}, index=1)

    def unselect(state: RegistryState) -> None:
        state.objects["vid-000001"].selected_views = [frame.key]

    Registry(tmp_path, namespace="scene").update("scene", unselect)
    result = segment_furniture("scene", data_dir=tmp_path, provider=FakeProvider())
    (mask,) = result.objects[0].masks
    evidence = object_evidence(result, "vid-000001")
    masked, plain = evidence.frames
    assert masked.frame_index == frame.frame_index and masked.mask_url == mask.mask_path
    assert masked.bbox_px == tuple(float(v) for v in mask.bbox_px)
    assert read_mask(tmp_path, masked.mask_url).sum() == mask.area_px
    # A sighting outside the selected views keeps its #14 box and has no mask.
    box = loose_box(RED)
    assert plain.frame_index == other.frame_index and plain.mask_url is None
    assert plain.bbox_px == (box.x * W, box.y * H, box.width * W, box.height * H)


def png(mask: Mask) -> bytes:
    ok, encoded = cv2.imencode(".png", mask.astype(np.uint8) * 255)
    assert ok
    return bytes(encoded.tobytes())


def sam(files: dict[str, bytes], order: list[int]) -> FalSamProvider:
    """A live provider whose network edges are replaced: `order[i]` is mask i's prompt index."""
    provider = FalSamProvider(key="test-never-sent", fetch=files.__getitem__)
    provider.client = Mock()
    provider.client.upload.return_value = "https://v3b.fal.media/files/frame.png"
    handle = provider.client.submit.return_value
    handle.request_id = "request-one"
    handle.status.return_value = fal_client.Completed(metrics={}, logs=[])
    urls = list(files)
    handle.get.return_value = {
        "masks": [{"url": urls[i]} for i in range(len(order))],
        # Best score first, as the live endpoint orders them.
        "metadata": [{"index": index, "score": 0.9 - 0.2 * i} for i, index in enumerate(order)],
    }
    provider.client.get_handle.return_value = handle
    return provider


def sam_scene(tmp_path: Path) -> tuple[Frame, NDArray[np.uint8], list[Box], Registry]:
    frame = make_scene(tmp_path, {"vid-000001": RED, "vid-000002": BLUE})
    image = cv2.imread(str(tmp_path / frame.image_path)).astype(np.uint8)
    return frame, image, [loose_box(RED), loose_box(BLUE)], Registry(tmp_path, namespace="scene")


# The provider returns masks best-score first, so BLUE (prompt 1) can precede RED (prompt 0).
BLUE_FIRST = {
    "https://v3b.fal.media/files/blue.png": png(rect_mask(BLUE)),
    "https://v3b.fal.media/files/red.png": png(rect_mask(RED)),
}


def test_sam_masks_are_matched_to_items_by_prompt_index_not_by_position(tmp_path: Path) -> None:
    frame, image, boxes, registry = sam_scene(tmp_path)
    provider = sam(BLUE_FIRST, [1, 0])
    red, blue = provider.segment(frame, image, boxes, registry)
    assert red is not None and blue is not None
    assert np.array_equal(red.pixels, rect_mask(RED)) and red.score == 0.7
    assert np.array_equal(blue.pixels, rect_mask(BLUE)) and blue.score == 0.9
    arguments = provider.client.submit.call_args.kwargs["arguments"]
    assert provider.client.submit.call_args.args == ("fal-ai/sam-3/image",)
    assert arguments["box_prompts"] == [
        {"x_min": 24, "y_min": 34, "x_max": 106, "y_max": 116, "object_id": 1},
        {"x_min": 134, "y_min": 24, "x_max": 216, "y_max": 96, "object_id": 2},
    ]
    assert arguments["prompt"] == "" and arguments["apply_mask"] is False
    assert arguments["return_multiple_masks"] is True and arguments["max_masks"] == 2
    assert arguments["image_url"] == "https://v3b.fal.media/files/frame.png"
    assert provider.client.upload.call_args.args[1] == "image/png"


def test_sam_item_without_a_returned_mask_is_none(tmp_path: Path) -> None:
    frame, image, boxes, registry = sam_scene(tmp_path)
    only_blue = {"https://v3b.fal.media/files/blue.png": png(rect_mask(BLUE))}
    red, blue = sam(only_blue, [1]).segment(frame, image, boxes, registry)
    assert red is None and blue is not None and np.array_equal(blue.pixels, rect_mask(BLUE))


def test_sam_rerun_rereads_the_saved_request_and_refresh_pays_again(tmp_path: Path) -> None:
    frame, image, boxes, registry = sam_scene(tmp_path)
    budget = RequestBudget(5)
    first = sam(BLUE_FIRST, [1, 0])
    first.segment(frame, image, boxes, registry, budget=budget)
    again = sam(BLUE_FIRST, [1, 0])
    red, _ = again.segment(frame, image, boxes, registry, budget=budget)
    assert red is not None and np.array_equal(red.pixels, rect_mask(RED))
    assert again.client.submit.call_count == 0 and again.client.upload.call_count == 0
    again.client.get_handle.assert_called_once_with("fal-ai/sam-3/image", "request-one")
    assert budget.used == 1
    again.refresh = "second-opinion"
    again.segment(frame, image, boxes, registry, budget=budget)
    assert again.client.submit.call_count == 1 and budget.used == 2


def test_sam_exhausted_budget_submits_nothing_and_stays_retryable(tmp_path: Path) -> None:
    frame, image, boxes, registry = sam_scene(tmp_path)
    provider = sam(BLUE_FIRST, [1, 0])
    with pytest.raises(MaskError, match="budget"):
        provider.segment(frame, image, boxes, registry, budget=RequestBudget(0))
    assert provider.client.upload.call_count == 0 and provider.client.submit.call_count == 0
    red, _ = provider.segment(frame, image, boxes, registry, budget=RequestBudget(1))
    assert red is not None and provider.client.submit.call_count == 1


def test_sam_uncertain_submission_and_malformed_result_are_never_repeated(tmp_path: Path) -> None:
    frame, image, boxes, registry = sam_scene(tmp_path)
    provider = sam(BLUE_FIRST, [1, 0])
    provider.client.submit.side_effect = RuntimeError("secret body: submit result lost")
    with pytest.raises(MaskError, match="request state retained") as raised:
        provider.segment(frame, image, boxes, registry)
    assert "secret" not in str(raised.value)
    with pytest.raises(MaskError, match="duplicate charge"):
        provider.segment(frame, image, boxes, registry)
    assert provider.client.submit.call_count == 1
    malformed = sam(BLUE_FIRST, [1, 0])
    malformed.refresh = "malformed"
    malformed.client.submit.return_value.get.return_value = {"masks": "not a list"}
    with pytest.raises(MaskError, match="malformed"):
        malformed.segment(frame, image, boxes, registry)
    with pytest.raises(MaskError, match="previous request failed"):
        malformed.segment(frame, image, boxes, registry)
    assert malformed.client.submit.call_count == 1


@pytest.mark.parametrize(
    "url",
    [
        "http://v3b.fal.media/files/red.png",
        "https://evil.example/red.png",
        "https://fal.media.evil.example/red.png",
        "file:///etc/passwd",
    ],
)
def test_sam_downloads_masks_only_over_https_from_fal_media(tmp_path: Path, url: str) -> None:
    frame, image, boxes, registry = sam_scene(tmp_path)
    fetched: list[str] = []
    provider = sam({url: png(rect_mask(RED))}, [0])
    provider.fetch = lambda target: fetched.append(target) or b""
    with pytest.raises(MaskError, match="not allowed"):
        provider.segment(frame, image, boxes, registry)
    assert fetched == []


def test_live_masks_flow_through_the_pipeline_with_their_provenance(tmp_path: Path) -> None:
    make_scene(tmp_path, {"vid-000001": RED, "vid-000002": BLUE})
    provider = sam(BLUE_FIRST, [1, 0])
    result = segment_furniture("scene", data_dir=tmp_path, provider=provider)
    assert result.complete
    for obj, rect, score in zip(result.objects, (RED, BLUE), (0.7, 0.9), strict=True):
        (mask,) = obj.masks
        assert mask.method == "sam3" and mask.score == score
        assert np.array_equal(read_mask(tmp_path, mask.mask_path), rect_mask(rect))
    # The provider's own confidence singles out the mask a person should look at.
    (warning,) = result.warnings
    assert "low-confidence" in warning and "vid-000001" in warning and "0.70" in warning


def test_cli_writes_masks_evidence_and_review_images_offline(tmp_path: Path) -> None:
    data, out = tmp_path / "data", tmp_path / "report"
    data.mkdir()
    make_scene(data, {"vid-000001": RED, "vid-000002": BLUE})
    assert main(["--scene-id", "scene", "--data-dir", str(data), "--out", str(out)]) == 0
    result = SegmentationResult.model_validate_json((out / "segmentation.json").read_text())
    assert result.complete and len(result.objects) == 2
    evidence = json.loads((out / "evidence.json").read_text())
    assert sorted(evidence) == ["vid-000001", "vid-000002"]
    for object_id, raw in evidence.items():
        (frame,) = AssetEvidence.model_validate(raw).frames
        assert frame.mask_url is not None and read_mask(data, frame.mask_url).any()
        assert (out / f"{object_id}-0-mask.jpg").is_file()
        assert (
            cv2.imread(str(out / f"{object_id}-0-cutout.png"), cv2.IMREAD_UNCHANGED).shape[2] == 4
        )
    report = (out / "report.md").read_text()
    assert "vid-000001" in report and "grabcut" in report


def test_cli_exit_codes_for_incomplete_and_invalid_runs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    data, out = tmp_path / "data", tmp_path / "report"
    data.mkdir()
    make_scene(data, {"vid-000001": RED})
    lost = make_scene(data, {"vid-000001": RED}, index=1)
    (data / lost.image_path).unlink()
    base = ["--data-dir", str(data), "--out", str(out)]
    assert main(["--scene-id", "scene", *base]) == 2
    assert "unavailable" in (out / "report.md").read_text()
    assert (out / "vid-000001-0-mask.jpg").is_file()
    assert main(["--scene-id", "scene", "--object-id", "vid-9", *base]) == 1
    assert main(["--scene-id", "absent", *base]) == 1
    monkeypatch.delenv("FAL_KEY", raising=False)
    assert main(["--scene-id", "scene", "--live", *base]) == 1


def test_reviewed_real_room_items_all_get_masks_offline(tmp_path: Path) -> None:
    video = Path(__file__).resolve().parents[3] / "examples/three_floor_3.mp4"
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None or not video.exists():
        pytest.skip("needs FFmpeg/FFprobe and the optional repository example video")
    discovery = Discovery.model_validate_json(
        (Path(__file__).parent / "fixtures/opening_room.reviewed.json").read_text()
    )
    selection = select_furniture_frames(
        [video],
        "reviewed-room",
        data_dir=tmp_path,
        provider=RecordedProvider(discovery),
        options=SelectionOptions(end_s=6, max_frames_per_video=8, batch_size=3),
    )
    first = segment_furniture("reviewed-room", data_dir=tmp_path)
    assert first.complete and [obj.id for obj in first.objects] == [o.id for o in selection.objects]
    for obj in first.objects:
        assert len(obj.selected_views) >= 3
        assert [m.frame_key for m in obj.masks] == sorted(obj.selected_views)
        evidence = object_evidence(first, obj.id)
        primary = next(f for f in evidence.frames if f.frame_index == evidence.primary_frame_index)
        assert primary.mask_url is not None and read_mask(tmp_path, primary.mask_url).any()
    assert segment_furniture("reviewed-room", data_dir=tmp_path).objects == first.objects


def test_primary_evidence_frame_avoids_a_low_confidence_mask(tmp_path: Path) -> None:
    sharp = make_scene(tmp_path, {"vid-000001": RED})
    other = make_scene(tmp_path, {"vid-000001": RED}, index=1)
    registry = Registry(tmp_path, namespace="scene")

    def prefer_first(state: RegistryState) -> None:
        state.objects["vid-000001"].sightings[0].quality = 0.9

    registry.update("scene", prefer_first)
    result = segment_furniture("scene", data_dir=tmp_path, provider=FakeProvider())
    assert object_evidence(result, "vid-000001").primary_frame_index == sharp.frame_index

    def doubt_first(state: RegistryState) -> None:
        state.objects["vid-000001"].masks[0].score = 0.5

    registry.update("scene", doubt_first)
    result = segment_furniture("scene", data_dir=tmp_path, provider=FakeProvider())
    assert object_evidence(result, "vid-000001").primary_frame_index == other.frame_index


def test_frame_image_that_no_longer_matches_its_record_is_reported(tmp_path: Path) -> None:
    frame = make_scene(tmp_path, {"vid-000001": RED})
    assert cv2.imwrite(str(tmp_path / frame.image_path), np.zeros((H // 2, W // 2, 3), np.uint8))
    provider = FakeProvider()
    result = segment_furniture("scene", data_dir=tmp_path, provider=provider)
    assert [m.reason for m in result.missing] == ["frame artifact size differs from its record"]
    assert provider.calls == [] and result.objects[0].masks == []
