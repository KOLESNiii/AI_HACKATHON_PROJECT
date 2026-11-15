from __future__ import annotations

import json
import shutil
import sqlite3
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import Mock

import cv2
import fal_client
import numpy as np
import pytest
from pydantic import ValidationError

from services.reconstruction.assets.providers import (
    DiscoveryError,
    FalVisionProvider,
    RecordedProvider,
    RequestBudget,
    parse_discovery,
)
from services.reconstruction.assets.registry import Registry
from services.reconstruction.assets.select_frames import main, write_report
from services.reconstruction.assets.selection import (
    discover_frames,
    object_evidence,
    reconcile,
    sample_sources,
    select_furniture_frames,
)
from services.reconstruction.assets.selection_models import (
    Box,
    DiscoveredObject,
    Discovery,
    Frame,
    RegistryState,
    SelectedObject,
    SelectionOptions,
    Sighting,
)
from services.reconstruction.assets.video import read_image, sample_video


@pytest.fixture
def media_tools() -> None:
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        pytest.skip("video integration tests require FFmpeg and FFprobe on PATH")


@pytest.fixture
def video(tmp_path: Path, media_tools: None) -> Path:
    path = tmp_path / "vfr.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-nostdin",
            "-v",
            "error",
            "-f",
            "lavfi",
            "-i",
            "testsrc2=size=160x96:rate=10:duration=0.6",
            "-vf",
            "setpts=N*N/(10*TB)",
            "-fps_mode",
            "vfr",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            str(path),
        ],
        check=True,
    )
    return path


def frame(index: int, *, source: str = "a" * 64) -> Frame:
    return Frame(
        key=f"{source}:0:{index}",
        source_id=source,
        frame_index=index,
        pts=index * 100,
        timestamp_s=float(index),
        image_size_px=(160, 96),
        image_path=f"{index}.png",
        quality=0.8,
    )


def track(frames: list[Frame], x: float, **kwargs: object) -> DiscoveredObject:
    data = {
        "name": "Brown sofa",
        "category": "sofa",
        "appearance": "brown two-seat sofa",
        "sightings": [
            Sighting(frame_key=f.key, box=Box(x=x, y=0.3, width=0.25, height=0.4), quality=0.8)
            for f in frames
        ],
        **kwargs,
    }
    return DiscoveredObject.model_validate(data)


def test_rotation_vfr_and_timestamp_provenance(video: Path, tmp_path: Path) -> None:
    rotated = tmp_path / "rotated.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-nostdin",
            "-v",
            "error",
            "-display_rotation:v:0",
            "90",
            "-i",
            str(video),
            "-c",
            "copy",
            str(rotated),
        ],
        check=True,
    )
    options = SelectionOptions(sample_interval_s=0.25, max_frames_per_video=24)
    source, frames, warnings = sample_video(rotated, tmp_path / "data", options)
    assert not warnings
    assert source.encoded_size == (160, 96) and source.upright_size == (96, 160)
    assert source.rotation_deg == 90
    assert len(frames) >= 3
    times = [f.timestamp_s for f in frames]
    assert times == sorted(set(times))
    assert any(abs(f.timestamp_s - f.frame_index / 10) > 0.15 for f in frames)
    for f in frames:
        assert float(f.pts * __import__("fractions").Fraction(source.time_base)) == f.timestamp_s
        assert read_image(tmp_path / "data", f).shape == (160, 96, 3)
    # Verify the recorded transform against FFmpeg's actual decoded pixel orientation.
    original_source, originals, _ = sample_video(video, tmp_path / "data", options)
    chosen = frames[0]
    original = next(f for f in originals if f.frame_index == chosen.frame_index)
    expected = cv2.rotate(read_image(tmp_path / "data", original), cv2.ROTATE_90_COUNTERCLOCKWISE)
    assert np.array_equal(expected, read_image(tmp_path / "data", chosen))
    transform = np.array(source.encoded_to_upright)
    assert np.array_equal(transform @ [10, 20, 1], [20, 149, 1])
    assert source.source_id != original_source.source_id


