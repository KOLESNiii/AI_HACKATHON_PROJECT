"""Typed Dev 2 -> Dev 1 asset handoff (see README.md in this folder).

Evidence stays inside the reconstruction service, so these models live here and not in
`contracts/`. `FurnitureAsset` mirrors `FurnitureItem` without `pose`; a test keeps the two in
step, and every asset is validated by the `FurnitureItem` rules.
"""

from typing import Any, Literal

from pydantic import Field, model_validator

from contracts.schema import (
    GLB_URL_PATTERN,
    ITEM_ID_PATTERN,
    BBoxM,
    CollisionPart,
    ContractModel,
    FurnitureItem,
    Pose2D,
)


class EvidenceFrame(ContractModel):
    """One video frame an asset was seen in. Optional fields are null for fixtures."""

    frame_index: int = Field(ge=0)
    timestamp_s: float = Field(ge=0)
    image_size_px: tuple[int, int] | None = None
    """(width, height) of the frame."""
    mask_url: str | None = None
    bbox_px: tuple[float, float, float, float] | None = None
    """(x, y, w, h) in pixels."""
    provider_pose: dict[str, Any] | None = None
    """Raw per-object pose from fal.ai `sam-3d-objects`; shape unverified until a live call."""


class AssetEvidence(ContractModel):
    frames: list[EvidenceFrame] = Field(min_length=1)
    primary_frame_index: int
    """The `frame_index` of one of `frames`."""

    @model_validator(mode="after")
    def _check_primary(self) -> "AssetEvidence":
        if self.primary_frame_index not in {f.frame_index for f in self.frames}:
            raise ValueError("primary_frame_index must name one of frames")
        return self


class FurnitureAsset(ContractModel):
    """What Dev 2 returns: every `FurnitureItem` field except `pose`, plus evidence."""

    id: str = Field(pattern=ITEM_ID_PATTERN)
    name: str
    category: Literal[
        "bed", "desk", "chair", "table", "wardrobe", "sofa", "storage", "fixture", "other"
    ]
    source: Literal["extracted_video", "catalog_search", "url_import"]
    glb_url: str = Field(pattern=GLB_URL_PATTERN)
    product_url: str | None = None
    price_gbp: float | None = None
    bbox_m: BBoxM
    has_screen: bool = False
    requires_front_clear_m: float = 0.6
    wall_flush_preferred: bool = True
    is_proxy: bool = False
    dimension_source: Literal["measured", "catalog", "estimated", "user_corrected"] = "estimated"
    correction_needed: list[Literal["dimensions", "placement", "orientation"]] = []
    collision_parts: list[CollisionPart] = []
    collision_source: Literal["template", "mesh", "user_corrected"] = "template"
    is_fixed: bool = False
    evidence: AssetEvidence

    @model_validator(mode="after")
    def _check_item_rules(self) -> "FurnitureAsset":
        # Apply the FurnitureItem validators (collision parts, fixtures) at the handoff.
        self.to_item(Pose2D(x=0, z=0, yaw_deg=0))
        return self

    def to_item(self, pose: Pose2D) -> FurnitureItem:
        """Dev 1 places the asset: add the pose it aligned from the floor plan."""
        return FurnitureItem.model_validate(
            {**self.model_dump(exclude={"evidence"}), "pose": pose.model_dump()}
        )


class NormalisedMesh(ContractModel):
    """Output of `normalise_mesh` (#17): a re-hosted mesh fitted to `bbox_m`."""

    glb_url: str = Field(pattern=GLB_URL_PATTERN)
    bbox_m: BBoxM
    collision_parts: list[CollisionPart] = []
    collision_source: Literal["template", "mesh", "user_corrected"] = "template"
    correction_needed: list[Literal["dimensions", "placement", "orientation"]] = []
