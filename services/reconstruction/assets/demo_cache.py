"""Published demo assets that load with no provider, key or network (#20).

A demo cache is one folder per scene holding generations. A generation is a folder,
`g-<hex>`, named by the hash of its `manifest.json` (the delivered `FurnitureAsset`s and every
file they reference, each with its SHA-256) and holding those files, under the same paths they
have in the pipeline's data directory. The scene folder's `CURRENT` file names the published
generation. Installing a cache copies the files into a data directory, so each `glb_url` is
served by the existing asset route and each evidence `mask_url` resolves with
`segmentation.read_mask`, then runs the delivery checks again on the installed files. Nothing
is regenerated: a cache is exactly what was delivered.

Publishing takes a scene that already passed delivery (`deliver_furniture` for video
furniture, `imported_assets` for catalog imports). It writes a complete new generation, then
switches `CURRENT` to it with one atomic replace, so a reader sees the old cache or the new
one, and a refused or interrupted publish leaves the previous cache published. A generation is
never changed once written; a reader resolves `CURRENT` once and reads only that generation.
The generation just replaced is kept, so a reader that resolved it before the switch can
finish; older ones are removed. Run one publisher at a time per cache directory.

CLI, offline:

    python -m services.reconstruction.assets.demo_cache publish --scene-id reviewed-opening-room
    python -m services.reconstruction.assets.demo_cache verify --scene-id reviewed-opening-room

Exit 0: published, or the cache verified; 2: refused (a check failed, too few items) or the
cache is missing or broken; 1: unusable input or storage.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sqlite3
import tempfile
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Literal

from pydantic import ValidationError

from .asset_store import ASSET_DIR, ASSET_URL_BASE, write_atomic
from .catalog import catalog_scene, imported_assets
from .delivery import deliver_furniture, inspect_asset
from .models import FurnitureAsset
from .proxies import KnownDimensions
from .reconstruct_items import load_dimensions
from .selection_models import Record

CACHE_FORMAT: Literal[1] = 1
MANIFEST = "manifest.json"
CURRENT = "CURRENT"
_GENERATION = re.compile(r"g-[a-f0-9]{16}")
_SLUG = re.compile(r"[^a-z0-9_-]+")
_SHA256 = re.compile(r"[a-f0-9]{64}")

Source = Literal["video", "catalog"]


class CacheError(ValueError):
    """A cache that cannot be published, or a published cache that is broken."""


class CachedFile(Record):
    path: str
    """Relative to the cache folder, and to the data directory it is installed into."""
    sha256: str
    size_bytes: int


class DemoCache(Record):
    format: Literal[1] = CACHE_FORMAT
    scene_id: str
    """The registry key: a video scene ID, or `catalog:<scene>` for catalog imports."""
    source: Source
    registry_revision: int | None = None
    """The pipeline registry revision the assets were delivered from, when known."""
    assets: list[FurnitureAsset]
    files: list[CachedFile]
    """Every mesh and evidence mask the assets reference, sorted by path."""


def cache_folder(cache_dir: Path, scene_id: str) -> Path:
    """A scene's folder: readable, and distinct for scene IDs that read alike."""
    slug = _SLUG.sub("-", scene_id.lower()).strip("-")[:60] or "scene"
    return cache_dir / f"{slug}-{hashlib.sha256(scene_id.encode()).hexdigest()[:8]}"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _inside(root: Path, relative: str) -> Path:
    """`root / relative`, refusing anything that leaves `root`."""
    if not relative or Path(relative).is_absolute():
        raise CacheError(f"cache path {relative!r} is not relative")
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise CacheError(f"cache path {relative!r} leaves its folder")
    return path


