"""Retailer products through the shared asset pipeline (Dev 2.7, #19): source, image and
dimension provenance are kept, the same normaliser and checks run, and a missing size asks for
a correction. Offline: every retailer response is a local double."""

from __future__ import annotations

import io
import json
from pathlib import Path

import cv2
import numpy as np
import pytest
import trimesh
from test_reconstruction import MeshDouble

from contracts.schema import GLB_BBOX_TOLERANCE_M, BBoxM
from services.reconstruction.assets import retailer
from services.reconstruction.assets.catalog import (
    RetailerModelProvider,
    catalog_id,
    catalog_scene,
    import_catalog_asset,
    import_product,
    imported_assets,
    item_box,
)
from services.reconstruction.assets.delivery import deliver_furniture
from services.reconstruction.assets.import_product import main
from services.reconstruction.assets.mesh_providers import MeshError
from services.reconstruction.assets.normalisation import MAX_BYTES, normalise_mesh
from services.reconstruction.assets.proxies import KnownDimensions
from services.reconstruction.assets.retailer import (
    CatalogError,
    RetailerProduct,
    fetch_product,
    guess_category,
    parse_product_page,
    search_ikea,
    sides_from_text,
)

URL = "https://shop.example/p/desk-123/"
IMAGE = "https://shop.example/images/desk.png"
MODEL = "https://cdn.example/models/desk.glb"
DRACO = "https://cdn.example/models/glb_draco/desk.glb"


def page(product: dict | None = None, *, model: bool = True, body: str = "") -> bytes:
    """A retailer page the way IKEA writes one: schema.org Product and 3DModel JSON-LD."""
    described = {
        "@context": "https://schema.org/",
        "@type": "Product",
        "name": "MICKE Desk - white",
        "category": "Home office desks",
        "image": [{"@type": "ImageObject", "contentUrl": "/images/desk.png"}],
        "width": "105 cm",
        "height": "75 cm",
        "depth": "50 cm",
        "offers": {"@type": "Offer", "price": "79", "priceCurrency": "GBP"},
        **(product or {}),
    }
    blocks = [{k: v for k, v in described.items() if v is not None}]
    if model:
        encodings = [
            {"contentUrl": DRACO, "encodingFormat": "model/gltf-binary"},
            {"contentUrl": MODEL, "encodingFormat": "model/gltf-binary"},
            {"contentUrl": MODEL.replace(".glb", ".gltf"), "encodingFormat": "model/gltf"},
        ]
        blocks.append({"@type": "3DModel", "encoding": encodings})
    scripts = "".join(
        f'<script type="application/ld+json">{json.dumps(block)}</script>' for block in blocks
    )
    return f"<html><head><title>Shop</title>{scripts}</head><body>{body}</body></html>".encode()


def product_image(*, plain: bool = True) -> bytes:
    """A dark desk-sized blob on white, or a busy room photo."""
    if plain:
        image = np.full((300, 400, 3), 255, np.uint8)
        image[90:230, 80:330] = (60, 90, 140)
    else:
        image = np.random.default_rng(0).integers(0, 255, (300, 400, 3), dtype=np.uint8)
    ok, encoded = cv2.imencode(".png", image)
    assert ok
    return encoded.tobytes()


def model_glb(extents=(1.049, 0.754, 0.5), *, subdivisions: int = 0) -> bytes:
    """A published model in metres, centred like a retailer's, not on the floor."""
    mesh = trimesh.creation.box(extents=extents)
    for _ in range(subdivisions):
        mesh = mesh.subdivide()
    glb = mesh.export(file_type="glb")
    assert isinstance(glb, bytes)
    return glb


class Web:
    """The retailer: URL -> bytes. Records what was downloaded."""

    def __init__(self, **overrides: bytes | None) -> None:
        self.pages: dict[str, bytes | None] = {
            URL: page(),
            IMAGE: product_image(),
            MODEL: model_glb(),
            DRACO: b"glTF-but-draco",
            **{{"page": URL, "image": IMAGE, "model": MODEL}[k]: v for k, v in overrides.items()},
        }
        self.calls: list[str] = []

    def __call__(self, url: str, limit: int) -> tuple[bytes, str]:
        self.calls.append(url)
        body = self.pages.get(url)
        if body is None:
            raise CatalogError("the retailer answered HTTP 404")
        assert len(body) <= limit
        return body, url