def test_sampling_cap_and_invalid_input(video: Path, tmp_path: Path) -> None:
    _, frames, warnings = sample_video(
        video, tmp_path / "data", SelectionOptions(max_frames_per_video=1)
    )
    assert len(frames) == 1 and "coverage incomplete" in warnings[0]
    with pytest.raises(ValueError, match="no decoded"):
        sample_video(video, tmp_path / "data", SelectionOptions(start_s=100))
    with pytest.raises(ValueError, match="one and five"):
        select_furniture_frames([], "test", data_dir=tmp_path)
    with pytest.raises(ValidationError):
        SelectionOptions(start_s=5, end_s=4)


@pytest.mark.parametrize(
    "box",
    [
        {"x": 0.9, "y": 0, "width": 0.2, "height": 0.2},
        {"x": float("nan"), "y": 0, "width": 0.2, "height": 0.2},
        {"x": 0, "y": 0, "width": 0, "height": 0.2},
    ],
)
def test_boxes_validate_external_coordinates(box: dict[str, float]) -> None:
    with pytest.raises(ValidationError):
        Box.model_validate(box)


def test_distinct_sofas_rerun_order_category_and_co_visibility() -> None:
    frames = [frame(0), frame(30)]
    state = RegistryState(frames={f.key: f for f in frames})
    objects = [track(frames, 0.05), track(frames, 0.65)]
    reconcile(state, Discovery(objects=objects), state.frames, None)
    original = {obj.sightings[0].box.x: obj.id for obj in state.objects.values()}
    assert len(original) == 2 and state.unresolved == []
    objects[0].category = "chair"  # IDs do not encode or depend on category.
    reconcile(state, Discovery(objects=objects[::-1]), state.frames, None)
    assert {obj.sightings[0].box.x: obj.id for obj in state.objects.values()} == original
    assert state.objects[original[0.05]].category == "sofa"
    assert any("metadata category conflict" in issue for issue in state.unresolved)
    assert all(len(obj.sightings) == 2 and obj.selected_views for obj in state.objects.values())
    new_frame = frame(60)
    state.frames[new_frame.key] = new_frame
    # Two co-visible tracks cannot be assigned to one old ID, even if the provider asks.
    reconcile(
        state,
        Discovery(
            objects=[
                track([new_frame], 0.05, reference_id=original[0.05]),
                track([new_frame], 0.65, reference_id=original[0.05]),
            ]
        ),
        state.frames,
        None,
    )
    assert len(state.objects) == 3
    assert any("co-visible" in issue for issue in state.unresolved)


def test_cross_video_requires_grounded_room_and_uncertain_reruns_are_stable() -> None:
    a, b = frame(0), frame(0, source="b" * 64)
    state = RegistryState(frames={a.key: a, b.key: b})
    reconcile(state, Discovery(objects=[track([a], 0.1)]), state.frames, "floor1-room2")
    identity = next(iter(state.objects))
    reconcile(
        state, Discovery(objects=[track([b], 0.1, reference_id=identity)]), state.frames, None
    )
    assert len(state.objects) == 2 and state.unresolved
    separate = RegistryState(frames=state.frames)
    reconcile(separate, Discovery(objects=[track([a], 0.1)]), state.frames, "floor1-room2")
    reconcile(
        separate,
        Discovery(objects=[track([b], 0.1, reference_id=identity)]),
        state.frames,
        "floor1-room2",
    )
    assert len(separate.objects) == 1
    uncertain = Discovery(objects=[track([a], 0.1, uncertain=True)])
    reconcile(separate, uncertain, state.frames, "floor1-room2")
    reconcile(separate, uncertain, state.frames, "floor1-room2")
    assert len(separate.objects) == 1 and separate.unresolved


def test_reflections_are_reported_not_physical_items() -> None:
    f = frame(0)
    state = RegistryState(frames={f.key: f})
    reconcile(state, Discovery(objects=[track([f], 0.1, reflection=True)]), state.frames, None)
    assert not state.objects and not state.unresolved
    assert "reflection excluded" in state.warnings_by_frame[f.key][0]