def referenced_files(asset: FurnitureAsset, *, url_base: str = ASSET_URL_BASE) -> list[str]:
    """Data-directory paths of an asset's mesh and evidence masks; `url_base` is the asset
    store's URL prefix the cache was published with."""
    prefix, _, name = asset.glb_url.rpartition("/")
    if prefix != url_base.rstrip("/"):
        raise CacheError(f"{asset.id}: glb_url is not under {url_base!r}")
    paths = [f"{ASSET_DIR}/{name}"]
    paths += [f.mask_url for f in asset.evidence.frames if f.mask_url is not None]
    return paths


def publish_demo_cache(
    scene_id: str,
    assets: Sequence[FurnitureAsset],
    *,
    data_dir: Path,
    cache_dir: Path,
    source: Source,
    registry_revision: int | None = None,
    min_items: int = 1,
    url_base: str = ASSET_URL_BASE,
) -> DemoCache:
    """Publish delivered assets and their files as the scene's cache, replacing any earlier one.

    Refuses (CacheError, the earlier cache untouched) when there are fewer than `min_items`,
    an ID repeats, an asset fails `inspect_asset`, or a referenced file is missing.
    """
    if len(assets) < min_items:
        raise CacheError(f"{len(assets)} assets; at least {min_items} required")
    ids = [asset.id for asset in assets]
    if len(set(ids)) != len(ids):
        raise CacheError("an item ID repeats")
    faults = []
    for asset in assets:
        check = inspect_asset(asset, data_dir=data_dir, url_base=url_base)
        faults += [f"{asset.id}: {problem}" for problem in check.problems]
    if faults:
        raise CacheError("; ".join(faults))
    paths = sorted(
        {path for asset in assets for path in referenced_files(asset, url_base=url_base)}
    )
    sources = {path: _inside(data_dir, path) for path in paths}
    if missing := [path for path, file in sources.items() if not file.is_file()]:
        raise CacheError(f"referenced files are missing: {', '.join(missing)}")

    folder = cache_folder(cache_dir, scene_id)
    folder.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(dir=folder, prefix=".staging-"))
    try:
        files = []
        for path, file in sources.items():
            target = staging / path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(file, target)
            files.append(
                CachedFile(path=path, sha256=_sha256(target), size_bytes=target.stat().st_size)
            )
        cache = DemoCache(
            scene_id=scene_id,
            source=source,
            registry_revision=registry_revision,
            assets=list(assets),
            files=files,
        )
        manifest = (cache.model_dump_json(indent=2) + "\n").encode()
        (staging / MANIFEST).write_bytes(manifest)
        generation = folder / f"g-{hashlib.sha256(manifest).hexdigest()[:16]}"
        if _intact(generation, cache):
            shutil.rmtree(staging)  # Exactly this content is already a generation.
        else:
            shutil.rmtree(generation, ignore_errors=True)  # A damaged copy, never served.
            staging.rename(generation)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    try:
        previous = current_generation(cache_dir, scene_id)
    except CacheError:
        previous = None
    write_atomic(folder / CURRENT, f"{generation.name}\n".encode())  # The switch.
    keep = {generation.name} | ({previous.name} if previous is not None else set())
    for entry in folder.iterdir():
        if _GENERATION.fullmatch(entry.name) and entry.name not in keep:
            shutil.rmtree(entry, ignore_errors=True)
    return cache


def _intact(generation: Path, cache: DemoCache) -> bool:
    try:
        return all(_sha256(generation / f.path) == f.sha256 for f in cache.files)
    except OSError:
        return False


def publish_video_scene(
    scene_id: str,
    *,
    data_dir: Path,
    cache_dir: Path,
    dimensions: Mapping[str, KnownDimensions] | None = None,
    object_ids: Sequence[str] | None = None,
    min_items: int = 2,
) -> DemoCache:
    """Publish a video scene's delivery (#18). The delivery must pass every check; a delivered
    proxy is allowed and stays a proxy."""
    delivery = deliver_furniture(
        scene_id, data_dir=data_dir, dimensions=dimensions, object_ids=object_ids
    )
    if not delivery.ok:
        failed = [c.object_id for c in delivery.checks if c.problems] or delivery.problems
        raise CacheError(f"delivery failed its checks: {', '.join(failed)}")
    return publish_demo_cache(
        scene_id,
        delivery.assets,
        data_dir=data_dir,
        cache_dir=cache_dir,
        source="video",
        registry_revision=delivery.registry_revision,
        min_items=min_items,
    )


