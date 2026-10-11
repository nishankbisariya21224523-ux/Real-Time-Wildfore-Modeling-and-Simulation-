"""Pydantic schemas for active and historical fire endpoints."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from .geojson import GeoJSONPoint, GeoJSONFeature, GeoJSONFeatureCollection


class ActiveFireProperties(BaseModel):
    """Properties for active fire satellite hotspot detection."""
    satellite: str
    detected_at: str
    brightness_temp_k: Optional[float] = None
    frp_mw: Optional[float] = None
    confidence_pct: float
    is_active: bool = True
    day_night: Optional[str] = "D"


class ActiveFireFeature(BaseModel):
    """GeoJSON Feature for a fire event."""
    type: str = "Feature"
    id: str
    geometry: GeoJSONPoint
    properties: ActiveFireProperties


class ActiveFireCollection(BaseModel):
    """GeoJSON FeatureCollection of fire detections."""
    type: str = "FeatureCollection"
    features: List[ActiveFireFeature]
    properties: Optional[Dict[str, Any]] = None