def test_registry_rollback_concurrency_corruption_and_request_scopes(tmp_path: Path) -> None:
    registry = Registry(tmp_path)

    def increment(_: int) -> None:
        registry.update("scene", lambda state: setattr(state, "next_id", state.next_id + 1))

    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(increment, range(12)))
    assert registry.load("scene").next_id == 13

    def fail(state: RegistryState) -> None:
        state.next_id = 100
        raise RuntimeError("interrupted")

    with pytest.raises(RuntimeError):
        registry.update("scene", fail)
    assert Registry(tmp_path).load("scene").next_id == 13
    assert Registry(tmp_path, namespace="one").reserve_request("key")[0]
    assert not Registry(tmp_path, namespace="one").reserve_request("key")[0]
    assert Registry(tmp_path, namespace="two").reserve_request("key")[0]
    with sqlite3.connect(registry.path) as con:
        con.execute("UPDATE scenes SET payload='not json'")
    with pytest.raises(ValidationError):
        registry.load("scene")
    with sqlite3.connect(registry.path) as con:
        con.execute("PRAGMA user_version=2")
    with pytest.raises(ValueError, match="unsupported registry"):
        Registry(tmp_path)


def test_provider_output_validation_and_reference_mapping() -> None:
    f = frame(0)
    obj = track([f], 0.1)
    reference = SelectedObject(
        id="vid-000001",
        **obj.model_dump(
            exclude={
                "reference_id",
                "uncertain",
                "reflection",
            }
        ),
    )
    raw = Discovery(objects=[obj]).model_dump()
    raw["objects"][0]["reference_id"] = "R0"
    raw["objects"][0]["sightings"][0]["frame_key"] = "F0"
    parsed = parse_discovery("```json\n" + json.dumps(raw) + "\n```", [f], [reference])
    assert parsed.objects[0].reference_id == reference.id
    assert parsed.objects[0].sightings[0].frame_key == f.key
    for bad in [
        "not json",
        '{"objects":[],"empty_frames":[]}',
        json.dumps(
            {
                **raw,
                "empty_frames": ["F0"],
            }
        ),
    ]:
        with pytest.raises(DiscoveryError):
            parse_discovery(bad, [f], [reference])
    raw["objects"][0]["sightings"].append(raw["objects"][0]["sightings"][0])
    with pytest.raises(DiscoveryError):
        parse_discovery(json.dumps(raw), [f], [reference])


def test_end_to_end_recorded_cli_and_offline_failure(video: Path, tmp_path: Path) -> None:
    data = tmp_path / "data"
    options = SelectionOptions(sample_interval_s=0.25, batch_size=1)
    offline = select_furniture_frames([video], "demo", data_dir=data, options=options)
    assert not offline.complete and offline.frames and not offline.objects
    discovery = Discovery(objects=[track(offline.frames, 0.05), track(offline.frames, 0.65)])
    provider = RecordedProvider(discovery)
    first = select_furniture_frames(
        [video], "demo", data_dir=data, options=options, provider=provider
    )
    assert first.complete and len(first.objects) == 2
    assert all(len(obj.sightings) == len(first.frames) for obj in first.objects)
    provider.discovery.objects.reverse()
    second = select_furniture_frames(
        [video], "demo", data_dir=data, options=options, provider=provider
    )
    assert [(obj.id, len(obj.sightings)) for obj in first.objects] == [
        (obj.id, len(obj.sightings)) for obj in second.objects
    ]
    failed = select_furniture_frames([video], "demo", data_dir=data, options=options)
    assert not failed.complete and len(failed.objects) == 2
    output = tmp_path / "report"
    write_report(second, data, output)
    assert len(list(output.glob("vid-*.jpg"))) == 2
    assert (output / "frames-00.jpg").exists()
    assert json.loads((output / "selection.json").read_text())["complete"]
    assert (
        main([str(video), "--scene-id", "offline", "--data-dir", str(data), "--out", str(output)])
        == 2
    )
    assert main([str(video), "--scene-id", "offline", "--out", str(output), "--end", "-1"]) == 1


