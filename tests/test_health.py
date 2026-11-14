import importlib

import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize("service", ["reconstruction", "spatial_engine", "media_gen"])
def test_service_health_and_cors(service: str) -> None:
    app = importlib.import_module(f"services.{service}.main").app
    with TestClient(app) as client:
        response = client.get("/health", headers={"Origin": "http://localhost:5173"})
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "service": service}
        assert response.headers["access-control-allow-origin"] == "*"
