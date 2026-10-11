"""Unit tests for Pydantic request and response schemas."""

import pytest
from pydantic import ValidationError
from services.api.app.schemas.region import RegionListItem, RegionDetailResponse
from services.api.app.schemas.simulation import (
    SimulationCreateRequest,
    IgnitionPointInput,
    WeatherScenarioInput,
)
from services.api.app.schemas.common import HealthResponse, ServiceStatus
from services.api.app.schemas.geojson import GeoJSONPoint, GeoJSONFeature


def test_ignition_point_coordinates_validation():
    """Verify IgnitionPointInput enforces valid WGS 84 latitude [-90, 90] and longitude [-180, 180]."""
    valid = IgnitionPointInput(latitude=30.2, longitude=78.7)
    assert valid.latitude == 30.2
    assert valid.longitude == 78.7

    with pytest.raises(ValidationError):
        IgnitionPointInput(latitude=95.0, longitude=78.7)

    with pytest.raises(ValidationError):
        IgnitionPointInput(latitude=30.2, longitude=200.0)


def test_simulation_create_request_validation():
    """Verify SimulationCreateRequest schema constraints."""
    req = SimulationCreateRequest(
        region_id="3fa85f64-5717-4562-b3fc-2c963f66afa6",
        ignition_point=IgnitionPointInput(latitude=30.2, longitude=78.7),
        ignition_time="2026-10-06T12:00:00Z",
        duration_hours=12,
        weather_scenario=WeatherScenarioInput(wind_speed_ms=8.5, wind_direction_deg=180.0),
    )
    assert req.duration_hours == 12
    assert req.weather_scenario.wind_speed_ms == 8.5

    # Duration must be between 1 and 12 hours
    with pytest.raises(ValidationError):
        SimulationCreateRequest(
            region_id="test",
            ignition_point=IgnitionPointInput(latitude=30.2, longitude=78.7),
            ignition_time="2026-10-06T12:00:00Z",
            duration_hours=24,  # Exceeds max 12
        )


def test_health_response_schema():
    """Verify HealthResponse structure."""
    hr = HealthResponse(
        status="healthy",
        service="forest-fire-api",
        version="1.0.0",
        environment="development",
        timestamp="2026-10-06T00:00:00Z",
        database="healthy",
        services=ServiceStatus(database="connected", redis="connected", celery_broker="connected"),
    )
    assert hr.status == "healthy"
    assert hr.database == "healthy"
    assert hr.services.database == "connected"
