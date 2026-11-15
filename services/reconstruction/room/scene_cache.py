"""A published scene cache (#12): the demo room loads with no upload, key or network.

One JSON file per floor plan, `<plan_id>.json`, holds the parsed plan and the assembled scene
of each of its rooms that is bound to furniture (`fixtures/real_rooms.json`). The service
restores every published plan when it starts (`restore_published`), as if the plan had been
uploaded and its labels read. From there nothing is special: `GET /scenes/{scene_id}`
assembles the room through the usual path (pipeline furniture, else Dev 2's furniture cache,
#20), the shell is built from the room, and corrections work as for any uploaded plan.
Uploading the same image again returns the restored plan without a provider call, because a
plan ID is the hash of the image bytes.

The stored assembled scene is the published result. `verify` assembles the room again from
the stored plan and the furniture cache and reports any difference, so a checkout that
verifies serves exactly the published scene.

Publishing parses the images, assembles each bound room from the furniture cache alone (never
from local pipeline data), and refuses unless every bound item is placed where it fits, the
delivered assets are unchanged and the shell builds. The file is replaced atomically, so a
refused publish leaves the earlier cache as it was.

CLI, offline with `--annotations`:

    python -m services.reconstruction.room.scene_cache publish examples/three_floor.png \
        --annotations services/reconstruction/room/fixtures/three_floor.annotations.json
    python -m services.reconstruction.room.scene_cache verify --plan-id plan-83a12322e933

Exit 0: published, or the cache verified; 2: refused, or the cache is missing, broken or not
reproduced; 1: unusable input or storage.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import tempfile
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from contracts.schema import ParsedFloorPlan, RoomScene
from services.reconstruction.assets.asset_store import write_atomic
from services.reconstruction.assets.delivery import check_placed
from services.reconstruction.assets.demo_cache import CacheError, read_demo_cache

from . import routes
from .annotate import FalVisionAnnotator, FixedAnnotator, PlanAnnotations, PlanAnnotator
from .assemble import Assembly, assemble_scene
from .openings import conform_openings
from .parse import parse_floor_plan, plan_id_for
from .raster import UnreadableImage
from .shell import shell_glb
from .video_furniture import RealRoomFurniture, RoomVideo, default_bindings

CACHE_FORMAT: Literal[1] = 1
FROM_SCENE_CACHE = (
    "from the published scene cache: recorded room labels, no provider used "
    "(services/reconstruction/room/README.md, 'Demo scene cache')"
)
"""Added to a restored plan's warnings."""
COMPARE_TOLERANCE_M = 1e-3
"""Numbers closer than this are the same when a scene is compared with its published copy:
the spatial audit's position tolerance (1 mm; 0.001 degrees for a yaw)."""
MAX_REPORTED = 8
"""Differences named per scene; the rest are counted."""


class SceneCacheError(ValueError):
    """A scene cache that cannot be published, or a published one that is broken. Its message
    names cache-relative things only (IDs, fields), never a server path."""


