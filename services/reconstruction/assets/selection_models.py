"""Internal #14-#16 records. Source evidence is deliberately separate from RoomScene."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from contracts.schema import ITEM_ID_PATTERN

from .models import FurnitureAsset

Category = Literal[
    "bed", "desk", "chair", "table", "wardrobe", "sofa", "storage", "fixture", "other"
]


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class SourceVideo(Record):
    source_id: str = Field(pattern=r"^[a-f0-9]{64}$")
    name: str
    stream_index: int = Field(ge=0)
    encoded_size: tuple[int, int]
    upright_size: tuple[int, int]
    rotation_deg: int
    encoded_to_upright: list[list[float]]
    time_base: str


class Frame(Record):
    key: str
    source_id: str
    frame_index: int = Field(ge=0)
    pts: int
    timestamp_s: float = Field(ge=0)
    image_size_px: tuple[int, int]
    image_path: str
    """Relative to the runtime data directory, never a browser URL."""
    quality: float = Field(ge=0, le=1)


class Box(Record):
    """Upright normalised coordinates; convert to original pixels only at the handoff."""

    x: float = Field(ge=0, lt=1)
    y: float = Field(ge=0, lt=1)
    width: float = Field(gt=0, le=1)
    height: float = Field(gt=0, le=1)

    @model_validator(mode="after")
    def _inside(self) -> Box:
        if self.x + self.width > 1.000001 or self.y + self.height > 1.000001:
            raise ValueError("box extends outside the upright image")
        return self


class Sighting(Record):
    frame_key: str
    box: Box
    quality: float = Field(default=0, ge=0, le=1)


class DiscoveredObject(Record):
    name: str = Field(min_length=1, max_length=160)
    category: Category
    appearance: str = Field(min_length=1, max_length=1000)
    sightings: list[Sighting] = Field(min_length=1)
    reference_id: str | None = Field(default=None, pattern=ITEM_ID_PATTERN)
    """An existing registry ID suggested by the provider, subject to local validation."""
    uncertain: bool = False
    reflection: bool = False

    @model_validator(mode="after")
    def _distinct_frames(self) -> DiscoveredObject:
        keys = [s.frame_key for s in self.sightings]
        if len(keys) != len(set(keys)):
            raise ValueError("one physical object cannot have two sightings in one frame")
        return self


class Discovery(Record):
    objects: list[DiscoveredObject]
    empty_frames: list[str] = []
    warnings: list[str] = []

    def validate_frames(self, keys: set[str]) -> None:
        observed = {s.frame_key for obj in self.objects for s in obj.sightings}
        empty = set(self.empty_frames)
        if observed | empty != keys or observed & empty:
            raise ValueError("provider must account for exactly the requested frames")


LOW_MASK_SCORE = 0.8
"""Live SAM 3 run: clean masks scored 0.92-0.98; ragged ones on blurred close-ups 0.57-0.71."""


class MaskRecord(Record):
    """One stored instance mask (#15) for one sighting of one item."""

    frame_key: str
    box: Box
    """The sighting box used as the prompt. A mask is current only while this still matches."""
    method: Literal["sam3", "grabcut"]
    mask_path: str
    """8-bit PNG, 255 = item, in upright source-frame pixels. Relative to the data directory."""
    crop_path: str
    """RGBA cut-out of the original pixels, cropped to `bbox_px`. Relative to the data directory."""
    bbox_px: tuple[int, int, int, int]
    """Tight (x, y, w, h) of the mask in upright source-frame pixels."""
    area_px: int = Field(gt=0)
    score: float | None = Field(default=None, ge=0, le=1)
    """The provider's own confidence when it reports one (SAM 3); None for GrabCut."""

    @property
    def low_confidence(self) -> bool:
        return self.score is not None and self.score < LOW_MASK_SCORE


class MeshRecord(Record):
    """One stored raw provider mesh (#16) for one item. Not normalised and not servable (#17)."""

    frame_key: str
    mask_path: str
    """The mask sent with the frame. A mesh is current only while this is still the item's
    current mask for that frame."""
    provider: Literal["sam3d"]
    mesh_path: str
    """glTF 2.0 binary as the provider returned it. Relative to the data directory."""
    size_bytes: int = Field(gt=0)
    triangles: int = Field(gt=0)
    extents: tuple[float, float, float]
    """Axis-aligned size in the provider's own units (SAM 3D: longest side about 1), not metres."""
    pose: dict[str, Any] | None = None
    """Raw per-object provider metadata (SAM 3D: scale, rotation, translation, camera_pose)."""


class SelectedObject(Record):
    id: str = Field(pattern=ITEM_ID_PATTERN)
    name: str
    category: Category
    appearance: str
    room_key: str | None = None
    sightings: list[Sighting] = Field(min_length=1)
    selected_views: list[str] = Field(default_factory=list, max_length=4)
    masks: list[MaskRecord] = []
    mesh: MeshRecord | None = None

    @model_validator(mode="after")
    def _views(self) -> SelectedObject:
        keys = [s.frame_key for s in self.sightings]
        if len(keys) != len(set(keys)) or not set(self.selected_views).issubset(keys):
            raise ValueError("object views must refer to unique sightings")
        masked = [m.frame_key for m in self.masks]
        if len(masked) != len(set(masked)) or not set(masked).issubset(keys):
            raise ValueError("object masks must refer to unique sightings")
        if self.mesh is not None and self.mesh.frame_key not in keys:
            raise ValueError("object mesh must refer to a sighting")
        return self

    def mask_for(self, frame_key: str) -> MaskRecord | None:
        """The stored mask for a sighting, unless its box has changed since."""
        box = next((s.box for s in self.sightings if s.frame_key == frame_key), None)
        return next((m for m in self.masks if m.frame_key == frame_key and m.box == box), None)

    def current_mesh(self) -> MeshRecord | None:
        """The stored raw mesh, unless the mask it was made from has been replaced since."""
        if self.mesh is None:
            return None
        mask = self.mask_for(self.mesh.frame_key)
        return self.mesh if mask is not None and mask.mask_path == self.mesh.mask_path else None


class RegistryState(Record):
    revision: int = Field(default=0, ge=0)
    next_id: int = Field(default=1, ge=1)
    sources: dict[str, SourceVideo] = {}
    frames: dict[str, Frame] = {}
    objects: dict[str, SelectedObject] = {}
    unresolved: list[str] = []
    unresolved_by_frame: dict[str, list[str]] = {}
    warnings_by_frame: dict[str, list[str]] = {}

    @model_validator(mode="after")
    def _links(self) -> RegistryState:
        if any(key != obj.id for key, obj in self.objects.items()):
            raise ValueError("registry object key does not match its ID")
        if any(key != frame.key for key, frame in self.frames.items()):
            raise ValueError("registry frame key does not match source evidence")
        if any(
            s.frame_key not in self.frames for obj in self.objects.values() for s in obj.sightings
        ):
            raise ValueError("registry object has missing source evidence")
        # Older snapshots stored unscoped messages. Conservatively attach them to the
        # existing frames, so reviewing those frames clears them without dropping IDs.
        if self.unresolved and not self.unresolved_by_frame:
            self.unresolved_by_frame = {key: list(self.unresolved) for key in self.frames}
        if (set(self.unresolved_by_frame) | set(self.warnings_by_frame)) - self.frames.keys():
            raise ValueError("registry diagnostic has missing source evidence")
        return self


class SelectionResult(Record):
    scene_id: str
    registry_revision: int
    sources: list[SourceVideo]
    frames: list[Frame]
    objects: list[SelectedObject]
    geometry_frame_keys: list[str]
    unresolved: list[str]
    warnings: list[str]
    complete: bool
    """All sampled frames processed without unresolved identities, not an exhaustive inventory."""


class MissingMask(Record):
    object_id: str
    frame_key: str
    reason: str


class SegmentationResult(Record):
    scene_id: str
    registry_revision: int
    frames: list[Frame]
    """Every frame the returned objects were sighted in."""
    objects: list[SelectedObject]
    missing: list[MissingMask]
    warnings: list[str]
    complete: bool
    """Every selected view of every requested item has a stored mask; not a quality claim."""


FailureKind = Literal["not_attempted", "no_view", "budget", "timeout", "provider", "invalid_mesh"]
"""Why an item has no mesh: no provider was passed; it has no usable #15 mask; the request
budget ran out; the local deadline passed (the remote request is kept and collected by the next
run); the provider or its transport failed; or what it returned is not a usable mesh."""


class MeshFailure(Record):
    kind: FailureKind
    reason: str
    """Safe to show: never credentials, provider bodies or private paths."""


class ItemReconstruction(Record):
    """One furniture item after #16/#17: its raw mesh or the reason there is none, its proxy,
    and the normalised mesh asset when there is one."""

    object_id: str = Field(pattern=ITEM_ID_PATTERN)
    mesh: MeshRecord | None
    """The item's current stored raw mesh, from this run or an earlier one."""
    failure: MeshFailure | None
    """Why this run produced no mesh. Set together with `mesh` when a replacement failed and
    the stored mesh was kept."""
    proxy: FurnitureAsset
    """A labelled box (`is_proxy`): what to serve while `asset` is None."""
    asset: FurnitureAsset | None = None
    """The raw mesh normalised to the furniture profile (#17), with the same ID. None when
    there is no mesh or it could not be normalised; the result's warnings say which."""

    @model_validator(mode="after")
    def _outcome(self) -> ItemReconstruction:
        if self.mesh is None and self.failure is None:
            raise ValueError("an item without a mesh must say why")
        return self


class ReconstructionResult(Record):
    scene_id: str
    registry_revision: int
    items: list[ItemReconstruction]
    warnings: list[str]
    complete: bool
    """Every requested item has a current raw mesh that normalised, and nothing failed in this
    run; not a quality claim."""


class SelectionOptions(Record):
    start_s: float = Field(default=0, ge=0)
    end_s: float | None = Field(default=None, gt=0)
    sample_interval_s: float = Field(default=1, ge=0.25)
    max_frames_per_video: int = Field(default=24, ge=1, le=120)
    batch_size: int = Field(default=4, ge=1, le=8)
    max_requests: int = Field(default=8, ge=0, le=100)
    room_key: str | None = Field(default=None, max_length=200)
    """Caller-confirmed room identity; never guessed from a video filename."""

    @model_validator(mode="after")
    def _range(self) -> SelectionOptions:
        if self.end_s is not None and self.end_s <= self.start_s:
            raise ValueError("end_s must be greater than start_s")
        return self
