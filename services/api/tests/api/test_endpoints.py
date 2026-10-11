"""API endpoint tests verifying HTTP contracts, request IDs, and GeoJSON structures."""

from fastapi.testclient import TestClient
from services.api.app.main import app

client = TestClient(app)


def test_health_check_api():
    """Verify GET /api/v1/health responds with 200 OK and valid health report."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "services" in data
    assert "X-Request-ID" in response.headers


def test_regions_api_lifecycle():
    """Verify regions listing and single region retrieval with boundary."""
    resp = client.get("/api/v1/regions")
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] >= 2
    assert len(data["results"]) >= 2
    reg_id = data["results"][0]["id"]

    # Retrieve valid region details
    detail_resp = client.get(f"/api/v1/regions/{reg_id}")
    assert detail_resp.status_code == 200
    detail_data = detail_resp.json()
    assert detail_data["id"] == reg_id
    assert detail_data["boundary"]["type"] == "Feature"
    assert detail_data["boundary"]["geometry"]["type"] == "Polygon"

    # 404 Not Found error handling
    err_resp = client.get("/api/v1/regions/non-existent-region-id")
    assert err_resp.status_code == 404
    err_json = err_resp.json()
    assert "error" in err_json
    assert err_json["error"]["code"] == "RESOURCE_NOT_FOUND"
    assert "request_id" in err_json["error"]


def test_active_fires_api():
    """Verify GET /api/v1/fires/active returns GeoJSON FeatureCollection."""
    resp = client.get("/api/v1/fires/active?hours=24&min_confidence=50")
    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) >= 1
    feat = data["features"][0]
    assert feat["type"] == "Feature"
    assert feat["geometry"]["type"] == "Point"
    assert "satellite" in feat["properties"]


def test_risk_endpoints_api():
    """Verify GET /api/v1/risk/{region_id} and POST /api/v1/risk/predict contracts."""
    resp = client.get("/api/v1/risk/UTTARAKHAND_GARHWAL")
    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) >= 1

    predict_payload = {
        "region_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "target_date": "2026-10-06",
        "force_recompute": False,
        "model_name": "xgboost-baseline"
    }
    pred_resp = client.post("/api/v1/risk/predict", json=predict_payload)
    assert pred_resp.status_code == 200
    pred_data = pred_resp.json()
    assert pred_data["status"] == "COMPLETED"
    assert pred_data["cells_predicted"] > 0


def test_simulations_api_lifecycle():
    """Verify POST /api/v1/simulations, status, timeline, and timestep endpoints."""
    create_payload = {
        "region_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "ignition_point": {"latitude": 30.2104, "longitude": 78.7523},
        "ignition_time": "2026-10-06T12:00:00Z",
        "duration_hours": 12,
        "weather_scenario": {
            "wind_speed_ms": 7.5,
            "wind_direction_deg": 245.0,
            "temperature_c": 32.0,
            "relative_humidity_pct": 22.0
        }
    }
    create_resp = client.post("/api/v1/simulations", json=create_payload)
    assert create_resp.status_code == 202
    create_data = create_resp.json()
    assert create_data["status"] == "QUEUED"
    sim_id = create_data["simulation_id"]
    assert "poll_url" in create_data

    # Check simulation status
    status_resp = client.get(f"/api/v1/simulations/{sim_id}")
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert status_data["simulation_id"] == sim_id
    assert status_data["duration_hours"] == 12

    # Check 12-hour timeline
    timeline_resp = client.get(f"/api/v1/simulations/{sim_id}/timeline")
    assert timeline_resp.status_code == 200
    timeline_data = timeline_resp.json()
    assert timeline_data["total_steps"] == 12
    assert len(timeline_data["timeline"]) == 12

    # Check specific hour timestep boundary
    step_resp = client.get(f"/api/v1/simulations/{sim_id}/timesteps/3")
    assert step_resp.status_code == 200
    step_data = step_resp.json()
    assert step_data["step_hour"] == 3
    assert step_data["perimeter"]["type"] == "Feature"
    assert step_data["perimeter"]["geometry"]["type"] == "Polygon"

    # Out-of-bounds hour validation error (422)
    oob_resp = client.get(f"/api/v1/simulations/{sim_id}/timesteps/15")
    assert oob_resp.status_code == 422


def test_layers_api():
    """Verify GET /api/v1/layers/{layer_type} metadata and rejection of invalid types."""
    resp = client.get("/api/v1/layers/fuel?region_id=3fa85f64-5717-4562-b3fc-2c963f66afa6")
    assert resp.status_code == 200
    data = resp.json()
    assert data["layer_type"] == "fuel"
    assert data["resolution_meters"] == 500
    assert "1" in data["legend"]

    # Invalid layer type
    err_resp = client.get("/api/v1/layers/unsupported_layer?region_id=test")
    assert err_resp.status_code == 422
