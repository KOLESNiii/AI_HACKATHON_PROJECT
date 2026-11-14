from __future__ import annotations

import io
import re
from pathlib import Path
from unittest.mock import Mock

import fal_client
import numpy as np
import pytest
import trimesh
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError
from test_segmentation import BLUE, RED, FakeProvider, loose_box, make_scene, record

from contracts.schema import GLB_BBOX_TOLERANCE_M, GLB_URL_PATTERN, BBoxM
from services.reconstruction.assets import mesh_providers
from services.reconstruction.assets.asset_store import asset_router, store_asset
from services.reconstruction.assets.mesh_providers import FalSam3dProvider, MeshError, RawMesh
from services.reconstruction.assets.models import AssetEvidence, EvidenceFrame, FurnitureAsset
from services.reconstruction.assets.providers import RequestBudget
from services.reconstruction.assets.proxies import (
    CATEGORY_SIZE_M,
    KnownDimensions,
    proxy_asset,
    proxy_glb,
)
from services.reconstruction.assets.reconstruct_items import main
from services.reconstruction.assets.reconstruction import (
    choose_view,
    inspect_mesh,
    reconstruct_furniture,
)
from services.reconstruction.assets.registry import Registry
from services.reconstruction.assets.segmentation import read_mask, segment_furniture
from services.reconstruction.assets.selection_models import (
    ItemReconstruction,
    MeshFailure,
    MeshRecord,
    SelectedObject,
    Sighting,
)
from services.reconstruction.assets.video import read_image

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


def test_an_item_needs_a_mesh_or_failure_and_can_keep_a_failed_replacement(tmp_path: Path) -> None:
    proxy = proxy_asset("vid-000001", "Sofa", "sofa", EVIDENCE, data_dir=tmp_path)
    failure = MeshFailure(kind="timeout", reason="deadline exceeded")
    mesh = mesh_record("f:0:0")
    ItemReconstruction(object_id="vid-000001", mesh=mesh, failure=None, proxy=proxy)
    ItemReconstruction(object_id="vid-000001", mesh=None, failure=failure, proxy=proxy)
    ItemReconstruction(object_id="vid-000001", mesh=mesh, failure=failure, proxy=proxy)
    with pytest.raises(ValidationError, match="without a mesh"):
        ItemReconstruction(object_id="vid-000001", proxy=proxy, mesh=None, failure=None)


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


class MeshDouble:
    name = "sam3d"

    def __init__(self, error=None, glb=None):
        self.calls = []
        self.error = error
        self.glb = glb or proxy_glb(BBoxM(width=1, height=0.5, depth=0.6))

    def reconstruct(self, frame, image, mask, registry, *, budget=None):
        self.calls.append(frame.key)
        if self.error:
            raise self.error
        return RawMesh(self.glb, {"scale": [[0.7, 0.7, 0.7]]})


def masked_scene(tmp_path, *, two=True):
    frame = make_scene(tmp_path, {"vid-000001": RED, **({"vid-000002": BLUE} if two else {})})
    segment_furniture("scene", data_dir=tmp_path, provider=FakeProvider())
    return frame


def test_pipeline_stores_separate_meshes_reuses_and_preserves_pose(tmp_path):
    masked_scene(tmp_path)
    provider = MeshDouble()
    result = reconstruct_furniture("scene", data_dir=tmp_path, provider=provider)
    assert result.complete and len(provider.calls) == 2
    assert len({i.mesh.mesh_path for i in result.items}) == 2
    for item in result.items:
        assert (tmp_path / item.mesh.mesh_path).read_bytes() == provider.glb
        assert item.proxy.evidence.frames[0].provider_pose == item.mesh.pose
    again = reconstruct_furniture("scene", data_dir=tmp_path, provider=provider)
    assert again.complete and len(provider.calls) == 2
    reconstruct_furniture("scene", data_dir=tmp_path, provider=provider, replace=True)
    assert len(provider.calls) == 4
    mesh = result.items[0].mesh
    (tmp_path / mesh.mesh_path).unlink()
    reconstruct_furniture("scene", data_dir=tmp_path, provider=provider)
    assert len(provider.calls) == 5


