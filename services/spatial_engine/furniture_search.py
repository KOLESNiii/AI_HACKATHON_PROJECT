"""Find real furniture to buy: Linkup web search plus IKEA's own search.

The agent's `search_products` tool calls `search_products` here. It returns at most three
products, each with a product page and an image, and puts an IKEA product among them whenever
IKEA has one: IKEA publishes a 3D model per product, so its results import as real meshes.

Search finds candidates only. Nothing here sizes or places furniture: picking a result sends
its product page through the reconstruction service's import, which reads the published
dimensions, and then the spatial `/place` endpoint finds an audited spot for it.
"""

from __future__ import annotations

import logging
import re
from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Literal
from urllib.parse import urlsplit

import httpx
from pydantic import BaseModel, Field

from contracts.schema import BBoxM
from services.reconstruction.assets.retailer import (
    CatalogError,
    RetailerProduct,
    fetch_product,
    fetch_public,
    search_ikea,
)

logger = logging.getLogger(__name__)

LINKUP_SEARCH_URL = "https://api.linkup.so/v1/search"
MAX_RESULTS = 3
_LINKUP_TIMEOUT_S = 25.0
_PAGE_TIMEOUT_S = 8.0
_PAGE_CANDIDATES = 8
"""Linkup pages read in parallel for an image and price; many are product pages."""
_STOP_WORDS = {"the", "and", "for", "with", "buy", "online", "cheap", "best", "small", "large"}
_SKIPPED_HOSTS = (
    "ikea.",  # Searched directly instead.
    "amazon.",
    "ebay.",
    "pinterest.",
    "youtube.",
    "reddit.",
    "facebook.",
    "instagram.",
    "tiktok.",
    "wikipedia.",
)
"""Hosts whose pages are not readable product pages, or that are searched another way."""

Category = Literal["bed", "desk", "chair", "table", "wardrobe", "sofa", "storage", "other"]


class SearchUnavailable(Exception):
    """No search could run (no key, provider down). The message is safe to show."""


class ProductOption(BaseModel):
    """One product the user can add. Dimensions are what the retailer published, if read."""

    name: str = Field(min_length=1, max_length=160)
    retailer: str
    product_url: str = Field(pattern=r"^https?://\S+$", max_length=2000)
    image_url: str = Field(pattern=r"^https?://\S+$", max_length=2000)
    category: Category
    price_gbp: float | None = None
    bbox_m: BBoxM | None = None
    dimensions_text: str | None = None


LinkupPost = Callable[[dict[str, Any]], dict[str, Any]]
"""Linkup request body -> response JSON. Raises SearchUnavailable."""
PageReader = Callable[[str], RetailerProduct]
IkeaSearch = Callable[[str, int], list[RetailerProduct]]


def linkup_client(api_key: str) -> LinkupPost:
    """POST to Linkup's search API. The key is sent only as a bearer token and never logged."""

    def post(body: dict[str, Any]) -> dict[str, Any]:
        try:
            response = httpx.post(
                LINKUP_SEARCH_URL,
                json=body,
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=_LINKUP_TIMEOUT_S,
            )
            response.raise_for_status()
            data = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            logger.warning("Linkup search failed: %s", type(exc).__name__)
            raise SearchUnavailable("the web search is unavailable") from exc
        if not isinstance(data, dict):
            raise SearchUnavailable("the web search returned an unreadable result")
        return data

    return post


def _read_page(url: str) -> RetailerProduct:
    return fetch_product(
        url,
        source="catalog_search",
        fetch=lambda target, limit: fetch_public(target, limit, timeout_s=_PAGE_TIMEOUT_S),
    )


def _ikea(query: str, limit: int) -> list[RetailerProduct]:
    return search_ikea(query, limit=limit)


def _host(url: str) -> str:
    host = (urlsplit(url).hostname or "").lower()
    return host.removeprefix("www.")


def _skipped(url: str) -> bool:
    host = _host(url)
    return any(host.startswith(name) or f".{name}" in f".{host}" for name in _SKIPPED_HOSTS)


def _linkup_urls(post: LinkupPost, body: dict[str, Any]) -> list[str]:
    data = post(body)
    urls: list[str] = []
    for result in data.get("results") or []:
        if not isinstance(result, dict) or result.get("type") != "text":
            continue
        url = result.get("url")
        if isinstance(url, str) and url.startswith(("http://", "https://")) and url not in urls:
            urls.append(url)
    return urls


def _words(text: str) -> set[str]:
    return {
        word.removesuffix("s")
        for word in re.findall(r"[a-z0-9]+", text.lower())
        if len(word) > 2 and word not in _STOP_WORDS
    }


_EDITORIAL = re.compile(
    r"^\d+\s|\b(best|ideas?|guide|review|reviews|inspiration|tips|vs|ranked)\b", re.IGNORECASE
)
"""Article titles ("8 small desks for compact spaces"), not products."""