def publish_catalog_scene(
    scene_id: str, *, data_dir: Path, cache_dir: Path, min_items: int = 1
) -> DemoCache:
    """Publish every product imported into `scene_id` (#19), with its retailer provenance
    (`product_url`, `source`, `price_gbp`, name). Cached under `catalog:<scene_id>`."""
    imports = imported_assets(scene_id, data_dir=data_dir)
    if failed := [record.asset.id for record in imports if not record.ok]:
        raise CacheError(f"imports failed their checks: {', '.join(failed)}")
    return publish_demo_cache(
        catalog_scene(scene_id),
        [record.asset for record in imports],
        data_dir=data_dir,
        cache_dir=cache_dir,
        source="catalog",
        min_items=min_items,
    )


def current_generation(cache_dir: Path, scene_id: str) -> Path | None:
    """The folder of the scene's published generation; None when none is published."""
    folder = cache_folder(cache_dir, scene_id)
    try:
        name = (folder / CURRENT).read_text().strip()
    except FileNotFoundError:
        return None
    if not _GENERATION.fullmatch(name):
        raise CacheError(f"{CURRENT} names {name[:40]!r}, not a generation")
    return folder / name


def read_demo_cache(
    scene_id: str, *, cache_dir: Path, url_base: str = ASSET_URL_BASE
) -> DemoCache | None:
    """The scene's published cache, its files verified; None when none is published.

    Raises CacheError for a bad `CURRENT`, an unreadable manifest, one for another scene, an
    asset outside `url_base`, a path outside the folder, or a missing or altered file.
    """
    read = _read(scene_id, cache_dir, url_base)
    return None if read is None else read[0]


def _read(scene_id: str, cache_dir: Path, url_base: str) -> tuple[DemoCache, Path] | None:
    """The verified cache and the generation it was read from, resolved once."""
    generation = current_generation(cache_dir, scene_id)
    if generation is None:
        return None
    try:
        raw = (generation / MANIFEST).read_bytes()
    except FileNotFoundError as exc:
        raise CacheError(f"the published generation {generation.name} is missing") from exc
    try:
        cache = DemoCache.model_validate_json(raw)
    except ValidationError as exc:
        raise CacheError(f"unreadable cache manifest ({exc.error_count()} errors)") from exc
    if cache.scene_id != scene_id:
        raise CacheError(f"the cache folder holds {cache.scene_id!r}, not {scene_id!r}")
    listed = {file.path for file in cache.files}
    referenced = {p for a in cache.assets for p in referenced_files(a, url_base=url_base)}
    if missing := sorted(referenced - listed):
        raise CacheError(f"the manifest does not list {', '.join(missing)}")
    for file in cache.files:
        path = _inside(generation, file.path)
        if not _SHA256.fullmatch(file.sha256):
            raise CacheError(f"{file.path}: not a SHA-256 digest")
        if not path.is_file():
            raise CacheError(f"{file.path}: missing from the cache")
        if _sha256(path) != file.sha256:
            raise CacheError(f"{file.path}: altered since it was published")
    return cache, generation


