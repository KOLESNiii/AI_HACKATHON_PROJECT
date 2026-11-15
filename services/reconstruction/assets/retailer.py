"""A retailer product page or search result -> what the asset pipeline needs (#19).

`RetailerProduct` keeps where everything came from: the product URL, the image URL, and the
published text a size was read from, and any 3D model the retailer itself publishes (IKEA does,
as schema.org `3DModel`). Nothing here makes a mesh; `catalog.import_product` sends
the product through the same pipeline as video furniture.
"""

from __future__ import annotations

import ipaddress
import json
import math
import re
import socket
from collections.abc import Callable, Iterator
from html.parser import HTMLParser
from typing import Any, Literal, get_args
from urllib.parse import urljoin, urlsplit

import httpx
from pydantic import Field

from contracts.schema import BBoxM

from .selection_models import Category, Record

MAX_PAGE_BYTES = 3_000_000
MAX_REDIRECTS = 4
MAX_MODEL_URLS = 6
MIN_SIDE_M, MAX_SIDE_M = 0.01, 5.0
"""A published side outside this range is taken to be a misread unit, not furniture."""
USER_AGENT = "Mozilla/5.0 (compatible; furniture-importer/1.0)"


class CatalogError(ValueError):
    """The product cannot be imported at all. The message is safe to show."""


class ProductDimensions(Record):
    """A size the retailer published, in metres, with the text it was read from."""

    bbox_m: BBoxM
    found_in: Literal["structured_data", "page_text", "search_result"]
    text: str = Field(max_length=300)
    """The published values as written, for example "Width: 120 cm; Height: 75 cm; Depth: 60 cm"."""


class RetailerProduct(Record):
    """One retailer product, from its page (`url_import`) or a search result (`catalog_search`)."""

    product_url: str = Field(pattern=r"^https?://\S+$", max_length=2000)
    source: Literal["url_import", "catalog_search"] = "url_import"
    retailer: str
    """The host that published the product."""
    name: str = Field(min_length=1, max_length=160)
    category: Category
    image_url: str | None = Field(default=None, pattern=r"^https?://\S+$", max_length=2000)
    model_urls: list[str] = Field(default=[], max_length=MAX_MODEL_URLS)
    """Binary glTF models the retailer publishes for this product, best candidate first."""
    price_gbp: float | None = Field(default=None, ge=0)
    dimensions: ProductDimensions | None = None
    """None when the retailer published no complete, readable size: the import then asks the
    user for the dimensions and never invents them."""
    warnings: list[str] = []


Fetch = Callable[[str, int], tuple[bytes, str]]
"""(url, byte limit) -> (body, final URL after redirects). Raises CatalogError."""


def _check_public(url: str) -> None:
    """Refuse anything but http(s) to a public address: an imported URL is untrusted input."""
    target = urlsplit(url)
    if target.scheme not in ("http", "https") or not target.hostname or target.username:
        raise CatalogError("only public http(s) URLs can be imported")
    try:
        port = target.port or (443 if target.scheme == "https" else 80)
        found = socket.getaddrinfo(target.hostname, port, type=socket.SOCK_STREAM)
    except (OSError, ValueError) as exc:
        raise CatalogError("the URL's host could not be resolved") from exc
    if not found or not all(ipaddress.ip_address(entry[4][0]).is_global for entry in found):
        raise CatalogError("only public http(s) URLs can be imported")


def fetch_public(url: str, limit: int, *, timeout_s: float = 20) -> tuple[bytes, str]:
    """Download a public URL with a size cap, re-checking every redirect hop."""
    for _ in range(MAX_REDIRECTS + 1):
        _check_public(url)
        try:
            with httpx.stream(
                "GET",
                url,
                timeout=timeout_s,
                follow_redirects=False,
                headers={"User-Agent": USER_AGENT, "Accept-Language": "en-GB,en;q=0.8"},
            ) as response:
                if response.is_redirect and "location" in response.headers:
                    url = urljoin(url, response.headers["location"])
                    continue
                response.raise_for_status()
                data = bytearray()
                for chunk in response.iter_bytes():
                    if len(data) + len(chunk) > limit:
                        raise CatalogError("the retailer's response is too large")
                    data.extend(chunk)
                return bytes(data), url
        except httpx.HTTPStatusError as exc:
            raise CatalogError(f"the retailer answered HTTP {exc.response.status_code}") from exc
        except httpx.HTTPError as exc:
            raise CatalogError(f"the retailer could not be reached ({type(exc).__name__})") from exc
    raise CatalogError("too many redirects")