def test_fal_cache_recovery_malformed_and_uncertain_submission(tmp_path: Path) -> None:
    f = frame(0)
    cv2.imwrite(str(tmp_path / f.image_path), np.zeros((96, 160, 3), np.uint8))
    provider = FalVisionProvider(key="test-never-sent")
    provider.client = Mock()
    handle = provider.client.submit.return_value
    handle.request_id = "request-one"
    handle.status.return_value = fal_client.Completed(metrics={}, logs=[])
    handle.get.return_value = {"output": json.dumps({"objects": [], "empty_frames": ["F0"]})}
    registry = Registry(tmp_path, namespace="scene")
    first = provider.discover([f], [], {f.key: f}, tmp_path, registry)
    second = provider.discover([f], [], {f.key: f}, tmp_path, registry)
    assert first == second and provider.client.submit.call_count == 1
    assert provider.client.upload.call_count == 1
    provider.refresh = "recover"
    handle.status.side_effect = RuntimeError("network interrupted")
    with pytest.raises(DiscoveryError, match="request state retained"):
        provider.discover([f], [], {f.key: f}, tmp_path, registry)
    handle.status.side_effect = None
    provider.client.get_handle.return_value = handle
    recovered = provider.discover([f], [], {f.key: f}, tmp_path, registry)
    assert recovered == first and provider.client.submit.call_count == 2
    provider.refresh = "malformed"
    handle.get.return_value = {"output": "secret response not echoed"}
    with pytest.raises(DiscoveryError, match="did not contain"):
        provider.discover([f], [], {f.key: f}, tmp_path, registry)
    with pytest.raises(DiscoveryError, match="previous request failed"):
        provider.discover([f], [], {f.key: f}, tmp_path, registry)
    provider.refresh = "uncertain"
    provider.client.submit.side_effect = RuntimeError("submit result lost")
    with pytest.raises(DiscoveryError, match="retained"):
        provider.discover([f], [], {f.key: f}, tmp_path, registry)
    submits = provider.client.submit.call_count
    with pytest.raises(DiscoveryError, match="duplicate charge"):
        provider.discover([f], [], {f.key: f}, tmp_path, registry)
    assert provider.client.submit.call_count == submits


def test_budget_retains_known_objects(video: Path, tmp_path: Path) -> None:
    provider = FalVisionProvider(key="test-never-sent")
    provider.client = Mock()
    result = select_furniture_frames(
        [video],
        "demo",
        data_dir=tmp_path / "data",
        provider=provider,
        options=SelectionOptions(
            max_requests=0,
        ),
    )
    assert not result.complete and result.frames and "budget exhausted" in result.warnings[0]
    provider.client.submit.assert_not_called()
    provider.client.upload.assert_not_called()


def test_reviewed_real_room_coverage_and_identity(tmp_path: Path, media_tools: None) -> None:
    root = Path(__file__).resolve().parents[3]
    video = root / "examples/three_floor_3.mp4"
    if not video.exists():
        pytest.skip("optional repository example video not available")
    discovery = Discovery.model_validate_json(
        (Path(__file__).parent / "fixtures/opening_room.reviewed.json").read_text()
    )
    provider = RecordedProvider(discovery)
    options = SelectionOptions(end_s=6, max_frames_per_video=8, batch_size=3)
    first = select_furniture_frames(
        [video], "reviewed-room", data_dir=tmp_path, provider=provider, options=options
    )
    assert first.complete and len(first.objects) == 4
    assert sorted(obj.category for obj in first.objects) == ["chair", "sofa", "sofa", "table"]
    assert {frame.frame_index for frame in first.frames} == {0, 30, 59, 105, 134, 150}
    assert sorted(len(obj.sightings) for obj in first.objects) == [3, 3, 4, 4]
    provider.discovery.objects.reverse()
    second = select_furniture_frames(
        [video], "reviewed-room", data_dir=tmp_path, provider=provider, options=options
    )
    assert first.objects == second.objects
    for obj in second.objects:
        evidence = object_evidence(second, obj.id)
        assert evidence.primary_frame_index in {f.frame_index for f in evidence.frames}
        assert all(
            f.bbox_px and f.mask_url is None and f.provider_pose is None for f in evidence.frames
        )
    write_report(second, tmp_path, tmp_path / "report")


