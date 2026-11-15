"""Fetch a balanced, offline IKEA library using only published retailer meshes.

Run: uv run --extra reconstruction --with DracoPy==2.2.0 python -m scripts.cache_ikea_library
No fal calls or credentials. Downloads are cached in /tmp/spaceshift-ikea-library.
Only complete products with published dimensions and validated meshes are selected.
"""

from __future__ import annotations

import hashlib
import io
import json
import struct
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path

import DracoPy
import numpy as np
from PIL import Image

from services.reconstruction.assets.catalog import _along_mesh
from services.reconstruction.assets.delivery import inspect_asset
from services.reconstruction.assets.mesh_providers import MeshError, inspect_mesh
from services.reconstruction.assets.models import AssetEvidence, EvidenceFrame, FurnitureAsset
from services.reconstruction.assets.normalisation import normalise_mesh
from services.reconstruction.assets.retailer import fetch_product, fetch_public, search_ikea

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "frontend/public/catalog/ikea"
DOWNLOADS = Path("/tmp/spaceshift-ikea-library")
URL_BASE = "/catalog/ikea/assets"
QUERIES = {
    "bed": [
        "bed frame",
        "MALM bed",
        "SLATTUM",
        "HEMNES bed",
        "BRIMNES bed",
        "TARVA bed",
        "SONGESAND bed",
        "IDANAS bed",
        "TONSTAD bed",
        "VEVELSTAD bed",
        "NEIDEN bed",
        "single bed",
        "double bed",
        "SLATTUM bed",
        "day bed",
    ],
    "desk": ["desk", "MICKE", "desk table", "TROTTEN", "BEKANT", "LAGKAPTEN"],
    "chair": ["chair", "office chair", "armchair", "dining chair"],
    "table": ["coffee table", "side table", "dining table", "LACK"],
    "wardrobe": ["wardrobe", "PAX wardrobe", "KLEPPSTAD", "BRIMNES wardrobe", "RAKKESTAD"],
    "sofa": ["sofa", "two-seat sofa", "three-seat sofa", "KLIPPAN", "KIVIK", "VIMLE"],
    "storage": ["bookcase", "chest of drawers", "cabinet", "shelving unit"],
    "other": ["floor lamp", "plant pot", "room divider", "mirror", "coat stand", "stool"],
}


def fetch(url: str, limit: int) -> tuple[bytes, str]:
    """Reuse bounded, public-only downloads; keep raw evidence outside the project."""
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    path = DOWNLOADS / hashlib.sha256(url.encode()).hexdigest()
    if path.exists():
        data = path.read_bytes()
        if len(data) > limit:
            raise ValueError("cached response exceeds limit")
        return data, url
    data, final = fetch_public(url, limit, timeout_s=45)
    path.write_bytes(data)
    return data, final


def unpack_model(data: bytes) -> bytes:
    """Expand retailer Draco geometry and expose WebP sources to the shared reader.

    Some IKEA `/glb/` URLs contain Draco too. Decode by glTF attribute unique ID,
    preserving materials, UVs, tangents and node transforms before normalisation.
    """
    length, kind = struct.unpack_from("<II", data, 12)
    if kind != 0x4E4F534A:
        raise ValueError("model has no glTF JSON chunk")
    document = json.loads(data[20 : 20 + length])
    offset = 20 + length
    bin_length, bin_kind = struct.unpack_from("<II", data, offset)
    if bin_kind != 0x004E4942:
        raise ValueError("model has no embedded binary chunk")
    binary = bytearray(data[offset + 8 : offset + 8 + bin_length])
    types = {5121: "u1", 5123: "<u2", 5125: "<u4", 5126: "<f4"}

    def write_accessor(index: int, values: np.ndarray) -> None:
        accessor = document["accessors"][index]
        values = np.asarray(values, dtype=types[accessor["componentType"]])
        binary.extend(b"\0" * (-len(binary) % 4))
        view = {"buffer": 0, "byteOffset": len(binary), "byteLength": values.nbytes}
        binary.extend(values.tobytes())
        accessor["bufferView"] = len(document["bufferViews"])
        accessor["byteOffset"] = 0
        document["bufferViews"].append(view)
        if accessor["type"] != "SCALAR":
            accessor["min"] = values.min(axis=0).tolist()
            accessor["max"] = values.max(axis=0).tolist()

    for mesh in document.get("meshes", []):
        for primitive in mesh["primitives"]:
            compressed = primitive.get("extensions", {}).pop("KHR_draco_mesh_compression", None)
            if compressed is None:
                continue
            view = document["bufferViews"][compressed["bufferView"]]
            start = view.get("byteOffset", 0)
            decoded = DracoPy.decode(bytes(binary[start : start + view["byteLength"]]))
            write_accessor(primitive["indices"], decoded.faces.flatten())
            for name, unique_id in compressed["attributes"].items():
                attribute = decoded.get_attribute_by_unique_id(unique_id)
                write_accessor(primitive["attributes"][name], attribute["data"])
    for texture in document.get("textures", []):
        webp = texture.get("extensions", {}).pop("EXT_texture_webp", None)
        if webp:
            texture["source"] = webp["source"]
    for key in ("extensionsUsed", "extensionsRequired"):
        document[key] = [
            name
            for name in document.get(key, [])
            if name not in ("KHR_draco_mesh_compression", "EXT_texture_webp")
        ]
    document["buffers"][0]["byteLength"] = len(binary)
    header = json.dumps(document, separators=(",", ":")).encode()
    header += b" " * (-len(header) % 4)
    binary.extend(b"\0" * (-len(binary) % 4))
    total = 12 + 8 + len(header) + 8 + len(binary)
    return (
        struct.pack("<III", 0x46546C67, 2, total)
        + struct.pack("<II", len(header), 0x4E4F534A)
        + header
        + struct.pack("<II", len(binary), 0x004E4942)
        + binary
    )


