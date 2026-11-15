"""Published demo assets (Dev 2.8, #20): a cache is exactly what was delivered, verified by
hash, installable into any data directory with no provider, and refused when broken. Offline:
catalog imports use the retailer double of `test_catalog`."""

from __future__ import annotations

import json
import shutil
import struct
from pathlib import Path

import numpy as np
import pytest
import trimesh
from test_catalog import URL, Web, page

from services.reconstruction.assets.asset_store import store_asset
from services.reconstruction.assets.catalog import catalog_scene, import_catalog_asset
from services.reconstruction.assets.delivery import inspect_asset
from services.reconstruction.assets.demo_cache import (
    MANIFEST,
    CacheError,
    DemoCache,
    cache_folder,
    install_demo_cache,
    main,
    publish_catalog_scene,
    publish_demo_cache,
    read_demo_cache,
)
from services.reconstruction.assets.segmentation import read_mask
from services.reconstruction.config import REPO_ROOT
from services.reconstruction.room.video_furniture import load_bindings

COMMITTED = REPO_ROOT / "services/reconstruction/assets/fixtures/demo_cache"
CHAIR = "https://shop.example/p/chair-9/"
SCENE = catalog_scene("room")


def import_two(data_dir: Path) -> None:
    """A desk with the retailer's model, and a chair with no model or width (a proxy)."""
    web = Web()
    web.pages[CHAIR] = page({"name": "Chair", "width": None}, model=False)
    import_catalog_asset(URL, "room", data_dir=data_dir, fetch=web)
    import_catalog_asset(CHAIR, "room", data_dir=data_dir, fetch=web)


@pytest.fixture()
def published(tmp_path: Path) -> tuple[Path, Path, DemoCache]:
    data_dir, cache_dir = tmp_path / "pipeline", tmp_path / "cache"
    import_two(data_dir)
    cache = publish_catalog_scene("room", data_dir=data_dir, cache_dir=cache_dir)
    return data_dir, cache_dir, cache


def test_a_cache_installs_into_a_fresh_data_directory(
    published: tuple[Path, Path, DemoCache], tmp_path: Path
) -> None:
    data_dir, cache_dir, cache = published
    assert cache.scene_id == SCENE and cache.source == "catalog"
    desk, chair = sorted(cache.assets, key=lambda a: a.name.startswith("Chair"))
    assert not desk.is_proxy and desk.dimension_source == "catalog"
    assert desk.product_url == URL and desk.source == "url_import"  # provenance kept
    assert chair.is_proxy and "dimensions" in chair.correction_needed  # a proxy stays a proxy

    fresh = tmp_path / "fresh"
    installed = install_demo_cache(SCENE, cache_dir=cache_dir, data_dir=fresh)
    assert installed == cache
    for asset in installed.assets:
        assert not inspect_asset(asset, data_dir=fresh).problems
        name = asset.glb_url.rsplit("/", 1)[1]
        assert (fresh / "assets" / name).read_bytes() == (data_dir / "assets" / name).read_bytes()
        for frame in asset.evidence.frames:
            if frame.mask_url is not None:  # evidence still resolves
                assert read_mask(fresh, frame.mask_url).any()
    assert install_demo_cache(SCENE, cache_dir=cache_dir, data_dir=fresh) == cache  # idempotent


def test_the_manifest_is_deterministic_and_a_republish_drops_stale_files(
    published: tuple[Path, Path, DemoCache],
) -> None:
    data_dir, cache_dir, cache = published
    folder = cache_folder(cache_dir, SCENE)
    first = (folder / MANIFEST).read_bytes()
    publish_catalog_scene("room", data_dir=data_dir, cache_dir=cache_dir)
    assert (folder / MANIFEST).read_bytes() == first

    desk = next(a for a in cache.assets if not a.is_proxy)
    smaller = publish_demo_cache(
        SCENE, [desk], data_dir=data_dir, cache_dir=cache_dir, source="catalog"
    )
    on_disk = sorted(str(p.relative_to(folder)) for p in folder.rglob("*") if p.is_file())
    assert on_disk == sorted([MANIFEST, *(f.path for f in smaller.files)])
    assert [p.name for p in cache_dir.iterdir()] == [folder.name]  # no staging left behind