def bounds(tmp_path: Path, glb_url: str) -> np.ndarray:
    data = (tmp_path / "assets" / glb_url.rsplit("/", 1)[1]).read_bytes()
    return np.asarray(trimesh.load_scene(io.BytesIO(data), file_type="glb").bounds)


# --- Reading a product ----------------------------------------------------------------------


def test_page_keeps_source_image_models_price_and_published_dimensions() -> None:
    product = fetch_product(URL, fetch=Web())
    assert product.product_url == URL and product.source == "url_import"
    assert product.retailer == "shop.example"
    assert product.name == "MICKE Desk - white" and product.category == "desk"
    assert product.image_url == IMAGE, "relative links resolve against the page"
    assert product.model_urls == [MODEL, DRACO], "binary glTF only, Draco last"
    assert product.price_gbp == 79
    assert product.dimensions is not None
    assert product.dimensions.bbox_m == BBoxM(width=1.05, height=0.75, depth=0.5)
    assert product.dimensions.found_in == "structured_data"
    assert product.dimensions.text == "width: 105 cm; height: 75 cm; depth: 50 cm"
    assert product.warnings == []


def test_units_and_quantitative_values_become_metres() -> None:
    quantity = {"@type": "QuantitativeValue", "value": 1200, "unitCode": "MMT"}
    product = parse_product_page(
        page(
            {"width": quantity, "height": "29.5 in", "depth": {"value": "0.6", "unitText": "m"}}
        ).decode(),
        URL,
    )
    assert product.dimensions is not None
    assert product.dimensions.bbox_m == BBoxM(width=1.2, height=0.7493, depth=0.6)


def test_page_text_only_fills_what_structured_data_leaves_out() -> None:
    # IKEA's sofa pages: no schema.org height, and a list of part sizes next to the real ones.
    rows = [
        ("Armrest width", "13 cm"),
        ("Seat height", "46 cm"),
        ("Width", "999 cm"),
        ("Free height under furniture", "17 cm"),
        ("Height including back cushions", "90 cm"),
    ]
    body = "".join(f"<li><span>{name}</span><span>{value}</span></li>" for name, value in rows)
    product = parse_product_page(
        page({"name": "2-seat sofa", "width": "164 cm", "height": None, "depth": "88 cm"},
             body=body).decode(), URL,
    )  # fmt: skip
    assert product.category == "sofa" and product.dimensions is not None
    assert product.dimensions.bbox_m == BBoxM(width=1.64, height=0.9, depth=0.88)
    assert product.dimensions.found_in == "page_text"
    assert "Height including back cushions 90 cm" in product.dimensions.text


def test_labelled_text_sizes_are_read_and_unlabelled_ones_are_not() -> None:
    assert {k: v[0] for k, v in sides_from_text("Size: W120 x D60 x H75cm").items()} == {
        "width": 1.2, "depth": 0.6, "height": 0.75,
    }  # fmt: skip
    prose = "Width: 1.2 m. Height (max): 75 cm; Depth 600mm"
    assert {k: v[0] for k, v in sides_from_text(prose).items()} == {
        "width": 1.2, "height": 0.75, "depth": 0.6,
    }  # fmt: skip
    assert sides_from_text("Desk 120 x 60 x 75 cm, seat width 40 cm, widths: 3") == {}


@pytest.mark.parametrize(
    ("changes", "warning"),
    [
        ({"height": None}, "incomplete: no height"),
        ({"width": "105"}, "incomplete: no width"),  # No unit: cm or mm?
        ({"depth": "5000 cm"}, "implausible"),
    ],
)
def test_missing_or_unusable_dimensions_are_not_invented(changes: dict, warning: str) -> None:
    product = parse_product_page(page(changes).decode(), URL)
    assert product.dimensions is None
    assert any(warning in note for note in product.warnings)
    assert any("ask the user" in note for note in product.warnings)


