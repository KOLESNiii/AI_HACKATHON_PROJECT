"""Masked views -> one stored raw mesh per item, or an explicit failure, and always a proxy (#16).

Raw meshes are in the provider's frame and scale and are never served. Each current one is
normalised to the furniture profile (#17) into the item's servable `asset`.
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping, Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

from .asset_store import ASSET_URL_BASE, write_atomic
from .mesh_providers import MeshError, MeshProvider, RawMesh, inspect_mesh
from .models import FurnitureAsset
from .normalisation import PROVIDER_FRONT, NormalisationError, normalise_mesh
from .providers import RequestBudget
from .proxies import KnownDimensions, proxy_asset
from .registry import Registry
from .segmentation import read_mask
from .selection import evidence_for
from .selection_models import (
    Frame,
    ItemReconstruction,
    MaskRecord,
    MeshFailure,
    MeshRecord,
    ReconstructionResult,
    RegistryState,
    SelectedObject,
)
from .video import read_image

UNCLIPPED_AREA_SHARE = 0.5
"""A view that the frame edge does not cut is preferred while it has at least this share of
the largest usable mask's area: a whole small view beats a slightly larger truncated one."""


def _clipped(mask: MaskRecord, frame: Frame) -> bool:
    x, y, w, h = mask.bbox_px
    width, height = frame.image_size_px
    return x <= 0 or y <= 0 or x + w >= width or y + h >= height


def choose_view(
    obj: SelectedObject, frames: Mapping[str, Frame], data_dir: Path
) -> MaskRecord | None:
    """The one masked view to reconstruct from: confident, then whole, then large."""
    masks = [
        mask
        for key in obj.selected_views
        if (mask := obj.mask_for(key)) is not None and (data_dir / mask.mask_path).is_file()
    ]
    masks = [m for m in masks if not m.low_confidence] or masks
    if not masks:
        return None
    largest = max(masks, key=lambda m: (m.area_px, m.frame_key))
    whole = [
        m
        for m in masks
        if not _clipped(m, frames[m.frame_key])
        and m.area_px >= UNCLIPPED_AREA_SHARE * largest.area_px
    ]
    return max(whole, key=lambda m: (m.area_px, m.frame_key)) if whole else largest


@dataclass(frozen=True)
class _Job:
    object_id: str
    frame: Frame
    mask: MaskRecord