def test_fixed_evidence_cannot_confuse_frame_zero_across_videos() -> None:
    from services.reconstruction.assets.selection_models import SelectionResult

    a, b = frame(0), frame(0, source="b" * 64)
    obj = SelectedObject(
        id="vid-000001",
        name="Sofa",
        category="sofa",
        appearance="brown",
        sightings=track([a, b], 0.1).sightings,
        selected_views=[a.key],
    )
    result = SelectionResult(
        scene_id="demo",
        registry_revision=1,
        sources=[],
        frames=[a, b],
        objects=[obj],
        geometry_frame_keys=[],
        unresolved=[],
        warnings=[],
        complete=True,
    )
    with pytest.raises(ValueError, match="source_id"):
        object_evidence(result, obj.id)
    assert object_evidence(result, obj.id, source_id=a.source_id).frames[0].frame_index == 0


def test_unknown_reference_rolls_back_and_duplicate_detections_do_not_multiply() -> None:
    f = frame(0)
    state = RegistryState(frames={f.key: f})
    duplicated = Discovery(objects=[track([f], 0.1), track([f], 0.1)])
    reconcile(state, duplicated, state.frames, None)
    reconcile(state, duplicated, state.frames, None)
    assert len(state.objects) == 1 and state.unresolved
    with pytest.raises(ValueError, match="unknown reference"):
        reconcile(
            state, Discovery(objects=[track([f], 0.6, reference_id="unknown")]), state.frames, None
        )


def test_multiple_sources_are_separate_without_room_confirmation(
    video: Path, tmp_path: Path
) -> None:
    second = tmp_path / "second.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-nostdin",
            "-v",
            "error",
            "-i",
            str(video),
            "-c",
            "copy",
            "-metadata",
            "title=second capture",
            str(second),
        ],
        check=True,
    )
    data = tmp_path / "data"
    options = SelectionOptions(max_frames_per_video=1)
    sampled = select_furniture_frames([video, second], "sample", data_dir=data, options=options)
    assert len(sampled.sources) == 2 and len(sampled.frames) == 2
    discovery = Discovery(objects=[track(sampled.frames, 0.1)])
    separate = select_furniture_frames(
        [video, second],
        "separate",
        data_dir=data,
        options=options,
        provider=RecordedProvider(discovery),
    )
    assert len(separate.objects) == 2 and not separate.complete
    confirmed = select_furniture_frames(
        [second, video],
        "confirmed",
        data_dir=data,
        options=options.model_copy(update={"room_key": "room-1"}),
        provider=RecordedProvider(discovery),
    )
    assert len(confirmed.objects) == 1
    assert len(confirmed.objects[0].sightings) == 2


def test_partial_results_are_not_accepted_and_timeout_resumes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import services.reconstruction.assets.providers as providers

    f = frame(0)
    cv2.imwrite(str(tmp_path / f.image_path), np.zeros((96, 160, 3), np.uint8))
    provider = FalVisionProvider(key="test-never-sent", timeout_s=1)
    provider.client = Mock()
    handle = provider.client.submit.return_value
    handle.request_id = "timeout-request"
    registry = Registry(tmp_path)
    monkeypatch.setattr(providers.time, "monotonic", Mock(side_effect=[0, 2]))
    with pytest.raises(DiscoveryError, match="deadline exceeded"):
        provider.discover([f], [], {f.key: f}, tmp_path, registry)
    handle.cancel.assert_not_called()
    monkeypatch.setattr(providers.time, "monotonic", lambda: 0)
    handle.status.return_value = fal_client.Completed(logs=[], metrics={})
    handle.get.return_value = {"output": '{"objects":[],"empty_frames":["F0"]}'}
    provider.client.get_handle.return_value = handle
    result = provider.discover([f], [], {f.key: f}, tmp_path, registry)
    assert result.warnings and "requires review" in result.warnings[0]
    assert provider.client.submit.call_count == 1
    provider.refresh = "partial"
    handle.get.return_value = {"partial": True, "output": '{"objects":[],"empty_frames":["F0"]}'}
    with pytest.raises(DiscoveryError, match="partial/failed"):
        provider.discover([f], [], {f.key: f}, tmp_path, registry)
    with pytest.raises(ValueError, match="FAL_KEY"):
        FalVisionProvider(key="")


