"""Video furniture for a real plan room (#10): Dev 2's extracted items, placed from hints.

A `RoomVideo` binds one parsed room (by scene ID) to the furniture Dev 2's pipeline extracted
from a video of it (by furniture scene ID), with reviewed placement hints for those items.
`RealRoomFurniture` is the `FurnitureSource` that reads that furniture from the pipeline's data
directory. It is offline: it reuses what the pipeline stored and never submits a provider
request. Each item is its normalised mesh (#17) when the pipeline has one, otherwise Dev 2's
labelled proxy (a dimensioned box with a front marker, `is_proxy`).

Rooms without a binding get `NoFurniture`. A bound room is checked against the walls the
binding was made for: a scene ID only names the plan image, and the same image parsed without
its labels is a different room. Such a room gets no furniture and says why. The check is on
shape, so a room whose scale the user corrected (#11) keeps its furniture. A bound room
whose furniture is not (fully) extracted yet gets what there is so far, a warning, and
`complete = False`, so the scene is not kept and the next request looks again.

Demo cache (#20): when the data directory has nothing for the bound video, the furniture comes
from Dev 2's published demo cache for that video (`assets/demo_cache.py`), installed into the
data directory so the asset route serves it. Pipeline data, when present, always wins.
"""

from __future__ import annotations

import logging
import math
from collections.abc import Mapping, Sequence
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, ConfigDict, TypeAdapter

from contracts.schema import RoomScene
from services.reconstruction.assets.demo_cache import CacheError, install_demo_cache
from services.reconstruction.assets.models import FurnitureAsset
from services.reconstruction.assets.reconstruction import reconstruct_furniture

from .assemble import NoFurniture, SceneFurniture
from .observe import FixedObserver, PlacementHint

log = logging.getLogger(__name__)

BINDINGS_PATH = Path(__file__).parent / "fixtures" / "real_rooms.json"

WALL_TOLERANCE = 0.05
"""Relative wall-length tolerance, after fitting the room's scale."""
WALL_TOLERANCE_M = 0.05
"""Absolute floor for the tolerance, for very short walls."""

NOT_EXTRACTED = (
    "No furniture extracted for this room yet: run the furniture pipeline for its video into "
    "the furniture data directory (services/reconstruction/room/README.md, 'Real-input room')."
)


class RoomVideo(BaseModel):
    """One plan room and the video its furniture comes from."""

    model_config = ConfigDict(extra="forbid")

    scene_id: str
    """The parsed room's scene ID (`<plan_id>-<room_id>`; the plan ID hashes the image)."""
    plan: str
    """The plan image, relative to the repository root."""
    room_id: str
    video: str
    """The video, relative to the repository root."""
    furniture_scene_id: str
    """Dev 2's scene ID for the furniture extracted from that video."""
    note: str = ""
    walls_m: dict[str, float]
    """The bound room's wall IDs and lengths, as parsed when the hints were made."""
    hints: list[PlacementHint]
    """Where each extracted item stands, by Dev 2's item ID and the room's wall IDs."""


def load_bindings(path: Path = BINDINGS_PATH) -> dict[str, RoomVideo]:
    """Bindings by scene ID."""
    rooms = TypeAdapter(list[RoomVideo]).validate_json(path.read_text())
    return {room.scene_id: room for room in rooms}


@lru_cache(maxsize=1)
def default_bindings() -> dict[str, RoomVideo]:
    return load_bindings()


def geometry_mismatch(binding: RoomVideo, room: RoomScene) -> str | None:
    """Why `room` is not the room `binding` was made for, or None when it is.

    Compares shape, not size: the user may correct the floor's scale (#11), so the walls are
    compared after fitting one factor (total length over total expected length).
    """
    walls = {w.id: math.dist((w.start.x, w.start.z), (w.end.x, w.end.z)) for w in room.walls}
    if walls.keys() != binding.walls_m.keys():
        return f"{len(walls)} walls, expected {len(binding.walls_m)}"
    factor = sum(walls.values()) / sum(binding.walls_m.values())
    for wall_id, parsed in binding.walls_m.items():
        expected = parsed * factor
        if abs(walls[wall_id] - expected) > max(WALL_TOLERANCE * expected, WALL_TOLERANCE_M):
            return f"{wall_id} is {walls[wall_id]:.2f} m, expected {expected:.2f} m"
    return None


