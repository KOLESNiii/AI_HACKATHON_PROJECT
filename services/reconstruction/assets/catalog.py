"""Retailer products through the shared asset pipeline (#19).

A product is registered as an item with one view (its product image) in the same registry as
video furniture, under its own scene key, and then takes the same steps: `segment_furniture`,
`reconstruct_furniture`, `normalise_mesh` and the `deliver_furniture` checks. There is no
second generator or normaliser. The raw mesh is the retailer's own published model when there
is one (IKEA), otherwise the caller's mesh providers on the product image in turn (TRELLIS.2,
then SAM 3D; see `mesh_providers.catalog_mesh_providers`), otherwise the item is a labelled
proxy box.

Published dimensions are recorded as `catalog`. A product without them is `estimated` and asks
for `"dimensions"`: a size is never invented.
"""

from __future__ import annotations

import hashlib
import io
import json
import math
from collections.abc import Sequence
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit, urlunsplit

import cv2
import numpy as np
from numpy.typing import NDArray
from PIL import Image, UnidentifiedImageError
from pydantic import computed_field

from contracts.schema import BBoxM

from .asset_store import ASSET_URL_BASE, write_atomic
from .delivery import AssetCheck, deliver_furniture, inspect_asset
from .mask_providers import Mask, MaskError, MaskProvider
from .mesh_providers import MAX_MESH_BYTES, MeshError, MeshProvider, RawMesh, inspect_mesh
from .models import AssetEvidence, EvidenceFrame, FurnitureAsset
from .normalisation import MAX_TRIANGLES, PROVIDER_FRONT, NormalisationError, normalise_mesh
from .providers import RequestBudget
from .proxies import CATEGORY_SIZE_M, KnownDimensions, proxy_asset
from .reconstruction import reconstruct_furniture
from .registry import Registry
from .retailer import (
    CatalogError,
    Fetch,
    RetailerProduct,
    fetch_product,
    fetch_public,
)
from .segmentation import segment_furniture
from .selection_models import (
    Box,
    Category,
    Frame,
    ItemReconstruction,
    Record,
    RegistryState,
    SelectedObject,
    Sighting,
)
from .video import image_quality

MAX_IMAGE_BYTES = 15_000_000
MAX_IMAGE_PIXELS = 25_000_000
MAX_IMAGE_SIDE_PX = 2048
MIN_IMAGE_SIDE_PX = 64
BACKGROUND_TOLERANCE = 18
"""Per-channel difference from the border colour that still counts as background."""
PLAIN_BORDER_SHARE = 0.9
"""A product shot has a plain background when this share of its border is one colour."""
BOX_PAD = 0.02
INSET = 0.04
"""The item box always stays this far inside the image, so a mask provider sees background."""


def catalog_scene(scene_id: str) -> str:
    """The registry key of a scene's retailer products, apart from its video furniture: a
    video delivery never lists a catalog item, and neither renumbers the other."""
    if not scene_id.strip() or len(scene_id) > 190:
        raise ValueError("scene_id must contain 1..190 non-blank characters")
    return f"catalog:{scene_id}"


def catalog_id(product_url: str) -> str:
    """One product URL is one item ID, so importing it again updates the same item."""
    parts = urlsplit(product_url)
    canonical = urlunsplit(
        (parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip("/"), "", "")
    )
    return f"cat-{hashlib.sha256(canonical.encode()).hexdigest()[:12]}"


class ImageProvenance(Record):
    """The product image the item's view was made from."""

    url: str
    sha256: str
    """Of the bytes the retailer served."""
    path: str
    """The stored upright PNG, relative to the data directory."""
    size_px: tuple[int, int]


class CatalogImport(Record):
    """One imported product: the placed-ready asset, its checks, and where it all came from."""

    scene_id: str
    product: RetailerProduct
    """Source URL, image URL, model URLs, price and the published dimension text."""
    asset: FurnitureAsset
    check: AssetCheck
    image: ImageProvenance | None
    mesh_source: Literal["retailer_model", "generated", "proxy"]
    """Where the delivered geometry came from: the retailer's own model, a mesh generated from
    the product image, or a box."""
    warnings: list[str]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def ok(self) -> bool:
        """The delivered asset passed every check. A proxy or a requested correction is allowed
        and listed; see `asset.is_proxy` and `asset.correction_needed`."""
        return not self.check.problems


