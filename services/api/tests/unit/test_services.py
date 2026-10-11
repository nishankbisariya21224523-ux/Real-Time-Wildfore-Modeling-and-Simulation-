"""Unit tests for service layer behavior and business logic."""

import pytest
from services.api.app.services.region_service import RegionService
from services.api.app.services.fire_service import FireService
from services.api.app.services.risk_service import RiskService
from services.api.app.services.simulation_service import SimulationService
from services.api.app.services.layer_service import LayerService
from services.api.app.schemas.simulation import SimulationCreateRequest, IgnitionPointInput
from services.api.app.schemas.risk import RiskPredictRequest
from services.api.app.core.exceptions import ResourceNotFoundException, ValidationException


def test_region_service_list_and_get():
    """Verify RegionService returns structured items and raises 404 for missing region."""
    service = RegionService()
    regions = service.list_regions()
    assert regions.count >= 2
    assert len(regions.results) >= 2

    # Filter by state
    kerala_regions = service.list_regions(state="Kerala")
    assert kerala_regions.count >= 1
    assert any("Wayanad" in r.name for r in kerala_regions.results)

    # Get valid region
    reg = service.get_region("UTTARAKHAND_GARHWAL")
    assert reg.code == "UTTARAKHAND_GARHWAL"
    assert reg.boundary.geometry["type"] == "Polygon"

    # Missing region raises ResourceNotFoundException
    with pytest.raises(ResourceNotFoundException):
        service.get_region("NON_EXISTENT_REGION_CODE")


def test_fire_service_active_fires():
    """Verify FireService returns FeatureCollection with detections."""
    service = FireService()
    fires_fc = service.get_active_fires(min_confidence=50.0)
    assert fires_fc.type == "FeatureCollection"
    assert len(fires_fc.features) >= 1
    assert fires_fc.features[0].geometry["type"] == "Point"


def test_risk_service_contracts():
    """Verify RiskService returns risk layer and predict response."""
    service = RiskService()
    layer = service.get_risk_layer("UTTARAKHAND_GARHWAL")
    assert layer.type == "FeatureCollection"
    assert len(layer.features) >= 1

    predict_req = RiskPredictRequest(
        region_id="UTTARAKHAND_GARHWAL",
        target_date="2026-10-06"
    )
    pred_res = service.predict_risk(predict_req)
    assert pred_res.status == "COMPLETED"
    assert pred_res.cells_predicted > 0


def test_simulation_service_lifecycle():
    """Verify SimulationService handles creation, timeline, and timesteps."""
    service = SimulationService()
    req = SimulationCreateRequest(
        region_id="3fa85f64-5717-4562-b3fc-2c963f66afa6",
        ignition_point=IgnitionPointInput(latitude=30.21, longitude=78.75),
        ignition_time="2026-10-06T10:00:00Z",
        duration_hours=12,
    )
    created = service.create_simulation(req)
    assert created.status == "QUEUED"
    assert created.duration_hours == 12

    # Status
    status_res = service.get_simulation_status(created.simulation_id)
    assert status_res.simulation_id == created.simulation_id

    # Timeline (12 steps)
    timeline = service.get_simulation_timeline(created.simulation_id)
    assert timeline.total_steps == 12
    assert len(timeline.timeline) == 12

    # Specific timestep
    step = service.get_simulation_timestep(created.simulation_id, hour=3)
    assert step.step_hour == 3
    assert step.perimeter.geometry["type"] == "Polygon"

    # Invalid hour raises ValidationException
    with pytest.raises(ValidationException):
        service.get_simulation_timestep(created.simulation_id, hour=15)


def test_layer_service():
    """Verify LayerService serves allowed layer types and rejects invalid ones."""
    service = LayerService()
    meta = service.get_layer_metadata("fuel", "UTTARAKHAND_GARHWAL")
    assert meta.layer_type == "fuel"
    assert meta.resolution_meters == 500
    assert "1" in meta.legend

    with pytest.raises(ValidationException):
        service.get_layer_metadata("invalid_layer_xyz", "UTTARAKHAND_GARHWAL")
