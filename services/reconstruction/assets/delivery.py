"""The handoff to Dev 1, with its checks (#18): one servable asset per item, verified.

`deliver_furniture` gives a scene's furniture as Dev 1 places it: each item's normalised mesh
when the stored file passes its checks, otherwise its labelled proxy. The ID is the same either
way and no item is dropped. It is offline: it reuses what the pipeline stored and never submits
a provider request. `check_placed` then confirms that an assembled scene still carries what was
delivered.
"""

from __future__ import annotations

import hashlib
import io
import json
import re
import struct
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

import numpy as np
import trimesh
from pydantic import ValidationError, computed_field

from contracts.schema import GLB_BBOX_TOLERANCE_M, BBoxM, RoomScene

from .asset_store import ASSET_DIR, ASSET_URL_BASE
from .models import FurnitureAsset
from .normalisation import MAX_BYTES, MAX_TRIANGLES
from .proxies import KnownDimensions
from .reconstruction import reconstruct_furniture
from .selection_models import Record

_NAME = re.compile(r"[a-f0-9]{64}\.glb")
_IDENTITY = [1.0, 0, 0, 0, 0, 1.0, 0, 0, 0, 0, 1.0, 0, 0, 0, 0, 1.0]
_NODE_DEFAULTS = {
    "matrix": _IDENTITY,
    "translation": [0.0, 0, 0],
    "rotation": [0.0, 0, 0, 1],
    "scale": [1.0, 1, 1],
}


class AssetCheck(Record):
    """What was delivered for one item and what re-reading its stored file found."""

    object_id: str
    delivered: Literal["mesh", "proxy"]
    fallback_reason: str | None = None
    """Why a proxy is delivered in place of a mesh."""
    glb_url: str
    bbox_m: BBoxM
    dimension_source: str
    correction_needed: list[str]
    bounds_error_m: float | None = None
    """Largest difference between the stored file's bounds and `bbox_m`; None if unreadable."""
    triangles: int | None = None
    size_bytes: int | None = None
    problems: list[str] = []
    """Empty when every check passed."""


class Delivery(Record):
    scene_id: str
    registry_revision: int
    assets: list[FurnitureAsset]
    """One per item, in item-ID order: what Dev 1 places."""
    checks: list[AssetCheck]
    """One per asset, in the same order."""
    warnings: list[str]
    problems: list[str] = []
    """Faults of the delivery as a whole (duplicate IDs)."""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def ok(self) -> bool:
        """Every delivered asset passed its checks. Proxies are allowed; they are listed."""
        return not self.problems and not any(check.problems for check in self.checks)


def _gltf_problems(glb: bytes) -> list[str]:
    """Scene-graph rules of the furniture profile, read from the file's JSON chunk."""
    try:
        if glb[:4] != b"glTF" or struct.unpack("<I", glb[4:8])[0] != 2:
            return ["not a binary glTF 2.0 file"]
        length, kind = struct.unpack("<II", glb[12:20])
        if kind != 0x4E4F534A:
            return ["not a binary glTF 2.0 file"]
        document: dict[str, Any] = json.loads(glb[20 : 20 + length])
    except (struct.error, ValueError):
        return ["not a binary glTF 2.0 file"]
    problems = [f"has {name}" for name in ("skins", "animations", "cameras") if document.get(name)]
    if "KHR_lights_punctual" in document.get("extensions", {}) or any(
        "KHR_lights_punctual" in node.get("extensions", {}) for node in document.get("nodes", [])
    ):
        problems.append("has lights")
    for node in document.get("nodes", []):
        for name, default in _NODE_DEFAULTS.items():
            if name in node and not np.allclose(node[name], default, atol=1e-9):
                problems.append("has a node transform that is not baked into the vertices")
                return problems
    return problems


