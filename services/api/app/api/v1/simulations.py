"""Fire Spread Simulation API router delegating to SimulationService."""

from fastapi import APIRouter, Path, Depends, status
from ...schemas.simulation import (
    SimulationCreateRequest,
    SimulationCreateResponse,
    SimulationStatusResponse,
    SimulationTimelineResponse,
    SimulationTimestepDetailResponse,
)
from ...schemas.geojson import GeoJSONFeatureCollection
from ...services.simulation_service import SimulationService
from ...dependencies.services import get_simulation_service

router = APIRouter(prefix="/simulations", tags=["Fire Spread Simulations"])


@router.post(
    "",
    response_model=SimulationCreateResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Initiate 12-Hour Fire Spread Simulation"
)
async def create_simulation(
    request: SimulationCreateRequest,
    service: SimulationService = Depends(get_simulation_service),
) -> SimulationCreateResponse:
    """
    Accept an ignition point and environmental parameters, queue an
    asynchronous Cellular Automata spread simulation job, and return tracking ID.
    """
    return service.create_simulation(request)


@router.get(
    "/{simulation_id}",
    response_model=SimulationStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Simulation Lifecycle Status & Metrics"
)
async def get_simulation_status(
    simulation_id: str = Path(..., description="Simulation UUID"),
    service: SimulationService = Depends(get_simulation_service),
) -> SimulationStatusResponse:
    """Retrieve current processing progress or completed metrics for a simulation job."""
    return service.get_simulation_status(simulation_id)


@router.get(
    "/{simulation_id}/timeline",
    response_model=SimulationTimelineResponse,
    status_code=status.HTTP_200_OK,
    summary="Get 12-Hour Spread Timeline Progression"
)
async def get_simulation_timeline(
    simulation_id: str = Path(..., description="Simulation UUID"),
    service: SimulationService = Depends(get_simulation_service),
) -> SimulationTimelineResponse:
    """Retrieve hourly burned area, velocity, and intensity metrics for all timesteps."""
    return service.get_simulation_timeline(simulation_id)


@router.get(
    "/{simulation_id}/timesteps/{hour}",
    response_model=SimulationTimestepDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Spatial Boundary for Specific Simulation Hour"
)
async def get_simulation_timestep(
    simulation_id: str = Path(..., description="Simulation UUID"),
    hour: int = Path(..., ge=0, le=12, description="Timestep hour (0-12)"),
    service: SimulationService = Depends(get_simulation_service),
) -> SimulationTimestepDetailResponse:
    """Retrieve GeoJSON boundary perimeter for a specific hour of the fire spread."""
    return service.get_simulation_timestep(simulation_id, hour)


@router.get(
    "/{simulation_id}/steps",
    response_model=GeoJSONFeatureCollection,
    status_code=status.HTTP_200_OK,
    summary="Get All Simulation Timestep Perimeters as GeoJSON FeatureCollection"
)
async def get_simulation_steps(
    simulation_id: str = Path(..., description="Simulation UUID"),
    service: SimulationService = Depends(get_simulation_service),
) -> GeoJSONFeatureCollection:
    """Retrieve all hourly boundary perimeters as a unified GeoJSON FeatureCollection."""
    return service.get_simulation_steps_collection(simulation_id)