def install_demo_cache(
    scene_id: str, *, cache_dir: Path, data_dir: Path, url_base: str = ASSET_URL_BASE
) -> DemoCache | None:
    """Copy a scene's cache into `data_dir` and check the installed assets again.

    Returns None when no cache is published. A file already in `data_dir` with the same
    digest is kept; a different one is replaced (paths are content-named, so that only repairs
    a damaged file). Every file comes from the one generation that was read, even if another
    is published meanwhile. `url_base` must be the one the cache was published with. Raises
    CacheError when the cache is broken or an installed asset fails `inspect_asset`; OSError
    when `data_dir` cannot be written.
    """
    read = _read(scene_id, cache_dir, url_base)
    if read is None:
        return None
    cache, generation = read
    for file in cache.files:
        target = _inside(data_dir, file.path)
        if not target.is_file() or _sha256(target) != file.sha256:
            data = (generation / file.path).read_bytes()
            if hashlib.sha256(data).hexdigest() != file.sha256:
                raise CacheError(f"{file.path}: altered since it was published")
            write_atomic(target, data)
    faults = []
    for asset in cache.assets:
        check = inspect_asset(asset, data_dir=data_dir, url_base=url_base)
        faults += [f"{asset.id}: {problem}" for problem in check.problems]
    if faults:
        raise CacheError("; ".join(faults))
    return cache


def summary(cache: DemoCache) -> dict[str, object]:
    return {
        "scene_id": cache.scene_id,
        "source": cache.source,
        "items": len(cache.assets),
        "meshes": sum(not a.is_proxy for a in cache.assets),
        "proxies": sorted(a.id for a in cache.assets if a.is_proxy),
        "corrections": {a.id: a.correction_needed for a in cache.assets if a.correction_needed},
        "bytes": sum(f.size_bytes for f in cache.files),
    }


def main(argv: list[str] | None = None) -> int:
    from services.reconstruction.config import demo_cache_dir, furniture_data_dir

    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    publish = commands.add_parser("publish", help="publish a delivered scene as its cache")
    verify = commands.add_parser("verify", help="check a published cache, offline")
    for command in (publish, verify):
        command.add_argument("--scene-id", required=True)
        command.add_argument(
            "--catalog", action="store_true", help="the scene's catalog imports (#19)"
        )
        command.add_argument("--cache-dir", type=Path, default=demo_cache_dir())
    publish.add_argument("--data-dir", type=Path, default=furniture_data_dir())
    publish.add_argument("--object-id", action="append")
    publish.add_argument("--dimensions", type=Path, help="JSON object: item ID to {bbox_m, source}")
    publish.add_argument(
        "--min-items", type=int, help="fewest items to accept (default: 2 video, 1 catalog)"
    )
    verify.add_argument(
        "--data-dir", type=Path, help="install into this directory (default: a temporary one)"
    )
    args = parser.parse_args(argv)
    scene_id = catalog_scene(args.scene_id) if args.catalog else args.scene_id
    try:
        if args.command == "publish":
            if args.catalog:
                cache = publish_catalog_scene(
                    args.scene_id,
                    data_dir=args.data_dir,
                    cache_dir=args.cache_dir,
                    min_items=1 if args.min_items is None else args.min_items,
                )
            else:
                cache = publish_video_scene(
                    args.scene_id,
                    data_dir=args.data_dir,
                    cache_dir=args.cache_dir,
                    dimensions=load_dimensions(args.dimensions) if args.dimensions else None,
                    object_ids=args.object_id,
                    min_items=2 if args.min_items is None else args.min_items,
                )
            folder = current_generation(args.cache_dir, scene_id)
            print(json.dumps(summary(cache) | {"folder": str(folder)}))
            return 0
        with tempfile.TemporaryDirectory(prefix="demo-cache-verify-") as temporary:
            data_dir = args.data_dir or Path(temporary)
            installed = install_demo_cache(scene_id, cache_dir=args.cache_dir, data_dir=data_dir)
        if installed is None:
            print(json.dumps({"scene_id": scene_id, "ok": False, "error": "no cache published"}))
            return 2
        print(json.dumps(summary(installed) | {"ok": True}))
        return 0
    except CacheError as exc:
        print(json.dumps({"scene_id": scene_id, "ok": False, "error": str(exc)}))
        return 2
    except (ValueError, OSError, sqlite3.Error) as exc:
        print(f"Demo cache {args.command} failed ({type(exc).__name__}: {exc}).")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
