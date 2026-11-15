"""Import a retailer product as a furniture asset through the shared pipeline (#19).

    --url URL            import the product on that page
    --search QUERY       list IKEA products matching QUERY; add --pick N to import result N
    --product FILE       import a RetailerProduct JSON (for example a stored search result)

Offline apart from the retailer's own pages, image and published model. --live adds fal.ai
(FAL_KEY): SAM 3 masks, and a SAM 3D mesh when the retailer publishes no model.

Exit 0: the asset passed its checks and asks for no correction; 2: it failed a check or asks
for a correction (the report is still written); 1: the product or the input is unusable.
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
from pathlib import Path
from typing import Literal

from contracts.schema import BBoxM

from .catalog import CatalogImport, import_catalog_asset, import_product
from .mask_providers import FalSamProvider, MaskProvider
from .mesh_providers import FalSam3dProvider, MeshProvider
from .proxies import KnownDimensions
from .retailer import CatalogError, RetailerProduct, search_ikea


def write_report(result: CatalogImport, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "import.json").write_text(result.model_dump_json(indent=2) + "\n")
    (output / "assets.json").write_text(
        json.dumps([result.asset.model_dump(mode="json")], indent=2) + "\n"
    )
    asset, product, box = result.asset, result.product, result.asset.bbox_m
    published = product.dimensions
    lines = [
        f"# Retailer import: {asset.name}",
        "",
        f"Checks passed: {result.ok}. Item `{asset.id}` in scene `{result.scene_id}`.",
        "",
        "| | |",
        "|---|---|",
        f"| Source | {product.source}, {product.product_url} |",
        f"| Image | {product.image_url or 'none published'} |",
        f"| Geometry | {result.mesh_source} |",
        f"| W × H × D (m) | {box.width:g} × {box.height:g} × {box.depth:g} |",
        f"| Size from | {asset.dimension_source} |",
        "| Published size | "
        + (f"{published.text} ({published.found_in})" if published else "none found")
        + " |",
        f"| Needs correction | {', '.join(asset.correction_needed) or 'nothing'} |",
        f"| Price | {'' if asset.price_gbp is None else f'£{asset.price_gbp:g}'} |",
        f"| Checks | {'; '.join(result.check.problems) or 'pass'} |",
    ]
    if result.warnings:
        lines.extend(["", "## Warnings", "", *(f"- {note}" for note in result.warnings)])
    (output / "report.md").write_text("\n".join(lines) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    what = parser.add_mutually_exclusive_group(required=True)
    what.add_argument("--url")
    what.add_argument("--search")
    what.add_argument("--product", type=Path)
    parser.add_argument("--pick", type=int, help="with --search: import result N (from 1)")
    parser.add_argument("--limit", type=int, default=5, help="with --search: results to list")
    parser.add_argument("--scene-id")
    parser.add_argument("--data-dir", type=Path, default=Path("artifacts/furniture"))
    parser.add_argument(
        "--out", type=Path, help="directory for import.json, assets.json, report.md"
    )
    parser.add_argument("--category", help="override the category read from the page")
    parser.add_argument(
        "--dimensions",
        nargs=3,
        type=float,
        metavar=("WIDTH", "HEIGHT", "DEPTH"),
        help="the user's own size in metres; overrides the published one",
    )
    parser.add_argument("--live", action="store_true", help="use fal.ai (FAL_KEY)")
    parser.add_argument("--max-requests", type=int, default=2)
    args = parser.parse_args(argv)
    try:
        url: str | None = args.url
        source: Literal["url_import", "catalog_search"] = "url_import"
        if args.search is not None:
            found = search_ikea(args.search, limit=args.limit)
            if args.pick is None:
                print(json.dumps([r.model_dump(mode="json") for r in found], indent=2))
                return 0
            if not 1 <= args.pick <= len(found):
                raise CatalogError("no such search result")
            url, source = found[args.pick - 1].product_url, "catalog_search"
        if not args.scene_id:
            raise CatalogError("--scene-id is required to import")
        masks: MaskProvider | None = None
        meshes: MeshProvider | None = None
        if args.live:
            key = os.environ.get("FAL_KEY", "")
            masks, meshes = FalSamProvider(key=key), FalSam3dProvider(key=key)
        known = None
        if args.dimensions:
            width, height, depth = args.dimensions
            known = KnownDimensions(
                bbox_m=BBoxM(width=width, height=height, depth=depth), source="user_corrected"
            )
        options = {
            "data_dir": args.data_dir,
            "dimensions": known,
            "mask_provider": masks,
            "mesh_provider": meshes,
            "max_requests": args.max_requests,
        }
        if url is not None:
            result = import_catalog_asset(
                url, args.scene_id, category=args.category, source=source, **options
            )
        else:
            product = RetailerProduct.model_validate_json(args.product.read_text())
            result = import_product(product, args.scene_id, **options)
        if args.out:
            write_report(result, args.out)
    except CatalogError as exc:
        print(f"Import failed: {exc}.")
        return 1
    except (ValueError, OSError, sqlite3.Error) as exc:
        print(f"Import failed ({type(exc).__name__}); check the input, scene and data directory.")
        return 1
    asset = result.asset
    print(
        json.dumps(
            {
                "id": asset.id,
                "geometry": result.mesh_source,
                "bbox_m": asset.bbox_m.model_dump(),
                "dimension_source": asset.dimension_source,
                "correction_needed": asset.correction_needed,
                "ok": result.ok,
            }
        )
    )
    return 0 if result.ok and not asset.correction_needed else 2


if __name__ == "__main__":
    raise SystemExit(main())
