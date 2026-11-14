"""Labelled, dimensioned proxy boxes (#16): what an item is when it has no usable mesh."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Literal

import trimesh
from pydantic import model_validator

from contracts.schema import MIN_PART_DIMENSION_M, BBoxM

from .asset_store import ASSET_URL_BASE, store_asset
from .models import AssetEvidence, FurnitureAsset
from .selection_models import Category, Record

CATEGORY_SIZE_M: dict[Category, tuple[float, float, float]] = {
    "bed": (1.4, 0.6, 2.0),
    "desk": (1.1, 0.75, 0.55),
    "chair": (0.5, 0.95, 0.55),
    "table": (1.15, 0.75, 0.65),
    "wardrobe": (0.95, 1.95, 0.55),
    "sofa": (1.55, 0.85, 0.75),
    "storage": (0.6, 0.8, 0.4),
    "fixture": (0.6, 0.85, 0.4),
    "other": (0.6, 0.6, 0.6),
}
"""(width, height, depth) guesses, rounded from the typical sizes in the shared fixture scenes.
A proxy sized from this table is always `estimated` and asks for its dimensions."""

BODY_RGBA = [176, 178, 186, 255]
FRONT_MARKER_RGBA = [30, 30, 35, 255]


class KnownDimensions(Record):
    """A size someone can vouch for, with where it came from."""

    bbox_m: BBoxM
    source: Literal["measured", "catalog", "user_corrected"]

    @model_validator(mode="after")
    def _usable(self) -> KnownDimensions:
        sides = (self.bbox_m.width, self.bbox_m.height, self.bbox_m.depth)
        if not all(math.isfinite(side) and side >= MIN_PART_DIMENSION_M for side in sides):
            raise ValueError(f"every dimension must be at least {MIN_PART_DIMENSION_M} m")
        return self


def proxy_glb(bbox: BBoxM) -> bytes:
    """A box of exactly `bbox`: bottom-centre at the origin, front +Z.

    The dark strip on the top-front edge shows the yaw. It lies inside the bounds, and the body
    stops below it, so no faces overlap and the bounds are still exactly `bbox`.
    """
    w, h, d = bbox.width, bbox.height, bbox.depth
    marker_h, marker_d = min(0.02, h / 4), min(0.06, d / 4)
    body_h = h - marker_h
    body = trimesh.creation.box(extents=[w, body_h, d])
    body.apply_translation([0, body_h / 2, 0])
    body.visual.vertex_colors = BODY_RGBA
    marker = trimesh.creation.box(extents=[w * 0.8, marker_h, marker_d])
    marker.apply_translation([0, body_h + marker_h / 2, d / 2 - marker_d / 2])
    marker.visual.vertex_colors = FRONT_MARKER_RGBA
    glb = trimesh.util.concatenate([body, marker]).export(file_type="glb")
    assert isinstance(glb, bytes)
    return glb


def proxy_asset(
    asset_id: str,
    name: str,
    category: Category,
    evidence: AssetEvidence,
    *,
    data_dir: Path,
    known: KnownDimensions | None = None,
    url_base: str = ASSET_URL_BASE,
) -> FurnitureAsset:
    """The fallback asset for an item: same ID, a stored box, and honest dimension provenance.

    Without `known` dimensions the size is a category guess: `estimated`, with `"dimensions"`
    in `correction_needed`, so it surfaces as a request to the user and never as a measurement.
    """
    if known is None:
        width, height, depth = CATEGORY_SIZE_M[category]
        bbox = BBoxM(width=width, height=height, depth=depth)
    else:
        bbox = known.bbox_m
    return FurnitureAsset(
        id=asset_id,
        name=name,
        category=category,
        source="extracted_video",
        glb_url=store_asset(data_dir, proxy_glb(bbox), url_base=url_base),
        bbox_m=bbox,
        is_proxy=True,
        dimension_source="estimated" if known is None else known.source,
        correction_needed=["dimensions"] if known is None else [],
        is_fixed=category == "fixture",
        evidence=evidence,
    )
