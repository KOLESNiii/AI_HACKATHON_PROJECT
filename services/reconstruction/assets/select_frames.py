"""Local #14 CLI. Defaults to offline sampling; --live explicitly permits provider uploads."""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
from pathlib import Path

import cv2
import numpy as np

from .providers import DiscoveryProvider, FalVisionProvider, RecordedProvider
from .selection import select_furniture_frames
from .selection_models import Discovery, SelectionOptions, SelectionResult
from .video import read_image


def write_report(result: SelectionResult, data_dir: Path, output: Path) -> None:
    """Full-resolution source artifacts stay separate; the report shows boxes and IDs."""
    output.mkdir(parents=True, exist_ok=True)
    (output / "selection.json").write_text(result.model_dump_json(indent=2) + "\n")
    frames = {frame.key: frame for frame in result.frames}
    lines = [
        f"# Furniture selection: {result.scene_id}",
        "",
        f"Complete sampled discovery: {result.complete}. "
        f"Registry revision {result.registry_revision}.",
        "",
        "Completeness does not certify an exhaustive inventory or metric placement.",
        "",
    ]
    # Keep overview pages bounded even when a scene accumulates evidence over many runs.
    for page, start in enumerate(range(0, len(result.frames), 12)):
        tiles = []
        for frame in result.frames[start : start + 12]:
            original = read_image(data_dir, frame)
            h, w = original.shape[:2]
            scale = min(160 / w, 280 / h)
            image = cv2.resize(original, (max(1, round(w * scale)), max(1, round(h * scale))))
            tile = np.full((300, 160, 3), 255, np.uint8)
            tile[20 : 20 + image.shape[0], : image.shape[1]] = image
            cv2.putText(
                tile,
                f"{frame.source_id[:6]}:{frame.frame_index}",
                (2, 14),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.35,
                (0, 0, 0),
                1,
            )
            tiles.append(tile)
        while len(tiles) % 4:
            tiles.append(np.full((300, 160, 3), 255, np.uint8))
        sheet = np.vstack([np.hstack(tiles[i : i + 4]) for i in range(0, len(tiles), 4)])
        name = f"frames-{page:02}.jpg"
        if not cv2.imwrite(str(output / name), sheet):
            raise ValueError("could not write frame overview")
        lines.extend([f"![Selected source frames]({name})", ""])
    for obj in result.objects:
        lines.extend(
            [f"## {obj.id}: {obj.name}", "", f"Category: {obj.category}. {obj.appearance}", ""]
        )
        for number, key in enumerate(obj.selected_views):
            frame = frames[key]
            sighting = next(s for s in obj.sightings if s.frame_key == key)
            image = read_image(data_dir, frame)
            h, w = image.shape[:2]
            box = sighting.box
            cv2.rectangle(
                image,
                (round(box.x * w), round(box.y * h)),
                (round((box.x + box.width) * w), round((box.y + box.height) * h)),
                (0, 255, 255),
                2,
            )
            cv2.putText(image, obj.id, (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            name = f"{obj.id}-{number}.jpg"
            if not cv2.imwrite(str(output / name), image):
                raise ValueError("could not write report image")
            lines.extend(
                [
                    f"![{obj.id}]({name})",
                    "",
                    f"Source {frame.source_id[:12]}, frame {frame.frame_index}, "
                    f"PTS {frame.pts}, time {frame.timestamp_s:.3f} s, "
                    f"quality {sighting.quality:.3f}.",
                    "",
                ]
            )
    lines.extend(["## Warnings / unresolved identities", ""])
    lines.extend(f"- {warning}" for warning in [*result.warnings, *result.unresolved])
    (output / "report.md").write_text("\n".join(lines) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("videos", type=Path, nargs="+")
    parser.add_argument("--scene-id", required=True)
    parser.add_argument("--data-dir", type=Path, default=Path("artifacts/furniture"))
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--start", type=float, default=0)
    parser.add_argument("--end", type=float)
    parser.add_argument("--interval", type=float, default=1)
    parser.add_argument("--max-frames", type=int, default=24)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument(
        "--max-requests",
        type=int,
        default=8,
        help="new inference submission attempts per run; cache/recorded/recovery reads are free",
    )
    parser.add_argument(
        "--room-key", help="caller-confirmed physical room, for cross-video matching"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--live", action="store_true", help="upload sampled images to fal.ai")
    mode.add_argument(
        "--recorded", type=Path, help="reviewed Discovery JSON, using full frame keys"
    )
    parser.add_argument(
        "--refresh", default="", help="explicit cache namespace for paid re-detection"
    )
    args = parser.parse_args(argv)
    try:
        options = SelectionOptions(
            start_s=args.start,
            end_s=args.end,
            sample_interval_s=args.interval,
            max_frames_per_video=args.max_frames,
            batch_size=args.batch_size,
            max_requests=args.max_requests,
            room_key=args.room_key,
        )
        provider: DiscoveryProvider | None = None
        if args.live:
            provider = FalVisionProvider(
                key=os.environ.get("FAL_KEY", ""),
                endpoint=os.environ.get("FAL_VISION_ENDPOINT", "fal-ai/any-llm/vision"),
                model=os.environ.get("FAL_VISION_MODEL", "google/gemini-2.5-flash"),
                refresh=args.refresh,
            )
        elif args.recorded:
            provider = RecordedProvider(Discovery.model_validate_json(args.recorded.read_text()))
        result = select_furniture_frames(
            args.videos,
            args.scene_id,
            data_dir=args.data_dir,
            options=options,
            provider=provider,
        )
        write_report(result, args.data_dir, args.out)
        print(
            json.dumps(
                {
                    "objects": len(result.objects),
                    "frames": len(result.frames),
                    "complete": result.complete,
                    "report": str(args.out / "report.md"),
                }
            )
        )
        return 0 if result.complete else 2
    except ImportError:
        print("Live discovery needs fal-client; install the reconstruction Python extra.")
        return 1
    except (ValueError, OSError, sqlite3.Error) as exc:
        # Do not echo raw invalid JSON, credentials, or provider payloads in CLI errors.
        print(f"Selection failed ({type(exc).__name__}); check media, options and registry.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
