"""Check the furniture a scene delivers to Dev 1: normalisation and proxy fallback (#18).

Offline. Exit 0: every delivered asset passed its checks and there are at least --min-items
of them; 2: a check failed or there are too few items (the report is still written); 1: unknown
scene or item, or unusable input or storage.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

from .delivery import Delivery, deliver_furniture
from .reconstruct_items import load_dimensions


def write_report(delivery: Delivery, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "delivery.json").write_text(delivery.model_dump_json(indent=2) + "\n")
    (output / "assets.json").write_text(
        json.dumps([asset.model_dump(mode="json") for asset in delivery.assets], indent=2) + "\n"
    )
    lines = [
        f"# Furniture delivery: {delivery.scene_id}",
        "",
        f"Checks passed: {delivery.ok}. Registry revision {delivery.registry_revision}.",
        "",
        "assets.json is what Dev 1 places: each item's checked mesh, or its labelled proxy.",
        "",
        "| Item | Delivered | W × H × D (m) | Size from | Needs correction | Bounds error (mm) "
        "| Triangles | Bytes | Result |",
        "|---|---|---|---|---|---:|---:|---:|---|",
    ]
    for asset, check in zip(delivery.assets, delivery.checks, strict=True):
        box = check.bbox_m
        error = "" if check.bounds_error_m is None else f"{check.bounds_error_m * 1000:.4f}"
        lines.append(
            f"| `{check.object_id}` {asset.name} | {check.delivered} "
            f"| {box.width:g} × {box.height:g} × {box.depth:g} | {check.dimension_source} "
            f"| {', '.join(check.correction_needed) or 'nothing'} | {error} "
            f"| {check.triangles or ''} | {check.size_bytes or ''} "
            f"| {'; '.join(check.problems) or 'pass'} |"
        )
    fallbacks = [c for c in delivery.checks if c.fallback_reason]
    if fallbacks:
        lines.extend(["", "## Proxies", ""])
        lines.extend(f"- `{c.object_id}`: {c.fallback_reason}" for c in fallbacks)
    notes = [*delivery.problems, *delivery.warnings]
    if notes:
        lines.extend(["", "## Warnings", "", *(f"- {note}" for note in notes)])
    (output / "report.md").write_text("\n".join(lines) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene-id", required=True)
    parser.add_argument("--data-dir", type=Path, default=Path("artifacts/furniture"))
    parser.add_argument(
        "--out", type=Path, help="directory for delivery.json, assets.json, report.md"
    )
    parser.add_argument("--object-id", action="append")
    parser.add_argument("--dimensions", type=Path, help="JSON object: item ID to {bbox_m, source}")
    parser.add_argument("--min-items", type=int, default=2, help="fewest items to accept")
    args = parser.parse_args(argv)
    try:
        delivery = deliver_furniture(
            args.scene_id,
            data_dir=args.data_dir,
            dimensions=load_dimensions(args.dimensions) if args.dimensions else None,
            object_ids=args.object_id,
        )
        if args.out:
            write_report(delivery, args.out)
    except (ValueError, OSError, sqlite3.Error) as exc:
        print(f"Delivery check failed ({type(exc).__name__}); check scene, items and registry.")
        return 1
    enough = len(delivery.assets) >= args.min_items
    print(
        json.dumps(
            {
                "items": len(delivery.assets),
                "meshes": sum(c.delivered == "mesh" for c in delivery.checks),
                "proxies": sum(c.delivered == "proxy" for c in delivery.checks),
                "failed": sorted(c.object_id for c in delivery.checks if c.problems),
                "ok": delivery.ok and enough,
            }
        )
    )
    return 0 if delivery.ok and enough else 2


if __name__ == "__main__":
    raise SystemExit(main())
