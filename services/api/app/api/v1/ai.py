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


# =============================================================================
# DigitalOcean Gradient AI Core Intelligence Endpoints
# =============================================================================

from ...schemas.ai import (
    RiskExplanationRequest,
    RiskExplanationResponse,
    CopilotQuestionRequest,
    CopilotQuestionResponse,
    GuidanceRetrievalRequest,
    GuidanceRetrievalResponse,
    SituationBriefRequest,
    SituationBriefResponse,
)
from ...services.gradient_ai_service import DigitalOceanGradientAIService
from ...dependencies.services import get_gradient_ai_service


@router.post(
    "/explain-risk",
    response_model=RiskExplanationResponse,
    status_code=status.HTTP_200_OK,
    summary="Explain Elevated Predicted Risk Using Model Features",
)
async def explain_risk_features_endpoint(
    payload: RiskExplanationRequest,
    service: DigitalOceanGradientAIService = Depends(get_gradient_ai_service),
) -> RiskExplanationResponse:
    """
    Explains why a selected region has elevated predicted risk using actual
    XGBoost model features (NDVI, NDWI, slope, temperature, humidity, wind, fuel).
    """
    result = await service.explain_risk_features(
        region_name=payload.region_name,
        predicted_probability=payload.predicted_probability,
        risk_class=payload.risk_class,
        features=payload.features,
    )
    return RiskExplanationResponse(**result)


@router.post(
    "/ask-copilot",
    response_model=CopilotQuestionResponse,
    status_code=status.HTTP_200_OK,
    summary="Answer Questions About Risk Map & Simulated Spread",
)
async def ask_copilot_endpoint(
    payload: CopilotQuestionRequest,
    service: DigitalOceanGradientAIService = Depends(get_gradient_ai_service),
) -> CopilotQuestionResponse:
    """
    Answers natural language questions about the displayed risk map, active hotspots,
    and Cellular Automata spread simulation parameters.
    """
    result = await service.answer_copilot_question(
        question=payload.question,
        map_context=payload.map_context,
    )
    return CopilotQuestionResponse(**result)


@router.post(
    "/retrieve-guidance",
    response_model=GuidanceRetrievalResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve Wildfire Preparedness Guidance from Trusted Documents",
)
async def retrieve_guidance_endpoint(
    payload: GuidanceRetrievalRequest,
    service: DigitalOceanGradientAIService = Depends(get_gradient_ai_service),
) -> GuidanceRetrievalResponse:
    """
    Retrieves official preparedness and safety doctrine from trusted authorities (NDMA, NWCG, NFPA, FSI).
    """
    result = service.retrieve_guidance(query=payload.query)
    return GuidanceRetrievalResponse(**result)


@router.post(
    "/situation-brief",
    response_model=SituationBriefResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Concise Evidence-Linked Regional Situation Brief",
)
async def generate_situation_brief_endpoint(
    payload: SituationBriefRequest,
    service: DigitalOceanGradientAIService = Depends(get_gradient_ai_service),
) -> SituationBriefResponse:
    """
    Generates a concise, evidence-linked regional situation brief (SITBRIEF) linking
    telemetry, machine learning predictions, satellite observations, and doctrine citations.
    """
    result = await service.generate_situation_brief(
        region_name=payload.region_name,
        fire_danger_index=payload.fire_danger_index,
        temperature_c=payload.temperature_c,
        relative_humidity=payload.relative_humidity,
        wind_speed_kmh=payload.wind_speed_kmh,
        active_hotspots=payload.active_hotspots,
        burned_area_ha=payload.burned_area_ha,
    )
    return SituationBriefResponse(**result)

