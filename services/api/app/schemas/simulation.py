"""Pydantic schemas for 12-hour fire spread simulation endpoints."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, model_validator
from .geojson import GeoJSONPoint, GeoJSONFeature, GeoJSONPolygon, GeoJSONFeatureCollection


class IgnitionPointInput(BaseModel):
    """Input coordinates for simulation ignition origin."""
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude in WGS 84")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude in WGS 84")


class WeatherScenarioInput(BaseModel):
    """Optional meteorological scenario overrides."""
    wind_speed_ms: Optional[float] = Field(default=7.5, ge=0.0)
    wind_direction_deg: Optional[float] = Field(default=225.0, ge=0.0, le=360.0)
    temperature_c: Optional[float] = 30.0
    relative_humidity_pct: Optional[float] = Field(default=25.0, ge=0.0, le=100.0)


class SimulationCreateRequest(BaseModel):
    """Payload to initiate a 12-hour simulation job."""
    region_id: str
    ignition_point: Optional[IgnitionPointInput] = None
    ignition_points: Optional[List[IgnitionPointInput]] = None
    ignition_time: Optional[str] = None
    duration_hours: Optional[int] = Field(default=12, ge=1, le=12)
    max_duration_hours: Optional[int] = None
    temporal_step_minutes: Optional[int] = None
    weather_scenario: Optional[WeatherScenarioInput] = None
    fuel_type: Optional[str] = None
    slope_deg: Optional[float] = None
    aspect_deg: Optional[float] = None
    name: Optional[str] = "12-Hour Fire Spread Simulation"

    @model_validator(mode="after")
    def resolve_ignition_and_duration(self) -> "SimulationCreateRequest":
        # Resolve ignition_point from ignition_points if needed
        if self.ignition_point is None:
            if self.ignition_points and len(self.ignition_points) > 0:
                self.ignition_point = self.ignition_points[0]
            else:
                raise ValueError("Must provide ignition_point with latitude and longitude.")

        # Resolve duration
        if self.max_duration_hours is not None:
            self.duration_hours = max(1, min(12, self.max_duration_hours))
        elif self.duration_hours is None:
            self.duration_hours = 12

        return self


class SimulationCreateResponse(BaseModel):
    """Response returned upon successfully enqueuing a simulation."""
    simulation_id: str
    status: str
    created_at: str
    duration_hours: int
    poll_url: str


class SimulationMetrics(BaseModel):
    """Summary metrics of completed simulation."""
    total_area_burned_ha: float
    peak_spread_velocity_kmh: float
    dominant_spread_direction_deg: float


class SimulationStatusResponse(BaseModel):
    """Status tracking payload for simulation sessions."""
    simulation_id: str
    status: str
    progress_pct: float
    duration_hours: int
    created_at: str
    completed_at: Optional[str] = None
    ignition_point: GeoJSONPoint
    metrics: Optional[SimulationMetrics] = None
    engine_version: Optional[str] = "spread-ca-v001"
    completed_steps: Optional[int] = None
    total_steps: Optional[int] = None
    error_message: Optional[str] = None


class SimulationTimestepItem(BaseModel):
    """Item in the 12-hour progression timeline."""
    step_hour: int
    burned_area_ha: float
    spread_velocity_kmh: float
    spread_direction_deg: float
    intensity_mw: float


class SimulationTimelineResponse(BaseModel):
    """Full progression metrics timeline."""
    simulation_id: str
    total_steps: int
    timeline: List[SimulationTimestepItem]


class SimulationTimestepDetailResponse(BaseModel):
    """Detailed spatial boundary for a specific timestep hour."""
    simulation_id: str
    step_hour: int
    metrics: SimulationTimestepItem
    perimeter: GeoJSONFeature


class SimulationStepsFeatureCollectionResponse(BaseModel):
    """FeatureCollection of all simulation timestep boundaries."""
    type: str = "FeatureCollection"
    features: List[GeoJSONFeature]
    properties: Optional[Dict[str, Any]] = None
