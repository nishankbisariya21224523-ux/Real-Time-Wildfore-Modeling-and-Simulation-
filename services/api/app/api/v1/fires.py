"""Active Fire Hotspots API router delegating to FireService."""

from typing import Optional
from fastapi import APIRouter, Query, Depends, status
from ...schemas.geojson import GeoJSONFeatureCollection
from ...services.fire_service import FireService
from ...dependencies.services import get_fire_service

router = APIRouter(prefix="/fires", tags=["Active Fires"])


@router.get(
    "/active",
    response_model=GeoJSONFeatureCollection,
    status_code=status.HTTP_200_OK,
    summary="Get Active Satellite Fire Detections"
)
async def get_active_fires(
    region_id: Optional[str] = Query(None, description="Filter active detections by region"),
    hours: int = Query(24, ge=1, le=72, description="Observation time window in hours"),
    min_confidence: float = Query(50.0, ge=0.0, le=100.0, description="Minimum detection confidence percentage"),
    service: FireService = Depends(get_fire_service),
) -> GeoJSONFeatureCollection:
    """
    Retrieve active thermal anomalies and hotspot locations detected via
    MODIS, VIIRS, or INSAT-3D sensors within the specified time window.
    """
    return service.get_active_fires(
        region_id=region_id,
        hours=hours,
        min_confidence=min_confidence,
    )