def _relevant(product: RetailerProduct, query: str) -> bool:
    """A web page counts only if it reads as a product and its name shares a word with the
    request. A product publishes a price, or its size in structured data; articles, listing
    pages and hijacked domains rarely do."""
    dims = product.dimensions
    readable = product.price_gbp is not None or (
        dims is not None and dims.found_in == "structured_data"
    )
    return (
        readable
        and not _EDITORIAL.search(product.name)
        and bool(_words(product.name) & _words(query))
    )


def _option(product: RetailerProduct, category: Category | None) -> ProductOption | None:
    if not product.image_url:
        return None
    guessed = product.category if product.category != "fixture" else "other"
    dims = product.dimensions
    return ProductOption(
        name=product.name,
        retailer=_host(product.product_url) or product.retailer,
        product_url=product.product_url,
        image_url=product.image_url,
        category=category or guessed,
        price_gbp=product.price_gbp,
        bbox_m=dims.bbox_m if dims else None,
        dimensions_text=dims.text if dims else None,
    )


def _read_all(urls: Sequence[str], read: PageReader) -> list[RetailerProduct | None]:
    """Read product pages in parallel, keeping the search order. A failed page is None."""

    def one(url: str) -> RetailerProduct | None:
        try:
            return read(url)
        except (CatalogError, ValueError, OSError):
            return None

    if not urls:
        return []
    with ThreadPoolExecutor(max_workers=len(urls)) as pool:
        return list(pool.map(one, urls))


def _ikea_options(
    query: str,
    category: Category | None,
    *,
    ikea: IkeaSearch,
    post: LinkupPost | None,
    read: PageReader,
) -> list[ProductOption]:
    """IKEA's own search first; Linkup restricted to ikea.com if that search is down."""
    try:
        found = ikea(query, MAX_RESULTS)
    except CatalogError:
        found = []
    options = [option for product in found if (option := _option(product, category))]
    if options or post is None:
        return options
    try:
        urls = _linkup_urls(
            post,
            {
                "q": query,
                "depth": "standard",
                "outputType": "searchResults",
                "includeDomains": ["ikea.com"],
            },
        )
    except SearchUnavailable:
        return []
    pages = [url for url in urls if "/p/" in urlsplit(url).path][:2]
    return [
        option
        for product in _read_all(pages, read)
        if product is not None and (option := _option(product, category))
    ]


def _web_options(
    query: str, category: Category | None, *, post: LinkupPost, read: PageReader
) -> list[ProductOption]:
    """Other retailers through Linkup, one product per retailer, each read from its page."""
    urls = _linkup_urls(
        post,
        {
            "q": f"{query} buy online UK",
            "depth": "standard",
            "outputType": "searchResults",
        },
    )
    candidates: list[str] = []
    hosts: set[str] = set()
    for url in urls:
        if _skipped(url) or _host(url) in hosts:
            continue
        hosts.add(_host(url))
        candidates.append(url)
        if len(candidates) == _PAGE_CANDIDATES:
            break
    return [
        option
        for product in _read_all(candidates, read)
        if product is not None
        and _relevant(product, query)
        and (option := _option(product, category))
    ]


def search_products(
    query: str,
    *,
    category: Category | None = None,
    max_price_gbp: float | None = None,
    linkup: LinkupPost | None,
    ikea: IkeaSearch = _ikea,
    read: PageReader = _read_page,
) -> list[ProductOption]:
    """Up to three purchasable products for `query`, IKEA first when IKEA has a match.

    Without Linkup only IKEA is searched. Raises SearchUnavailable when nothing could be
    searched at all; an empty list means the searches ran and found no usable product.
    """
    query = " ".join(query.split())[:100]
    if not query:
        raise SearchUnavailable("a search needs some words")

    def affordable(options: list[ProductOption]) -> list[ProductOption]:
        if max_price_gbp is None:
            return options
        return [o for o in options if o.price_gbp is None or o.price_gbp <= max_price_gbp]

    with ThreadPoolExecutor(max_workers=2) as pool:
        ikea_job = pool.submit(_ikea_options, query, category, ikea=ikea, post=linkup, read=read)
        web_job = (
            pool.submit(_web_options, query, category, post=linkup, read=read)
            if linkup is not None
            else None
        )
        ikea_found = affordable(ikea_job.result())
        web_error: SearchUnavailable | None = None
        try:
            web_found = affordable(web_job.result()) if web_job else []
        except SearchUnavailable as exc:
            web_found, web_error = [], exc
    if web_error and not ikea_found:
        raise web_error

    # One IKEA product, then other retailers, then more IKEA to fill three.
    picked = ikea_found[:1] + web_found[: MAX_RESULTS - min(1, len(ikea_found))]
    picked += ikea_found[1 : 1 + MAX_RESULTS - len(picked)]
    unique = {option.product_url: option for option in picked}
    return list(unique.values())[:MAX_RESULTS]