@pytest.mark.parametrize("kind", ["budget", "timeout", "provider", "invalid_mesh"])
def test_failures_are_explicit_with_dimensioned_proxies_and_keep_old_mesh(tmp_path, kind):
    masked_scene(tmp_path, two=False)
    known = KnownDimensions(bbox_m=BBoxM(width=2, height=1, depth=1), source="measured")
    provider = MeshDouble(error=MeshError("safe diagnostic", kind=kind))
    failed = reconstruct_furniture(
        "scene", data_dir=tmp_path, provider=provider, dimensions={"vid-000001": known}
    )
    item = failed.items[0]
    assert not failed.complete and item.failure.kind == kind and item.mesh is None
    assert item.proxy.name == "vid-000001" and item.proxy.bbox_m == known.bbox_m
    assert item.proxy.dimension_source == "measured"
    good = reconstruct_furniture("scene", data_dir=tmp_path, provider=MeshDouble())
    replacement = reconstruct_furniture("scene", data_dir=tmp_path, provider=provider, replace=True)
    assert not replacement.complete and replacement.items[0].mesh == good.items[0].mesh
    assert replacement.items[0].failure.kind == kind
    assert (tmp_path / good.items[0].mesh.mesh_path).is_file()


@pytest.mark.parametrize(
    "glb", [b"bad", b"glTF" + bytes(30), trimesh.exchange.gltf.export_glb(trimesh.Scene())]
)
def test_invalid_meshes_fall_back(tmp_path, glb):
    masked_scene(tmp_path, two=False)
    result = reconstruct_furniture("scene", data_dir=tmp_path, provider=MeshDouble(glb=glb))
    assert result.items[0].failure.kind == "invalid_mesh" and result.items[0].mesh is None


def test_unexpected_failure_does_not_drop_other_items(tmp_path):
    masked_scene(tmp_path)
    provider = MeshDouble()
    original = provider.reconstruct

    def reply(frame, image, mask, registry, *, budget=None):
        if np.where(mask)[1].mean() < 120:
            raise RuntimeError("private provider response")
        return original(frame, image, mask, registry, budget=budget)

    provider.reconstruct = reply
    result = reconstruct_furniture("scene", data_dir=tmp_path, provider=provider)
    assert len(result.items) == 2 and not result.complete
    assert result.items[0].failure.kind == "provider"
    assert "private" not in result.items[0].failure.reason
    assert result.items[1].mesh is not None


def test_missing_provider_mask_and_unknown_inputs(tmp_path):
    masked_scene(tmp_path, two=False)
    assert (
        reconstruct_furniture("scene", data_dir=tmp_path).items[0].failure.kind == "not_attempted"
    )
    with pytest.raises(ValueError):
        reconstruct_furniture("other", data_dir=tmp_path)
    with pytest.raises(ValueError):
        reconstruct_furniture("scene", data_dir=tmp_path, object_ids=["vid-999999"])
    with pytest.raises(ValueError):
        reconstruct_furniture("scene", data_dir=tmp_path, max_requests=-1)
    for path in (tmp_path / "masks").rglob("*.png"):
        path.unlink()
    assert reconstruct_furniture("scene", data_dir=tmp_path).items[0].failure.kind == "no_view"