@pytest.mark.parametrize("stage", ["read", "encode", "upload"])
def test_pre_submit_failure_can_retry_without_refresh(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    stage: str,
) -> None:
    import services.reconstruction.assets.providers as providers

    f = frame(0)
    cv2.imwrite(str(tmp_path / f.image_path), np.zeros((96, 160, 3), np.uint8))
    provider = FalVisionProvider(key="test-never-sent")
    provider.client = Mock()
    provider.client.upload = Mock(return_value="https://example.test/frame.jpg")
    handle = provider.client.submit.return_value
    handle.request_id = "retry-request"
    handle.status.return_value = fal_client.Completed(logs=[], metrics={})
    handle.get.return_value = {"output": '{"objects":[],"empty_frames":["F0"]}'}
    registry = Registry(tmp_path)
    with monkeypatch.context() as patch:
        if stage == "read":
            patch.setattr(providers, "read_image", Mock(side_effect=ValueError("missing image")))
        elif stage == "encode":
            patch.setattr(providers.cv2, "imencode", Mock(return_value=(False, None)))
        else:
            patch.setattr(
                provider.client, "upload", Mock(side_effect=RuntimeError("upload failed"))
            )
        with pytest.raises(DiscoveryError):
            provider.discover([f], [], {f.key: f}, tmp_path, registry)
        provider.client.submit.assert_not_called()
    # Same cache namespace, without --refresh, now submits exactly once.
    provider.discover([f], [], {f.key: f}, tmp_path, registry)
    provider.client.submit.assert_called_once()