def test_a_combination_is_priced_by_its_current_price_specification() -> None:
    specs = [
        {
            "price": "140",
            "priceCurrency": "GBP",
            "priceType": "https://schema.org/StrikethroughPrice",
        },
        {"price": "125", "priceCurrency": "GBP"},
    ]
    product = parse_product_page(page({"offers": {"priceSpecification": specs}}).decode(), URL)
    assert product.price_gbp == 125


def test_page_without_structured_data_uses_meta_tags_and_model_viewer() -> None:
    html = (
        '<html><head><meta property="og:title" content="Oak bookcase">'
        '<meta property="og:image" content="https://shop.example/b.jpg">'
        '<meta property="product:price:amount" content="1,250.00">'
        '<meta property="product:price:currency" content="EUR"></head><body>'
        '<model-viewer src="/m/bookcase.glb"></model-viewer>'
        "<p>Width: 80 cm</p><p>Height: 202 cm</p><p>Depth: 28 cm</p>"
        "<script>var width = '13 cm'</script></body></html>"
    )
    product = parse_product_page(html, URL)
    assert product.name == "Oak bookcase" and product.category == "storage"
    assert product.image_url == "https://shop.example/b.jpg"
    assert product.model_urls == ["https://shop.example/m/bookcase.glb"]
    assert product.price_gbp is None and any("not in GBP" in w for w in product.warnings)
    assert product.dimensions is not None
    assert product.dimensions.bbox_m == BBoxM(width=0.8, height=2.02, depth=0.28)


def test_a_page_that_names_no_product_is_refused() -> None:
    with pytest.raises(CatalogError, match="does not name a product"):
        parse_product_page("<html><body>Not found</body></html>", URL)
    with pytest.raises(CatalogError, match="category"):
        parse_product_page(page().decode(), URL, category="lamp")  # type: ignore[arg-type]


def test_categories_come_from_the_products_own_words() -> None:
    assert guess_category("Bedside table") == "storage"
    assert guess_category("KIVIK 3-seat sofa-bed") == "sofa"
    assert guess_category("Thing", "Dining tables") == "table"
    assert guess_category("MALM Bed frame, high") == "bed"
    assert guess_category("Floor lamp") == "other"


@pytest.mark.parametrize(
    "url",
    [
        "file:///etc/passwd",
        "ftp://shop.example/x",
        "http://127.0.0.1/admin",
        "http://localhost:8001/scenes",
        "http://169.254.169.254/latest/meta-data",
        "http://10.0.0.5/",
        "https://user:pw@8.8.8.8/",
    ],
)
def test_only_public_web_addresses_are_fetched(url: str) -> None:
    with pytest.raises(CatalogError):
        retailer.fetch_public(url, 1000)
    with pytest.raises(CatalogError):
        fetch_product(url, fetch=Web())


def test_ikea_search_results_keep_their_source_and_ask_for_the_page() -> None:
    def entry(name: str, kind: str, price: dict) -> dict:
        return {"product": {"name": name, "typeName": kind, "salesPrice": price,
                            "pipUrl": f"https://www.ikea.com/gb/en/p/{name.lower()}/",
                            "mainImageUrl": "https://www.ikea.com/i.jpg",
                            "itemMeasureReferenceText": "140x60 cm"}}  # fmt: skip

    items = [
        entry("LAGKAPTEN", "Desk", {"currencyCode": "GBP", "numeral": 135.0}),
        {"product": {"name": "broken"}},
        entry("KALLAX", "Shelving unit", {"currencyCode": "EUR", "numeral": 40}),
    ]
    body = json.dumps({"searchResultPage": {"products": {"main": {"items": items}}}}).encode()
    asked: list[str] = []

    def fetch(url: str, limit: int) -> tuple[bytes, str]:
        asked.append(url)
        return body, url

    found = search_ikea("  office   desk ", fetch=fetch)
    assert "q=office+desk" in asked[0] and "/gb/en/" in asked[0]
    assert [(p.name, p.category, p.price_gbp) for p in found] == [
        ("LAGKAPTEN Desk", "desk", 135.0),
        ("KALLAX Shelving unit", "storage", None),
    ]
    assert all(p.source == "catalog_search" and p.dimensions is None for p in found)
    with pytest.raises(CatalogError, match="unreadable"):
        search_ikea("desk", fetch=lambda url, limit: (b"<html>", url))
    with pytest.raises(CatalogError):
        search_ikea(" ")