def test_a_refused_publish_keeps_the_previous_cache(
    published: tuple[Path, Path, DemoCache],
) -> None:
    data_dir, cache_dir, cache = published
    desk = next(a for a in cache.assets if not a.is_proxy)
    wrong = desk.model_copy(update={"bbox_m": desk.bbox_m.model_copy(update={"width": 2.0})})
    lost = desk.model_copy(update={"glb_url": f"/api/reconstruction/assets/{'0' * 64}.glb"})
    for assets, reason in (
        ([wrong], "bounds differ"),
        ([lost], "does not name a file"),
        ([desk, desk], "repeats"),
        ([], "at least 1"),
    ):
        with pytest.raises(CacheError, match=reason):
            publish_demo_cache(
                SCENE, assets, data_dir=data_dir, cache_dir=cache_dir, source="catalog"
            )
    assert read_demo_cache(SCENE, cache_dir=cache_dir) == cache
    assert len(list(cache_dir.iterdir())) == 1


def test_a_missing_evidence_mask_refuses_the_publish(
    published: tuple[Path, Path, DemoCache],
) -> None:
    data_dir, cache_dir, cache = published
    mask = next(f.mask_url for a in cache.assets for f in a.evidence.frames if f.mask_url)
    (data_dir / mask).unlink()
    with pytest.raises(CacheError, match="missing"):
        publish_catalog_scene("room", data_dir=data_dir, cache_dir=cache_dir)


def _manifest(cache_dir: Path) -> dict:
    return json.loads((cache_folder(cache_dir, SCENE) / MANIFEST).read_text())


def _rewrite(cache_dir: Path, manifest: dict) -> None:
    (cache_folder(cache_dir, SCENE) / MANIFEST).write_text(json.dumps(manifest))


def test_a_broken_cache_is_refused(published: tuple[Path, Path, DemoCache], tmp_path: Path) -> None:
    _, cache_dir, cache = published
    folder = cache_folder(cache_dir, SCENE)
    glb = folder / next(f.path for f in cache.files if f.path.endswith(".glb"))
    original = _manifest(cache_dir)

    good = glb.read_bytes()
    data = bytearray(good)
    data[-1] ^= 0xFF
    glb.write_bytes(bytes(data))
    with pytest.raises(CacheError, match="altered"):
        install_demo_cache(SCENE, cache_dir=cache_dir, data_dir=tmp_path / "x")
    glb.unlink()
    with pytest.raises(CacheError, match="missing from the cache"):
        read_demo_cache(SCENE, cache_dir=cache_dir)
    glb.write_bytes(good)

    for change, reason in (
        ({"files": [*original["files"], {**original["files"][0], "path": "../x.glb"}]}, "leaves"),
        ({"files": original["files"][1:]}, "does not list"),
        ({"scene_id": "catalog:other"}, "holds 'catalog:other'"),
        ({"format": 2}, "unreadable"),
    ):
        _rewrite(cache_dir, {**original, **change})
        with pytest.raises(CacheError, match=reason):
            read_demo_cache(SCENE, cache_dir=cache_dir)
    assert not (tmp_path / "x" / "assets").exists() or not any((tmp_path / "x/assets").iterdir())


def test_no_published_cache_is_none(tmp_path: Path) -> None:
    assert read_demo_cache("nothing", cache_dir=tmp_path) is None
    assert install_demo_cache("nothing", cache_dir=tmp_path, data_dir=tmp_path / "d") is None


def test_install_repairs_a_damaged_copy_in_the_data_directory(
    published: tuple[Path, Path, DemoCache], tmp_path: Path
) -> None:
    _, cache_dir, cache = published
    fresh = tmp_path / "fresh"
    install_demo_cache(SCENE, cache_dir=cache_dir, data_dir=fresh)
    glb = fresh / next(f.path for f in cache.files if f.path.endswith(".glb"))
    glb.write_bytes(b"glTF broken")
    install_demo_cache(SCENE, cache_dir=cache_dir, data_dir=fresh)
    cached = cache_folder(cache_dir, SCENE) / glb.relative_to(fresh)
    assert glb.read_bytes() == cached.read_bytes()


def test_scene_ids_that_read_alike_get_their_own_folders(tmp_path: Path) -> None:
    folders = {cache_folder(tmp_path, s) for s in ("catalog:demo", "catalog-demo", "Catalog:Demo")}
    assert len(folders) == 3


# --- The committed cache ----------------------------------------------------------------------


