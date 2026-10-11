"""DigitalOcean AI incident briefing request and response schemas."""
from typing import List
from pydantic import BaseModel, Field


class IncidentBriefingRequest(BaseModel):
    region_name: str = Field(..., description="Target wildfire observation region name")
    fire_danger_index: float = Field(..., ge=0.0, le=100.0, description="Composite FDI (0-100)")
    temperature_c: float = Field(..., description="Surface temperature in Celsius")
    relative_humidity: float = Field(..., ge=0.0, le=100.0, description="Relative humidity percentage")
    wind_speed_kmh: float = Field(..., ge=0.0, description="Wind speed in km/h")
    wind_direction_deg: float = Field(..., ge=0.0, le=360.0, description="Wind direction azimuth (0-360)")
    active_hotspots: int = Field(0, ge=0, description="Number of active thermal hotspot detections")
    slope_pct: float = Field(0.0, description="Average terrain slope percentage")
    fuel_type: str = Field("Timber / Mixed Conifer", description="Dominant fuel bed vegetation type")
    evacuation_status: str = Field("ADVISORY", description="Current civil alert status")


class IncidentBriefingResponse(BaseModel):
    region_name: str
    threat_level: str
    fire_danger_index: float
    summary: str
    tactical_actions: List[str]
    evacuation_directive: str
    provider: str
    model: str
    timestamp: str


class AIStatusResponse(BaseModel):
    provider: str = "DigitalOcean GenAI"
    is_configured: bool
    default_model: str
    status: str
