"""The library route delegates to the retailer pipeline and reports failures honestly."""

from fastapi.testclient import TestClient

from services.reconstruction import catalog_routes
from services.reconstruction.assets.retailer import CatalogError
from services.reconstruction.main import app

client = TestClient(app)


def test_import_rejects_invalid_inputs():
    for payload in [
        {"url": "file:///etc/passwd", "scene_id": "room"},
        {"url": "https://www.ikea.com/product", "scene_id": " "},
    ]:
        assert client.post("/catalog/import", json=payload).status_code == 422


def test_import_returns_readable_retailer_failure(monkeypatch):
    def fail(url, scene_id, **kwargs):
        assert url == "https://www.ikea.com/gb/en/p/micke-123/"
        assert scene_id == "room"
        raise CatalogError("The page did not describe a product")

    monkeypatch.setattr(catalog_routes, "import_catalog_asset", fail)
    response = client.post(
        "/catalog/import",
        json={"url": "https://www.ikea.com/gb/en/p/micke-123/", "scene_id": "room"},
    )
    assert response.status_code == 422
    assert response.json()["detail"] == "The page did not describe a product"


def test_import_configures_live_providers_when_key_present(monkeypatch):
    from unittest.mock import Mock

    masks, meshes = Mock(), Mock()
    monkeypatch.setenv("FAL_KEY", "test-key")
    mask_factory, mesh_factory = Mock(return_value=masks), Mock(return_value=meshes)
    monkeypatch.setattr(catalog_routes, "FalSamProvider", mask_factory)
    monkeypatch.setattr(catalog_routes, "catalog_mesh_providers", mesh_factory)

    def inspect(url, scene_id, **kwargs):
        assert kwargs["mask_provider"] is masks
        assert kwargs["mesh_provider"] is meshes
        raise CatalogError("verified")

    monkeypatch.setattr(catalog_routes, "import_catalog_asset", inspect)
    response = client.post(
        "/catalog/import", json={"url": "https://www.ikea.com/p/test", "scene_id": "room"}
    )
    assert response.status_code == 422
    assert response.json()["detail"] == "verified"
    mask_factory.assert_called_once_with(key="test-key")
    mesh_factory.assert_called_once_with("test-key", timeout_s=300)


def test_import_stays_offline_without_key(monkeypatch):
    monkeypatch.delenv("FAL_KEY", raising=False)

    def inspect(url, scene_id, **kwargs):
        assert kwargs["mask_provider"] is None
        assert kwargs["mesh_provider"] is None
        raise CatalogError("verified")

    monkeypatch.setattr(catalog_routes, "import_catalog_asset", inspect)
    response = client.post(
        "/catalog/import", json={"url": "https://www.ikea.com/p/test", "scene_id": "room"}
    )
    assert response.json()["detail"] == "verified"