def test_changed_mask_invalidates_mesh_and_racing_mask_is_not_attached(tmp_path):
    frame = masked_scene(tmp_path, two=False)
    first = reconstruct_furniture("scene", data_dir=tmp_path, provider=MeshDouble())

    def change(state):
        mask = state.objects["vid-000001"].masks[0]
        target = mask.mask_path + ".new.png"
        (tmp_path / target).write_bytes((tmp_path / mask.mask_path).read_bytes())
        mask.mask_path = target

    Registry(tmp_path).update("scene", change)
    provider = MeshDouble()
    second = reconstruct_furniture("scene", data_dir=tmp_path, provider=provider)
    assert (
        len(provider.calls) == 1 and second.items[0].mesh.mask_path != first.items[0].mesh.mask_path
    )
    original = provider.reconstruct

    def racing(*args, **kwargs):
        raw = original(*args, **kwargs)
        Registry(tmp_path).update("scene", change)
        return raw

    provider.reconstruct = racing
    result = reconstruct_furniture("scene", data_dir=tmp_path, provider=provider, replace=True)
    assert result.items[0].mesh is None and result.items[0].failure.kind == "no_view"
    assert frame.key == second.items[0].mesh.frame_key


def test_view_choice_prefers_confident_whole_views(tmp_path):
    masked_scene(tmp_path, two=False)
    make_scene(tmp_path, {"vid-000001": RED}, index=1)
    segment_furniture("scene", data_dir=tmp_path, provider=FakeProvider())
    state = Registry(tmp_path).load("scene")
    obj = state.objects["vid-000001"]
    a, b = obj.masks
    a.bbox_px = (0, 0, 90, 90)
    a.area_px = 8000
    b.area_px = 4500
    assert choose_view(obj, state.frames, tmp_path) == b
    b.score = 0.2
    assert choose_view(obj, state.frames, tmp_path) == a
    Registry(tmp_path).update("scene", lambda s: s.objects.update({obj.id: obj}))
    result = reconstruct_furniture("scene", data_dir=tmp_path, provider=MeshDouble())
    assert any("frame edge" in w for w in result.warnings)


def sam_setup(tmp_path, monkeypatch, result=None, **kwargs):
    frame = masked_scene(tmp_path, two=False)
    state = Registry(tmp_path).load("scene")
    image = read_image(tmp_path, frame)
    mask = read_mask(tmp_path, state.objects["vid-000001"].masks[0].mask_path)
    client = Mock()
    handle = client.submit.return_value
    handle.request_id = "mesh-request"
    handle.status.return_value = fal_client.Completed(logs=[], metrics={})
    handle.get.return_value = (
        result
        if result is not None
        else {
            "model_glb": {"url": "https://v3.fal.media/model.glb"},
            "metadata": [{"scale": [[0.7, 0.7, 0.7]], "object_index": 0}],
        }
    )
    client.get_handle.return_value = handle
    client.upload.side_effect = ["https://upload/frame", "https://upload/mask"]
    monkeypatch.setattr(fal_client, "SyncClient", Mock(return_value=client))
    fetch = Mock(return_value=proxy_glb(BBoxM(width=1, height=1, depth=1)))
    provider = FalSam3dProvider(key="fake", fetch=fetch, **kwargs)
    return provider, client, fetch, (frame, image, mask, Registry(tmp_path, namespace="scene"))


def test_sam_uploads_and_recovers_cached_handle_without_spending(tmp_path, monkeypatch):
    provider, client, fetch, args = sam_setup(tmp_path, monkeypatch)
    budget = RequestBudget(1)
    raw = provider.reconstruct(*args, budget=budget)
    assert inspect_mesh(raw.glb)[0] > 0 and raw.pose["object_index"] == 0
    assert client.upload.call_count == 2
    for call in client.upload.call_args_list:
        assert call.args[0].startswith(b"\x89PNG") and call.args[1] == "image/png"
    sent = client.submit.call_args.kwargs["arguments"]
    assert sent["image_url"] == "https://upload/frame" and sent["mask_urls"] == [
        "https://upload/mask"
    ]
    assert provider.reconstruct(*args, budget=RequestBudget(0)) == raw
    assert client.submit.call_count == 1 and budget.used == 1
    assert fetch.call_count == 2


