from __future__ import annotations

import io
import re
from pathlib import Path

import numpy as np
import pytest
import trimesh
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError
from test_segmentation import RED, loose_box, record

from contracts.schema import GLB_BBOX_TOLERANCE_M, GLB_URL_PATTERN, BBoxM
from services.reconstruction.assets.asset_store import asset_router, store_asset
from services.reconstruction.assets.models import AssetEvidence, EvidenceFrame
from services.reconstruction.assets.proxies import (
    CATEGORY_SIZE_M,
    KnownDimensions,
    proxy_asset,
    proxy_glb,
)
from services.reconstruction.assets.selection_models import (
    ItemReconstruction,
    MeshFailure,
    MeshRecord,
    SelectedObject,
    Sighting,
)

EVIDENCE = AssetEvidence(
    frames=[EvidenceFrame(frame_index=3, timestamp_s=0.1)], primary_frame_index=3
)


def mesh_record(frame_key: str, mask_path: str = "masks/m.png") -> MeshRecord:
    return MeshRecord(
        frame_key=frame_key,
        mask_path=mask_path,
        provider="sam3d",
        mesh_path="meshes/m.raw.glb",
        size_bytes=100,
        triangles=12,
        extents=(1.0, 0.5, 0.6),
        pose={"scale": [[0.7, 0.7, 0.7]]},
    )


def test_mesh_record_belongs_to_a_sighting_and_goes_stale_with_its_mask() -> None:
    box = loose_box(RED)
    base = {
        "id": "vid-000001",
        "name": "Sofa",
        "category": "sofa",
        "appearance": "brown",
        "sightings": [Sighting(frame_key="f:0:0", box=box)],
        "masks": [record("f:0:0", box)],
    }
    assert SelectedObject.model_validate(base).current_mesh() is None
    obj = SelectedObject.model_validate({**base, "mesh": mesh_record("f:0:0")})
    assert obj.current_mesh() == obj.mesh
    # The mesh was made from a mask that has since been replaced, or removed.
    stale = SelectedObject.model_validate({**base, "mesh": mesh_record("f:0:0", "masks/old.png")})
    assert stale.mesh is not None and stale.current_mesh() is None
    assert SelectedObject.model_validate({**base, "masks": [], "mesh": mesh_record("f:0:0")})
    assert obj.model_copy(update={"masks": []}).current_mesh() is None
    with pytest.raises(ValidationError, match="mesh"):
        SelectedObject.model_validate({**base, "mesh": mesh_record("f:0:9")})
    # Registry snapshots written before #16 have no mesh field.
    old = SelectedObject.model_validate(base).model_dump(exclude={"mesh"})
    assert SelectedObject.model_validate(old).mesh is None


def test_an_item_has_exactly_one_of_a_mesh_and_a_failure(tmp_path: Path) -> None:
    proxy = proxy_asset("vid-000001", "Sofa", "sofa", EVIDENCE, data_dir=tmp_path)
    failure = MeshFailure(kind="timeout", reason="deadline exceeded")
    mesh = mesh_record("f:0:0")
    ItemReconstruction(object_id="vid-000001", mesh=mesh, failure=None, proxy=proxy)
    ItemReconstruction(object_id="vid-000001", mesh=None, failure=failure, proxy=proxy)
    for both in ({"mesh": mesh, "failure": failure}, {"mesh": None, "failure": None}):
        with pytest.raises(ValidationError, match="either a mesh or a failure"):
            ItemReconstruction(object_id="vid-000001", proxy=proxy, **both)


def bounds(glb: bytes) -> np.ndarray:
    return np.asarray(trimesh.load_scene(io.BytesIO(glb), file_type="glb").bounds)


