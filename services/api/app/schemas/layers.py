"""Schemas for Static and Environmental GIS Layer endpoints."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class LayerMetadataResponse(BaseModel):
    """Metadata and legend for a static GIS layer."""
    layer_type: str
    region_id: str
    resolution_meters: int = 500
    legend: Dict[str, str] = Field(default_factory=dict)
    source: str


class LayerCatalogItem(BaseModel):
    """Metadata for a catalog GIS layer."""
    id: str
    name: str
    category: str
    description: str
    source: str
    is_available: bool = True
    resolution: str = "500m"
    legend: Optional[List[Dict[str, str]]] = None