def test_repeated_wait_timeouts_keep_one_live_handle(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import services.reconstruction.assets.providers as providers

    f = frame(0)
    cv2.imwrite(str(tmp_path / f.image_path), np.zeros((96, 160, 3), np.uint8))
    provider = FalVisionProvider(key="test-never-sent", timeout_s=1)
    provider.client = Mock()
    handle = provider.client.submit.return_value
    handle.request_id = "still-running"
    handle.status.return_value = fal_client.InProgress(logs=[])
    provider.client.get_handle.return_value = handle
    registry = Registry(tmp_path)
    for _ in range(3):
        monkeypatch.setattr(providers.time, "monotonic", Mock(side_effect=[0, 0.5, 2]))
        monkeypatch.setattr(providers.time, "sleep", Mock())
        with pytest.raises(DiscoveryError, match="remote request still active"):
            provider.discover([f], [], {f.key: f}, tmp_path, registry)
    provider.client.submit.assert_called_once()
    handle.cancel.assert_not_called()
    # The un-cancelled remote job genuinely can finish after the local deadlines.
    monkeypatch.setattr(providers.time, "monotonic", lambda: 0)
    handle.status.return_value = fal_client.Completed(logs=[], metrics={})
    handle.get.return_value = {"output": '{"objects":[],"empty_frames":["F0"]}'}
    provider.discover([f], [], {f.key: f}, tmp_path, registry, budget=RequestBudget(0))
    provider.client.submit.assert_called_once()


def test_request_budget_resumes_after_cache_hits_and_recorded_replays_are_free(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import services.reconstruction.assets.selection as selection
    from services.reconstruction.assets.selection_models import SourceVideo

    frames = [frame(i) for i in range(3)]
    source = SourceVideo(
        source_id=frames[0].source_id,
        name="synthetic.mp4",
        stream_index=0,
        encoded_size=(160, 96),
        upright_size=(160, 96),
        rotation_deg=0,
        encoded_to_upright=[[1, 0, 0], [0, 1, 0], [0, 0, 1]],
        time_base="1/100",
    )
    monkeypatch.setattr(selection, "sample_video", lambda *args: (source, frames, []))
    for f in frames:
        cv2.imwrite(str(tmp_path / f.image_path), np.zeros((96, 160, 3), np.uint8))
    provider = FalVisionProvider(key="test-never-sent")
    provider.client = Mock()
    handle = provider.client.submit.return_value
    handle.request_id = "completed"
    handle.status.return_value = fal_client.Completed(logs=[], metrics={})
    handle.get.return_value = {"output": '{"objects":[],"empty_frames":["F0"]}'}
    options = SelectionOptions(batch_size=1, max_requests=2)
    first = select_furniture_frames(
        [Path("synthetic.mp4")], "demo", data_dir=tmp_path, provider=provider, options=options
    )
    assert provider.client.submit.call_count == 2
    assert any("budget exhausted" in warning for warning in first.warnings)
    second = select_furniture_frames(
        [Path("synthetic.mp4")], "demo", data_dir=tmp_path, provider=provider, options=options
    )
    assert provider.client.submit.call_count == 3
    assert not any("budget exhausted" in warning for warning in second.warnings)
    # All results now come from the cache even with zero new paid requests allowed.
    select_furniture_frames(
        [Path("synthetic.mp4")],
        "demo",
        data_dir=tmp_path,
        provider=provider,
        options=SelectionOptions(batch_size=1, max_requests=0),
    )
    assert provider.client.submit.call_count == 3
    reviewed = RecordedProvider(Discovery(objects=[track(frames, 0.1)]))
    result = select_furniture_frames(
        [Path("synthetic.mp4")],
        "reviewed",
        data_dir=tmp_path,
        provider=reviewed,
        options=SelectionOptions(batch_size=1, max_requests=0),
    )
    assert result.complete and len(result.objects) == 1
    reflected = select_furniture_frames(
        [Path("synthetic.mp4")],
        "mirror",
        data_dir=tmp_path,
        provider=RecordedProvider(Discovery(objects=[track(frames, 0.1, reflection=True)])),
        options=SelectionOptions(batch_size=1, max_requests=0),
    )
    assert reflected.complete and not reflected.objects
    assert any("reflection excluded" in warning for warning in reflected.warnings)


def test_corrected_batches_clear_only_their_issues_and_reflections_are_nonblocking(
    tmp_path: Path,
) -> None:
    a, b = frame(0), frame(1)
    registry = Registry(tmp_path)

    def seed(state: RegistryState) -> None:
        state.frames.update({a.key: a, b.key: b})
        reconcile(
            state,
            Discovery(objects=[track([a], 0.1, uncertain=True), track([b], 0.1, uncertain=True)]),
            state.frames,
            None,
        )

    initial = registry.update("scene", seed)
    assert set(initial.unresolved_by_frame) == {a.key, b.key}
    ids = list(initial.objects)
    after_a = registry.update(
        "scene",
        lambda state: reconcile(
            state,
            Discovery(objects=[track([a], 0.1)]),
            {a.key: a},
            None,
        ),
    )
    assert set(after_a.unresolved_by_frame) == {b.key}
    after_b = registry.update(
        "scene",
        lambda state: reconcile(
            state,
            Discovery(objects=[track([b], 0.1)]),
            {b.key: b},
            None,
        ),
    )
    assert not after_b.unresolved and list(after_b.objects) == ids
    reflection = registry.update(
        "mirror",
        lambda state: (
            state.frames.update({a.key: a}),
            reconcile(
                state, Discovery(objects=[track([a], 0.1, reflection=True)]), {a.key: a}, None
            ),
        ),
    )
    assert not reflection.objects and not reflection.unresolved
    corrected = registry.update(
        "mirror",
        lambda state: reconcile(
            state,
            Discovery(objects=[], empty_frames=[a.key]),
            {a.key: a},
            None,
        ),
    )
    assert not corrected.warnings_by_frame and not corrected.unresolved


def test_legacy_unresolved_snapshots_can_be_reviewed_without_resetting_ids(tmp_path: Path) -> None:
    f = frame(0)
    registry = Registry(tmp_path)
    state = RegistryState(frames={f.key: f})
    reconcile(state, Discovery(objects=[track([f], 0.1)]), state.frames, None)
    legacy = state.model_dump(exclude={"unresolved_by_frame", "warnings_by_frame"})
    legacy["unresolved"] = ["legacy ambiguity"]
    with sqlite3.connect(registry.path) as connection:
        connection.execute("INSERT INTO scenes VALUES (?,?)", ("scene", json.dumps(legacy)))
    assert registry.load("scene").unresolved_by_frame == {f.key: ["legacy ambiguity"]}
    corrected = registry.update(
        "scene",
        lambda current: reconcile(
            current,
            Discovery(objects=[track([f], 0.1)]),
            {f.key: f},
            None,
        ),
    )
    assert not corrected.unresolved and list(corrected.objects) == list(state.objects)


def test_large_reference_registry_uses_bounded_context_and_still_hits_cache(tmp_path: Path) -> None:
    f = frame(0)
    cv2.imwrite(str(tmp_path / f.image_path), np.zeros((96, 160, 3), np.uint8))
    references = [
        SelectedObject(
            id=f"vid-{i:06d}",
            name="Sofa",
            category="sofa",
            appearance="brown",
            sightings=track([f], 0.1).sightings,
            selected_views=[f.key],
        )
        for i in range(1, 18)
    ]
    provider = FalVisionProvider(key="test-never-sent")
    provider.client = Mock()
    handle = provider.client.submit.return_value
    handle.request_id = "large-registry"
    handle.status.return_value = fal_client.Completed(logs=[], metrics={})
    handle.get.return_value = {"output": '{"objects":[],"empty_frames":["F0"]}'}
    registry = Registry(tmp_path)
    result = provider.discover(
        [f], references, {f.key: f}, tmp_path, registry, budget=RequestBudget(1)
    )
    assert provider.client.upload.call_count == 17  # one full frame plus 16 reference crops
    assert any("context limited" in warning for warning in result.warnings)
    assert (
        provider.discover([f], references, {}, tmp_path, registry, budget=RequestBudget(0))
        == result
    )
    provider.client.submit.assert_called_once()


def test_later_metadata_does_not_reclassify_established_items() -> None:
    a, b = frame(0), frame(1)
    state = RegistryState(frames={a.key: a, b.key: b})
    reconcile(state, Discovery(objects=[track([a], 0.1)]), {a.key: a}, None)
    original = next(iter(state.objects.values())).model_copy(deep=True)
    changed = track(
        [b],
        0.1,
        reference_id=original.id,
        category="chair",
        name="New name",
        appearance="new misleading appearance",
    )
    reconcile(state, Discovery(objects=[changed]), {b.key: b}, None)
    current = state.objects[original.id]
    assert (current.name, current.category, current.appearance) == (
        original.name,
        original.category,
        original.appearance,
    )
    assert len(current.sightings) == 2 and state.unresolved


def test_live_cli_missing_fal_client_exits_cleanly(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    import builtins

    original_import = builtins.__import__

    def missing_sdk(name: str, *args: object, **kwargs: object) -> object:
        if name == "fal_client":
            raise ModuleNotFoundError("No module named fal_client")
        return original_import(name, *args, **kwargs)

    monkeypatch.setenv("FAL_KEY", "test-never-sent")
    monkeypatch.setattr(builtins, "__import__", missing_sdk)
    assert main(["not-read.mp4", "--scene-id", "demo", "--live", "--out", str(tmp_path)]) == 1
    assert "install the reconstruction Python extra" in capsys.readouterr().out


def test_sampling_once_then_discovering_matches_one_call(video: Path, tmp_path: Path) -> None:
    """`select_furniture_frames` is `sample_sources` then `discover_frames`; the halves let a
    caller sample once and discover in subsets of the frames (one namespace per room)."""
    options = SelectionOptions(sample_interval_s=0.25, batch_size=1)
    probe = select_furniture_frames([video], "probe", data_dir=tmp_path / "probe", options=options)
    discovery = Discovery(objects=[track(probe.frames, 0.05), track(probe.frames, 0.65)])
    whole = select_furniture_frames(
        [video],
        "demo",
        data_dir=tmp_path / "one",
        options=options,
        provider=RecordedProvider(discovery),
    )
    sources, frames, notes = sample_sources([video], tmp_path / "two", options)
    split = discover_frames(
        "demo",
        sources,
        frames,
        data_dir=tmp_path / "two",
        provider=RecordedProvider(discovery),
        options=options,
        warnings=notes,
    )
    assert split.complete == whole.complete
    assert [f.key for f in split.frames] == [f.key for f in whole.frames]
    assert [(o.id, o.name, len(o.sightings)) for o in split.objects] == [
        (o.id, o.name, len(o.sightings)) for o in whole.objects
    ]
    subset = frames[:2]
    part = discover_frames(
        "part",
        sources,
        subset,
        data_dir=tmp_path / "two",
        provider=RecordedProvider(Discovery(objects=[track(subset, 0.05)])),
        options=options,
    )
    assert {f.key for f in part.frames} == {f.key for f in subset}
    assert len(part.objects) == 1 and len(part.objects[0].sightings) == len(subset)
