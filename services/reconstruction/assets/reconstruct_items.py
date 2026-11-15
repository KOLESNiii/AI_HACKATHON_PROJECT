"""Reconstruct registered furniture. Offline proxies by default; --live uploads to fal.ai."""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
from pathlib import Path

from .mesh_providers import FalSam3dProvider, MeshProvider
from .proxies import KnownDimensions
from .reconstruction import reconstruct_furniture
from .selection_models import ReconstructionResult


def write_report(result: ReconstructionResult, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "reconstruction.json").write_text(result.model_dump_json(indent=2) + "\n")
    (output / "assets.json").write_text(
        json.dumps(
            [(item.asset or item.proxy).model_dump(mode="json") for item in result.items], indent=2
        )
        + "\n"
    )
    lines = [
        f"# Furniture reconstruction: {result.scene_id}",
        "",
        f"Complete: {result.complete}. Registry revision {result.registry_revision}.",
        "",
        "Raw meshes retain provider units and orientation and are not served. assets.json holds "
        "each item's normalised mesh, or its proxy when there is none. Estimated dimensions "
        "need correction.",
        "",
    ]
    for item in result.items:
        bbox = item.proxy.bbox_m
        lines.extend(
            [
                f"## {item.object_id}: {item.proxy.name}",
                "",
                f"Proxy: {bbox.width:g} × {bbox.height:g} × {bbox.depth:g} m (W × H × D); "
                f"{item.proxy.dimension_source}. `{item.proxy.glb_url}`.",
                "",
            ]
        )
        if item.mesh:
            lines.extend(
                [
                    f"Raw mesh: `{item.mesh.mesh_path}`; {item.mesh.triangles} triangles; "
                    f"{item.mesh.size_bytes} bytes. Frame `{item.mesh.frame_key}`.",
                    "",
                ]
            )
        if item.asset:
            size, needs = item.asset.bbox_m, ", ".join(item.asset.correction_needed) or "nothing"
            lines.extend(
                [
                    f"Normalised mesh: {size.width:g} × {size.height:g} × {size.depth:g} m "
                    f"(W × H × D); {item.asset.dimension_source}; needs correction: {needs}. "
                    f"`{item.asset.glb_url}`.",
                    "",
                ]
            )
        if item.failure:
            lines.extend([f"Failure ({item.failure.kind}): {item.failure.reason}.", ""])
    lines.extend(["## Warnings", "", *(f"- {w}" for w in result.warnings)])
    (output / "report.md").write_text("\n".join(lines) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene-id", required=True)
    parser.add_argument("--data-dir", type=Path, default=Path("artifacts/furniture"))
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--object-id", action="append")
    parser.add_argument("--dimensions", type=Path, help="JSON object: item ID to {bbox_m, source}")
    parser.add_argument(
        "--replace",
        action="store_true",
        help="rebuild from the current mask; reuses the paid result unless --refresh is given",
    )
    parser.add_argument("--live", action="store_true", help="upload frames and masks to fal.ai")
    parser.add_argument("--refresh", default="", help="explicit namespace for paid regeneration")
    parser.add_argument("--max-requests", type=int, default=8)
    parser.add_argument("--concurrency", type=int, default=4)
    args = parser.parse_args(argv)
    try:
        dimensions = None
        if args.dimensions:
            payload = json.loads(args.dimensions.read_text())
            if not isinstance(payload, dict):
                raise ValueError("dimensions must be an object keyed by item ID")
            dimensions = {
                key: KnownDimensions.model_validate(value) for key, value in payload.items()
            }
        provider: MeshProvider | None = None
        if args.live:
            provider = FalSam3dProvider(key=os.environ.get("FAL_KEY", ""), refresh=args.refresh)
        result = reconstruct_furniture(
            args.scene_id,
            data_dir=args.data_dir,
            provider=provider,
            object_ids=args.object_id,
            dimensions=dimensions,
            replace=args.replace,
            max_requests=args.max_requests,
            concurrency=args.concurrency,
        )
        write_report(result, args.out)
        print(
            json.dumps(
                {
                    "items": len(result.items),
                    "meshes": sum(i.mesh is not None for i in result.items),
                    "complete": result.complete,
                    "report": str(args.out / "report.md"),
                }
            )
        )
        return 0 if result.complete else 2
    except ImportError:
        print("Live reconstruction needs fal-client; install the reconstruction Python extra.")
        return 1
    except (ValueError, OSError, sqlite3.Error) as exc:
        print(f"Reconstruction failed ({type(exc).__name__}); check scene, items and registry.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
