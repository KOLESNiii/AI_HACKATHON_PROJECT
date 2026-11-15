"""The same canonical, non-proxy mesh inventory used by the editor Library."""

import struct
from pathlib import Path

from contracts.schema import FurnitureItem, RoomScene

FIXTURE_ROOT = Path(__file__).resolve().parents[2] / "contracts" / "mock_room"
FLOORS = ("ground", "first", "second")
BROWSER_ROOT = "/api/reconstruction/mock-room"


def _has_mesh(root: Path, url: str) -> bool:
    if not url.startswith("/assets/"):
        return False
    directory = (root / "assets").resolve()
    path = (root / url.lstrip("/")).resolve()
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
    for floor in FLOORS:
        scene = RoomScene.model_validate_json(
            (FIXTURE_ROOT / f"three_floor_{floor}_scene.json").read_text(encoding="utf-8")
        )
        for item in scene.furniture:
            if item.is_fixed or item.is_proxy or not _has_mesh(FIXTURE_ROOT, item.glb_url):
                continue
            if item.id in assets:
                raise ValueError("Duplicate Library asset ID")
            assets[item.id] = item.model_copy(
                deep=True, update={"glb_url": BROWSER_ROOT + item.glb_url}
            )
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
