"""The one fixture scene: Dev 2's fixture assets placed in the mock room (issues #5 and #13)."""

import itertools
import json
import math
from pathlib import Path
from typing import Any

import pytest

from contracts.schema import (
    GLB_BBOX_TOLERANCE_M,
    MIN_HEIGHT_OVERLAP_M,
    MIN_PLAN_OVERLAP_M2,
    CollisionPart,
    FurnitureItem,
    RoomScene,
)
from services.reconstruction.assets.models import AssetEvidence, FurnitureAsset

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
    seat_top = min(p.y_max for p in chair.collision_parts if p.y_min == 0)
    desktop_underside = max(p.y_min for p in desk.collision_parts)
    assert seat_top < desktop_underside


def _plan_parts(it: FurnitureItem) -> list[tuple[Any, float, float]]:
    """Each collision part as (rotated plan polygon, y_min, y_max) in room coordinates."""
    from shapely.geometry import Polygon

    b = it.bbox_m
    parts = it.collision_parts or [
        CollisionPart(x=0, z=0, width=b.width, depth=b.depth, y_min=0, y_max=b.height)
    ]
    yaw = math.radians(it.pose.yaw_deg)
    c, s = math.cos(yaw), math.sin(yaw)
    out = []
    for p in parts:
        corners = []
        for dx, dz in [(-1, -1), (1, -1), (1, 1), (-1, 1)]:
            lx, lz = p.x + dx * p.width / 2, p.z + dz * p.depth / 2
            # Three.js rotation.y: x' = x cos + z sin, z' = -x sin + z cos.
            corners.append((it.pose.x + lx * c + lz * s, it.pose.z - lx * s + lz * c))
        out.append((Polygon(corners), p.y_min, p.y_max))
    return out


def test_fixture_scene_has_no_collisions() -> None:
    """The module-doc collision rule: touching is allowed, overlapping is not."""
    pytest.importorskip("shapely")
    parts = {it.id: _plan_parts(it) for it in SCENE.furniture}
    for a, b in itertools.combinations(parts, 2):
        for (pa, lo_a, hi_a), (pb, lo_b, hi_b) in itertools.product(parts[a], parts[b]):
            plan = pa.intersection(pb).area
            height = min(hi_a, hi_b) - max(lo_a, lo_b)
            assert not (plan > MIN_PLAN_OVERLAP_M2 and height > MIN_HEIGHT_OVERLAP_M), (a, b)


def test_front_clearances_stay_inside_the_room() -> None:
    xs = [p.x for p in SCENE.floor_polygon]
    zs = [p.z for p in SCENE.floor_polygon]
    for it in SCENE.furniture:
        yaw = math.radians(it.pose.yaw_deg)
        reach = it.bbox_m.depth / 2 + it.requires_front_clear_m
        fx, fz = it.pose.x + reach * math.sin(yaw), it.pose.z + reach * math.cos(yaw)
        assert min(xs) - 1e-9 <= fx <= max(xs) + 1e-9, it.id
        assert min(zs) - 1e-9 <= fz <= max(zs) + 1e-9, it.id


def test_evidence_matches_the_agreed_shape() -> None:
    assert set(EVIDENCE) == FIXTURE_IDS
    for record in EVIDENCE.values():
        evidence = AssetEvidence.model_validate(record)
        assert evidence.frames[0].mask_url is None  # fixtures have no source video


def test_dev1_consumes_fixtures_through_the_asset_interface() -> None:
    for fid in FIXTURE_IDS:
        item = BY_ID[fid]
        asset = FurnitureAsset.model_validate(
            {**item.model_dump(exclude={"pose"}), "evidence": EVIDENCE[fid]}
        )
        assert asset.to_item(item.pose) == item


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