def inspect_asset(
    asset: FurnitureAsset, *, data_dir: Path, url_base: str = ASSET_URL_BASE
) -> AssetCheck:
    """Re-read an asset's stored file and check it against the furniture profile and its own
    `bbox_m`. Never raises for a bad file: every fault is listed in `problems`."""
    problems: list[str] = []
    measured: dict[str, Any] = {}
    try:
        FurnitureAsset.model_validate(asset.model_dump())
    except ValidationError as exc:
        problems.append(f"breaks the furniture item rules ({exc.error_count()} errors)")
    if asset.dimension_source == "estimated" and "dimensions" not in asset.correction_needed:
        problems.append("estimated size does not ask for a dimensions correction")

    prefix, _, name = asset.glb_url.rpartition("/")
    path = data_dir / ASSET_DIR / name
    if prefix != url_base.rstrip("/") or not _NAME.fullmatch(name) or not path.is_file():
        problems.append("glb_url does not name a file in the asset store")
    else:
        glb = path.read_bytes()
        measured["size_bytes"] = len(glb)
        if f"{hashlib.sha256(glb).hexdigest()}.glb" != name:
            problems.append("stored file does not match its content address")
        if len(glb) > MAX_BYTES:
            problems.append(f"file is {len(glb)} bytes; the limit is {MAX_BYTES}")
        problems += _gltf_problems(glb)
        try:
            scene = trimesh.load_scene(io.BytesIO(glb), file_type="glb")
            triangles = sum(
                len(g.faces) for g in scene.geometry.values() if isinstance(g, trimesh.Trimesh)
            )
            bounds = None if scene.bounds is None else np.asarray(scene.bounds, dtype=float)
        except Exception:  # An unreadable file is one fault, whatever the reader raised.
            triangles, bounds = 0, None
        if bounds is None or not triangles:
            problems.append("file has no readable triangle geometry")
        else:
            box = asset.bbox_m
            expected = [
                [-box.width / 2, 0, -box.depth / 2],
                [box.width / 2, box.height, box.depth / 2],
            ]
            error = float(np.abs(bounds - expected).max())
            measured |= {"triangles": triangles, "bounds_error_m": error}
            if triangles > MAX_TRIANGLES:
                problems.append(f"has {triangles} triangles; the limit is {MAX_TRIANGLES}")
            if not error < GLB_BBOX_TOLERANCE_M:  # Also catches NaN.
                problems.append(
                    f"bounds differ from bbox_m by {error:.4f} m "
                    f"(tolerance {GLB_BBOX_TOLERANCE_M} m, bottom-centre at the origin)"
                )
    return AssetCheck(
        object_id=asset.id,
        delivered="proxy" if asset.is_proxy else "mesh",
        glb_url=asset.glb_url,
        bbox_m=asset.bbox_m,
        dimension_source=asset.dimension_source,
        correction_needed=list(asset.correction_needed),
        problems=problems,
        **measured,
    )


def deliver_furniture(
    scene_id: str,
    *,
    data_dir: Path,
    dimensions: Mapping[str, KnownDimensions] | None = None,
    object_ids: Sequence[str] | None = None,
    url_base: str = ASSET_URL_BASE,
) -> Delivery:
    """A scene's furniture for Dev 1 to place: per item, its checked mesh or its labelled proxy.

    Batch preparation only: persist the CLI output and load assets.json during scene
    assembly. This function re-normalises and inspects meshes on every call.

    Offline. An item whose mesh is missing, could not be normalised or fails `inspect_asset`
    is delivered as its proxy, with the reason on its check and in `warnings`; a mesh is never
    delivered with a known fault. A proxy is delivered even when it has problems (the item is
    not dropped), and then `ok` is false. Unknown scenes and items raise ValueError.
    """
    result = reconstruct_furniture(
        scene_id, data_dir=data_dir, dimensions=dimensions, object_ids=object_ids, url_base=url_base
    )
    warnings = list(result.warnings)
    assets: list[FurnitureAsset] = []
    checks: list[AssetCheck] = []
    for item in result.items:
        reason: str | None = None
        if item.asset is not None:
            check = inspect_asset(item.asset, data_dir=data_dir, url_base=url_base)
            if not check.problems and not item.asset.is_proxy:
                assets.append(item.asset)
                checks.append(check)
                continue
            reason = f"mesh failed its checks: {'; '.join(check.problems) or 'marked as a proxy'}"
            warnings.append(f"{item.object_id}: {reason}; the proxy is delivered")
        elif item.mesh is not None:
            reason = "mesh could not be normalised"
        elif item.failure is not None:
            reason = f"no mesh ({item.failure.kind}): {item.failure.reason}"
        check = inspect_asset(item.proxy, data_dir=data_dir, url_base=url_base)
        if not item.proxy.is_proxy:
            check.problems.append("fallback asset is not marked is_proxy")
        check.delivered, check.fallback_reason = "proxy", reason
        assets.append(item.proxy)
        checks.append(check)
    repeated = sorted(key for key, count in Counter(a.id for a in assets).items() if count > 1)
    return Delivery(
        scene_id=scene_id,
        registry_revision=result.registry_revision,
        assets=assets,
        checks=checks,
        warnings=warnings,
        problems=[f"duplicate item ID: {key}" for key in repeated],
    )


def check_placed(scene: RoomScene, assets: Sequence[FurnitureAsset]) -> list[str]:
    """Faults in how a scene carries delivered assets; empty when every asset appears exactly
    once with its ID, bounds, mesh and every other field unchanged. Placement adds the `pose`
    and may add to `correction_needed`, never remove from it."""
    problems: list[str] = []
    for asset in assets:
        placed = [item for item in scene.furniture if item.id == asset.id]
        if len(placed) != 1:
            problems.append(f"{asset.id}: in the scene {len(placed)} times, expected once")
            continue
        got = placed[0].model_dump(exclude={"pose"})
        want = asset.model_dump(exclude={"evidence"})
        changed = sorted(
            key for key in want if key != "correction_needed" and got[key] != want[key]
        )
        if not set(want["correction_needed"]) <= set(got["correction_needed"]):
            changed.append("correction_needed")
        if changed:
            problems.append(f"{asset.id}: changed by placement: {', '.join(changed)}")
    return problems