# --- Importing ------------------------------------------------------------------------------


def test_published_model_goes_through_the_shared_normaliser_with_catalog_size(
    tmp_path: Path,
) -> None:
    web = Web()
    result = import_catalog_asset(URL, "room", data_dir=tmp_path, fetch=web)
    asset = result.asset
    assert result.ok and result.mesh_source == "retailer_model" and not asset.is_proxy
    assert asset.id == catalog_id(URL) and asset.source == "url_import"
    assert asset.product_url == URL and asset.price_gbp == 79
    assert asset.dimension_source == "catalog" and asset.correction_needed == []
    assert asset.bbox_m == BBoxM(width=1.05, height=0.75, depth=0.5)
    # The retailer's centred model was fitted to the published size and put on the floor.
    expected = [[-0.525, 0, -0.25], [0.525, 0.75, 0.25]]
    assert np.abs(bounds(tmp_path, asset.glb_url) - expected).max() < GLB_BBOX_TOLERANCE_M
    assert len(asset.collision_parts) > 1, "the desk template, as for video furniture"
    # Provenance: the page, the image it was seen in, the model it was made from.
    assert result.product.dimensions is not None
    assert result.product.dimensions.text.startswith("width: 105 cm")
    assert result.image is not None and result.image.url == IMAGE
    assert (tmp_path / result.image.path).is_file()
    frame = asset.evidence.frames[0]
    assert frame.mask_url is not None and frame.provider_pose == {"model_url": MODEL}
    assert DRACO not in web.calls, "the readable model was enough"
    # It is an item of the same registry, delivered by the same function as video furniture.
    delivery = deliver_furniture(catalog_scene("room"), data_dir=tmp_path)
    assert delivery.ok and [a.id for a in delivery.assets] == [asset.id]


def test_reimport_reuses_the_stored_mesh_and_is_listed_once(tmp_path: Path) -> None:
    first = import_catalog_asset(URL, "room", data_dir=tmp_path, fetch=Web())
    web = Web()
    again = import_catalog_asset(URL, "room", data_dir=tmp_path, fetch=web)
    assert again.asset == first.asset and MODEL not in web.calls
    other = "https://shop.example/p/chair-9/"
    web.pages[other] = page({"name": "Chair", "width": None}, model=False)
    import_catalog_asset(other, "room", data_dir=tmp_path, fetch=web)
    listed = imported_assets("room", data_dir=tmp_path)
    assert sorted(r.asset.id for r in listed) == sorted({catalog_id(URL), catalog_id(other)})
    assert next(r for r in listed if r.asset.id == first.asset.id) == again
    assert imported_assets("another-room", data_dir=tmp_path) == []
    assert not deliver_furniture(catalog_scene("room"), data_dir=tmp_path).problems


def test_missing_dimensions_request_a_correction_and_a_user_size_settles_it(
    tmp_path: Path,
) -> None:
    web = Web(page=page({"height": None}))
    result = import_catalog_asset(URL, "room", data_dir=tmp_path, fetch=web)
    asset = result.asset
    assert result.ok and not asset.is_proxy, "the published model is still used"
    assert asset.dimension_source == "estimated" and "dimensions" in asset.correction_needed
    assert asset.bbox_m == BBoxM(width=1.049, height=0.754, depth=0.5)
    assert np.ptp(bounds(tmp_path, asset.glb_url), axis=0) == pytest.approx(
        [1.049, 0.754, 0.5], abs=GLB_BBOX_TOLERANCE_M
    )
    again = import_catalog_asset(URL, "room", data_dir=tmp_path, fetch=web)
    assert again.asset == asset
    assert any("ask the user" in note for note in result.warnings)
    assert main(["--url", URL, "--scene-id", "room", "--data-dir", str(tmp_path)]) == 1, (
        "the CLI uses the real network guard; example hosts do not resolve to a product"
    )
    size = KnownDimensions(
        bbox_m=BBoxM(width=1.05, height=0.74, depth=0.5), source="user_corrected"
    )
    fixed = import_catalog_asset(URL, "room", data_dir=tmp_path, fetch=web, dimensions=size)
    assert fixed.asset.id == asset.id and fixed.asset.bbox_m == size.bbox_m
    assert fixed.asset.dimension_source == "user_corrected"
    assert fixed.asset.correction_needed == []


