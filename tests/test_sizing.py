"""Furniture sizes measured against the floor plan (`room/sizing.py`). No test calls fal."""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path

import pytest

cv2 = pytest.importorskip("cv2")

import numpy as np  # noqa: E402

from contracts.schema import BBoxM, ParsedFloorPlan, RoomScene  # noqa: E402
from services.reconstruction.assets.models import (  # noqa: E402
    AssetEvidence,
    EvidenceFrame,
    FurnitureAsset,
)
from services.reconstruction.room.assemble import assets_of  # noqa: E402
from services.reconstruction.room.sizing import (  # noqa: E402
    FalSizeEstimator,
    build_prompt,
    fallback,
    parse_reply,
    plausible,
    references,
)

ROOT = Path(__file__).parents[1]
PLAN = ParsedFloorPlan.model_validate(
    json.loads(
        (
            ROOT / "services/reconstruction/room/fixtures/scene_cache/plan-83a12322e933.json"
        ).read_text()
    )["plan"]
)
BEDROOM = next(r.scene for f in PLAN.floors for r in f.rooms if r.name == "Master Bedroom")
TEMPLATE = assets_of(
    RoomScene.model_validate_json((ROOT / "contracts/mock_room/mock_scene.json").read_text())
)[0]


def _asset(asset_id: str, name: str, category: str, w: float, h: float, d: float) -> FurnitureAsset:
    evidence = AssetEvidence(
        frames=[
            EvidenceFrame(
                frame_index=0,
                timestamp_s=0,
                image_size_px=(160, 120),
                bbox_px=(10.0, 10.0, 60.0, 50.0),
            )
        ],
        primary_frame_index=0,
    )
    return TEMPLATE.model_copy(
        update={
            "id": asset_id,
            "name": name,
            "category": category,
            "bbox_m": BBoxM(width=w, height=h, depth=d),
            "evidence": evidence,
            "is_fixed": category == "fixture",
        }
    )


# The master bedroom's bed as the first live run normalised it: SAM 3D extents
# 0.72 x 1.00 x 0.90 scaled so its height is a bed's 0.6 m.
TOY_BED = _asset("vid-000001", "storage bed", "bed", 0.43, 0.6, 0.54)
WARDROBE = _asset("vid-000003", "wooden wardrobe", "wardrobe", 1.26, 1.95, 0.51)


def test_every_metric_reference_of_the_room_is_listed() -> None:
    text = references(BEDROOM)
    assert text.count("- wall ") == len(BEDROOM.walls)
    assert text.count("- door ") == len(BEDROOM.doors)
    assert text.count("- window ") == len(BEDROOM.windows)
    assert " high" in text and " wide" in text
    prompt = build_prompt(BEDROOM, [TOY_BED, WARDROBE])
    assert "- 1: storage bed (bed)" in prompt and "- 2: wooden wardrobe (wardrobe)" in prompt


def test_reply_parsing_keeps_confident_known_items() -> None:
    text = json.dumps(
        {
            "items": [
                {"asset": 1, "width": 1.5, "depth": 2.0, "height": 0.5, "confidence": 0.8},
                {"asset": 2, "width": 1.0, "depth": 0.6, "height": 2.0, "confidence": 0.1},
                {"asset": 9, "width": 1.0, "depth": 0.6, "height": 2.0},
            ]
        }
    )
    assert set(parse_reply(text, 2)) == {1}
    with pytest.raises(ValueError):
        parse_reply("no idea", 2)


def test_sizes_that_cannot_fit_the_item_or_the_room_are_rejected() -> None:
    assert plausible("bed", BBoxM(width=1.5, height=0.5, depth=2.0), BEDROOM) is None
    assert plausible("bed", BBoxM(width=6.0, height=0.5, depth=2.0), BEDROOM) is not None
    assert plausible("wardrobe", BBoxM(width=1.0, height=0.03, depth=0.6), BEDROOM) is not None
    assert plausible("fixture", BBoxM(width=1.0, height=0.6, depth=0.1), BEDROOM) is None
    # A footprint covering most of the floor is not a piece of furniture.
    huge = BBoxM(width=3.4, height=0.5, depth=4.9)
    assert plausible("bed", huge, BEDROOM) is not None


def test_fallback_scales_low_items_by_length_and_tall_items_by_height() -> None:
    bed = fallback(TOY_BED)
    assert max(bed.width, bed.depth) == pytest.approx(2.0, abs=0.01)
    assert bed.width / bed.depth == pytest.approx(0.43 / 0.54, rel=0.01)  # proportions kept
    wardrobe = fallback(WARDROBE)
    assert wardrobe.height == pytest.approx(1.95, abs=0.01)


def _frames(asset_id: str, frame: EvidenceFrame) -> bytes:
    ok, data = cv2.imencode(".jpg", np.full((120, 160, 3), 200, np.uint8))
    assert ok
    return bytes(data.tobytes())


def test_measured_sizes_are_used_and_implausible_ones_fall_back() -> None:
    seen: list[tuple[str, int]] = []

    def ask(prompt: str, images: Sequence[bytes]) -> str:
        seen.append((prompt, len(images)))
        return json.dumps(
            {
                "items": [
                    {"asset": 1, "width": 1.5, "depth": 2.05, "height": 0.45, "confidence": 0.7},
                    {"asset": 2, "width": 9.0, "depth": 0.6, "height": 2.0, "confidence": 0.7},
                ]
            }
        )

    sizes = FalSizeEstimator(ask=ask).estimate(BEDROOM, [TOY_BED, WARDROBE], _frames)
    assert len(seen) == 1 and seen[0][1] >= 2  # the plan, then at least one marked frame
    bed = sizes.dimensions["vid-000001"]
    assert bed.source == "estimated"
    assert (bed.bbox_m.width, bed.bbox_m.depth, bed.bbox_m.height) == (1.5, 2.05, 0.45)
    wardrobe = sizes.dimensions["vid-000003"]
    assert wardrobe.bbox_m == fallback(WARDROBE)  # 9 m wide was rejected
    assert sizes.warnings == ["sized from their category, could not be measured: wooden wardrobe"]


def test_no_answer_falls_back_for_every_item() -> None:
    def broken(prompt: str, images: Sequence[bytes]) -> str:
        raise TimeoutError

    for estimator, frames in (
        (FalSizeEstimator(ask=broken), _frames),
        (FalSizeEstimator(ask=lambda p, i: "sorry"), _frames),
        (FalSizeEstimator(ask=broken), None),
    ):
        sizes = estimator.estimate(BEDROOM, [TOY_BED], frames)
        assert sizes.dimensions["vid-000001"].bbox_m == fallback(TOY_BED)
        assert sizes.warnings
