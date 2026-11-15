"""Product search offline: IKEA first, one product per web retailer, junk dropped."""

from typing import Any

import pytest

from contracts.schema import BBoxM
from services.reconstruction.assets.retailer import (
    CatalogError,
    ProductDimensions,
    RetailerProduct,
)
from services.spatial_engine.furniture_search import SearchUnavailable, search_products


def product(url: str, name: str, *, price: float | None = 99.0, image: bool = True) -> Any:
    return RetailerProduct(
        product_url=url,
        source="catalog_search",
        retailer="x",
        name=name,
        category="desk",
        image_url=f"{url}/image.jpg" if image else None,
        price_gbp=price,
    )


IKEA = [
    product("https://www.ikea.com/gb/en/p/micke-1/", "MICKE Desk"),
    product("https://www.ikea.com/gb/en/p/alex-2/", "ALEX Desk"),
    product("https://www.ikea.com/gb/en/p/tonstad-3/", "TONSTAD Desk"),
]
PAGES = {
    "https://shop-a.co.uk/oak-desk": product("https://shop-a.co.uk/oak-desk", "Oak Desk"),
    "https://shop-a.co.uk/other-desk": product("https://shop-a.co.uk/other-desk", "Other Desk"),
    "https://www.amazon.co.uk/desk": product("https://www.amazon.co.uk/desk", "Desk"),
    "https://spam.example/x": product("https://spam.example/x", "Casino bonus"),
    "https://mag.example/desks": product("https://mag.example/desks", "8 small desks for flats"),
    "https://listing.example/desks": product("https://listing.example/desks", "Desks", price=None),
    "https://shop-b.com/desk": RetailerProduct(
        product_url="https://shop-b.com/desk",
        retailer="shop-b.com",
        name="Walnut writing desk",
        category="desk",
        image_url="https://shop-b.com/desk.jpg",
        dimensions=ProductDimensions(
            bbox_m=BBoxM(width=1.1, depth=0.5, height=0.75),
            found_in="structured_data",
            text="110 x 50 x 75 cm",
        ),
    ),
}


class Linkup:
    def __init__(self, urls: list[str], *, fail: bool = False) -> None:
        self.urls, self.fail = urls, fail
        self.bodies: list[dict[str, Any]] = []

    def __call__(self, body: dict[str, Any]) -> dict[str, Any]:
        self.bodies.append(body)
        if self.fail:
            raise SearchUnavailable("the web search is unavailable")
        results = [{"type": "text", "name": "page", "url": url} for url in self.urls]
        return {"results": [*results, {"type": "image", "url": "https://img.example/a.jpg"}]}


def read(url: str) -> RetailerProduct:
    if url not in PAGES:
        raise CatalogError("the retailer answered HTTP 404")
    return PAGES[url]


def ikea(found: list[RetailerProduct] | Exception) -> Any:
    def search(query: str, limit: int) -> list[RetailerProduct]:
        if isinstance(found, Exception):
            raise found
        return found[:limit]

    return search


WEB = [
    "https://www.amazon.co.uk/desk",
    "https://spam.example/x",
    "https://mag.example/desks",
    "https://listing.example/desks",
    "https://shop-a.co.uk/oak-desk",
    "https://shop-a.co.uk/other-desk",
    "https://missing.example/desk",
    "https://shop-b.com/desk",
]


def test_ikea_first_then_one_product_per_relevant_retailer() -> None:
    options = search_products("oak desk", linkup=Linkup(WEB), ikea=ikea(IKEA), read=read)
    assert [o.product_url for o in options] == [
        IKEA[0].product_url,
        "https://shop-a.co.uk/oak-desk",
        "https://shop-b.com/desk",
    ]
    assert options[0].retailer == "ikea.com" and options[0].image_url
    assert options[2].bbox_m == BBoxM(width=1.1, depth=0.5, height=0.75)
    assert options[2].dimensions_text == "110 x 50 x 75 cm"


def test_ikea_fills_the_three_when_the_web_finds_nothing() -> None:
    options = search_products("desk", linkup=Linkup([]), ikea=ikea(IKEA), read=read)
    assert [o.name for o in options] == ["MICKE Desk", "ALEX Desk", "TONSTAD Desk"]


def test_without_linkup_only_ikea_is_searched() -> None:
    assert len(search_products("desk", linkup=None, ikea=ikea(IKEA), read=read)) == 3


def test_linkup_finds_ikea_when_ikea_search_is_down() -> None:
    page = "https://www.ikea.com/gb/en/p/micke-1/"
    PAGES[page] = IKEA[0]
    try:
        linkup = Linkup([page, "https://www.ikea.com/gb/en/cat/desks/"])
        options = search_products("desk", linkup=linkup, ikea=ikea(CatalogError("down")), read=read)
    finally:
        del PAGES[page]
    assert options[0].product_url == page
    assert any(body.get("includeDomains") == ["ikea.com"] for body in linkup.bodies)


def test_price_limit_and_missing_images_filter_results() -> None:
    cheap = [product("https://www.ikea.com/gb/en/p/a/", "Desk", price=40.0), *IKEA]
    cheap.append(product("https://www.ikea.com/gb/en/p/b/", "Desk", price=10.0, image=False))
    options = search_products("desk", max_price_gbp=50, linkup=None, ikea=ikea(cheap), read=read)
    assert [o.price_gbp for o in options] == [40.0]


def test_failed_web_search_without_ikea_raises() -> None:
    with pytest.raises(SearchUnavailable):
        search_products(
            "desk", linkup=Linkup([], fail=True), ikea=ikea(CatalogError("down")), read=read
        )


def test_failed_web_search_still_returns_ikea() -> None:
    options = search_products("desk", linkup=Linkup([], fail=True), ikea=ikea(IKEA), read=read)
    assert len(options) == 3