def test_without_a_model_the_item_is_a_catalog_sized_proxy_offline(tmp_path: Path) -> None:
    result = import_catalog_asset(URL, "room", data_dir=tmp_path, fetch=Web(page=page(model=False)))
    asset = result.asset
    assert result.ok and result.mesh_source == "proxy" and asset.is_proxy
    assert asset.bbox_m == BBoxM(width=1.05, height=0.75, depth=0.5)
    assert asset.dimension_source == "catalog" and asset.correction_needed == []
    assert asset.source == "url_import" and asset.product_url == URL
    assert any("proxy delivered" in note for note in result.warnings)


def test_without_a_model_the_shared_mesh_provider_generates_from_the_image(
    tmp_path: Path,
) -> None:
    web = Web(page=page(model=False))
    generator = MeshDouble()
    result = import_catalog_asset(
        URL, "room", data_dir=tmp_path, fetch=web, mesh_provider=generator, source="catalog_search"
    )
    assert len(generator.calls) == 1 and result.mesh_source == "generated"
    assert not result.asset.is_proxy and result.asset.source == "catalog_search"
    assert result.asset.dimension_source == "catalog"
    assert result.asset.bbox_m == BBoxM(width=1.05, height=0.75, depth=0.5)
    # A generated shape that disagrees with the published size says so.
    assert "dimensions" in result.asset.correction_needed
    # A published model is preferred to a paid generation.
    paid = MeshDouble()
    import_catalog_asset(URL, "other-room", data_dir=tmp_path, fetch=Web(), mesh_provider=paid)
    assert paid.calls == []


def test_an_oversized_model_gives_way_to_the_retailers_lighter_variant(tmp_path: Path) -> None:
    heavy, light = "https://cdn.example/q3/desk.glb", "https://cdn.example/q1/desk.glb"
    encodings = [{"contentUrl": heavy}, {"contentUrl": heavy + "?again"}, {"contentUrl": light}]
    html = page(model=False).replace(
        b"</head>",
        b'<script type="application/ld+json">'
        + json.dumps({"@type": "3DModel", "encoding": encodings}).encode()
        + b"</script></head>",
    )
    web = Web(page=html)
    web.pages |= {
        heavy: model_glb(subdivisions=6),  # 49,152 triangles: over the profile's budget.
        heavy + "?again": model_glb(subdivisions=6),
        light: model_glb(),
    }
    result = import_catalog_asset(URL, "room", data_dir=tmp_path, fetch=web)
    assert result.mesh_source == "retailer_model" and result.check.triangles == 12
    assert result.asset.evidence.frames[0].provider_pose == {"model_url": light}


def test_published_footprint_follows_the_models_axes(tmp_path: Path) -> None:
    # IKEA's SKOGSTA table: "width 100, depth 235", while its model is 2.35 m along X.
    web = Web(
        page=page({"name": "Dining table", "width": "100 cm", "height": "74 cm",
                   "depth": "235 cm"}),
        model=model_glb((2.35, 0.743, 1.005)),
    )  # fmt: skip
    result = import_catalog_asset(URL, "room", data_dir=tmp_path, fetch=web)
    assert result.asset.bbox_m == BBoxM(width=2.35, height=0.74, depth=1.0)
    assert result.asset.dimension_source == "catalog" and result.asset.correction_needed == []
    assert any("exchanged" in note for note in result.warnings)
    assert result.product.dimensions is not None
    assert result.product.dimensions.bbox_m.width == 1.0, "what was published is kept as written"
    # Without a model (IKEA's LAGKAPTEN desk: "width 60, depth 140") a proxy follows its
    # category: a desk's long side is its front, a bed's is not.
    desk = Web(page=page({"width": "60 cm", "height": "73 cm", "depth": "140 cm"}, model=False))
    proxy = import_catalog_asset(URL, "desks", data_dir=tmp_path, fetch=desk).asset
    assert proxy.is_proxy and proxy.bbox_m == BBoxM(width=1.4, height=0.73, depth=0.6)
    bed = Web(page=page({"name": "Bed frame", "width": "150 cm", "depth": "199 cm"}, model=False))
    assert (
        import_catalog_asset(URL, "beds", data_dir=tmp_path, fetch=bed).asset.bbox_m.depth == 1.99
    )
    # A size the user typed is never turned.
    typed = KnownDimensions(
        bbox_m=BBoxM(width=0.6, height=0.73, depth=1.4), source="user_corrected"
    )
    kept = import_catalog_asset(URL, "desks", data_dir=tmp_path, fetch=desk, dimensions=typed)
    assert kept.asset.bbox_m == typed.bbox_m


