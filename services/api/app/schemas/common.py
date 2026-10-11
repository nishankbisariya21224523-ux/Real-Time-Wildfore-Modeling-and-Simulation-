"""Common Pydantic models for errors, health, and pagination."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from .geojson import (
    GeoJSONGeometry,
    GeoJSONPoint,
    GeoJSONPolygon,
    GeoJSONMultiPolygon,
    GeoJSONFeature,
    GeoJSONFeatureCollection,
    to_geojson_geometry,
)


class ErrorDetail(BaseModel):
    """Inner error payload model."""
    code: str
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)
    request_id: str


class ErrorResponse(BaseModel):
    """Standardized API error envelope conforming to API_CONTRACT.md."""
    error: ErrorDetail


class ServiceStatus(BaseModel):
    """Status tracking for backing services."""
    database: str = "connected"
    redis: str = "connected"
    celery_broker: str = "connected"
    risk_model: Optional[str] = "available"



class HealthResponse(BaseModel):
    """API health check response model."""
    status: str = "healthy"
    service: str = "forest-fire-api"
    version: str
    environment: str
    timestamp: str
    database: str = "healthy"
    services: ServiceStatus


class PaginationMeta(BaseModel):
    """Pagination metadata model."""
    total: int
    limit: int
    offset: int
    has_more: bool