def test_sam_budget_is_retryable_and_timeout_retains_request(tmp_path, monkeypatch):
    provider, client, _, args = sam_setup(tmp_path, monkeypatch, timeout_s=1)
    with pytest.raises(MeshError) as failure:
        provider.reconstruct(*args, budget=RequestBudget(0))
    assert failure.value.kind == "budget" and client.submit.call_count == 0
    client.submit.return_value.status.return_value = object()
    monkeypatch.setattr(mesh_providers.time, "monotonic", Mock(side_effect=[0, 2]))
    with pytest.raises(MeshError) as failure:
        provider.reconstruct(*args, budget=RequestBudget(1))
    assert failure.value.kind == "timeout"
    client.submit.return_value.status.return_value = fal_client.Completed(logs=[], metrics={})
    monkeypatch.setattr(mesh_providers.time, "monotonic", lambda: 0)
    assert provider.reconstruct(*args, budget=RequestBudget(0)).glb
    assert client.submit.call_count == 1


@pytest.mark.parametrize(
    "url", ["http://fal.media/a", "https://evil.test/a", "https://fal.media.evil.test/a"]
)
def test_sam_refuses_untrusted_artifacts(tmp_path, monkeypatch, url):
    provider, client, fetch, args = sam_setup(tmp_path, monkeypatch, {"model_glb": {"url": url}})
    with pytest.raises(MeshError, match="location not allowed"):
        provider.reconstruct(*args)
    fetch.assert_not_called()
    with pytest.raises(MeshError, match="previous request failed.*--refresh"):
        provider.reconstruct(*args, budget=RequestBudget(0))
    assert client.submit.call_count == 1
    client.get_handle.assert_not_called()


def test_sam_malformed_result_is_explicit(tmp_path, monkeypatch):
    provider, client, fetch, args = sam_setup(tmp_path, monkeypatch, {})
    with pytest.raises(MeshError) as failure:
        provider.reconstruct(*args)
    assert failure.value.kind == "invalid_mesh"
    fetch.assert_not_called()
    with pytest.raises(MeshError, match="previous request failed"):
        provider.reconstruct(*args)
    assert client.submit.call_count == 1


def test_cli_reports_valid_assets_and_exit_codes(tmp_path):
    import json

    masked_scene(tmp_path, two=False)
    out = tmp_path / "report"
    argv = ["--scene-id", "scene", "--data-dir", str(tmp_path), "--out", str(out)]
    assert main(argv) == 2
    assert "not_attempted" in (out / "report.md").read_text()
    assets = json.loads((out / "assets.json").read_text())
    assert len(assets) == 1 and FurnitureAsset.model_validate(assets[0]).is_proxy
    reconstruct_furniture("scene", data_dir=tmp_path, provider=MeshDouble())
    assert main(argv) == 0
    assert json.loads((out / "reconstruction.json").read_text())["complete"]
    assert main([*argv, "--scene-id", "unknown"]) == 1


def test_uncertain_submission_is_never_automatically_repeated(tmp_path, monkeypatch):
    provider, client, _, args = sam_setup(tmp_path, monkeypatch)
    client.submit.side_effect = RuntimeError("private failure")
    with pytest.raises(MeshError, match="request state retained"):
        provider.reconstruct(*args)
    with pytest.raises(MeshError, match="uncertain"):
        provider.reconstruct(*args)
    assert client.submit.call_count == 1


@pytest.mark.parametrize("invalid", ["oversized", "bad_header", "empty_geometry"])
def test_permanent_mesh_failure_is_not_downloaded_again(tmp_path, monkeypatch, invalid):
    provider, client, fetch, args = sam_setup(tmp_path, monkeypatch)
    if invalid == "oversized":
        fetch.side_effect = MeshError("mesh artifact too large", kind="invalid_mesh")
    elif invalid == "bad_header":
        fetch.return_value = b"invalid glb"
    else:
        fetch.return_value = trimesh.exchange.gltf.export_glb(trimesh.Scene())
    with pytest.raises(MeshError, match="--refresh") as failure:
        provider.reconstruct(*args)
    assert failure.value.kind == "invalid_mesh"
    with pytest.raises(MeshError, match="previous request failed.*--refresh"):
        provider.reconstruct(*args, budget=RequestBudget(0))
    assert client.submit.call_count == fetch.call_count == 1
    client.get_handle.assert_not_called()