@pytest.mark.parametrize("broken", ["image", "model"])
def test_a_failed_download_never_drops_the_item(tmp_path: Path, broken: str) -> None:
    result = import_catalog_asset(URL, "room", data_dir=tmp_path, fetch=Web(**{broken: None}))
    asset = result.asset
    assert result.ok and asset.is_proxy and result.mesh_source == "proxy"
    assert asset.id == catalog_id(URL) and asset.dimension_source == "catalog"
    assert asset.bbox_m == BBoxM(width=1.05, height=0.75, depth=0.5)
    assert result.warnings
    assert (result.image is None) == (broken == "image")


def test_a_failing_generator_or_an_unmaskable_photo_never_raises(tmp_path: Path) -> None:
    failing = MeshDouble(error=MeshError("remote reconstruction failed"))
    result = import_catalog_asset(
        URL, "room", data_dir=tmp_path, fetch=Web(page=page(model=False)), mesh_provider=failing
    )
    assert result.ok and result.asset.is_proxy and len(failing.calls) == 1
    assert any("remote reconstruction failed" in note for note in result.warnings)
    # A photo nothing can be cut out of: no mask, so no view to reconstruct from.
    busy = Web(page=page(model=False), image=product_image(plain=False))
    unused = MeshDouble()
    result = import_catalog_asset(URL, "busy", data_dir=tmp_path, fetch=busy, mesh_provider=unused)
    assert result.ok and result.asset.is_proxy and unused.calls == []
    assert result.asset.dimension_source == "catalog"
    assert any("no plain background" in note for note in result.warnings)
    assert any(note.startswith("mask:") for note in result.warnings)


def test_a_search_result_without_page_data_is_still_an_honest_item(tmp_path: Path) -> None:
    product = RetailerProduct(
        product_url=URL, source="catalog_search", retailer="shop.example",
        name="LAGKAPTEN Desk", category="desk", image_url=IMAGE, price_gbp=85,
    )  # fmt: skip
    result = import_product(product, "room", data_dir=tmp_path, fetch=Web())
    asset = result.asset
    assert asset.source == "catalog_search" and asset.price_gbp == 85 and asset.is_proxy
    assert asset.dimension_source == "estimated" and asset.correction_needed == ["dimensions"]
    with pytest.raises(ValueError, match="scene_id"):
        import_product(product, " ", data_dir=tmp_path, fetch=Web())


def test_item_box_finds_the_product_on_a_plain_background() -> None:
    image = cv2.imdecode(np.frombuffer(product_image(), np.uint8), cv2.IMREAD_COLOR)
    box, plain = item_box(image)
    assert plain
    assert box.x == pytest.approx(80 / 400 - 0.02) and box.width == pytest.approx(250 / 400 + 0.04)
    busy = cv2.imdecode(np.frombuffer(product_image(plain=False), np.uint8), cv2.IMREAD_COLOR)
    box, plain = item_box(busy)
    assert not plain and box.width == pytest.approx(0.92)


def test_retailer_model_provider_skips_unreadable_and_repeated_files() -> None:
    web = Web()
    provider = RetailerModelProvider(
        [DRACO, "https://cdn.example/gone.glb", MODEL, MODEL], fetch=web
    )
    raw = provider.reconstruct(None, None, None, None)  # type: ignore[arg-type]
    assert raw.glb == web.pages[MODEL] and raw.pose == {"model_url": MODEL}
    with pytest.raises(MeshError):
        provider.reconstruct(None, None, None, None)  # type: ignore[arg-type]


