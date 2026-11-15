"""HTTP import of a searched product: page -> unplaced, catalog-sized item."""

import json
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from contracts.schema import BBoxM, FurnitureItem
from services.reconstruction.assets.catalog_routes import WARNINGS_HEADER, catalog_router
from tests.reconstruction.assets.test_catalog import URL, Web


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.delenv("FAL_KEY", raising=False)  # Never call fal.ai from a test.
    app = FastAPI()
    app.include_router(catalog_router(tmp_path, fetch=Web()))
    return TestClient(app)


def test_import_returns_the_retailer_model_at_catalog_size(client: TestClient) -> None:
    response = client.post("/catalog/imports", json={"product_url": URL, "scene_id": "room-1"})
    assert response.status_code == 200
    item = FurnitureItem.model_validate(response.json())
    assert item.source == "catalog_search" and item.product_url == URL
    assert item.dimension_source == "catalog" and not item.is_proxy
    assert item.bbox_m == BBoxM(width=1.05, height=0.75, depth=0.5)
    assert item.glb_url.startswith("/api/reconstruction/assets/")
    assert (item.pose.x, item.pose.z, item.pose.yaw_deg) == (0, 0, 0)
    assert isinstance(json.loads(response.headers[WARNINGS_HEADER]), list)


@pytest.mark.parametrize(
    "body",
    [
        {"product_url": "https://shop.example/missing", "scene_id": "room-1"},
        {"product_url": "http://127.0.0.1/p/desk", "scene_id": "room-1"},
        {"product_url": URL, "scene_id": "   "},
    ],
)
def test_unusable_imports_are_422(client: TestClient, body: dict[str, str]) -> None:
    assert client.post("/catalog/imports", json=body).status_code == 422
