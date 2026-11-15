"""The same canonical, non-proxy mesh inventory used by the editor Library."""

import json
import struct
from pathlib import Path

from contracts.schema import FurnitureItem

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = PROJECT_ROOT / "frontend/src/data/ikeaCatalog.json"
ASSET_ROOT = PROJECT_ROOT / "frontend/public/catalog/ikea"
BROWSER_ROOT = "/catalog/ikea"


def _has_mesh(root: Path, url: str) -> bool:
    if not url.startswith(BROWSER_ROOT + "/assets/"):
        return False
    directory = (root / "assets").resolve()
    path = (root / url.removeprefix(BROWSER_ROOT + "/")).resolve()
    if path.parent != directory or path.suffix != ".glb":
        return False
    try:
        with path.open("rb") as source:
            header = source.read(12)
        return len(header) == 12 and struct.unpack("<4sII", header) == (
            b"glTF",
            2,
            path.stat().st_size,
        )
    except OSError:
        return False


def library_assets() -> dict[str, FurnitureItem]:
    """Copyable assets keyed by the Library SKU; metadata and mesh URLs stay authoritative.

    Recheck files on each request: missing/broken models are unavailable, never proxies.
    No provider, reconstruction-service import or network access is required.
    """
    assets = {}
    for entry in json.loads(CATALOG_PATH.read_text(encoding="utf-8")):
        item = FurnitureItem.model_validate(
            {**entry["asset"], "pose": {"x": 0, "z": 0, "yaw_deg": 0}}
        )
        if item.is_fixed or item.is_proxy or not _has_mesh(ASSET_ROOT, item.glb_url):
            continue
        if item.id in assets:
            raise ValueError("Duplicate Library asset ID")
        assets[item.id] = item
    return assets


def describe_library(assets: dict[str, FurnitureItem]) -> list[dict[str, object]]:
    return [
        {
            "asset_id": item.id,
            "name": item.name,
            "category": item.category,
            "bbox_m": item.bbox_m.model_dump(),
            "requires_front_clear_m": item.requires_front_clear_m,
            "dimension_source": item.dimension_source,
            "correction_needed": list(item.correction_needed),
        }
        for item in assets.values()
    ]
