"""Pydantic schemas for region endpoints."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from .geojson import GeoJSONPoint, GeoJSONFeature


class RegionListItem(BaseModel):
    """Summary item for region list queries."""
    id: str
    code: str
    name: str
    state: str
    area_sqkm: float
    centroid: GeoJSONPoint
    created_at: Optional[str] = None


class RegionListResponse(BaseModel):
    """Paginated list of regions response."""
    count: int
    results: List[RegionListItem]


class RegionDetailResponse(BaseModel):
    """Detailed regional metadata with PostGIS boundary polygon."""
    id: str
    code: str
    name: str
    state: str
    area_sqkm: float
    boundary: GeoJSONFeature
    grid_resolution_meters: int = 500
    total_cells: int
