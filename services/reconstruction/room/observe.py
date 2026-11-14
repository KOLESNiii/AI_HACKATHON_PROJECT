"""Where each asset was seen: coarse placement hints, relative to a wall of the room.

A hint is semantics, not geometry: "against wall X, about a third of the way along, facing into
the room". `align.py` turns hints into poses and resolves conflicts. Observers never decide a
pose and never raise; an asset without a hint gets a default placement flagged for correction.

Every placement is expressed in one wall's frame, which covers flush, free-standing and sideways
items with one parametrisation:

- `along_frac`: the item's centre, as a fraction of the wall from its `start` to its `end`.
- `offset_m`: the gap between the wall face and the nearest face of the item (0 = flush).
- `facing`: which way the item's front points, in quarter turns of the wall.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Literal, Protocol

from pydantic import BaseModel, Field

from contracts.schema import RoomScene
from services.reconstruction.assets.models import EvidenceFrame, FurnitureAsset

Facing = Literal["into_room", "toward_wall", "wall_start", "wall_end"]
"""`into_room`: back to the wall. `toward_wall`: front to the wall. `wall_start` / `wall_end`:
side-on, front pointing at that end of the wall."""

FrameSource = Callable[[str, EvidenceFrame], bytes | None]
"""(asset ID, evidence frame) -> the encoded upright frame image, or None when unavailable.
`EvidenceFrame` carries no image reference, so pixels reach the observer through this."""


class PlacementHint(BaseModel):
    asset_id: str
    wall_id: str
    """The wall the item stands against, or the nearest one for a free-standing item."""
    along_frac: float = Field(ge=0, le=1)
    offset_m: float = Field(default=0.0, ge=0, le=20)
    facing: Facing | None = None
    """None when the front cannot be told; the item is placed back-to-wall and flagged."""
    seated_at: str | None = None
    """For a chair pushed in at a desk or table: that item's ID. Overrides the wall placement."""
    confidence: float = Field(default=0.5, ge=0, le=1)


class PlacementHints(BaseModel):
    """File shape of recorded hints (`fixtures/*.hints.json`)."""

    hints: list[PlacementHint] = []


class PlacementObserver(Protocol):
    def observe(
        self, scene: RoomScene, assets: Sequence[FurnitureAsset], frames: FrameSource
    ) -> list[PlacementHint]: ...


class NullObserver:
    """No hints: every asset gets the default wall placement, flagged for correction."""

    def observe(
        self, scene: RoomScene, assets: Sequence[FurnitureAsset], frames: FrameSource
    ) -> list[PlacementHint]:
        return []


class FixedObserver:
    """Returns pre-recorded hints (tests, the debug CLI, cached demo rooms)."""

    def __init__(self, hints: Sequence[PlacementHint]) -> None:
        self._hints = list(hints)

    @classmethod
    def from_file(cls, path: Path) -> FixedObserver:
        return cls(PlacementHints.model_validate_json(path.read_text()).hints)

    def observe(
        self, scene: RoomScene, assets: Sequence[FurnitureAsset], frames: FrameSource
    ) -> list[PlacementHint]:
        return list(self._hints)
