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


# --- Feature 1: Explain Elevated Risk Schemas ---
class FeatureImpactItem(BaseModel):
    feature: str
    value: str
    impact: str
    contribution_direction: str
    physical_rationale: str


class RiskExplanationRequest(BaseModel):
    region_name: str = Field(..., description="Target wildfire region name")
    predicted_probability: float = Field(..., ge=0.0, le=1.0, description="XGBoost predicted risk probability")
    risk_class: str = Field("HIGH", description="Predicted risk tier category")
    features: dict = Field(default_factory=dict, description="Actual numerical & categorical model feature values")


class RiskExplanationResponse(BaseModel):
    region_name: str
    predicted_probability: float
    risk_class: str
    explanation: str
    feature_importance: List[FeatureImpactItem]
    model_version: str
    provider: str
    timestamp: str


# --- Feature 2: Answer Copilot Questions Schemas ---
class CopilotQuestionRequest(BaseModel):
    question: str = Field(..., description="User question about the map or simulation")
    map_context: dict = Field(default_factory=dict, description="Active GIS map and simulation parameters")


class CopilotQuestionResponse(BaseModel):
    question: str
    answer: str
    context_region: str
    provider: str
    timestamp: str


# --- Feature 3: Retrieve Guidance Schemas ---
class GuidanceItem(BaseModel):
    document_id: str
    title: str
    jurisdiction: str
    excerpt: str


class GuidanceRetrievalRequest(BaseModel):
    query: str = Field(..., description="Search query for wildfire doctrine and preparedness")


class GuidanceRetrievalResponse(BaseModel):
    query: str
    total_documents_searched: int
    retrieved_guidance: List[GuidanceItem]
    timestamp: str


# --- Feature 4: Evidence-Linked Situation Brief Schemas ---
class SituationBriefRequest(BaseModel):
    region_name: str = Field(..., description="Monitored sector region name")
    fire_danger_index: float = Field(..., ge=0.0, le=100.0, description="Composite FDI (0-100)")
    temperature_c: float = Field(..., description="Surface temperature in Celsius")
    relative_humidity: float = Field(..., ge=0.0, le=100.0, description="Relative humidity percentage")
    wind_speed_kmh: float = Field(..., ge=0.0, description="Wind speed in km/h")
    active_hotspots: int = Field(0, ge=0, description="Active thermal detections count")
    burned_area_ha: float = Field(0.0, description="Burned or projected perimeter area in hectares")


class SituationBriefResponse(BaseModel):
    region_name: str
    fire_danger_index: float
    active_hotspots: int
    situation_brief: str
    evidence_citations: List[str]
    provider: str
    timestamp: str