def prepare(candidate: tuple[str, str]) -> dict | None:
    url, category = candidate
    try:
        product = fetch_product(url, source="catalog_search", fetch=fetch)
        if product.category != category:
            return None
        if category == "bed" and (
            "frame" not in product.name.lower() or "storage box" in product.name.lower()
        ):
            return None  # Bed bases, storage boxes and canopies are accessories.
        if product.dimensions is None or product.image_url is None:
            return None
        for model_url in product.model_urls:
            try:
                data, _ = fetch(model_url, 20_000_000)
                data = unpack_model(data)
                _, extents = inspect_mesh(data)
                raw = DOWNLOADS / (hashlib.sha256(model_url.encode()).hexdigest() + ".glb")
                raw.write_bytes(data)
                mesh = normalise_mesh(
                    raw,
                    category=category,
                    target_bbox=_along_mesh(product.dimensions.bbox_m, extents),
                    data_dir=OUTPUT,
                    front="+z",
                    preserve_scale=True,
                    url_base=URL_BASE,
                )
                if mesh.correction_needed:
                    continue  # Reject dimensions inconsistent with the published model.
                sku = "ikea-" + url.rstrip("/").split("-")[-1]
                asset = FurnitureAsset(
                    **mesh.model_dump(),
                    id=sku,
                    name=product.name,
                    category=category,
                    source="catalog_search",
                    product_url=product.product_url,
                    price_gbp=product.price_gbp,
                    dimension_source="catalog",
                    evidence=AssetEvidence(
                        frames=[EvidenceFrame(frame_index=0, timestamp_s=0)], primary_frame_index=0
                    ),
                )
                check = inspect_asset(asset, data_dir=OUTPUT, url_base=URL_BASE)
                if check.problems:
                    continue
                image_data, _ = fetch(product.image_url, 15_000_000)
                with Image.open(io.BytesIO(image_data)) as image:
                    image.thumbnail((320, 320))
                    image_path = OUTPUT / "images" / f"{sku}.webp"
                    image_path.parent.mkdir(parents=True, exist_ok=True)
                    image.convert("RGB").save(image_path, "WEBP", quality=85)
                return {
                    "sku": sku,
                    "name": product.name,
                    "category": category,
                    "bbox_m": mesh.bbox_m.model_dump(),
                    "price_gbp": product.price_gbp,
                    "product_url": product.product_url,
                    "image_url": f"/catalog/ikea/images/{sku}.webp",
                    "asset": asset.model_dump(exclude={"evidence"}),
                    "provenance": {
                        "fetched_at": datetime.now(UTC).isoformat(),
                        "model_url": model_url,
                        "image_url": product.image_url,
                        "dimensions": product.dimensions.model_dump(),
                        "checks": check.model_dump(),
                    },
                }
            except (ValueError, OSError, MeshError) as exc:
                print(f"Skip model {url}: {exc}", flush=True)
    except (ValueError, OSError) as exc:
        print(f"Skip product {url}: {exc}", flush=True)
    return None


def main() -> None:
    progress = DOWNLOADS / "selected.json"
    items = json.loads(progress.read_text()) if progress.exists() else []
    seen = {item["product_url"] for item in items}
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for category, queries in QUERIES.items():
        target = 9 if category == "other" else 13
        selected = [item for item in items if item["category"] == category]
        for query in queries:
            if len(selected) >= target:
                break
            candidates = search_ikea(query, limit=24, fetch=fetch)
            urls = [item.product_url for item in candidates if item.product_url not in seen]
            seen.update(urls)
            with ThreadPoolExecutor(max_workers=4) as pool:
                for result in pool.map(prepare, [(url, category) for url in urls]):
                    if result is not None and len(selected) < target:
                        selected.append(result)
                        items.append(result)
                        progress.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n")
                        print(f"{category} {len(selected)}/{target}: {result['name']}", flush=True)
        if len(selected) != target:
            raise RuntimeError(f"Not enough usable {category} products: {len(selected)}/{target}")
    # Keep only selected files; workers may have prepared surplus candidates.
    keep = {item["asset"]["glb_url"].split("/")[-1] for item in items}
    for path in (OUTPUT / "assets").glob("*.glb"):
        if path.name not in keep:
            path.unlink()
    keep_images = {item["image_url"].split("/")[-1] for item in items}
    for path in (OUTPUT / "images").glob("*.webp"):
        if path.name not in keep_images:
            path.unlink()
    path = ROOT / "frontend/src/data/ikeaCatalog.json"
    path.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n")
    print(f"Stored {len(items)} IKEA products", flush=True)


if __name__ == "__main__":
    main()