class CachedScene(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scene: RoomScene
    """The room as `GET /scenes/{scene_id}` first returns it: furniture placed, revision 0."""
    warnings: list[str] = []
    """What that response's warning header lists."""


class SceneCache(BaseModel):
    model_config = ConfigDict(extra="forbid")

    format: Literal[1] = CACHE_FORMAT
    plan: ParsedFloorPlan
    """The plan as parsed, every room without furniture. Its ID hashes the image bytes."""
    scenes: list[CachedScene] = Field(min_length=1)
    """The assembled scene of every room of the plan that is bound to furniture."""


def cache_path(cache_dir: Path, plan_id: str) -> Path:
    return cache_dir / f"{plan_id}.json"


def _rooms(plan: ParsedFloorPlan) -> dict[str, RoomScene]:
    return {room.scene.scene_id: room.scene for floor in plan.floors for room in floor.rooms}


def _check(cache: SceneCache) -> None:
    """Refuse a cache whose parts do not belong together."""
    plan = cache.plan
    rooms: dict[str, RoomScene] = {}
    for floor in plan.floors:
        for room in floor.rooms:
            scene_id = room.scene.scene_id
            if scene_id != f"{plan.plan_id}-{room.room_id}":
                raise SceneCacheError(f"room {room.room_id} has the scene ID of another plan")
            if scene_id in rooms:
                raise SceneCacheError(f"{scene_id} is in the plan twice")
            if room.scene.furniture:
                raise SceneCacheError(f"{scene_id}: a plan room must have no furniture")
            rooms[scene_id] = room.scene
    seen: set[str] = set()
    for cached in cache.scenes:
        scene = cached.scene
        if scene.scene_id not in rooms:
            raise SceneCacheError(f"{scene.scene_id} is not a room of {plan.plan_id}")
        if scene.scene_id in seen:
            raise SceneCacheError(f"{scene.scene_id} is cached twice")
        seen.add(scene.scene_id)
        if scene.revision != 0:
            raise SceneCacheError(f"{scene.scene_id}: revision {scene.revision}, expected 0")
        conformed, _ = conform_openings(rooms[scene.scene_id])  # as assembly does
        changed = sorted(
            name
            for name in RoomScene.model_fields
            if name != "furniture" and getattr(scene, name) != getattr(conformed, name)
        )
        if changed:
            raise SceneCacheError(
                f"{scene.scene_id} is not its plan room: {', '.join(changed)} differ"
            )


def read_scene_cache(path: Path) -> SceneCache:
    """The cache in `path`, checked: contract-valid, named after its plan, and every cached
    scene is a room of that plan with that room's geometry. Raises `SceneCacheError` when it
    is not, `OSError` when the file cannot be read."""
    try:
        cache = SceneCache.model_validate_json(path.read_bytes())
    except ValidationError as exc:
        raise SceneCacheError(f"not a scene cache ({exc.error_count()} errors)") from exc
    if path.stem != cache.plan.plan_id:
        raise SceneCacheError(f"holds {cache.plan.plan_id}, which is not the file's name")
    _check(cache)
    return cache


def restore_published(cache_dir: Path) -> list[str]:
    """Serve every plan published in `cache_dir` (`routes.restore_plan`); a plan already
    served is left alone. Never raises: returns why each unusable file was skipped, naming the
    file only. A missing directory publishes nothing."""
    problems: list[str] = []
    try:
        paths = sorted(cache_dir.glob("*.json"))
    except OSError as exc:
        return [f"the scene cache directory cannot be read ({type(exc).__name__})"]
    for path in paths:
        try:
            cache = read_scene_cache(path)
        except SceneCacheError as exc:
            problems.append(f"{path.name}: {exc}")
            continue
        except Exception as exc:  # a bad file must not stop the service from starting
            # An OSError may name a server path: say only what kind of error it was.
            problems.append(f"{path.name}: {type(exc).__name__}")
            continue
        plan = cache.plan
        routes.restore_plan(
            plan.model_copy(update={"warnings": [*plan.warnings, FROM_SCENE_CACHE]})
        )
    return problems


# --- assembly and its checks ------------------------------------------------------------------


def _assemble(
    room: RoomScene, bindings: Mapping[str, RoomVideo], furniture_cache_dir: Path
) -> Assembly:
    """The room assembled from the published furniture cache alone: the data directory is a
    new empty one, so local pipeline data never reaches a published scene."""
    with tempfile.TemporaryDirectory(prefix="scene-cache-") as data_dir:
        source = RealRoomFurniture(bindings, Path(data_dir), furniture_cache_dir)
        return assemble_scene(room, source)


def _faults(assembly: Assembly, binding: RoomVideo, furniture_cache_dir: Path) -> list[str]:
    """Why an assembled room is not fit to publish; empty when it is."""
    faults: list[str] = []
    scene = assembly.scene
    if not assembly.complete:
        faults.append("the assembly is incomplete (" + "; ".join(assembly.warnings) + ")")
    placed = {item.id for item in scene.furniture}
    if missing := sorted(h.asset_id for h in binding.hints if h.asset_id not in placed):
        reason = "; ".join(assembly.warnings) or "no reason given"
        faults.append(f"not placed: {', '.join(missing)} ({reason})")
    faults += [
        f"{record.asset_id} fits nowhere in the room"
        for record in assembly.records.values()
        if not record.fits
    ]
    furniture_scene = binding.furniture_scene_id
    try:
        furniture = read_demo_cache(furniture_scene, cache_dir=furniture_cache_dir)
    except CacheError as exc:
        faults.append(f"the furniture cache of {furniture_scene!r} is broken: {exc}")
    else:
        if furniture is None:
            faults.append(f"no furniture cache is published for {furniture_scene!r}")
        else:
            faults += check_placed(scene, furniture.assets)
    try:
        shell_glb(scene)
    except ValueError as exc:
        faults.append(f"the shell cannot be built ({exc})")
    return faults


def differences(
    published: object, found: object, tolerance: float = COMPARE_TOLERANCE_M, path: str = ""
) -> list[str]:
    """Where two JSON-like values differ: the paths, such as `furniture[vid-000004].pose.x`.
    Numbers within `tolerance` are equal; list entries that carry an `id` are named by it."""
    here = path or "(root)"
    if isinstance(published, bool) or isinstance(found, bool):
        return [] if published is found else [here]
    if isinstance(published, int | float) and isinstance(found, int | float):
        return [] if abs(published - found) <= tolerance else [here]
    if isinstance(published, dict) and isinstance(found, dict):
        if published.keys() != found.keys():
            return [f"{here} (fields)"]
        prefix = f"{path}." if path else ""
        return [
            difference
            for key in published
            for difference in differences(published[key], found[key], tolerance, prefix + key)
        ]
    if isinstance(published, list) and isinstance(found, list):
        if len(published) != len(found):
            return [f"{here} ({len(published)} published, {len(found)} found)"]
        found_differences: list[str] = []
        for index, (a, b) in enumerate(zip(published, found, strict=True)):
            name = a["id"] if isinstance(a, dict) and isinstance(a.get("id"), str) else index
            found_differences += differences(a, b, tolerance, f"{path}[{name}]")
        return found_differences
    return [] if published == found else [here]


def _named(scene_id: str, found: Sequence[str]) -> list[str]:
    """At most `MAX_REPORTED` differences of one scene, the rest counted."""
    listed = [f"{scene_id}: differs at {where}" for where in found[:MAX_REPORTED]]
    if len(found) > MAX_REPORTED:
        listed.append(f"{scene_id}: and {len(found) - MAX_REPORTED} more differences")
    return listed


# --- publish and verify -----------------------------------------------------------------------


def publish_scene_cache(
    images: Sequence[tuple[bytes, str]],
    annotator: PlanAnnotator,
    *,
    cache_dir: Path,
    furniture_cache_dir: Path,
    bindings: Mapping[str, RoomVideo],
) -> SceneCache:
    """Parse `images` (bytes and content type) and publish the plan with the assembled scene
    of every bound room, replacing the plan's earlier cache.

    Refuses (`SceneCacheError`, the earlier cache untouched) when no room of the plan is
    bound to furniture, or a bound room fails a check (`_faults`). Raises
    `raster.UnreadableImage` for an image that cannot be read.
    """
    plan = parse_floor_plan(list(images), annotator)
    scenes: list[CachedScene] = []
    faults: list[str] = []
    for scene_id, room in _rooms(plan).items():
        binding = bindings.get(scene_id)
        if binding is None:
            continue
        assembly = _assemble(room, bindings, furniture_cache_dir)
        faults += [
            f"{scene_id}: {fault}" for fault in _faults(assembly, binding, furniture_cache_dir)
        ]
        scenes.append(CachedScene(scene=assembly.scene, warnings=assembly.warnings))
    if not scenes:
        raise SceneCacheError(
            f"no room of {plan.plan_id} is bound to furniture (room/fixtures/real_rooms.json)"
        )
    if faults:
        raise SceneCacheError("; ".join(faults))
    cache = SceneCache(plan=plan, scenes=scenes)
    _check(cache)
    data = (cache.model_dump_json(indent=2) + "\n").encode()
    write_atomic(cache_path(cache_dir, plan.plan_id), data)
    return cache


def verify_scene_cache(
    path: Path,
    *,
    furniture_cache_dir: Path,
    bindings: Mapping[str, RoomVideo],
    images: Sequence[tuple[bytes, str]] | None = None,
    annotator: PlanAnnotator | None = None,
) -> list[str]:
    """What stops this checkout from serving the published scenes; empty when nothing does.

    Offline. Each cached scene's room is assembled again from the cached plan and the
    furniture cache, checked like a publish, and compared with the published scene and
    warnings. With `images`, the plan is also parsed again (labels from `annotator`) and
    compared with the cached plan. Raises `SceneCacheError` for a broken cache.
    """
    cache = read_scene_cache(path)
    plan = cache.plan
    problems: list[str] = []
    if images is not None:
        if plan_id_for([data for data, _ in images]) != plan.plan_id:
            problems.append(f"the images are not those of {plan.plan_id}")
        else:
            parsed = parse_floor_plan(list(images), annotator or FalVisionAnnotator())
            found = differences(plan.model_dump(mode="json"), parsed.model_dump(mode="json"))
            problems += _named(plan.plan_id, found)
    rooms = _rooms(plan)
    for cached in cache.scenes:
        scene_id = cached.scene.scene_id
        binding = bindings.get(scene_id)
        if binding is None:
            problems.append(f"{scene_id}: no longer bound to furniture")
            continue
        assembly = _assemble(rooms[scene_id], bindings, furniture_cache_dir)
        faults = _faults(assembly, binding, furniture_cache_dir)
        problems += [f"{scene_id}: {fault}" for fault in faults]
        found = differences(
            cached.scene.model_dump(mode="json"), assembly.scene.model_dump(mode="json")
        )
        problems += _named(scene_id, found)
        if cached.warnings != assembly.warnings:
            problems.append(f"{scene_id}: the warnings differ")
    return problems


def summary(cache: SceneCache) -> dict[str, object]:
    return {
        "plan_id": cache.plan.plan_id,
        "rooms": len(_rooms(cache.plan)),
        "scenes": {
            cached.scene.scene_id: {
                "items": len(cached.scene.furniture),
                "proxies": sorted(i.id for i in cached.scene.furniture if i.is_proxy),
                "warnings": len(cached.warnings),
            }
            for cached in cache.scenes
        },
    }


def _images(paths: Sequence[Path]) -> list[tuple[bytes, str]]:
    return [(p.read_bytes(), mimetypes.guess_type(p.name)[0] or "image/png") for p in paths]


def _annotator(paths: Sequence[Path] | None) -> PlanAnnotator:
    if not paths:
        return FalVisionAnnotator()
    return FixedAnnotator([PlanAnnotations.model_validate_json(p.read_text()) for p in paths])


def main(argv: list[str] | None = None) -> int:
    from services.reconstruction.config import demo_cache_dir, scene_cache_dir

    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    publish = commands.add_parser("publish", help="parse a plan and publish its scene cache")
    publish.add_argument("images", nargs="+", type=Path, help="the plan's images, in order")
    verify = commands.add_parser("verify", help="check that a published cache is reproduced")
    verify.add_argument("--plan-id", required=True)
    verify.add_argument(
        "--images", nargs="+", type=Path, help="also parse the plan's images again and compare"
    )
    for command in (publish, verify):
        command.add_argument(
            "--annotations",
            nargs="+",
            type=Path,
            help="recorded PlanAnnotations JSON, one per image (default: fal vision, FAL_KEY)",
        )
        command.add_argument("--cache-dir", type=Path, default=scene_cache_dir())
        command.add_argument("--furniture-cache-dir", type=Path, default=demo_cache_dir())
    args = parser.parse_args(argv)
    bindings = default_bindings()
    try:
        if args.command == "publish":
            cache = publish_scene_cache(
                _images(args.images),
                _annotator(args.annotations),
                cache_dir=args.cache_dir,
                furniture_cache_dir=args.furniture_cache_dir,
                bindings=bindings,
            )
            print(json.dumps(summary(cache) | {"ok": True}))
            return 0
        path = cache_path(args.cache_dir, args.plan_id)
        if not path.is_file():
            print(json.dumps({"plan_id": args.plan_id, "ok": False, "error": "no cache published"}))
            return 2
        problems = verify_scene_cache(
            path,
            furniture_cache_dir=args.furniture_cache_dir,
            bindings=bindings,
            images=_images(args.images) if args.images else None,
            annotator=_annotator(args.annotations),
        )
        if problems:
            print(json.dumps({"plan_id": args.plan_id, "ok": False, "problems": problems}))
            return 2
        print(json.dumps(summary(read_scene_cache(path)) | {"ok": True}))
        return 0
    except SceneCacheError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}))
        return 2
    except (UnreadableImage, ValueError, OSError) as exc:
        print(f"Scene cache {args.command} failed ({type(exc).__name__}: {exc}).")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
