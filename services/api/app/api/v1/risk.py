"""Fire Risk Prediction API router delegating to RiskService."""

from typing import Optional
from fastapi import APIRouter, Path, Query, Depends, status
from ...schemas.risk import RiskPredictRequest, RiskPredictResponse, RiskSummaryResponse
from ...schemas.geojson import GeoJSONFeatureCollection
from ...services.risk_service import RiskService
from ...dependencies.services import get_risk_service

router = APIRouter(prefix="/risk", tags=["Fire Risk"])


@router.get(
    "/{region_id}/summary",
    response_model=RiskSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get 24-Hour Risk Summary & Distribution for Region"
)
async def get_risk_summary(
    region_id: str = Path(..., description="Region UUID or code"),
    date: Optional[str] = Query(None, description="Forecast date (YYYY-MM-DD)"),
    target_date: Optional[str] = Query(None, description="Alias for forecast date (YYYY-MM-DD)"),
    service: RiskService = Depends(get_risk_service),
) -> RiskSummaryResponse:
    """
    Retrieve aggregated 24-hour fire risk statistics, total cell counts,
    and categorical risk level distributions for the specified region.
    """
    effective_date = date or target_date
    return service.get_risk_summary(
        region_id=region_id,
        target_date=effective_date,
    )


@router.get(
    "/{region_id}",
    response_model=GeoJSONFeatureCollection,
    status_code=status.HTTP_200_OK,
    summary="Get 24-Hour Fire Risk Grid Layer"
)
async def get_risk_layer(
    region_id: str = Path(..., description="Region UUID or code"),
    date: Optional[str] = Query(None, description="Forecast date (YYYY-MM-DD)"),
    target_date: Optional[str] = Query(None, description="Alias for forecast date (YYYY-MM-DD)"),
    min_risk: Optional[str] = Query(None, description="Filter minimum risk level (LOW, MODERATE, HIGH, EXTREME)"),
    service: RiskService = Depends(get_risk_service),
) -> GeoJSONFeatureCollection:
    """
    Retrieve 24-hour fire susceptibility predictions for 500m cells
    in the designated region formatted as a GeoJSON FeatureCollection.
    """
    effective_date = date or target_date
    return service.get_risk_layer(
        region_id=region_id,
        target_date=effective_date,
        min_risk=min_risk,
    )


@router.post(
    "/predict",
    response_model=RiskPredictResponse,
    status_code=status.HTTP_200_OK,
    summary="Trigger On-Demand Risk Prediction Inference"
)
async def predict_risk(
    request: RiskPredictRequest,
    service: RiskService = Depends(get_risk_service),
) -> RiskPredictResponse:
    """
    Execute or retrieve on-demand 24-hour fire susceptibility scoring
    for the selected region using the designated model pipeline.
    """
    return service.predict_risk(request)
