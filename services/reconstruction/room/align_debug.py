"""Debug CLI for furniture alignment: place assets in a room and draw the result.

    # Default layout for a scene's own furniture (poses stripped), compared with its poses:
    uv run python -m services.reconstruction.room align \
        contracts/mock_room/three_floor_ground_scene.json --out /tmp/align

    # Given assets in one room, placed from recorded hints or live from frames (needs FAL_KEY):
    ... align SCENE.json --out DIR --room g-reception-w00 --assets ASSETS.json --hints HINTS.json
    ... align SCENE.json --out DIR --room g-reception-w00 --assets ASSETS.json \
        --live --frames FRAMES_DIR --save-hints HINTS.json

A whole-floor scene is split into rooms; `--room` picks the one that has that wall. Without
`--assets`, each room's furniture is turned back into pose-less assets. Furniture the scene
already has under an asset's ID is taken out first and becomes the reference the result is
compared with. Writes `aligned.json`, `records.json` and one PNG per room.
"""

from __future__ import annotations

import argparse
import json
import math
from collections.abc import Sequence
from pathlib import Path

import cv2

from contracts.schema import FurnitureItem, RoomScene
from services.reconstruction.assets.models import AssetEvidence, EvidenceFrame, FurnitureAsset

from . import footprint as fp
from .align import AlignmentRecord, AlignmentResult, align_assets, wall_relative
from .observe import (
    FixedObserver,
    FrameSource,
    NullObserver,
    PlacementHint,
    PlacementHints,
    PlacementObserver,
)
from .plan_view import render_room, wall_letters


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


def pose_error(reference: FurnitureItem, item: FurnitureItem) -> tuple[float, float]:
    """(distance in metres, absolute yaw difference in degrees) between two poses."""
    distance = math.hypot(reference.pose.x - item.pose.x, reference.pose.z - item.pose.z)
    yaw = abs((reference.pose.yaw_deg - item.pose.yaw_deg + 180) % 360 - 180)
    return distance, yaw


def _report(room: RoomScene, result: AlignmentResult, reference: dict[str, FurnitureItem]) -> None:
    letters = wall_letters(room)
    for item in result.items:
        record = result.records[item.id]
        wall = letters.get(record.wall_id or "", "-")
        line = (
            f"  {item.id:<28} {record.method:<8} wall {wall:<3} "
            f"({item.pose.x:5.2f}, {item.pose.z:5.2f}, {item.pose.yaw_deg:5.1f})"
        )
        if item.id in reference:
            distance, yaw = pose_error(reference[item.id], item)
            expected = wall_relative(room, reference[item.id])
            same_wall = expected is not None and expected.wall_id == record.wall_id
            wall_match = "same wall" if same_wall else "other wall"
            line += f"  vs reference: {distance:4.2f} m, {yaw:5.1f} deg, {wall_match}"
        flags = ",".join(item.correction_needed) or "-"
        print(f"{line}  [{flags}] {'; '.join(record.notes)}")
    for warning in result.warnings:
        print("  warning:", warning)


class _Capture:
    """Passes hints through and keeps them, so a live run can be recorded."""

    def __init__(self, inner: PlacementObserver) -> None:
        self.inner = inner
        self.hints: list[PlacementHint] = []

    def observe(
        self, scene: RoomScene, assets: Sequence[FurnitureAsset], frames: FrameSource
    ) -> list[PlacementHint]:
        hints = self.inner.observe(scene, assets, frames)
        self.hints += hints
        return hints


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m services.reconstruction.room align")
    ap.add_argument("scene", type=Path, help="RoomScene JSON: one room or a whole floor")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--room", help="only the room that has this wall ID")
    ap.add_argument("--assets", type=Path, help="JSON list of FurnitureAsset, for one room")
    ap.add_argument("--hints", type=Path, help="recorded PlacementHints JSON")
    ap.add_argument("--live", action="store_true", help="ask the fal vision model for hints")
    ap.add_argument(
        "--frames", type=Path, help="evidence frames as <frame_index>.jpg|.png, for --live"
    )
    ap.add_argument("--save-hints", type=Path, help="write the hints the observer returned")
    args = ap.parse_args(argv)

    scene = RoomScene.model_validate_json(args.scene.read_text())
    rooms = fp.split_rooms(scene)
    if args.room:
        rooms = [r for r in rooms if any(w.id == args.room for w in r.walls)]
    if not rooms:
        print("no matching closed room outline in this scene")
        return 1
    given = None
    if args.assets:
        if len(rooms) != 1:
            print("--assets needs one room: pass --room or a single-room scene")
            return 1
        given = [FurnitureAsset.model_validate(a) for a in json.loads(args.assets.read_text())]

    inner: PlacementObserver = NullObserver()
    frames: FrameSource | None = None
    vision = None
    if args.hints:
        inner = FixedObserver.from_file(args.hints)
    elif args.live:
        from .observe_vision import FalVisionObserver, directory_frames

        inner = vision = FalVisionObserver()
        frames = directory_frames(args.frames) if args.frames else None
    observer = _Capture(inner)

    args.out.mkdir(parents=True, exist_ok=True)
    placed: list[FurnitureItem] = []
    records: dict[str, AlignmentRecord] = {}
    for room in rooms:
        assets = given if given is not None else assets_of(room)
        if not assets:
            continue
        ids = {a.id for a in assets}
        reference = {item.id: item for item in room.furniture if item.id in ids}
        start = room.model_copy(
            update={"furniture": [item for item in room.furniture if item.id not in ids]}
        )
        result = align_assets(start, assets, observer, frames)
        aligned = result.place_in(start)
        print(f"{room.scene_id}: {len(assets)} assets")
        if vision is not None:
            print("  camera:", vision.camera or "-")
            result.warnings += vision.warnings
        _report(room, result, reference)
        placed += aligned.furniture
        records.update(result.records)
        view = render_room(aligned, result.records, list(reference.values()))
        png = cv2.imencode(".png", view.image)[1].tobytes()
        (args.out / f"{room.scene_id}.png").write_bytes(png)

    whole = scene.model_copy(update={"furniture": placed})
    (args.out / "aligned.json").write_text(whole.model_dump_json(indent=2))
    (args.out / "records.json").write_text(
        json.dumps({k: v.model_dump() for k, v in records.items()}, indent=2)
    )
    if args.save_hints:
        args.save_hints.write_text(PlacementHints(hints=observer.hints).model_dump_json(indent=2))
    return 0
