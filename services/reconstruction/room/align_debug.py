"""Debug CLI for furniture alignment: place assets in a room and draw the result.

    # Default layout for the demo home's own furniture (poses stripped), compared with it:
    uv run python -m services.reconstruction.room align --demo all --out /tmp/align
    ... align --demo ground --out /tmp/align           # one floor; or room IDs: g-master f-bed4

    # Given assets in one room, placed from recorded hints:
    ... align --demo g-reception --out DIR --assets ASSETS.json --hints HINTS.json
    # or live from the evidence frames (FAL_KEY), outlining #15 masks when given their data dir:
    ... align --demo g-reception --out DIR --assets ASSETS.json \
        --live --frames FRAMES_DIR [--masks DATA_DIR] --save-hints HINTS.json

    # Any single-room scene, e.g. one room the floor-plan parser returned:
    ... align --scene ROOM.json --out DIR --assets ASSETS.json

Demo rooms are the editor's (`demo_assets.demo_room_scene`): `g-reception` is the reception
room of the ground floor. Without `--assets`, a room's furniture is turned back into pose-less
assets. Furniture the room already has under an asset's ID is taken out first and becomes the
reference the result is compared with. Writes `<scene_id>.json` (the aligned room) and
`<scene_id>.png` per room, and `records.json`.
"""

from __future__ import annotations

import argparse
import json
import math
from collections.abc import Sequence
from pathlib import Path

import cv2

from contracts.schema import FurnitureItem, RoomScene
from services.reconstruction import demo_assets
from services.reconstruction.assets.models import FurnitureAsset

from .align import AlignmentRecord, AlignmentResult, align_assets, wall_relative
from .assemble import assets_of
from .observe import (
    FixedObserver,
    FrameSource,
    NullObserver,
    PlacementHint,
    PlacementHints,
    PlacementObserver,
)
from .plan_view import render_room, wall_letters


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


def demo_selection(names: Sequence[str]) -> list[RoomScene]:
    """Demo rooms by room ID, floor name (`ground`, `first`, `second`) or `all`, in fixture
    order. Raises KeyError for a name that is none of these."""
    rooms = demo_assets.demo_rooms()
    wanted: list[str] = []
    for name in names:
        if name == "all":
            wanted += list(rooms)
        elif name in demo_assets.FLOORS:
            floor = demo_assets.demo_floors()[name]
            wanted += [r for r, scene in rooms.items() if scene.walls[0] in floor.walls]
        elif name in rooms:
            wanted.append(name)
        else:
            raise KeyError(name)
    return [demo_assets.demo_room_scene(room_id) for room_id in dict.fromkeys(wanted)]


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m services.reconstruction.room align")
    where = ap.add_mutually_exclusive_group(required=True)
    where.add_argument("--demo", nargs="+", help="demo room IDs, floor names, or `all`")
    where.add_argument("--scene", type=Path, help="one single-room RoomScene JSON")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--assets", type=Path, help="JSON list of FurnitureAsset, for one room")
    ap.add_argument("--hints", type=Path, help="recorded PlacementHints JSON")
    ap.add_argument("--live", action="store_true", help="ask the fal vision model for hints")
    ap.add_argument(
        "--frames", type=Path, help="evidence frames as <frame_index>.jpg|.png, for --live"
    )
    ap.add_argument(
        "--masks", type=Path, help="asset data directory that evidence `mask_url`s are under"
    )
    ap.add_argument("--save-hints", type=Path, help="write the hints the observer returned")
    args = ap.parse_args(argv)

    if args.scene:
        rooms = [RoomScene.model_validate_json(args.scene.read_text())]
    else:
        try:
            rooms = demo_selection(args.demo)
        except KeyError as exc:
            print(f"unknown demo room or floor {exc}; rooms: {', '.join(demo_assets.demo_rooms())}")
            return 1
    given = None
    if args.assets:
        if len(rooms) != 1:
            print("--assets needs exactly one room")
            return 1
        given = [FurnitureAsset.model_validate(a) for a in json.loads(args.assets.read_text())]

    inner: PlacementObserver = NullObserver()
    frames: FrameSource | None = None
    vision = None
    if args.hints:
        inner = FixedObserver.from_file(args.hints)
    elif args.live:
        from .observe_vision import FalVisionObserver, directory_frames, selection_masks

        inner = vision = FalVisionObserver(
            masks=selection_masks(args.masks) if args.masks else None
        )
        frames = directory_frames(args.frames) if args.frames else None
    observer = _Capture(inner)

    args.out.mkdir(parents=True, exist_ok=True)
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
        records.update(result.records)
        (args.out / f"{room.scene_id}.json").write_text(aligned.model_dump_json(indent=2))
        view = render_room(aligned, result.records, list(reference.values()))
        png = cv2.imencode(".png", view.image)[1].tobytes()
        (args.out / f"{room.scene_id}.png").write_bytes(png)

    (args.out / "records.json").write_text(
        json.dumps({k: v.model_dump() for k, v in records.items()}, indent=2)
    )
    if args.save_hints:
        args.save_hints.write_text(PlacementHints(hints=observer.hints).model_dump_json(indent=2))
    return 0
