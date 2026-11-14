"""Frame discovery -> permanent scene IDs. Masks are segmentation.py (#15); no meshes/poses."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from .models import AssetEvidence, EvidenceFrame
from .providers import DiscoveryError, DiscoveryProvider, OfflineProvider, RequestBudget
from .registry import Registry
from .selection_models import (
    Box,
    DiscoveredObject,
    Discovery,
    Frame,
    RegistryState,
    SegmentationResult,
    SelectedObject,
    SelectionOptions,
    SelectionResult,
    Sighting,
    SourceVideo,
)
from .video import crop, image_quality, read_image, sample_video


def overlap(a: Box, b: Box) -> float:
    intersection = max(0, min(a.x + a.width, b.x + b.width) - max(a.x, b.x)) * max(
        0, min(a.y + a.height, b.y + b.height) - max(a.y, b.y)
    )
    return intersection / (a.width * a.height + b.width * b.height - intersection)


def _select_views(obj: SelectedObject) -> None:
    # Coverage already comes from per-object discovery. Prefer large, sharp, uncut views.
    ranked = sorted(obj.sightings, key=lambda s: (-s.quality, s.frame_key))
    chosen: list[Sighting] = []
    for sighting in ranked:
        # Avoid adjacent near-identical framing; these are alternate views, not proven angles.
        if any(
            s.frame_key.rsplit(":", 1)[0] == sighting.frame_key.rsplit(":", 1)[0]
            and overlap(s.box, sighting.box) > 0.95
            for s in chosen
        ):
            continue
        chosen.append(sighting)
        if len(chosen) == 4:
            break
    obj.selected_views = [s.frame_key for s in chosen]


def _diagnostic(messages: dict[str, list[str]], track: DiscoveredObject, message: str) -> None:
    for sighting in track.sightings:
        messages.setdefault(sighting.frame_key, []).append(message)


def reconcile(
    state: RegistryState, discovery: Discovery, frames: dict[str, Frame], room_key: str | None
) -> None:
    """Conservative exact-evidence/reference matching; deliberately no custom assignment solver."""
    # A successful reprocessing replaces diagnostics only for that batch's source frames.
    # Other frames retain their issues until they are themselves reviewed again.
    for key in frames:
        state.unresolved_by_frame.pop(key, None)
        state.warnings_by_frame.pop(key, None)
    # Sorting makes first allocation independent of a provider's object ordering.
    tracks = sorted(
        discovery.objects,
        key=lambda obj: (
            min((s.frame_key, s.box.x, s.box.y) for s in obj.sightings),
            obj.name,
        ),
    )
    used: set[str] = set()
    for track in tracks:
        if track.reflection:
            _diagnostic(state.warnings_by_frame, track, f"reflection excluded: {track.name}")
            continue
        candidates: set[str] = set()
        for existing in state.objects.values():
            if any(
                a.frame_key == b.frame_key and overlap(a.box, b.box) >= 0.7
                for a in existing.sightings
                for b in track.sightings
            ):
                candidates.add(existing.id)
        if track.reference_id:
            reference = state.objects.get(track.reference_id)
            if reference is None:
                raise ValueError("provider suggested an unknown reference ID")
            sources = {state.frames[s.frame_key].source_id for s in reference.sightings}
            same_source = all(frames[s.frame_key].source_id in sources for s in track.sightings)
            same_room = room_key is not None and reference.room_key == room_key
            if same_source or same_room:
                candidates.add(reference.id)
            else:
                _diagnostic(
                    state.unresolved_by_frame,
                    track,
                    f"cross-video identity ungrounded: {track.name}",
                )
        identity = next(iter(candidates)) if len(candidates) == 1 else None
        if len(candidates) > 1 or track.uncertain:
            _diagnostic(state.unresolved_by_frame, track, f"identity needs review: {track.name}")
            # An uncertain cached observation must not allocate another object on each rerun.
            if len(candidates) > 1:
                continue
            if track.uncertain and not any(
                a.frame_key == b.frame_key and overlap(a.box, b.box) >= 0.7
                for candidate in candidates
                for a in state.objects[candidate].sightings
                for b in track.sightings
            ):
                identity = None
        if identity:
            existing = state.objects[identity]
            conflicting = any(
                a.frame_key == b.frame_key and overlap(a.box, b.box) < 0.7
                for a in existing.sightings
                for b in track.sightings
            )
            if identity in used and not conflicting:
                _diagnostic(
                    state.unresolved_by_frame,
                    track,
                    f"duplicate detection needs review: {track.name}",
                )
                continue
            if conflicting:
                _diagnostic(
                    state.unresolved_by_frame,
                    track,
                    f"co-visible objects cannot share ID: {track.name}",
                )
                identity = None
        if identity is None:
            identity = f"vid-{state.next_id:06d}"
            if identity in state.objects:
                raise ValueError("registry allocator conflicts with an existing ID")
            state.next_id += 1
            state.objects[identity] = SelectedObject(
                id=identity,
                name=track.name,
                category=track.category,
                appearance=track.appearance,
                room_key=room_key,
                sightings=track.sightings,
            )
        else:
            existing = state.objects[identity]
            sightings = {s.frame_key: s for s in existing.sightings}
            sightings.update({s.frame_key: s for s in track.sightings})
            existing.sightings = sorted(sightings.values(), key=lambda s: s.frame_key)
            if existing.category != track.category:
                _diagnostic(
                    state.unresolved_by_frame,
                    track,
                    f"metadata category conflict for {identity}: kept {existing.category}, "
                    f"proposed {track.category}",
                )
            elif existing.name != track.name or existing.appearance != track.appearance:
                _diagnostic(
                    state.warnings_by_frame,
                    track,
                    f"metadata suggestion ignored for established item {identity}",
                )
        used.add(identity)
        _select_views(state.objects[identity])
    state.unresolved = sorted(
        {message for issues in state.unresolved_by_frame.values() for message in issues}
    )


def _score_sightings(discovery: Discovery, frames: dict[str, Frame], data_dir: Path) -> None:
    images = {key: read_image(data_dir, frame) for key, frame in frames.items()}
    for obj in discovery.objects:
        for sighting in obj.sightings:
            box = sighting.box
            sharp = image_quality(crop(images[sighting.frame_key], box))
            area = min(1, box.width * box.height * 4)
            clipped = min(box.x, box.y, 1 - box.x - box.width, 1 - box.y - box.height) < 0.01
            sighting.quality = max(0, min(1, 0.6 * sharp + 0.4 * area - 0.15 * clipped))


def select_furniture_frames(
    video_paths: Sequence[Path],
    scene_id: str,
    *,
    data_dir: Path,
    provider: DiscoveryProvider | None = None,
    options: SelectionOptions | None = None,
) -> SelectionResult:
    """Select and persist source views; this is not the later extract_furniture façade.

    No network calls unless a provider is explicitly passed. Missing/failed discovery keeps
    previous identities and returns complete=False. Invalid media/registry raises ValueError
    or the underlying storage error; this internal API does not pretend invalid input worked.
    """
    if not scene_id.strip() or len(scene_id) > 200:
        raise ValueError("scene_id must contain 1..200 non-blank characters")
    if not 1 <= len(video_paths) <= 5:
        raise ValueError("provide between one and five videos")
    options = options or SelectionOptions()
    provider = provider or OfflineProvider()
    data_dir = data_dir.resolve()
    registry = Registry(data_dir, namespace=scene_id)
    sources: list[SourceVideo] = []
    frames: list[Frame] = []
    warnings: list[str] = []
    for path in video_paths:
        source, sampled, notes = sample_video(path, data_dir, options)
        if source.source_id in {s.source_id for s in sources}:
            continue
        sources.append(source)
        frames.extend(sampled)
        warnings.extend(notes)
    frames.sort(key=lambda f: (f.source_id, f.timestamp_s, f.frame_index))
    if len(sources) > 1 and options.room_key is None:
        warnings.append("cross-video identity unverified: supply a caller-confirmed room_key")

    def add_sources(state: RegistryState) -> None:
        state.sources.update({source.source_id: source for source in sources})
        state.frames.update({frame.key: frame for frame in frames})

    registry.update(scene_id, add_sources)
    complete = not warnings
    budget = RequestBudget(options.max_requests)
    batches: list[list[Frame]] = []
    for source in sources:
        group = [frame for frame in frames if frame.source_id == source.source_id]
        batches.extend(
            group[i : i + options.batch_size] for i in range(0, len(group), options.batch_size)
        )
    for batch_index, batch in enumerate(batches):
        before = registry.load(scene_id)
        # References are same-source unless a caller has confirmed the same physical room.
        source_ids = {f.source_id for f in batch}
        references = [
            obj
            for obj in before.objects.values()
            if (
                any(before.frames[s.frame_key].source_id in source_ids for s in obj.sightings)
                or (options.room_key is not None and obj.room_key == options.room_key)
            )
        ]
        try:
            discovery = provider.discover(
                batch,
                references,
                before.frames,
                data_dir,
                registry,
                budget=budget,
            )
            discovery.validate_frames({frame.key for frame in batch})
            _score_sightings(discovery, {frame.key: frame for frame in batch}, data_dir)
            registry.update(
                scene_id,
                lambda state: reconcile(
                    state, discovery, {frame.key: frame for frame in batch}, options.room_key
                ),
            )
            warnings.extend(discovery.warnings)
            if discovery.warnings:
                complete = False
        except (DiscoveryError, ValueError) as exc:
            warnings.append(f"batch {batch_index + 1}: {exc}")
            complete = False
    state = registry.load(scene_id)
    warnings.extend(message for notes in state.warnings_by_frame.values() for message in notes)
    geometry: list[str] = []
    for source in sources:
        keys = [frame.key for frame in frames if frame.source_id == source.source_id]
        geometry.extend(keys[:: max(1, (len(keys) + 23) // 24)])
    return SelectionResult(
        scene_id=scene_id,
        registry_revision=state.revision,
        sources=list(state.sources.values()),
        frames=list(state.frames.values()),
        objects=sorted(state.objects.values(), key=lambda obj: obj.id),
        geometry_frame_keys=geometry,
        unresolved=state.unresolved,
        warnings=sorted(set(warnings)),
        complete=complete and not state.unresolved,
    )


def object_evidence(
    result: SelectionResult | SegmentationResult, object_id: str, *, source_id: str | None = None
) -> AssetEvidence:
    """Adapt one source to the fixed evidence shape without inventing global frame indices.

    Full multi-source identity/images remain in the result. A sighting with a current #15 mask
    carries `mask_url` (relative to the data directory; read with `segmentation.read_mask`)
    and the mask's tight box; the others keep their coarse sighting box. provider_pose remains
    reserved for raw SAM 3D metadata.
    """
    obj = next((obj for obj in result.objects if obj.id == object_id), None)
    if obj is None:
        raise ValueError("unknown object ID")
    frames = {frame.key: frame for frame in result.frames}
    sources = {frames[s.frame_key].source_id for s in obj.sightings}
    if source_id is None:
        if len(sources) != 1:
            raise ValueError("choose one source_id for the fixed single-video evidence shape")
        source_id = next(iter(sources))
    sightings = [s for s in obj.sightings if frames[s.frame_key].source_id == source_id]
    if not sightings:
        raise ValueError("object has no sightings in the requested source")
    primary = max(sightings, key=lambda s: s.quality)
    evidence = []
    for sighting in sightings:
        frame = frames[sighting.frame_key]
        w, h = frame.image_size_px
        b = sighting.box
        mask = obj.mask_for(sighting.frame_key)
        evidence.append(
            EvidenceFrame(
                frame_index=frame.frame_index,
                timestamp_s=frame.timestamp_s,
                image_size_px=(w, h),
                mask_url=mask.mask_path if mask else None,
                bbox_px=mask.bbox_px if mask else (b.x * w, b.y * h, b.width * w, b.height * h),
            )
        )
    return AssetEvidence(frames=evidence, primary_frame_index=frames[primary.frame_key].frame_index)