def test_the_committed_cache_holds_the_bound_videos_four_meshes(tmp_path: Path) -> None:
    """What a fresh checkout shows in the real-input room: the four normalised SAM 3D meshes of
    the reviewed opening room, every size still an estimate asking for a correction."""
    (binding,) = load_bindings().values()
    cache = install_demo_cache(binding.furniture_scene_id, cache_dir=COMMITTED, data_dir=tmp_path)
    assert cache is not None and cache.source == "video"
    assert sorted(a.id for a in cache.assets) == sorted(h.asset_id for h in binding.hints)
    for asset in cache.assets:
        assert not asset.is_proxy and asset.source == "extracted_video"
        assert asset.dimension_source == "estimated" and asset.correction_needed == ["dimensions"]
        check = inspect_asset(asset, data_dir=tmp_path)
        assert not check.problems and check.bounds_error_m is not None
        assert check.bounds_error_m < 1e-6
    assert sum(f.size_bytes for f in cache.files) < 6_000_000
    assert not any("http" in f.path for f in cache.files)


# --- Declared bounds: what the editor fits --------------------------------------------------


def _with_declared(glb: bytes, low: list[float], high: list[float]) -> bytes:
    """The same file with every POSITION accessor declaring other min/max."""
    length = struct.unpack("<I", glb[12:16])[0]
    document = json.loads(glb[20 : 20 + length])
    for mesh in document["meshes"]:
        for primitive in mesh["primitives"]:
            accessor = document["accessors"][primitive["attributes"]["POSITION"]]
            accessor["min"], accessor["max"] = low, high
    chunk = json.dumps(document).encode()
    chunk += b" " * (-len(chunk) % 4)
    rest = glb[20 + length :]
    body = struct.pack("<II", len(chunk), 0x4E4F534A) + chunk + rest
    return b"glTF" + struct.pack("<II", 2, 12 + len(body)) + body


def test_declared_bounds_that_disagree_with_the_vertices_are_reported(
    published: tuple[Path, Path, DemoCache],
) -> None:
    """three.js fits a mesh from the accessor min/max; if they lie, the editor mis-sizes it
    even though the vertices are right."""
    data_dir, _, cache = published
    desk = next(a for a in cache.assets if not a.is_proxy)
    box = desk.bbox_m
    mesh = trimesh.creation.box(extents=[box.width, box.height, box.depth])
    mesh.apply_translation([0, box.height / 2, 0])
    honest = mesh.export(file_type="glb")
    assert isinstance(honest, bytes)
    low = [-box.width / 2, 0.0, -box.depth / 2]
    high = [box.width / 2, box.height, box.depth / 2]
    for glb, fault in (
        (_with_declared(honest, low, high), None),
        (_with_declared(honest, low, [h * 2 for h in high]), "declared bounds"),
    ):
        asset = desk.model_copy(update={"glb_url": store_asset(data_dir, glb)})
        problems = inspect_asset(asset, data_dir=data_dir).problems
        assert problems == [] if fault is None else any(fault in p for p in problems), problems
    assert np.isclose(box.height, high[1])


# --- CLI ------------------------------------------------------------------------------------


def test_cli_publishes_and_verifies(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    data_dir, cache_dir = tmp_path / "pipeline", tmp_path / "cache"
    args = ["--scene-id", "room", "--catalog", "--cache-dir", str(cache_dir)]
    assert main(["verify", *args]) == 2  # nothing published yet
    import_two(data_dir)
    assert main(["publish", *args, "--data-dir", str(data_dir), "--min-items", "3"]) == 2
    assert main(["publish", *args, "--data-dir", str(data_dir)]) == 0
    capsys.readouterr()
    assert main(["verify", *args]) == 0
    assert json.loads(capsys.readouterr().out)["items"] == 2
    glb = next(cache_folder(cache_dir, SCENE).rglob("*.glb"))
    glb.write_bytes(b"glTF broken")
    assert main(["verify", *args]) == 2
    single = tmp_path / "single"
    import_catalog_asset(URL, "one", data_dir=single, fetch=Web())
    one = ["--scene-id", "one", "--catalog", "--cache-dir", str(cache_dir)]
    assert main(["publish", *one, "--data-dir", str(single)]) == 0  # one product is enough
    unknown = ["--scene-id", "unknown", "--cache-dir", str(cache_dir), "--data-dir", str(data_dir)]
    assert main(["publish", *unknown]) == 1  # no such video scene in the registry
    shutil.rmtree(cache_dir)
