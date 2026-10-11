"""Comprehensive Phase 8 integration tests for asynchronous fire spread simulation.

Tests cover:
- FastAPI simulation session initiation and payload validation
- Boundary containment verification (inside vs outside region)
- Duration bounds (1-12 hours) validation
- Celery task execution invoking Phase 7 Cellular Automata Spread Engine
- Simulation lifecycle status polling and terminal states
- Hourly progression timeline retrieval
- Timestep GeoJSON boundary perimeters (Hour 0 through 12)
- FeatureCollection of all steps for GIS animation
- Environmental overrides (wind speed, wind direction, fuel type)
"""

import uuid
import pytest
from fastapi.testclient import TestClient

from services.api.app.main import app
from services.api.app.tasks.simulation_tasks import run_fire_spread_simulation, SIMULATION_CACHE

client = TestClient(app)

GARHWAL_REGION_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
VALID_IGNITION_POINT = {"latitude": 30.2104, "longitude": 78.7523}
OUTSIDE_IGNITION_POINT = {"latitude": 32.5000, "longitude": 81.0000}


def test_simulation_creation_success():
    """Verify POST /api/v1/simulations returns 202 Accepted with QUEUED job."""
    payload = {
        "region_id": GARHWAL_REGION_ID,
        "ignition_point": VALID_IGNITION_POINT,
        "duration_hours": 6,
        "name": "Integration Test Run",
        "weather_scenario": {
            "wind_speed_ms": 10.0,
            "wind_direction_deg": 225.0,
        },
        "fuel_type": "CONIFER_HIGH_FLAMMABILITY",
    }
    resp = client.post("/api/v1/simulations", json=payload)
    assert resp.status_code == 202
    data = resp.json()
    assert data["status"] in ("QUEUED", "RUNNING", "COMPLETED")
    assert "simulation_id" in data
    assert data["duration_hours"] == 6
    assert f"/api/v1/simulations/{data['simulation_id']}" in data["poll_url"]


def test_simulation_ignition_outside_region():
    """Verify ignition coordinate outside region boundary is rejected with 422."""
    payload = {
        "region_id": GARHWAL_REGION_ID,
        "ignition_point": OUTSIDE_IGNITION_POINT,
        "duration_hours": 6,
    }
    resp = client.post("/api/v1/simulations", json=payload)
    assert resp.status_code == 422
    err_json = resp.json()
    assert "error" in err_json
    assert err_json["error"]["code"] == "IGNITION_OUTSIDE_REGION"


def test_simulation_duration_bounds():
    """Verify duration exceeding 12 hours or below 1 hour is rejected."""
    # Exceeding 12h
    payload_high = {
        "region_id": GARHWAL_REGION_ID,
        "ignition_point": VALID_IGNITION_POINT,
        "duration_hours": 15,
    }
    resp_high = client.post("/api/v1/simulations", json=payload_high)
    assert resp_high.status_code == 422

    # Below 1h
    payload_low = {
        "region_id": GARHWAL_REGION_ID,
        "ignition_point": VALID_IGNITION_POINT,
        "duration_hours": 0,
    }
    resp_low = client.post("/api/v1/simulations", json=payload_low)
    assert resp_low.status_code == 422


def test_simulation_invalid_coordinates():
    """Verify invalid geographic coordinates are rejected."""
    payload = {
        "region_id": GARHWAL_REGION_ID,
        "ignition_point": {"latitude": 95.0, "longitude": 78.0},
        "duration_hours": 6,
    }
    resp = client.post("/api/v1/simulations", json=payload)
    assert resp.status_code == 422


def test_simulation_full_lifecycle_and_steps():
    """Verify complete lifecycle: initiate -> complete -> status -> timeline -> timestep -> steps."""
    payload = {
        "region_id": GARHWAL_REGION_ID,
        "ignition_point": VALID_IGNITION_POINT,
        "duration_hours": 4,
        "name": "Lifecycle 4h Test",
    }
    resp = client.post("/api/v1/simulations", json=payload)
    assert resp.status_code == 202
    sim_id = resp.json()["simulation_id"]

    # Status check
    status_resp = client.get(f"/api/v1/simulations/{sim_id}")
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert status_data["simulation_id"] == sim_id
    assert status_data["status"] == "COMPLETED"
    assert status_data["duration_hours"] == 4
    assert status_data["progress_pct"] == 100.0
    assert status_data["metrics"] is not None
    assert status_data["metrics"]["total_area_burned_ha"] > 0.0

    # Timeline check
    timeline_resp = client.get(f"/api/v1/simulations/{sim_id}/timeline")
    assert timeline_resp.status_code == 200
    timeline_data = timeline_resp.json()
    assert timeline_data["total_steps"] == 4
    assert len(timeline_data["timeline"]) == 4

    # Hour 0 timestep check (initial ignition cell)
    step0_resp = client.get(f"/api/v1/simulations/{sim_id}/timesteps/0")
    assert step0_resp.status_code == 200
    step0_data = step0_resp.json()
    assert step0_data["step_hour"] == 0
    assert step0_data["perimeter"]["type"] == "Feature"
    assert step0_data["perimeter"]["properties"]["elapsed_minutes"] == 0

    # Hour 2 timestep check
    step2_resp = client.get(f"/api/v1/simulations/{sim_id}/timesteps/2")
    assert step2_resp.status_code == 200
    step2_data = step2_resp.json()
    assert step2_data["step_hour"] == 2
    assert step2_data["perimeter"]["type"] == "Feature"
    assert step2_data["metrics"]["burned_area_ha"] > 0.0

    # FeatureCollection steps check
    steps_resp = client.get(f"/api/v1/simulations/{sim_id}/steps")
    assert steps_resp.status_code == 200
    steps_fc = steps_resp.json()
    assert steps_fc["type"] == "FeatureCollection"
    # Contains hour 0 through hour 4 = 5 features
    assert len(steps_fc["features"]) == 5
    for i, feature in enumerate(steps_fc["features"]):
        assert feature["type"] == "Feature"
        assert feature["geometry"]["type"] in ("Polygon", "MultiPolygon")
        assert feature["properties"]["step_hour"] == i


def test_celery_task_direct_execution_with_weather_overrides():
    """Verify Celery task directly calls Phase 7 CA Spread Engine with environmental inputs."""
    sim_id = str(uuid.uuid4())
    task_payload = {
        "region_id": GARHWAL_REGION_ID,
        "ignition_lat": 30.2104,
        "ignition_lon": 78.7523,
        "duration_hours": 3,
        "wind_speed_ms": 12.0,
        "wind_direction_deg": 180.0,
        "fuel_type": "CONIFER_HIGH_FLAMMABILITY",
        "slope_deg": 15.0,
        "aspect_deg": 180.0,
    }

    result = run_fire_spread_simulation(sim_id, task_payload)
    assert result["status"] == "COMPLETED"
    assert result["simulation_id"] == sim_id
    assert result["total_area_burned_ha"] > 0.0
    assert result["timesteps_count"] == 3
    assert sim_id in SIMULATION_CACHE
    assert SIMULATION_CACHE[sim_id]["status"] == "COMPLETED"
    assert len(SIMULATION_CACHE[sim_id]["steps_features"]) == 4  # hour 0 + 3 hours