class RetailerModelProvider:
    """The retailer's own published model as the item's raw mesh. No inference and no charge.

    It fits the `MeshProvider` boundary so that a published model is stored, reused, normalised
    and checked exactly like a generated one.
    """

    name = "retailer"

    def __init__(self, urls: list[str], *, fetch: Fetch | None = None) -> None:
        self.remaining, self.fetch = list(urls), fetch or fetch_public
        self._seen: set[str] = set()

    def reconstruct(
        self,
        frame: Frame,
        image: NDArray[np.uint8],
        mask: Mask,
        registry: Registry,
        *,
        budget: RequestBudget | None = None,
    ) -> RawMesh:
        """The next published model that is usable and within the triangle budget.

        Each call moves on to the next candidate, so a caller whose model did not normalise
        (too large) asks again for the retailer's next, usually lighter, variant.
        """
        while self.remaining:
            url = self.remaining.pop(0)
            try:
                glb, _ = self.fetch(url, MAX_MESH_BYTES)
                digest = hashlib.sha256(glb).hexdigest()
                if digest in self._seen:  # Retailers list one file under several links.
                    continue
                self._seen.add(digest)
                # Also refuses Draco files: without a decoder they read as empty geometry.
                triangles, _ = inspect_mesh(glb)
            except (CatalogError, MeshError):
                continue
            if triangles <= MAX_TRIANGLES:
                return RawMesh(glb, {"model_url": url})
        raise MeshError(
            "no published retailer model is readable and within the mesh budget",
            kind="invalid_mesh",
        )


def _decode(data: bytes) -> NDArray[np.uint8]:
    """An upright BGR image; transparency becomes white, as in a product shot."""
    try:
        with Image.open(io.BytesIO(data)) as image:
            width, height = image.size
            if width * height > MAX_IMAGE_PIXELS:
                raise CatalogError("the product image has too many pixels")
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError) as exc:
        raise CatalogError("the product image could not be read safely") from exc
    pixels = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_UNCHANGED)
    if pixels is None or pixels.dtype != np.uint8:
        raise CatalogError("the product image could not be read")
    if pixels.ndim == 2:
        pixels = cv2.cvtColor(pixels, cv2.COLOR_GRAY2BGR)
    elif pixels.shape[2] == 4:
        alpha = pixels[:, :, 3:4].astype(np.float32) / 255
        pixels = (pixels[:, :, :3] * alpha + 255 * (1 - alpha)).astype(np.uint8)
    height, width = pixels.shape[:2]
    if min(width, height) < MIN_IMAGE_SIDE_PX:
        raise CatalogError("the product image is too small")
    if max(width, height) > MAX_IMAGE_SIDE_PX:
        share = MAX_IMAGE_SIDE_PX / max(width, height)
        size = (max(1, round(width * share)), max(1, round(height * share)))
        pixels = cv2.resize(pixels, size, interpolation=cv2.INTER_AREA)
    return np.ascontiguousarray(pixels[:, :, :3], dtype=np.uint8)


def item_box(image: NDArray[np.uint8]) -> tuple[Box, bool]:
    """Where the product is in its image, and whether that was read off a plain background.

    On a plain background the box is the padded extent of everything that differs from the
    border colour. Otherwise it is the image less a margin, and the mask may take in
    surroundings.
    """
    height, width = image.shape[:2]
    border = np.concatenate([image[0], image[-1], image[:, 0], image[:, -1]]).astype(np.int16)
    colour = np.median(border, axis=0)
    plain = np.mean(np.abs(border - colour).max(axis=1) <= BACKGROUND_TOLERANCE)
    x0, y0, x1, y1 = INSET, INSET, 1 - INSET, 1 - INSET
    found = False
    if plain >= PLAIN_BORDER_SHARE:
        differs = np.abs(image.astype(np.int16) - colour).max(axis=2) > BACKGROUND_TOLERANCE
        differs = cv2.morphologyEx(differs.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3)))
        ys, xs = np.nonzero(differs)
        if len(xs) >= 0.01 * width * height:
            found = True
            x0 = max(INSET / 4, xs.min() / width - BOX_PAD)
            y0 = max(INSET / 4, ys.min() / height - BOX_PAD)
            x1 = min(1 - INSET / 4, (xs.max() + 1) / width + BOX_PAD)
            y1 = min(1 - INSET / 4, (ys.max() + 1) / height + BOX_PAD)
    return Box(x=x0, y=y0, width=x1 - x0, height=y1 - y0), found


