"""Video furniture for a real plan room (#10): Dev 2's extracted items, placed from hints.

A `RoomVideo` binds one parsed room (by scene ID) to the furniture Dev 2's pipeline extracted
from a video of it (by furniture scene ID), with reviewed placement hints for those items.
`RealRoomFurniture` is the `FurnitureSource` that reads that furniture from the pipeline's data
directory. It is offline: it reuses what the pipeline stored and never submits a provider
request. Until #17 normalises the raw meshes, every item is Dev 2's labelled proxy (a
dimensioned box with a front marker, `is_proxy`).

Rooms without a binding get `NoFurniture`. A bound room whose furniture is not extracted yet
gets the room alone, a warning, and `complete = False`, so the scene is not kept and the next
request looks again.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, ConfigDict, TypeAdapter

from contracts.schema import RoomScene
from services.reconstruction.assets.reconstruction import reconstruct_furniture

from .assemble import NoFurniture, SceneFurniture
from .observe import FixedObserver, PlacementHint

log = logging.getLogger(__name__)

BINDINGS_PATH = Path(__file__).parent / "fixtures" / "real_rooms.json"

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
    hints: list[PlacementHint]
    """Where each extracted item stands, by Dev 2's item ID and the room's wall IDs."""


def load_bindings(path: Path = BINDINGS_PATH) -> dict[str, RoomVideo]:
    """Bindings by scene ID."""
    rooms = TypeAdapter(list[RoomVideo]).validate_json(path.read_text())
    return {room.scene_id: room for room in rooms}


@lru_cache(maxsize=1)
def default_bindings() -> dict[str, RoomVideo]:
    return load_bindings()


def proxy_warning(ids: Sequence[str]) -> str:
    return f"labelled proxies (sized boxes; no normalised mesh yet, #17): {', '.join(ids)}"


class RealRoomFurniture:
    """Furniture for rooms bound to a video, read from Dev 2's pipeline data directory."""

    def __init__(self, bindings: Mapping[str, RoomVideo], data_dir: Path) -> None:
        self.bindings = dict(bindings)
        self.data_dir = data_dir

    def furniture_for(self, room: RoomScene) -> SceneFurniture:
        binding = self.bindings.get(room.scene_id)
        if binding is None:
            return NoFurniture().furniture_for(room)
        try:
            result = reconstruct_furniture(binding.furniture_scene_id, data_dir=self.data_dir)
        except ValueError as exc:  # no registry yet, or nothing selected for that video
            log.info("no furniture for %s yet: %s", room.scene_id, exc)
            return SceneFurniture(assets=[], warnings=[NOT_EXTRACTED], complete=False)
        assets = [item.proxy for item in result.items]
        warnings = list(result.warnings)
        # `not_attempted` is the normal offline state (meshes are made by the pipeline's CLI).
        warnings += [
            f"{item.object_id}: no mesh ({item.failure.kind}: {item.failure.reason})"
            for item in result.items
            if item.failure is not None and item.failure.kind != "not_attempted"
        ]
        if proxies := [asset.id for asset in assets if asset.is_proxy]:
            warnings.append(proxy_warning(proxies))
        known = {asset.id for asset in assets}
        if missing := sorted(h.asset_id for h in binding.hints if h.asset_id not in known):
            warnings.append(f"hints name items the video does not have: {', '.join(missing)}")
        return SceneFurniture(
            assets=assets, observer=FixedObserver(binding.hints), warnings=warnings
        )
