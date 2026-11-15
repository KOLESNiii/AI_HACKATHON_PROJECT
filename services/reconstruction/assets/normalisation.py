"""The one mesh normalisation path (#17, spec 8.3): any raw `.glb` -> the furniture profile.

Video and catalog meshes both go through `normalise_mesh`. The result is in metres, +Y up,
front +Z, with its bounding-box bottom-centre at the origin and its bounds equal to `bbox_m`.
"""

from __future__ import annotations

import io
import math
from pathlib import Path
from typing import Literal, cast, get_args

import numpy as np
import trimesh
from numpy.typing import NDArray
from PIL import Image

from contracts.schema import GLB_BBOX_TOLERANCE_M, MIN_PART_DIMENSION_M, BBoxM

from .asset_store import ASSET_URL_BASE, store_asset
from .collision_templates import template_parts
from .models import NormalisedMesh
from .proxies import CATEGORY_SIZE_M
from .selection_models import Category

Front = Literal["+z", "+x", "-z", "-x"]
"""The raw mesh's horizontal direction that is the item's logical front."""

MAX_TRIANGLES = 30_000
MAX_BYTES = 3_000_000
MAX_PRIMITIVES = 4
MAX_TEXTURE_PX = 1024
TEXTURE_STEPS_PX = (MAX_TEXTURE_PX, 768, 512)
"""A file over `MAX_BYTES` is written again with smaller textures before it is refused: a
retailer model with four full-size texture maps is otherwise lost for a few hundred kilobytes
(IKEA's SKOGSTA table, 2026-11-15)."""
MAX_DISTORTION = 0.15
"""Fitting stated dimensions may stretch one axis this much more than another before the
mesh's shape is taken to disagree with them."""
MAX_ESTIMATED_SIZE_RATIO = 3.0
"""Refuse height-based estimates with any side over this multiple of its category size."""
PROVIDER_FRONT: dict[str, Front] = {"sam3d": "+z", "trellis2": "+z", "retailer": "+z"}
"""Where each mesh provider puts the front. SAM 3D Objects: observed 2026-11-15 on the four
reviewed opening-room meshes (+Y up, axis-aligned, both sofas and the armchair facing +Z).
TRELLIS.2: the side facing the camera is +Z, observed 2026-11-15 on IKEA's TÄRNKULLEN bed
photo (headboard at -Z, foot of the bed at +Z).
Retailer models: +Z is glTF's own front, and what IKEA's models showed on 2026-11-15 (MICKE
desk drawers, BILLY bookcase opening and the foot of the MALM bed at +Z). Another retailer's
model may differ and is not checked."""

_YAW_TO_PLUS_Z: dict[Front, float] = {"+z": 0.0, "+x": -90.0, "-z": 180.0, "-x": 90.0}
_TEXTURES = ("baseColorTexture", "metallicRoughnessTexture", "normalTexture",
             "occlusionTexture", "emissiveTexture")  # fmt: skip


class NormalisationError(ValueError):
    """The raw mesh cannot meet the furniture profile. The message is safe to report; the item
    keeps its proxy."""


def _load(raw_glb: Path) -> list[trimesh.Trimesh]:
    """Every triangle mesh of the file in the file's world frame: node transforms baked."""
    try:
        data = raw_glb.read_bytes()
        dumped = trimesh.load_scene(io.BytesIO(data), file_type="glb").dump(concatenate=False)
    except Exception as exc:  # An untrusted file: any reader failure means the same thing.
        raise NormalisationError("raw mesh could not be read") from exc
    meshes = [m for m in dumped if isinstance(m, trimesh.Trimesh) and len(m.faces)]
    if not meshes:
        raise NormalisationError("raw mesh has no triangles")
    if len(meshes) > MAX_PRIMITIVES:
        raise NormalisationError(f"raw mesh has more than {MAX_PRIMITIVES} primitives")
    triangles = sum(len(m.faces) for m in meshes)
    if triangles > MAX_TRIANGLES:
        # There is no decimator among the dependencies; providers are asked for a budget instead.
        raise NormalisationError(
            f"raw mesh has {triangles} triangles; the limit is {MAX_TRIANGLES}"
        )
    for mesh in meshes:
        # Bounds and exported accessors must describe the same triangle geometry.
        mesh.remove_unreferenced_vertices()
    return meshes


def _cap_textures(mesh: trimesh.Trimesh, limit: int = MAX_TEXTURE_PX) -> None:
    material = getattr(mesh.visual, "material", None)
    for name in _TEXTURES:
        image = getattr(material, name, None)
        if isinstance(image, Image.Image) and max(image.size) > limit:
            share = limit / max(image.size)
            size = (max(1, round(image.width * share)), max(1, round(image.height * share)))
            setattr(material, name, image.resize(size, Image.Resampling.LANCZOS))


def _bounds(meshes: list[trimesh.Trimesh]) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    low = np.min([m.vertices[np.unique(m.faces)].min(axis=0) for m in meshes], axis=0)
    high = np.max([m.vertices[np.unique(m.faces)].max(axis=0) for m in meshes], axis=0)
    return low, high