def _store_image(
    data_dir: Path, url: str, fetch: Fetch, warnings: list[str]
) -> tuple[ImageProvenance, Frame, Box] | None:
    """Download the product image and store it as the item's one source frame."""
    try:
        data, _ = fetch(url, MAX_IMAGE_BYTES)
        image = _decode(data)
    except CatalogError as exc:
        warnings.append(f"product image unavailable ({exc})")
        return None
    digest = hashlib.sha256(data).hexdigest()
    path = f"catalog/images/{digest}.png"
    ok, encoded = cv2.imencode(".png", image)
    if not ok:
        warnings.append("product image could not be stored")
        return None
    if not (data_dir / path).is_file():  # Named by content: an existing file is the same image.
        write_atomic(data_dir / path, encoded.tobytes())
    height, width = image.shape[:2]
    box, plain = item_box(image)
    if not plain:
        warnings.append(
            "the product image has no plain background; its mask may include surroundings"
        )
    frame = Frame(
        key=f"{digest}:0:0",
        source_id=digest,
        frame_index=0,
        pts=0,
        timestamp_s=0,
        image_size_px=(width, height),
        image_path=path,
        quality=image_quality(image),
    )
    return ImageProvenance(url=url, sha256=digest, path=path, size_px=(width, height)), frame, box


def _along_mesh(bbox: BBoxM, extents: tuple[float, float, float]) -> BBoxM:
    """Published width and depth, assigned to X and Z of a shape with these extents.

    Retailers name a table's or a desk's long side its length or depth whichever way it faces
    (IKEA: "width 60, depth 140" for a desk). The mesh fixes which side is the front, so the
    footprint follows the mesh's proportions; without a mesh, the category's usual ones.
    """
    shape = math.log(extents[0] / extents[2])
    as_published = abs(shape - math.log(bbox.width / bbox.depth))
    exchanged = abs(shape - math.log(bbox.depth / bbox.width))
    if exchanged < as_published:
        return BBoxM(width=bbox.depth, height=bbox.height, depth=bbox.width)
    return bbox


def _normalises(item: ItemReconstruction, known: KnownDimensions | None, data_dir: Path) -> bool:
    """Whether the item's stored raw mesh meets the furniture profile at its size."""
    if item.mesh is None:
        return False
    try:
        normalise_mesh(
            data_dir / item.mesh.mesh_path,
            category=item.proxy.category,
            target_bbox=None if known is None else known.bbox_m,
            data_dir=data_dir,
            front=PROVIDER_FRONT.get(item.mesh.provider),
            preserve_scale=item.mesh.provider == "retailer",
        )
    except NormalisationError:
        return False
    return True


CARD_SHARE = 0.1
"""A generated mesh whose thinner horizontal side is under this share of its longest side is a
cut-out card, not furniture. Image-to-3D models return one when they cannot infer depth."""
FLAT_CATEGORIES: frozenset[Category] = frozenset({"other", "fixture"})
"""Categories that may truly be that thin (a mirror, a picture, a rug stood on edge)."""


def card_like(item: ItemReconstruction) -> bool:
    """Whether the item's generated mesh is a flat card instead of a piece of furniture."""
    if item.mesh is None or item.mesh.provider == "retailer":
        return False
    if item.proxy.category in FLAT_CATEGORIES:
        return False
    width, height, depth = item.mesh.extents
    return min(width, depth) < CARD_SHARE * max(width, height, depth)


def _relabel(asset: FurnitureAsset, product: RetailerProduct) -> FurnitureAsset:
    """The pipeline's asset, carrying the product's own source, link and price."""
    return FurnitureAsset.model_validate(
        {
            **asset.model_dump(),
            "source": product.source,
            "product_url": product.product_url,
            "price_gbp": product.price_gbp,
        }
    )


def _record_path(data_dir: Path, scene_id: str, item_id: str = "") -> Path:
    folder = data_dir / "catalog" / hashlib.sha256(scene_id.encode()).hexdigest()[:16]
    return folder / f"{item_id}.json" if item_id else folder