# --- Sizes -----------------------------------------------------------------------------------

_UNIT_M = {"mm": 0.001, "cm": 0.01, "m": 1.0, "in": 0.0254, "ft": 0.3048}
_UNIT_NAMES = {
    "mm": "mm", "mmt": "mm", "millimetre": "mm", "millimetres": "mm", "millimeter": "mm",
    "millimeters": "mm", "cm": "cm", "cmt": "cm", "centimetre": "cm", "centimetres": "cm",
    "centimeter": "cm", "centimeters": "cm", "m": "m", "mtr": "m", "metre": "m", "metres": "m",
    "meter": "m", "meters": "m", "in": "in", "inh": "in", "inch": "in", "inches": "in",
    '"': "in", "ft": "ft", "fot": "ft", "foot": "ft", "feet": "ft",
}  # fmt: skip
_NUMBER = r"\d{1,5}(?:[.,]\d{1,3})?"
_UNIT = r"mm|cm|m|inches|inch|in|\"|ft"
_QUANTITY = re.compile(rf"^\s*({_NUMBER})\s*({_UNIT})?\.?\s*$", re.IGNORECASE)
_AXES = {"width": "width", "w": "width", "height": "height", "h": "height",
         "depth": "depth", "d": "depth"}  # fmt: skip
_LABELLED = re.compile(
    # The label must open its line or clause: "Armrest width" and "Seat height" are not the
    # item's size. IKEA writes a sofa's overall height as "Height including back cushions".
    rf"(?:^|[.;,|(])[ \t]*(?:overall |total |max\.? )?(width|height|depth)\b"
    rf"(?: including back cushions)?\s*(?:\([^)]{{0,20}}\))?\s*[:=]?\s*"
    rf"({_NUMBER})\s*({_UNIT})(?![a-z])",
    re.IGNORECASE | re.MULTILINE,
)
_PART = rf"([whd])\s*:?\s*({_NUMBER})\s*({_UNIT})?"
_COMPACT = re.compile(rf"\b{_PART}\s*[x×]\s*{_PART}\s*[x×]\s*{_PART}(?![a-z])", re.IGNORECASE)


def _metres(value: Any, unit: Any = None) -> float | None:
    """A published length in metres, or None when it has no readable number and unit."""
    if isinstance(value, str) and (match := _QUANTITY.match(value)):
        value, unit = match.group(1).replace(",", "."), match.group(2) or unit
    if isinstance(value, bool) or not isinstance(unit, str):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    name = _UNIT_NAMES.get(unit.strip().lower().rstrip("."))
    if name is None or not math.isfinite(number):
        return None
    return round(number * _UNIT_M[name], 4)


def _dimensions(
    sides: dict[str, tuple[float, str]],
    found_in: Literal["structured_data", "page_text", "search_result"],
    warnings: list[str],
) -> ProductDimensions | None:
    """All three sides, each plausible, or nothing: a partial size is not a size."""
    if not sides:
        return None
    missing = [axis for axis in ("width", "height", "depth") if axis not in sides]
    if missing:
        warnings.append(
            f"published dimensions are incomplete: no {' or '.join(missing)} ({found_in})"
        )
        return None
    if not all(MIN_SIDE_M <= sides[axis][0] <= MAX_SIDE_M for axis in sides):
        warnings.append(f"published dimensions are implausible and were not used ({found_in})")
        return None
    return ProductDimensions(
        bbox_m=BBoxM(**{axis: sides[axis][0] for axis in ("width", "height", "depth")}),
        found_in=found_in,
        text="; ".join(sides[axis][1] for axis in ("width", "height", "depth"))[:300],
    )


def sides_from_text(text: str) -> dict[str, tuple[float, str]]:
    """Labelled sizes in prose: "Width: 120 cm" for each axis, or "W120 x D60 x H75 cm".

    Unlabelled triples ("120 x 60 x 75 cm") are not read: nothing says which side is which.
    """
    sides: dict[str, tuple[float, str]] = {}
    compact = _COMPACT.search(text)
    if compact:
        parts = [compact.groups()[i : i + 3] for i in (0, 3, 6)]
        shared = next((unit for _, _, unit in reversed(parts) if unit), None)
        snippet = compact.group(0).strip()
        for letter, number, unit in parts:
            metres = _metres(number.replace(",", "."), unit or shared)
            if metres is not None:
                sides[_AXES[letter.lower()]] = (metres, snippet)
        if len(sides) == 3:
            return sides
        sides = {}
    for match in _LABELLED.finditer(text):
        metres = _metres(match.group(2).replace(",", "."), match.group(3))
        if metres is not None:
            label = " ".join(match.group(0).strip(" .;,|(\n\t").split())
            sides.setdefault(match.group(1).lower(), (metres, label))
    return sides