def test_oversized_textures_are_reduced_before_a_mesh_is_refused(tmp_path: Path) -> None:
    from PIL import Image

    noise = np.random.default_rng(1).integers(0, 255, (1024, 1024, 3), dtype=np.uint8)
    mesh = trimesh.creation.box(extents=(1.0, 0.7, 0.5))
    uv = np.random.default_rng(2).random((len(mesh.vertices), 2))
    material = trimesh.visual.material.PBRMaterial(baseColorTexture=Image.fromarray(noise))
    mesh.visual = trimesh.visual.TextureVisuals(uv=uv, material=material)
    raw = tmp_path / "noisy.raw.glb"
    raw.write_bytes(mesh.export(file_type="glb"))
    assert raw.stat().st_size > MAX_BYTES, "incompressible at full size"
    fitted = normalise_mesh(
        raw, category="desk", target_bbox=BBoxM(width=1.0, height=0.7, depth=0.5),
        data_dir=tmp_path, front="+z",
    )  # fmt: skip
    stored = tmp_path / "assets" / fitted.glb_url.rsplit("/", 1)[1]
    assert stored.stat().st_size <= MAX_BYTES


def test_cli_lists_search_results_and_reports_unusable_input(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    found = [RetailerProduct(product_url=URL, source="catalog_search", retailer="shop.example",
                             name="Desk", category="desk")]  # fmt: skip
    monkeypatch.setattr(
        "services.reconstruction.assets.import_product.search_ikea", lambda q, limit: found
    )
    assert main(["--search", "desk"]) == 0
    assert json.loads(capsys.readouterr().out)[0]["product_url"] == URL
    assert main(["--search", "desk", "--pick", "2", "--scene-id", "room"]) == 1
    assert main(["--url", URL]) == 1, "an import needs a scene"
    stored = tmp_path / "product.json"
    stored.write_text(found[0].model_dump_json())
    out = tmp_path / "out"
    code = main(["--product", str(stored), "--scene-id", "room", "--data-dir", str(tmp_path),
                 "--out", str(out), "--dimensions", "1.2", "0.75", "0.6"])  # fmt: skip
    summary = json.loads(capsys.readouterr().out.splitlines()[-1])
    assert code == 0 and summary["dimension_source"] == "user_corrected"
    assert summary["geometry"] == "proxy" and summary["bbox_m"]["width"] == 1.2
    report = (out / "report.md").read_text()
    assert "catalog_search" in report and URL in report
    assert json.loads((out / "assets.json").read_text())[0]["id"] == catalog_id(URL)


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("Desk chair", "chair"),
        ("Table lamp", "other"),
        ("Desk lamp", "other"),
        ("Chair pad", "other"),
        ("Table and 4 chairs", "table"),
    ],
)
def test_review_categories(name, expected):
    assert guess_category(name) == expected


def test_download_pins_checked_address(monkeypatch):
    import socket
    from contextlib import contextmanager

    import httpx

    calls = []

    def resolve(*args, **kwargs):
        calls.append(args)
        address = "93.184.216.34" if len(calls) == 1 else "127.0.0.1"
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (address, 443))]

    @contextmanager
    def stream(self, method, url, **kwargs):
        assert url.host == "93.184.216.34"
        assert kwargs["headers"]["Host"] == "shop.example"
        assert kwargs["extensions"]["sni_hostname"] == "shop.example"
        yield httpx.Response(200, content=b"ok", request=httpx.Request(method, url))

    monkeypatch.setattr(retailer.socket, "getaddrinfo", resolve)
    monkeypatch.setattr(retailer.httpx.Client, "stream", stream)
    assert retailer.fetch_public("https://shop.example/product", 100)[0] == b"ok"
    assert len(calls) == 1


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("Dining table and chairs", "table"),
        ("Table with 4 chairs", "table"),
        ("Desk and chair set", "desk"),
        ("Corner sofa with removable covers", "sofa"),
        ("Armchair with cushion", "chair"),
        ("Office desk chair with pads", "chair"),
        ("Dining chair cushions", "other"),
        ("Table lamp with shade", "other"),
        ("Desk, chair included", "desk"),
        ("Bedside table with drawers", "storage"),
    ],
)
def test_category_uses_head_noun(name: str, expected: str) -> None:
    assert guess_category(name) == expected


