"""One room + its furniture -> the `RoomScene` the editor and the audit load (#9).

A `FurnitureSource` says what furniture a room has: pose-less `FurnitureAsset`s and an observer
that says where each was seen. `assemble_scene` puts the doors exactly on their walls, places
every asset with `align.align_assets` (#8), and returns the room with its shell reference, its
openings and one independently posed item per asset.

Dev 2's video pipeline plugs in as a source: `video_furniture.RealRoomFurniture` gives a room
bound to a video its extracted items, placed from reviewed hints (#10). Rooms without a video
get `NoFurniture`: the room alone, and a warning saying why.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Protocol

from contracts.schema import RoomScene
from services.reconstruction.assets.models import AssetEvidence, EvidenceFrame, FurnitureAsset

from .align import AlignmentRecord, align_assets
from .observe import FrameSource, NullObserver, PlacementObserver
from .openings import conform_openings

log = logging.getLogger(__name__)

NO_FURNITURE_YET = (
    "No furniture yet: no furniture video is linked to this room, so it has walls and "
    "openings only."
)


@dataclass
class SceneFurniture:
    """What a furniture source supplies for one room."""

    assets: list[FurnitureAsset]
    observer: PlacementObserver = field(default_factory=NullObserver)
    frames: FrameSource | None = None
    warnings: list[str] = field(default_factory=list)
    complete: bool = True
    """False when the source has less than it will have later (its furniture is not extracted
    yet): the room is shown, but the assembly is not kept, so the next request asks again."""
    pending: bool = False
    """The furniture is still being extracted (`video_jobs.py`): the client should ask again
    later. Implies `complete = False`."""


class FurnitureSource(Protocol):
    def furniture_for(self, room: RoomScene) -> SceneFurniture: ...


class NoFurniture:
    """The room alone: what parsed rooms get until #16 produces furniture assets."""

    def furniture_for(self, room: RoomScene) -> SceneFurniture:
        return SceneFurniture(assets=[], warnings=[NO_FURNITURE_YET])


@dataclass
class Assembly:
    scene: RoomScene
    records: dict[str, AlignmentRecord]
    """How each pose was decided, by asset ID. Stays inside the service."""
    warnings: list[str]
    complete: bool = True
    """False when the furniture source failed or was not ready, or the placement observer
    failed: the room came back with less than it should have, and a retry may give more, so
    callers should not keep it."""
    pending: bool = False
    """Assembled while the furniture was still being extracted: decided here, from the
    source's answer, never from the job's later state."""


def assemble_scene(room: RoomScene, source: FurnitureSource) -> Assembly:
    """The room with its furniture placed. Never drops the room: a source that fails or is not
    ready gives the room without furniture and a warning, and `complete = False`.

    Keeps the room's `scene_id`, shell and openings (doors conformed to their walls) and starts
    at revision 0. Furniture the room already has stays where it is.
    """
    room, warnings = conform_openings(room)
    source_failed = False
    try:
        furniture = source.furniture_for(room)
    except Exception as exc:  # a provider failure must not lose the room
        log.warning("furniture source failed for %s: %s", room.scene_id, exc)
        furniture = SceneFurniture(
            assets=[], warnings=[f"furniture unavailable ({type(exc).__name__})"]
        )
        source_failed = True
    warnings += furniture.warnings
    result = align_assets(room, furniture.assets, furniture.observer, furniture.frames)
    warnings += result.warnings
    scene = RoomScene.model_validate(result.place_in(room).model_dump() | {"revision": 0})
    return Assembly(
        scene=scene,
        records=result.records,
        warnings=warnings,
        complete=furniture.complete and not (source_failed or result.observer_failed),
        pending=furniture.pending and not source_failed,
    )


def assets_of(scene: RoomScene) -> list[FurnitureAsset]:
    """A scene's furniture as pose-less assets with placeholder evidence (no source frames)."""
    evidence = AssetEvidence(
        frames=[EvidenceFrame(frame_index=0, timestamp_s=0.0)], primary_frame_index=0
    )
    return [
        FurnitureAsset.model_validate(
            {**item.model_dump(exclude={"pose"}), "evidence": evidence.model_dump()}
        )
        for item in scene.furniture
    ]