def import_product(
    product: RetailerProduct,
    scene_id: str,
    *,
    data_dir: Path,
    dimensions: KnownDimensions | None = None,
    mask_provider: MaskProvider | None = None,
    mesh_provider: MeshProvider | Sequence[MeshProvider] | None = None,
    fetch: Fetch | None = None,
    max_requests: int = 2,
    url_base: str = ASSET_URL_BASE,
) -> CatalogImport:
    """Turn one retailer product into a furniture asset through the shared pipeline.

    `product` comes from `retailer.fetch_product` (a pasted URL) or from a search result. Its
    published dimensions size the asset as `catalog`; `dimensions` (a user's correction)
    overrides them. Without either, the size is a category estimate that asks for
    `"dimensions"`.

    Geometry, first that works: the retailer's published model; each `mesh_provider` in turn on
    the product image (paid, so only when passed; a flat card is not accepted while another
    provider is left); a labelled proxy box. A provider that timed out ends the chain: its
    request is still running and the next import collects it without a new charge. Masks use
    `mask_provider`, or local GrabCut offline. A failed download, mask, mesh or check never
    raises and never drops the item: it is delivered as its proxy, with the reason in
    `warnings`. The result is also stored, see `imported_assets`. Raises ValueError for an
    unusable scene ID.
    """
    scene_key = catalog_scene(scene_id)
    data_dir = data_dir.resolve()
    fetch = fetch or fetch_public
    item_id = catalog_id(product.product_url)
    generators: list[MeshProvider] = (
        []
        if mesh_provider is None
        else list(mesh_provider)
        if isinstance(mesh_provider, Sequence)
        else [mesh_provider]
    )
    warnings = list(product.warnings)
    known = dimensions or (
        KnownDimensions(bbox_m=product.dimensions.bbox_m, source="catalog")
        if product.dimensions is not None
        else None
    )
    stored = (
        _store_image(data_dir, product.image_url, fetch, warnings)
        if product.image_url is not None
        else None
    )
    mesh_source: Literal["retailer_model", "generated", "proxy"] = "proxy"

    def follow(extents: tuple[float, float, float], what: str) -> None:
        """Assign the published width and depth to the axes of the shape being delivered."""
        nonlocal known
        if known is None or known.source != "catalog":
            return  # A user's own size is taken as given.
        turned = _along_mesh(known.bbox_m, extents)
        if turned != known.bbox_m:
            known = KnownDimensions(bbox_m=turned, source="catalog")
            warnings.append(f"the published width and depth were exchanged to follow {what}")

    typical = "the category's usual shape: there is no model to say which side is the front"
    if stored is None:
        # Nothing to register a view from, so nothing to segment or reconstruct.
        if product.model_urls:
            warnings.append("the published model was not used: the product has no usable image")
        follow(CATEGORY_SIZE_M[product.category], typical)
        evidence = AssetEvidence(
            frames=[EvidenceFrame(frame_index=0, timestamp_s=0)], primary_frame_index=0
        )
        asset = proxy_asset(
            item_id, product.name, product.category, evidence,
            data_dir=data_dir, known=known, url_base=url_base,
        )  # fmt: skip
        image = None
    else:
        image, frame, box = stored
        registry = Registry(data_dir, namespace=scene_key)

        def register(state: RegistryState) -> None:
            state.frames[frame.key] = frame
            current = state.objects.get(item_id)
            sighting = Sighting(frame_key=frame.key, box=box, quality=frame.quality)
            if current is not None and current.sightings == [sighting]:
                # The same image: keep its stored mask and mesh.
                current.name, current.category = product.name, product.category
                return
            state.objects[item_id] = SelectedObject(
                id=item_id,
                name=product.name,
                category=product.category,
                appearance=product.name,
                sightings=[sighting],
                selected_views=[frame.key],
            )

        registry.update(scene_key, register)
        # Upgrade earlier offline imports, but keep successful SAM masks cached.
        existing = registry.load(scene_key).objects[item_id]
        upgrade_masks = (
            mask_provider is not None
            and mask_provider.method == "sam3"
            and any(mask.method == "grabcut" for mask in existing.masks)
        )
        try:
            masks = segment_furniture(
                scene_key, data_dir=data_dir, provider=mask_provider,
                object_ids=[item_id], max_requests=max_requests, replace=upgrade_masks,
            )  # fmt: skip
            warnings += [f"mask: {m.reason}" for m in masks.missing] + masks.warnings
            if masks.missing and mask_provider is not None:
                # Failed live requests must not prevent published models or proxy delivery.
                warnings.append(
                    "Live segmentation failed; using an existing mask or local GrabCut."
                )
                local = segment_furniture(
                    scene_key,
                    data_dir=data_dir,
                    object_ids=[item_id],
                    max_requests=max_requests,
                )
                warnings += [f"mask: {m.reason}" for m in local.missing] + local.warnings
        except MaskError as exc:
            warnings.append(f"mask: {exc}")

        def reconstruct(provider: MeshProvider, replace: bool) -> ItemReconstruction:
            item = reconstruct_furniture(
                scene_key, data_dir=data_dir, provider=provider, object_ids=[item_id],
                replace=replace, max_requests=max_requests, url_base=url_base,
            ).items[0]  # fmt: skip
            if item.mesh is not None:
                follow(item.mesh.extents, "the model's own axes")
            return item

        # A stored mesh is reused; otherwise the retailer's models are tried best first until
        # one fits the furniture profile, and only then is a (paid) generated mesh asked for.
        published = RetailerModelProvider(product.model_urls, fetch=fetch)
        item = reconstruct(published, False)
        while not _normalises(item, known, data_dir) and published.remaining:
            item = reconstruct(published, True)
        if item.failure is not None and product.model_urls:
            warnings.append(f"mesh: {item.failure.reason}")
        for provider in generators:
            if _normalises(item, known, data_dir) and not card_like(item):
                break
            item = reconstruct(provider, item.mesh is not None)
            if item.failure is not None:
                warnings.append(f"mesh ({provider.name}): {item.failure.reason}")
                if item.failure.kind == "timeout":
                    break
            elif card_like(item):
                warnings.append(f"mesh ({provider.name}): a flat card, not a 3D shape")
        if item.mesh is None:
            follow(CATEGORY_SIZE_M[product.category], typical)
        size = {item_id: known} if known is not None else None
        delivery = deliver_furniture(
            scene_key, data_dir=data_dir, dimensions=size, object_ids=[item_id], url_base=url_base
        )
        asset = delivery.assets[0]
        warnings += delivery.warnings
        made_by = registry.load(scene_key).objects[item_id].mesh
        if not asset.is_proxy and made_by is not None:
            mesh_source = "retailer_model" if made_by.provider == "retailer" else "generated"
        elif delivery.checks[0].fallback_reason:
            warnings.append(f"proxy delivered: {delivery.checks[0].fallback_reason}")
    asset = _relabel(asset, product)
    if "dimensions" in asset.correction_needed:
        warnings.append(
            "the size is not confirmed by the retailer's published dimensions; "
            "ask the user to correct it"
        )
    result = CatalogImport(
        scene_id=scene_id,
        product=product,
        asset=asset,
        check=inspect_asset(asset, data_dir=data_dir, url_base=url_base),
        image=image,
        mesh_source=mesh_source,
        warnings=list(dict.fromkeys(warnings)),
    )
    write_atomic(
        _record_path(data_dir, scene_id, item_id), result.model_dump_json(indent=2).encode()
    )
    return result