def test_catalog_identity_ignores_tracking_and_trailing_slashes() -> None:
    assert catalog_id(URL) == catalog_id(URL.rstrip("/") + "?utm_source=test#details")
    assert catalog_id(URL) != catalog_id(URL + "different")


def test_image_pixel_limit_is_checked_before_opencv_decode(monkeypatch) -> None:
    from PIL import Image

    from services.reconstruction.assets import catalog

    data = io.BytesIO()
    Image.new("RGB", (64, 64)).save(data, format="PNG")
    monkeypatch.setattr(catalog, "MAX_IMAGE_PIXELS", 4000)

    def unexpected_decode(*args):
        pytest.fail("oversized image must be refused before decoding")

    monkeypatch.setattr(catalog.cv2, "imdecode", unexpected_decode)
    with pytest.raises(CatalogError):
        catalog._decode(data.getvalue())


def test_download_deadline_stops_trickling_response(monkeypatch) -> None:
    from contextlib import contextmanager

    import httpx

    now = [0.0]
    monkeypatch.setattr(retailer.time, "monotonic", lambda: now[0])
    monkeypatch.setattr(retailer, "_check_public", lambda url: "93.184.216.34")

    class Trickle(httpx.SyncByteStream):
        def __iter__(self):
            for _ in range(100):
                now[0] += 0.4
                yield b"a"

    @contextmanager
    def stream(self, method, url, **kwargs):
        yield httpx.Response(200, stream=Trickle(), request=httpx.Request(method, url))

    monkeypatch.setattr(httpx.Client, "stream", stream)
    with pytest.raises(CatalogError, match="time limit"):
        retailer.fetch_public("https://shop.example/x", 1000, timeout_s=1)
    assert now[0] == pytest.approx(1.2)


class SamMaskDouble:
    method = "sam3"

    def __init__(self, *, fail=False):
        self.calls = 0
        self.fail = fail

    def segment(self, frame, image, boxes, registry, *, budget=None):
        from services.reconstruction.assets.mask_providers import GrabCutProvider, MaskError

        self.calls += 1
        if self.fail:
            raise MaskError("fal unavailable")
        return GrabCutProvider().segment(frame, image, boxes, registry, budget=budget)


def test_live_import_upgrades_offline_masks_and_reuses_sam(tmp_path):
    from services.reconstruction.assets.registry import Registry

    import_catalog_asset(URL, "room", data_dir=tmp_path, fetch=Web())
    sam = SamMaskDouble()
    paid = MeshDouble()
    for _ in range(2):
        result = import_catalog_asset(
            URL,
            "room",
            data_dir=tmp_path,
            fetch=Web(),
            mask_provider=sam,
            mesh_provider=paid,
        )
        assert result.ok and result.mesh_source == "retailer_model"
        assert not any("GrabCut masks are approximate" in w for w in result.warnings)
    assert sam.calls == 1
    assert not paid.calls
    obj = Registry(tmp_path, namespace=catalog_scene("room")).load(catalog_scene("room"))
    assert obj.objects[catalog_id(URL)].masks[0].method == "sam3"


def test_live_mask_failure_falls_back_without_losing_retailer_model(tmp_path):
    result = import_catalog_asset(
        URL,
        "room",
        data_dir=tmp_path,
        fetch=Web(),
        mask_provider=SamMaskDouble(fail=True),
    )
    assert result.ok and result.mesh_source == "retailer_model"
    assert any("fal unavailable" in w for w in result.warnings)
    assert any("GrabCut masks are approximate" in w for w in result.warnings)


def test_live_masks_and_generated_mesh_used_without_retailer_model(tmp_path):
    generator = MeshDouble()
    result = import_catalog_asset(
        URL,
        "room",
        data_dir=tmp_path,
        fetch=Web(page=page(model=False)),
        mask_provider=SamMaskDouble(),
        mesh_provider=generator,
    )
    assert result.ok and result.mesh_source == "generated"
    assert len(generator.calls) == 1
    assert result.asset.dimension_source == "catalog"