def test_proxy_box_matches_its_dimensions_with_bottom_centre_at_the_origin() -> None:
    bbox = BBoxM(width=1.2, height=0.75, depth=0.6)
    glb = proxy_glb(bbox)
    expected = [[-0.6, 0, -0.3], [0.6, 0.75, 0.3]]
    assert np.abs(bounds(glb) - expected).max() < GLB_BBOX_TOLERANCE_M
    assert glb == proxy_glb(bbox), "same box, same bytes: the URL is a content hash"
    # Thin items keep exact bounds too: the front marker shrinks with them.
    thin = BBoxM(width=0.6, height=0.04, depth=0.02)
    assert np.abs(bounds(proxy_glb(thin)) - [[-0.3, 0, -0.01], [0.3, 0.04, 0.01]]).max() < 1e-6


def test_proxy_with_unknown_size_is_an_estimate_that_asks_for_dimensions(tmp_path: Path) -> None:
    asset = proxy_asset("vid-000001", "Rear sofa", "sofa", EVIDENCE, data_dir=tmp_path)
    width, height, depth = CATEGORY_SIZE_M["sofa"]
    assert asset.is_proxy and asset.source == "extracted_video" and asset.evidence == EVIDENCE
    assert asset.bbox_m == BBoxM(width=width, height=height, depth=depth)
    assert asset.dimension_source == "estimated" and asset.correction_needed == ["dimensions"]
    assert asset.collision_parts == [] and not asset.is_fixed
    assert re.match(GLB_URL_PATTERN, asset.glb_url)
    stored = tmp_path / "assets" / asset.glb_url.rsplit("/", 1)[1]
    assert np.abs(bounds(stored.read_bytes())[1] - [width / 2, height, depth / 2]).max() < 1e-6
    # A fixture is part of the room; the shared contract requires it to be fixed.
    assert proxy_asset("vid-000002", "Radiator", "fixture", EVIDENCE, data_dir=tmp_path).is_fixed


def test_proxy_with_known_dimensions_keeps_their_provenance(tmp_path: Path) -> None:
    known = KnownDimensions(bbox_m=BBoxM(width=2.0, height=0.8, depth=0.9), source="measured")
    asset = proxy_asset("vid-000001", "Sofa", "sofa", EVIDENCE, data_dir=tmp_path, known=known)
    assert asset.is_proxy and asset.bbox_m == known.bbox_m
    assert asset.dimension_source == "measured" and asset.correction_needed == []
    for bad in (0.0, -1.0, float("nan"), float("inf")):
        with pytest.raises(ValidationError):
            KnownDimensions(bbox_m=BBoxM(width=bad, height=1, depth=1), source="measured")
    with pytest.raises(ValidationError):  # A guess is not a known dimension.
        KnownDimensions.model_validate(
            {"bbox_m": {"width": 1, "height": 1, "depth": 1}, "source": "estimated"}
        )


def test_asset_store_is_content_addressed_and_served_immutably(tmp_path: Path) -> None:
    glb = proxy_glb(BBoxM(width=1, height=1, depth=1))
    url = store_asset(tmp_path, glb)
    assert url == store_asset(tmp_path, glb) and re.match(GLB_URL_PATTERN, url)
    assert re.fullmatch(r"/api/reconstruction/assets/[a-f0-9]{64}\.glb", url)
    assert store_asset(tmp_path, glb, url_base="https://cdn.example/a/").startswith(
        "https://cdn.example/a/"
    )
    app = FastAPI()
    app.include_router(asset_router(tmp_path))
    client = TestClient(app)
    # In development Vite strips /api/reconstruction before the request reaches the service.
    response = client.get(url.removeprefix("/api/reconstruction"))
    assert response.status_code == 200 and response.content == glb
    assert response.headers["content-type"] == "model/gltf-binary"
    assert "immutable" in response.headers["cache-control"]
    (tmp_path / "assets" / "notes.glb").write_bytes(b"not an asset")
    (tmp_path / "registry.sqlite3").write_bytes(b"private")
    for name in (
        "notes.glb",
        "0" * 64 + ".glb",
        "..%2Fregistry.sqlite3",
        "%2e%2e/registry.sqlite3",
    ):
        assert client.get(f"/assets/{name}").status_code == 404