def import_catalog_asset(
    product_url: str,
    scene_id: str,
    *,
    data_dir: Path,
    category: Category | None = None,
    source: Literal["url_import", "catalog_search"] = "url_import",
    dimensions: KnownDimensions | None = None,
    mask_provider: MaskProvider | None = None,
    mesh_provider: MeshProvider | Sequence[MeshProvider] | None = None,
    fetch: Fetch | None = None,
    max_requests: int = 2,
    url_base: str = ASSET_URL_BASE,
) -> CatalogImport:
    """Import the product on a retailer page: read the page, then `import_product`.

    `source="catalog_search"` marks a link picked from search results. Raises CatalogError when
    the URL is not a public page or the page names no product; everything after that follows
    `import_product` and returns at least a proxy.
    """
    catalog_scene(scene_id)  # Refuse a bad scene before any download.
    product = fetch_product(product_url, category=category, source=source, fetch=fetch)
    return import_product(
        product,
        scene_id,
        data_dir=data_dir,
        dimensions=dimensions,
        mask_provider=mask_provider,
        mesh_provider=mesh_provider,
        fetch=fetch,
        max_requests=max_requests,
        url_base=url_base,
    )


def imported_assets(scene_id: str, *, data_dir: Path) -> list[CatalogImport]:
    """Every product imported into a scene, in item-ID order, as stored by the last import of
    each. Offline: reads the stored records and submits nothing."""
    folder = _record_path(data_dir.resolve(), scene_id)
    records = [json.loads(path.read_text()) for path in sorted(folder.glob("cat-*.json"))]
    # `ok` is computed from the check and is not an input.
    return [
        CatalogImport.model_validate({k: v for k, v in r.items() if k != "ok"}) for r in records
    ]