def normalise_mesh(
    raw_glb: Path,
    *,
    category: str,
    target_bbox: BBoxM | None,
    data_dir: Path,
    front: Front | None = None,
    preserve_scale: bool = False,
    url_base: str = ASSET_URL_BASE,
) -> NormalisedMesh:
    """Fit a raw glTF 2.0 binary to the furniture profile, store it and return its `glb_url`.

    `front` names the raw mesh's front; it is turned to +Z. With `None` the mesh is kept as
    given and `"orientation"` is requested. The raw file is taken to be +Y up, as glTF requires.

    With a `target_bbox` (measured, catalog or user-corrected) each axis is scaled to match it
    exactly; `"dimensions"` is requested if that distorts the shape by more than
    `MAX_DISTORTION`. Without one the mesh is scaled uniformly from the category's typical
    height and the returned `bbox_m` is an estimate that always requests `"dimensions"`: the
    caller records it as `dimension_source: "estimated"`. An estimated side exceeding
    `MAX_ESTIMATED_SIZE_RATIO` times its category size is refused; supply dimensions instead.

    `preserve_scale=True` keeps metre-scale retailer extents when no target is supplied,
    with the same estimated provenance, dimension correction and size limits.

    Raises NormalisationError when the file is unusable or over the profile's budgets, and
    ValueError for an unknown category. Nothing is stored in either case.
    """
    if category not in get_args(Category):
        raise ValueError(f"unknown furniture category: {category!r}")
    if front is not None and front not in _YAW_TO_PLUS_Z:
        raise ValueError(f"unknown front direction: {front!r}")
    meshes = _load(raw_glb)
    corrections: list[Literal["dimensions", "placement", "orientation"]] = []

    angle = math.radians(_YAW_TO_PLUS_Z[front or "+z"])
    turn = np.eye(4)  # A rotation about +Y.
    turn[0, 0] = turn[2, 2] = math.cos(angle)
    turn[0, 2], turn[2, 0] = math.sin(angle), -math.sin(angle)
    for mesh in meshes:
        mesh.apply_transform(turn)
    low, high = _bounds(meshes)
    extents = high - low
    if not np.all(np.isfinite(extents)) or extents.min() <= 1e-6:
        raise NormalisationError("raw mesh has no usable extent")

    size: NDArray[np.float64]
    if target_bbox is None:
        # Millimetre-rounded so the recorded size is a clean number the mesh then matches.
        typical_size = np.array(CATEGORY_SIZE_M[cast(Category, category)])
        size = np.round(extents if preserve_scale else extents * (typical_size[1] / extents[1]), 3)
        if np.any(size / typical_size > MAX_ESTIMATED_SIZE_RATIO):
            raise NormalisationError(
                f"estimated side exceeds {MAX_ESTIMATED_SIZE_RATIO:g} times the category size; "
                "supply dimensions"
            )
        corrections.append("dimensions")
    else:
        size = np.array([target_bbox.width, target_bbox.height, target_bbox.depth], dtype=float)
    if not np.all(np.isfinite(size)) or size.min() < MIN_PART_DIMENSION_M:
        raise NormalisationError(f"a side would be thinner than {MIN_PART_DIMENSION_M} m")
    scale = size / extents
    if target_bbox is not None and scale.max() / scale.min() - 1 > MAX_DISTORTION:
        corrections.append("dimensions")
    if front is None:
        corrections.append("orientation")

    # Bottom-centre to the origin, then scale about it.
    fit = np.diag([*scale, 1.0])
    fit[:3, 3] = -scale * [(low[0] + high[0]) / 2, low[1], (low[2] + high[2]) / 2]
    for mesh in meshes:
        mesh.apply_transform(fit)
    bbox = BBoxM(width=float(size[0]), height=float(size[1]), depth=float(size[2]))

    try:
        for limit in TEXTURE_STEPS_PX:
            for mesh in meshes:
                _cap_textures(mesh, limit)
            glb = trimesh.Scene(meshes).export(file_type="glb")  # type: ignore[no-untyped-call]
            assert isinstance(glb, bytes)
            if len(glb) <= MAX_BYTES:
                break
        written = np.asarray(trimesh.load_scene(io.BytesIO(glb), file_type="glb").bounds)
    except Exception as exc:
        raise NormalisationError("normalised mesh could not be written") from exc
    expected = [[-size[0] / 2, 0, -size[2] / 2], [size[0] / 2, size[1], size[2] / 2]]
    if not np.abs(written - expected).max() < GLB_BBOX_TOLERANCE_M:  # Also catches NaN.
        raise NormalisationError("normalised mesh does not match its bounds")
    if len(glb) > MAX_BYTES:
        raise NormalisationError(f"normalised mesh is {len(glb)} bytes; the limit is {MAX_BYTES}")

    return NormalisedMesh(
        glb_url=store_asset(data_dir, glb, url_base=url_base),
        bbox_m=bbox,
        collision_parts=template_parts(category, bbox),
        collision_source="template",
        correction_needed=corrections,
    )
