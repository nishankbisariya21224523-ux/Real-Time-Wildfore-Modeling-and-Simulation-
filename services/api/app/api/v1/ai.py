"""FastAPI Router for DigitalOcean GenAI Wildfire Incident Command & Tactical Advisories."""
from fastapi import APIRouter, Depends, status
from ...schemas.ai import (
    IncidentBriefingRequest,
    IncidentBriefingResponse,
    AIStatusResponse,
)
from ...services.do_ai_service import DigitalOceanAIService
from ...dependencies.services import get_do_ai_service

router = APIRouter(prefix="/ai", tags=["DigitalOcean AI"])


@router.get(
    "/status",
    response_model=AIStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Check DigitalOcean GenAI Service Health",
)
async def get_ai_status(
    service: DigitalOceanAIService = Depends(get_do_ai_service),
) -> AIStatusResponse:
    """Checks the health, configuration, and ready-state of the DigitalOcean GenAI integration."""
    return AIStatusResponse(
        provider="DigitalOcean GenAI",
        is_configured=service.is_configured,
        default_model=service.model,
        status="active" if service.is_configured else "fallback_heuristic_ready",
    )


@router.post(
    "/advisory",
    response_model=IncidentBriefingResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Wildfire Incident Tactical SITREP",
)
async def generate_wildfire_advisory(
    payload: IncidentBriefingRequest,
    service: DigitalOceanAIService = Depends(get_do_ai_service),
) -> IncidentBriefingResponse:
    """
    Generates an authoritative tactical SITREP and containment strategy
    using DigitalOcean GenAI serverless foundation models (with heuristic fallback).
    """
    result = await service.generate_incident_briefing(
        region_name=payload.region_name,
        fire_danger_index=payload.fire_danger_index,
        temperature_c=payload.temperature_c,
        relative_humidity=payload.relative_humidity,
        wind_speed_kmh=payload.wind_speed_kmh,
        wind_direction_deg=payload.wind_direction_deg,
        active_hotspots=payload.active_hotspots,
        slope_pct=payload.slope_pct,
        fuel_type=payload.fuel_type,
        evacuation_status=payload.evacuation_status,
    )
    return IncidentBriefingResponse(**result)
