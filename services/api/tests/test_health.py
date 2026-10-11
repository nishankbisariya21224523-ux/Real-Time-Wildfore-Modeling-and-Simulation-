"""Unit tests for FastAPI health and core endpoints using TestClient."""

from fastapi.testclient import TestClient
from services.api.app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Verify that GET /api/v1/health returns 200 OK and expected structure."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data
    assert "services" in data
    assert "database" in data["services"]
    assert "redis" in data["services"]


def test_root_endpoint():
    """Verify that root endpoint returns app metadata."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["name"] == "forest-fire-platform"


def test_regions_endpoints():
    """Verify that /api/v1/regions lists available regions and handles 404 cleanly."""
    resp = client.get("/api/v1/regions")
    assert resp.status_code == 200
    data = resp.json()
    assert "count" in data
    assert len(data["results"]) >= 1

    reg_id = data["results"][0]["id"]
    detail_resp = client.get(f"/api/v1/regions/{reg_id}")
    assert detail_resp.status_code == 200
    detail_data = detail_resp.json()
    assert detail_data["id"] == reg_id

    # 404 test
    not_found_resp = client.get("/api/v1/regions/non-existent-id")
    assert not_found_resp.status_code == 404
    err_data = not_found_resp.json()
    assert err_data["error"]["code"] == "RESOURCE_NOT_FOUND"


def test_active_fires_endpoint():
    """Verify GET /api/v1/fires/active returns GeoJSON FeatureCollection."""
    resp = client.get("/api/v1/fires/active")
    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "FeatureCollection"
    assert "features" in data