def test_remote_failure_is_terminal_and_explicit_refresh_can_retry(tmp_path, monkeypatch):
    provider, client, fetch, args = sam_setup(tmp_path, monkeypatch)
    handle = client.submit.return_value
    handle.status.return_value = fal_client.Completed(
        logs=[], metrics={}, error="private provider details"
    )
    with pytest.raises(MeshError, match="remote reconstruction failed.*--refresh") as failure:
        provider.reconstruct(*args)
    assert "private" not in str(failure.value)
    with pytest.raises(MeshError, match="previous request failed.*--refresh"):
        provider.reconstruct(*args, budget=RequestBudget(0))
    handle.get.assert_not_called()
    fetch.assert_not_called()
    client.get_handle.assert_not_called()
    assert client.submit.call_count == 1
    provider.refresh = "operator-approved-retry"
    client.upload.side_effect = ["https://upload/frame", "https://upload/mask"]
    handle.status.return_value = fal_client.Completed(logs=[], metrics={})
    budget = RequestBudget(1)
    assert provider.reconstruct(*args, budget=budget).glb
    assert client.submit.call_count == 2 and budget.used == 1


def test_transient_mesh_download_failure_recovers_without_new_submission(tmp_path, monkeypatch):
    provider, client, fetch, args = sam_setup(tmp_path, monkeypatch)
    fetch.side_effect = RuntimeError("private HTTP failure")
    with pytest.raises(MeshError, match="request state retained"):
        provider.reconstruct(*args)
    fetch.side_effect = None
    assert provider.reconstruct(*args, budget=RequestBudget(0)).glb
    assert client.submit.call_count == 1 and fetch.call_count == 2


def test_shared_budget_allows_only_one_concurrent_submission():
    from concurrent.futures import ThreadPoolExecutor

    from services.reconstruction.assets.providers import DiscoveryError

    budget = RequestBudget(1)

    def claim(_):
        try:
            budget.claim()
            return True
        except DiscoveryError:
            return False

    with ThreadPoolExecutor(max_workers=8) as pool:
        assert sum(pool.map(claim, range(32))) == 1
    assert budget.used == 1


def test_pipeline_runs_items_concurrently(tmp_path):
    import threading

    masked_scene(tmp_path)
    provider = MeshDouble()
    original = provider.reconstruct
    barrier = threading.Barrier(2, timeout=5)

    def reply(*args, **kwargs):
        barrier.wait()
        return original(*args, **kwargs)

    provider.reconstruct = reply
    assert reconstruct_furniture("scene", data_dir=tmp_path, provider=provider).complete


def test_cli_accepts_known_dimensions(tmp_path):
    import json

    masked_scene(tmp_path, two=False)
    dimensions = tmp_path / "dimensions.json"
    dimensions.write_text(
        json.dumps(
            {
                "vid-000001": {
                    "bbox_m": {"width": 1.2, "height": 0.7, "depth": 0.6},
                    "source": "measured",
                }
            }
        )
    )
    out = tmp_path / "report"
    assert (
        main(
            [
                "--scene-id",
                "scene",
                "--data-dir",
                str(tmp_path),
                "--out",
                str(out),
                "--dimensions",
                str(dimensions),
            ]
        )
        == 2
    )
    asset = FurnitureAsset.model_validate(json.loads((out / "assets.json").read_text())[0])
    assert asset.dimension_source == "measured" and asset.bbox_m.width == 1.2