def geometry_warning(reason: str) -> str:
    return (
        f"This room's geometry does not match the plan its furniture video was bound to "
        f"({reason}), so no furniture was placed. Upload the plan with its labels read "
        "(FAL_KEY)."
    )


def proxy_warning(ids: Sequence[str]) -> str:
    return f"labelled proxies (sized boxes; no normalised mesh): {', '.join(ids)}"


def still_extracting(ids: Sequence[str]) -> str:
    return f"furniture still being extracted: no {', '.join(ids)} yet"


def from_demo_cache(scene_id: str) -> str:
    return (
        f"furniture from the published demo cache of {scene_id!r} (no pipeline data for this "
        "video here; no provider used)"
    )


def broken_cache(reason: str) -> str:
    return f"the demo cache could not be used: {reason}"


class RealRoomFurniture:
    """Furniture for rooms bound to a video, read from Dev 2's pipeline data directory."""

    def __init__(
        self, bindings: Mapping[str, RoomVideo], data_dir: Path, cache_dir: Path | None = None
    ) -> None:
        self.bindings = dict(bindings)
        self.data_dir = data_dir
        self.cache_dir = cache_dir
        """Published demo caches, used when `data_dir` has no data for a video (#20)."""

    def furniture_for(self, room: RoomScene) -> SceneFurniture:
        binding = self.bindings.get(room.scene_id)
        if binding is None:
            return NoFurniture().furniture_for(room)
        if (reason := geometry_mismatch(binding, room)) is not None:
            return SceneFurniture(assets=[], warnings=[geometry_warning(reason)])
        try:
            result = reconstruct_furniture(binding.furniture_scene_id, data_dir=self.data_dir)
        except ValueError as exc:  # no registry yet, or nothing selected for that video
            log.info("no furniture for %s yet: %s", room.scene_id, exc)
            return self._cached(binding)
        assets = [item.asset or item.proxy for item in result.items]
        warnings = list(result.warnings)
        # `not_attempted` is the normal offline state (meshes are made by the pipeline's CLI).
        warnings += [
            f"{item.object_id}: no mesh ({item.failure.kind}: {item.failure.reason})"
            for item in result.items
            if item.failure is not None and item.failure.kind != "not_attempted"
        ]
        return self._furnished(binding, assets, warnings)

    def _cached(self, binding: RoomVideo) -> SceneFurniture:
        """The video's published demo cache, or the not-extracted answer when there is none.

        Not kept when the cache is missing or broken, so the pipeline (or a repaired cache)
        takes effect on the next request."""
        scene_id = binding.furniture_scene_id
        try:
            cache = (
                None
                if self.cache_dir is None
                else install_demo_cache(scene_id, cache_dir=self.cache_dir, data_dir=self.data_dir)
            )
        except (CacheError, OSError) as exc:
            log.warning("demo cache of %s unusable: %s", scene_id, exc)
            # A CacheError names cache-relative paths only; an OSError may name server paths.
            reason = str(exc) if isinstance(exc, CacheError) else type(exc).__name__
            return SceneFurniture(
                assets=[], warnings=[NOT_EXTRACTED, broken_cache(reason)], complete=False
            )
        if cache is None:
            return SceneFurniture(assets=[], warnings=[NOT_EXTRACTED], complete=False)
        return self._furnished(binding, cache.assets, [from_demo_cache(scene_id)])

    def _furnished(
        self, binding: RoomVideo, assets: list[FurnitureAsset], warnings: list[str]
    ) -> SceneFurniture:
        if proxies := [asset.id for asset in assets if asset.is_proxy]:
            warnings.append(proxy_warning(proxies))
        # Frame selection stores items batch by batch: until every hinted item is there, this
        # is a partial inventory and must not be kept.
        known = {asset.id for asset in assets}
        if missing := sorted(h.asset_id for h in binding.hints if h.asset_id not in known):
            warnings.append(still_extracting(missing))
        return SceneFurniture(
            assets=assets,
            observer=FixedObserver(binding.hints),
            warnings=warnings,
            complete=not missing,
        )