def reconstruct_furniture(
    scene_id: str,
    *,
    data_dir: Path,
    provider: MeshProvider | None = None,
    object_ids: Sequence[str] | None = None,
    dimensions: Mapping[str, KnownDimensions] | None = None,
    replace: bool = False,
    max_requests: int = 8,
    concurrency: int = 4,
    url_base: str = ASSET_URL_BASE,
) -> ReconstructionResult:
    """Give every (or each named) item of the scene its own raw mesh, and always a proxy.

    Offline unless a live provider is passed: without one every item without a stored mesh is
    reported as `not_attempted`. A stored mesh is reused unless `replace`, its mask was
    replaced or its file is gone. A provider failure, a timeout or an unusable mesh is reported
    on the item as a `failure`; it never raises, never removes an item and never discards a
    stored mesh. Every item carries a labelled proxy sized from `dimensions[id]` when given,
    otherwise from a category default marked as an estimate needing correction. Every current
    mesh is also normalised into `asset` (fitted to `dimensions[id]`, else an estimated size);
    one that cannot be is reported in `warnings` and keeps only its proxy.
    `replace` rebuilds from the current mask but reuses the paid provider result unless
    the provider is configured with a fresh `refresh` namespace.
    Unknown scenes/items raise ValueError.
    """
    if not scene_id.strip() or len(scene_id) > 200:
        raise ValueError("scene_id must contain 1..200 non-blank characters")
    if max_requests < 0:
        raise ValueError("max_requests must be non-negative")
    if concurrency < 1:
        raise ValueError("concurrency must be at least 1")
    data_dir = data_dir.resolve()
    if not (data_dir / "registry.sqlite3").is_file():  # Never create one in a mistyped folder.
        raise ValueError("no furniture registry in the data directory; run frame selection first")
    registry = Registry(data_dir, namespace=scene_id)
    state = registry.load(scene_id)
    if not state.objects:
        raise ValueError("scene has no selected furniture; run frame selection first")
    wanted = sorted(state.objects) if object_ids is None else sorted(set(object_ids))
    known = dict(dimensions or {})
    if (set(wanted) | known.keys()) - state.objects.keys():
        raise ValueError("unknown object ID")
    folder = f"meshes/{hashlib.sha256(scene_id.encode()).hexdigest()[:16]}"
    failures: dict[str, MeshFailure] = {}
    warnings: list[str] = []
    jobs: list[_Job] = []
    for object_id in wanted:
        obj = state.objects[object_id]
        stored = obj.current_mesh()
        if not replace and stored is not None and (data_dir / stored.mesh_path).is_file():
            continue
        view = choose_view(obj, state.frames, data_dir)
        if view is None:
            failures[object_id] = MeshFailure(
                kind="no_view", reason="no stored mask for a selected view; run segmentation first"
            )
        elif provider is None:
            failures[object_id] = MeshFailure(
                kind="not_attempted", reason="offline run: no mesh provider was requested"
            )
        else:
            frame = state.frames[view.frame_key]
            where = f"{object_id} from source {frame.source_id[:12]} frame {frame.frame_index}"
            if view.low_confidence:
                warnings.append(f"reconstructing {where} with a low-confidence mask")
            if _clipped(view, frame):
                warnings.append(
                    f"reconstructing {where}, which the frame edge cuts; the mesh may be truncated"
                )
            jobs.append(_Job(object_id, frame, view))

    budget = RequestBudget(max_requests)

    def attempt(job: _Job) -> tuple[RawMesh, int, tuple[float, float, float]] | MeshFailure:
        assert provider is not None
        try:
            image = read_image(data_dir, job.frame)
            mask = read_mask(data_dir, job.mask.mask_path)
        except ValueError:
            return MeshFailure(kind="no_view", reason="source frame or mask artifact unavailable")
        try:
            raw = provider.reconstruct(job.frame, image, mask, registry, budget=budget)
            return raw, *inspect_mesh(raw.glb)
        except MeshError as exc:
            return MeshFailure(kind=exc.kind, reason=str(exc))
        except Exception as exc:
            # The boundary promise: a provider failure never raises past here or drops an item.
            return MeshFailure(kind="provider", reason=f"provider error ({type(exc).__name__})")

    outcomes: list[tuple[RawMesh, int, tuple[float, float, float]] | MeshFailure] = []
    if jobs:
        # Providers take minutes per item (170 s observed), so items run side by side.
        with ThreadPoolExecutor(max_workers=min(concurrency, len(jobs))) as pool:
            outcomes = list(pool.map(attempt, jobs))

    for job, outcome in zip(jobs, outcomes, strict=True):
        if isinstance(outcome, MeshFailure):
            failures[job.object_id] = outcome
            continue
        raw, triangles, extents = outcome
        assert provider is not None
        record = MeshRecord.model_validate(
            {
                "frame_key": job.frame.key,
                "mask_path": job.mask.mask_path,
                "provider": provider.name,
                "mesh_path": f"{folder}/{job.object_id}/"
                f"{hashlib.sha256(raw.glb).hexdigest()[:16]}.raw.glb",
                "size_bytes": len(raw.glb),
                "triangles": triangles,
                "extents": extents,
                "pose": raw.pose,
            }
        )
        write_atomic(data_dir / record.mesh_path, raw.glb)
        superseded: list[MeshRecord] = []
        attached: list[bool] = []

        def attach(
            state: RegistryState,
            job: _Job = job,
            record: MeshRecord = record,
            superseded: list[MeshRecord] = superseded,
            attached: list[bool] = attached,
        ) -> None:
            # Segmentation may have run meanwhile: attach only while that mask is still current.
            current = state.objects.get(job.object_id)
            mask = None if current is None else current.mask_for(job.frame.key)
            if current is None or mask is None or mask.mask_path != record.mask_path:
                return
            if current.mesh is not None:
                superseded.append(current.mesh)
            current.mesh = record
            attached.append(True)

        after = registry.update(scene_id, attach)
        if not attached:
            failures[job.object_id] = MeshFailure(
                kind="no_view", reason="masks changed during reconstruction; run again"
            )
        kept = {obj.mesh.mesh_path for obj in after.objects.values() if obj.mesh is not None}
        for reference in {record.mesh_path, *(old.mesh_path for old in superseded)} - kept:
            path = (data_dir / reference).resolve()
            # Delete only generated files, after their replacement is committed.
            if path.is_relative_to(data_dir / folder):
                try:
                    path.unlink(missing_ok=True)
                except OSError:
                    warnings.append("could not remove a superseded mesh artifact")

    state = registry.load(scene_id)
    items = []
    for object_id in wanted:
        obj = state.objects[object_id]
        mesh = obj.current_mesh()
        if mesh is not None and not (data_dir / mesh.mesh_path).is_file():
            mesh = None
        failure = failures.get(object_id)
        if mesh is None and failure is None:
            failure = MeshFailure(kind="no_view", reason="stored mesh is not current; run again")
        if mesh is not None and failure is not None:
            warnings.append(
                f"{object_id}: replacement failed ({failure.kind}); the stored mesh is kept"
            )
        # The fixed evidence shape holds one source: the mesh's, else the item's best view's.
        best = mesh.frame_key if mesh else (obj.selected_views or [obj.sightings[0].frame_key])[0]
        evidence = evidence_for(obj, state.frames, source_id=state.frames[best].source_id)
        size = known.get(object_id)
        proxy = proxy_asset(
            obj.id,
            obj.name,
            obj.category,
            evidence,
            data_dir=data_dir,
            known=size,
            url_base=url_base,
        )
        asset = None
        if mesh is not None:
            try:
                fitted = normalise_mesh(
                    data_dir / mesh.mesh_path,
                    category=obj.category,
                    target_bbox=None if size is None else size.bbox_m,
                    data_dir=data_dir,
                    front=PROVIDER_FRONT.get(mesh.provider),
                    preserve_scale=mesh.provider == "retailer",
                    url_base=url_base,
                )
                # Only stated dimensions are trusted: a size read off the mesh is an estimate.
                asset = FurnitureAsset.model_validate(
                    {
                        **proxy.model_dump(),
                        **fitted.model_dump(),
                        "is_proxy": False,
                        "dimension_source": "estimated" if size is None else size.source,
                    }
                )
            except NormalisationError as exc:
                warnings.append(f"{object_id}: mesh not normalised ({exc}); the proxy is served")
        items.append(
            ItemReconstruction(
                object_id=object_id, mesh=mesh, failure=failure, proxy=proxy, asset=asset
            )
        )
    return ReconstructionResult(
        scene_id=scene_id,
        registry_revision=state.revision,
        items=items,
        warnings=warnings,
        complete=all(item.failure is None and item.asset is not None for item in items),
    )
