"""Local #15 CLI. Offline GrabCut masks by default; --live explicitly uploads frames to fal.ai."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sqlite3
from pathlib import Path

import cv2
import numpy as np

from .mask_providers import FalSamProvider, MaskError, MaskProvider
from .segmentation import read_mask, segment_furniture
from .selection import object_evidence
from .selection_models import SegmentationResult
from .video import read_image


def write_report(result: SegmentationResult, data_dir: Path, output: Path) -> None:
    """Review images plus the two machine-readable handoffs: the result and the evidence."""
    output.mkdir(parents=True, exist_ok=True)
    (output / "segmentation.json").write_text(result.model_dump_json(indent=2) + "\n")
    frames = {frame.key: frame for frame in result.frames}
    evidence = {}
    lines = [
        f"# Furniture masks: {result.scene_id}",
        "",
        f"Every selected view masked: {result.complete}. "
        f"Registry revision {result.registry_revision}.",
        "",
        "Masks are machine-generated evidence in upright source-frame pixels, not verified "
        "outlines, metric sizes or room positions.",
        "",
    ]
    for obj in result.objects:
        # The fixed evidence shape holds one source; use the one with the item's best view.
        best = frames[obj.selected_views[0] if obj.selected_views else obj.sightings[0].frame_key]
        evidence[obj.id] = object_evidence(result, obj.id, source_id=best.source_id).model_dump()
        lines.extend([f"## {obj.id}: {obj.name}", "", f"Category: {obj.category}.", ""])
        if len({frames[s.frame_key].source_id for s in obj.sightings}) > 1:
            lines.extend(
                [f"evidence.json covers source {best.source_id[:12]} only; see the result.", ""]
            )
        for number, mask in enumerate(m for m in obj.masks if obj.mask_for(m.frame_key) == m):
            if not all((data_dir / path).is_file() for path in (mask.mask_path, mask.crop_path)):
                continue  # A failed repair is already listed under missing masks.
            frame = frames[mask.frame_key]
            image = read_image(data_dir, frame)
            pixels = read_mask(data_dir, mask.mask_path)
            tint = np.array([0, 255, 0])
            image[pixels] = (0.5 * image[pixels] + 0.5 * tint).astype(np.uint8)
            x, y, w, h = mask.bbox_px
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 255), 1)
            cv2.putText(image, obj.id, (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            overlay, cutout = f"{obj.id}-{number}-mask.jpg", f"{obj.id}-{number}-cutout.png"
            if not cv2.imwrite(str(output / overlay), image):
                raise ValueError("could not write report image")
            shutil.copyfile(data_dir / mask.crop_path, output / cutout)
            lines.extend(
                [
                    f"![{obj.id} mask]({overlay}) ![{obj.id} cut-out]({cutout})",
                    "",
                    f"Source {frame.source_id[:12]}, frame {frame.frame_index}, PTS {frame.pts}, "
                    f"time {frame.timestamp_s:.3f} s. Method {mask.method}; box (x, y, w, h) "
                    f"{mask.bbox_px}; {mask.area_px} px; score "
                    f"{'n/a' if mask.score is None else format(mask.score, '.2f')}. "
                    f"Mask `{mask.mask_path}`.",
                    "",
                ]
            )
    (output / "evidence.json").write_text(json.dumps(evidence, indent=2) + "\n")
    lines.extend(["## Missing masks", ""])
    lines.extend(
        f"- {m.object_id}, source {frames[m.frame_key].source_id[:12]} frame "
        f"{frames[m.frame_key].frame_index}: {m.reason}"
        for m in result.missing
    )
    lines.extend(["", "## Warnings", ""])
    lines.extend(f"- {warning}" for warning in result.warnings)
    (output / "report.md").write_text("\n".join(lines) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene-id", required=True)
    parser.add_argument("--data-dir", type=Path, default=Path("artifacts/furniture"))
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument(
        "--object-id", action="append", help="limit to this item; repeat for several"
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="segment stored masks again; existing SAM 3 masks require --live",
    )
    parser.add_argument("--live", action="store_true", help="upload frames to fal.ai SAM 3")
    parser.add_argument(
        "--refresh", default="", help="explicit cache namespace for paid re-segmentation"
    )
    parser.add_argument(
        "--max-requests",
        type=int,
        default=16,
        help="new live submissions per run (one per frame); saved requests are re-read free",
    )
    args = parser.parse_args(argv)
    try:
        provider: MaskProvider | None = None
        if args.live:
            provider = FalSamProvider(key=os.environ.get("FAL_KEY", ""), refresh=args.refresh)
        result = segment_furniture(
            args.scene_id,
            data_dir=args.data_dir,
            provider=provider,
            object_ids=args.object_id,
            replace=args.replace,
            max_requests=args.max_requests,
        )
        write_report(result, args.data_dir, args.out)
        print(
            json.dumps(
                {
                    "objects": len(result.objects),
                    "masks": sum(len(obj.masks) for obj in result.objects),
                    "missing": len(result.missing),
                    "complete": result.complete,
                    "report": str(args.out / "report.md"),
                }
            )
        )
        return 0 if result.complete else 2
    except MaskError as exc:
        print(f"Segmentation failed: {exc}")
        return 1
    except ImportError:
        print("Live segmentation needs fal-client; install the reconstruction Python extra.")
        return 1
    except (ValueError, OSError, sqlite3.Error) as exc:
        # Do not echo credentials, provider payloads or private paths in CLI errors.
        print(f"Segmentation failed ({type(exc).__name__}); check scene, items and registry.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