# --- Product pages ---------------------------------------------------------------------------

_CATEGORY_WORDS: list[tuple[Category, tuple[str, ...]]] = [
    ("wardrobe", ("wardrobe", "armoire")),
    ("storage", ("bedside", "nightstand", "tv unit", "tv stand", "sideboard")),
    ("sofa", ("sofa", "couch", "settee", "loveseat")),
    ("desk", ("desk", "workstation")),
    ("chair", ("chair", "armchair", "stool", "recliner")),
    ("table", ("table",)),
    ("bed", ("bed", "mattress", "divan")),
    ("storage", ("shelf", "shelves", "shelving", "bookcase", "cabinet", "drawer", "drawers",
                 "chest", "cupboard", "dresser", "storage")),
]  # fmt: skip


def guess_category(*texts: str) -> Category:
    """A category from the product's own words, most specific first; "other" when none fits."""
    for text in texts:
        lowered = text.lower()
        for category, words in _CATEGORY_WORDS:
            if any(re.search(rf"\b{re.escape(word)}s?\b", lowered) for word in words):
                return category
    return "other"


class _Page(HTMLParser):
    """The few things a product page is read for: JSON-LD, meta tags, title and visible text."""

    _SKIPPED = {"script", "style", "noscript", "template", "svg"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.meta: dict[str, str] = {}
        self.json_ld: list[str] = []
        self.title = ""
        self.text: list[str] = []
        self.models: list[str] = []
        self._stack: list[str] = []
        self._ld = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {name: value or "" for name, value in attrs}
        if tag == "meta":
            key = (values.get("property") or values.get("name") or "").lower()
            if key and values.get("content"):
                self.meta.setdefault(key, values["content"].strip())
            return
        if tag in ("br", "img", "input", "link", "hr"):
            return
        if tag == "model-viewer" and values.get("src"):
            self.models.append(values["src"].strip())
        self._stack.append(tag)
        self._ld = tag == "script" and values.get("type", "").lower() == "application/ld+json"
        if self._ld:
            self.json_ld.append("")

    def handle_endtag(self, tag: str) -> None:
        if tag in self._stack:
            while self._stack and self._stack.pop() != tag:
                pass
        self._ld = False

    def handle_data(self, data: str) -> None:
        if self._ld:
            self.json_ld[-1] += data
        elif "title" in self._stack:
            self.title += data
        elif not self._SKIPPED.intersection(self._stack) and data.strip():
            self.text.append(data.strip())


def _nodes(value: Any) -> Iterator[dict[str, Any]]:
    """Every JSON-LD object, however the page nested it (lists, `@graph`)."""
    if isinstance(value, list):
        for entry in value:
            yield from _nodes(entry)
    elif isinstance(value, dict):
        yield value
        yield from _nodes(value.get("@graph"))


def _is_type(node: dict[str, Any], name: str) -> bool:
    kind = node.get("@type")
    return name in kind if isinstance(kind, list) else kind == name


def _first_url(value: Any) -> str | None:
    if isinstance(value, list):
        return next((url for entry in value if (url := _first_url(entry))), None)
    if isinstance(value, dict):
        return _first_url(value.get("url") or value.get("contentUrl"))
    return value.strip() if isinstance(value, str) and value.strip() else None


def _structured_sides(product: dict[str, Any]) -> dict[str, tuple[float, str]]:
    """schema.org `width`/`height`/`depth` and `additionalProperty` entries with those names."""
    candidates: list[tuple[str, Any]] = [(axis, product.get(axis)) for axis in _AXES.values()]
    properties = product.get("additionalProperty")
    for entry in properties if isinstance(properties, list) else [properties]:
        if isinstance(entry, dict) and isinstance(entry.get("name"), str):
            candidates.append((entry["name"].strip().lower(), entry))
    sides: dict[str, tuple[float, str]] = {}
    for label, value in candidates:
        if label not in ("width", "height", "depth") or label in sides or value is None:
            continue
        if isinstance(value, dict):
            unit = value.get("unitCode") or value.get("unitText")
            metres, shown = _metres(value.get("value"), unit), f"{value.get('value')} {unit}"
        else:
            metres, shown = _metres(value), str(value)
        if metres is not None:
            sides[label] = (metres, f"{label}: {shown}"[:90])
    return sides


def _binary_models(encodings: Any) -> list[str]:
    """`contentUrl`s of a schema.org 3DModel's binary glTF encodings."""
    return [
        entry["contentUrl"]
        for entry in (encodings if isinstance(encodings, list) else [encodings])
        if isinstance(entry, dict)
        and isinstance(entry.get("contentUrl"), str)
        and entry.get("encodingFormat") in (None, "model/gltf-binary")
    ]


def _model_urls(urls: list[str]) -> list[str]:
    """Usable `.glb` links without repeats. Draco-compressed files go last: the mesh reader has
    no Draco decoder, so they only stand in when nothing else is published."""
    usable = [
        url
        for url in dict.fromkeys(urls)
        if re.fullmatch(r"https?://\S+", url)
        and len(url) <= 2000
        and urlsplit(url).path.lower().endswith(".glb")
    ]
    return sorted(usable, key=lambda url: "draco" in url.lower())[:MAX_MODEL_URLS]


def _price_gbp(product: dict[str, Any], meta: dict[str, str], warnings: list[str]) -> float | None:
    offers = product.get("offers")
    offer = next((o for o in (offers if isinstance(offers, list) else [offers])
                  if isinstance(o, dict)), {})  # fmt: skip
    if "price" not in offer and "lowPrice" not in offer:
        # IKEA prices a combination as a list of specifications; the one without a
        # `priceType` is the current price, the others are struck-through former prices.
        listed = offer.get("priceSpecification")
        specs = [
            x for x in (listed if isinstance(listed, list) else [listed]) if isinstance(x, dict)
        ]
        offer = next((x for x in specs if "priceType" not in x), offer)
    amount = offer.get("price", offer.get("lowPrice", meta.get("product:price:amount")))
    currency = offer.get("priceCurrency") or meta.get("product:price:currency")
    if amount is None:
        return None
    try:
        price = float(str(amount).replace(",", ""))
    except ValueError:
        return None
    if not math.isfinite(price) or price < 0:
        return None
    if str(currency).upper() != "GBP":
        warnings.append("the published price is not in GBP and was not kept")
        return None
    return price


def parse_product_page(
    html: str, product_url: str, *, page_url: str | None = None, category: Category | None = None
) -> RetailerProduct:
    """Read a retailer page's product: schema.org JSON-LD first, then meta tags and page text.

    `product_url` is the URL the user gave and is kept as the source; `page_url` (after
    redirects) resolves relative image links. Raises CatalogError when the page names no product.
    """
    if category is not None and category not in get_args(Category):
        raise CatalogError(f"unknown furniture category: {category!r}")
    page = _Page()
    try:
        page.feed(html)
        page.close()
    except Exception as exc:  # Untrusted markup: any parser failure means the same thing.
        raise CatalogError("the product page could not be read") from exc
    product: dict[str, Any] = {}
    models: list[str] = []
    for block in page.json_ld:
        try:
            nodes = list(_nodes(json.loads(block)))
        except ValueError:
            continue
        for node in nodes:
            if _is_type(node, "Product") and not product:
                product = node
            if _is_type(node, "3DModel"):
                models += _binary_models(node.get("encoding"))
    base = page_url or product_url
    warnings: list[str] = []
    raw_name = product.get("name") if isinstance(product.get("name"), str) else None
    name = " ".join((raw_name or page.meta.get("og:title") or page.title).split())[:160]
    if not name:
        raise CatalogError("the page does not name a product")
    image = _first_url(product.get("image")) or page.meta.get("og:image")
    image_url = urljoin(base, image) if image else None
    if image_url is None:
        warnings.append("the page publishes no product image; a proxy box is used")
    elif not re.fullmatch(r"https?://\S+", image_url) or len(image_url) > 2000:
        warnings.append("the product image link is unusable; a proxy box is used")
        image_url = None
    sides = _structured_sides(product)
    found_in: Literal["structured_data", "page_text"] = "structured_data"
    if len(sides) < 3:
        # Structured data first; the page's own labelled text only fills what it leaves out.
        described = product.get("description")
        text = "\n".join([described if isinstance(described, str) else "", *page.text])
        written = {axis: side for axis, side in sides_from_text(text).items() if axis not in sides}
        if written:
            sides, found_in = {**sides, **written}, "page_text"
    dimensions = _dimensions(sides, found_in, warnings)
    if dimensions is None:
        warnings.append("no complete published dimensions were found; ask the user for them")
    breadcrumb = product.get("category")
    return RetailerProduct(
        product_url=product_url,
        retailer=urlsplit(product_url).hostname or "",
        name=name,
        category=category
        or guess_category(name, breadcrumb if isinstance(breadcrumb, str) else ""),
        image_url=image_url,
        model_urls=_model_urls([urljoin(base, url) for url in [*models, *page.models]]),
        price_gbp=_price_gbp(product, page.meta, warnings),
        dimensions=dimensions,
        warnings=warnings,
    )


def fetch_product(
    product_url: str,
    *,
    category: Category | None = None,
    source: Literal["url_import", "catalog_search"] = "url_import",
    fetch: Fetch | None = None,
) -> RetailerProduct:
    """Download and read one retailer product page. Raises CatalogError.

    `source` records how the product was found: a pasted link, or a picked search result.
    """
    if not re.fullmatch(r"https?://\S+", product_url) or len(product_url) > 2000:
        raise CatalogError("only public http(s) URLs can be imported")
    body, final_url = (fetch or fetch_public)(product_url, MAX_PAGE_BYTES)
    product = parse_product_page(
        body.decode("utf-8", errors="replace"), product_url, page_url=final_url, category=category
    )
    return product.model_copy(update={"source": source})


# --- Search ----------------------------------------------------------------------------------

IKEA_SEARCH_URL = "https://sik.search.blue.cdtapps.com/{market}/search-result-page"
"""The search the IKEA website itself calls. It needs no key but is not a documented API:
observed 2026-11-15, and it may change without notice."""


def search_ikea(
    query: str, *, limit: int = 5, market: str = "gb/en", fetch: Fetch | None = None
) -> list[RetailerProduct]:
    """IKEA products matching `query`, as `catalog_search` results.

    A result carries the product URL, image and price but no dimensions or model: IKEA's
    search publishes only an unlabelled size ("140x60 cm"). Import a picked result with
    `catalog.import_catalog_asset(result.product_url, ..., source="catalog_search")`, which
    reads both from the product page. Raises CatalogError when the search is unavailable.
    """
    query = " ".join(query.split())
    if not query or len(query) > 100:
        raise CatalogError("a search needs 1 to 100 characters")
    if not 1 <= limit <= 24 or not re.fullmatch(r"[a-z]{2}/[a-z]{2}", market):
        raise CatalogError("unsupported search limit or market")
    url = str(
        httpx.URL(
            IKEA_SEARCH_URL.format(market=market),
            params={"q": query, "size": limit, "types": "PRODUCT"},
        )
    )
    body, _ = (fetch or fetch_public)(url, MAX_PAGE_BYTES)
    try:
        items = json.loads(body)["searchResultPage"]["products"]["main"]["items"]
    except (ValueError, KeyError, TypeError) as exc:
        raise CatalogError("the retailer search returned an unreadable result") from exc
    results: list[RetailerProduct] = []
    for item in items if isinstance(items, list) else []:
        entry = item.get("product") if isinstance(item, dict) else None
        if not isinstance(entry, dict):
            continue
        kind, price = entry.get("typeName"), entry.get("salesPrice")
        kind = kind if isinstance(kind, str) else ""
        price = price if isinstance(price, dict) else {}
        amount = price.get("numeral")
        try:
            results.append(
                RetailerProduct(
                    product_url=entry["pipUrl"],
                    source="catalog_search",
                    retailer=urlsplit(entry["pipUrl"]).hostname or "",
                    name=" ".join(f"{entry['name']} {kind}".split())[:160],
                    category=guess_category(kind, str(entry["name"])),
                    image_url=entry.get("mainImageUrl"),
                    price_gbp=float(amount)
                    if isinstance(amount, int | float) and price.get("currencyCode") == "GBP"
                    else None,
                    warnings=["a search result has no dimensions; import its product page"],
                )
            )
        except (KeyError, TypeError, ValueError):
            continue  # One malformed entry does not hide the others.
    return results[:limit]
