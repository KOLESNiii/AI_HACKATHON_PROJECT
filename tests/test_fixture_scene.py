"""The one fixture scene: Dev 2's fixture assets placed in the mock room (issues #5 and #13)."""

import json
from pathlib import Path

import pytest

from contracts.schema import GLB_BBOX_TOLERANCE_M, RoomScene

ROOT = Path(__file__).resolve().parent.parent
SCENE_PATH = ROOT / "contracts/mock_room/mock_scene.json"
EVIDENCE_PATH = ROOT / "services/reconstruction/assets/fixtures/evidence.json"
SCENE = RoomScene.model_validate(json.loads(SCENE_PATH.read_text()))
BY_ID = {i.id: i for i in SCENE.furniture}
EVIDENCE = json.loads(EVIDENCE_PATH.read_text())
FIXTURE_IDS = {"vid-desk-01", "vid-chair-01", "vid-table-01", "fix-radiator-01"}


def test_scene_holds_the_fixture_items_and_the_two_originals() -> None:
    assert set(BY_ID) == FIXTURE_IDS | {"item_bed", "item_wardrobe"}


def test_fixture_items_carry_the_agreed_fields() -> None:
    for fid in FIXTURE_IDS:
        it = BY_ID[fid]
        assert it.is_proxy and it.dimension_source == "estimated"
        assert it.collision_source == "template" and it.correction_needed == []
        assert it.glb_url == f"/mock_room/{fid}.glb"
    assert [len(BY_ID[f].collision_parts) for f in sorted(FIXTURE_IDS)] == [0, 2, 3, 5]
    assert [BY_ID[f].is_fixed for f in sorted(FIXTURE_IDS)] == [True, False, False, False]


def test_chair_seat_clears_the_desktop() -> None:
    desk, chair = BY_ID["vid-desk-01"], BY_ID["vid-chair-01"]
    seat_top = max(p.y_max for p in chair.collision_parts if p.z > 0)
    desktop_underside = min(p.y_min for p in desk.collision_parts if p.width > 1)
    assert seat_top < desktop_underside


def test_evidence_matches_the_agreed_shape() -> None:
    assert set(EVIDENCE) == FIXTURE_IDS
    keys = {"frame_index", "timestamp_s", "image_size_px", "mask_url", "bbox_px", "provider_pose"}
    for record in EVIDENCE.values():
        assert set(record) == {"frames", "primary_frame_index"} and record["frames"]
        assert all(set(f) == keys for f in record["frames"])
        assert record["primary_frame_index"] in {f["frame_index"] for f in record["frames"]}
        assert record["frames"][0]["mask_url"] is None  # fixtures have no source video


def test_generated_meshes_match_bbox() -> None:
    trimesh = pytest.importorskip("trimesh")
    for it in SCENE.furniture:
        path = ROOT / "frontend/public" / it.glb_url.lstrip("/")
        if not path.exists():
            pytest.skip("run scripts/generate_mock_glbs.py first")
        lo, hi = trimesh.load(path, force="mesh").bounds
        b = it.bbox_m
        assert hi - lo == pytest.approx([b.width, b.height, b.depth], abs=GLB_BBOX_TOLERANCE_M)
        assert lo[1] == pytest.approx(0.0, abs=GLB_BBOX_TOLERANCE_M)
