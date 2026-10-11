"""Schemas for 24-hour Fire Risk endpoints conforming to API_CONTRACT.md and DATA_CONTRACTS.md."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from .common import GeoJSONPolygon, GeoJSONFeatureCollection


class RiskCellProperties(BaseModel):
    """Properties for a 500m risk grid cell in GeoJSON response."""
    grid_cell_id: str
    cell_id: Optional[str] = None
    risk_probability: float
    risk_class: str
    fwi: Optional[float] = None
    fwi_index: Optional[float] = None
    fuel_type: Optional[str] = None
    elevation_m: Optional[float] = None
    elevation: Optional[float] = None
    slope_deg: Optional[float] = None
    slope: Optional[float] = None
    aspect: Optional[float] = None
    temperature_c: Optional[float] = None
    relative_humidity_pct: Optional[float] = None
    wind_speed_ms: Optional[float] = None
    model_version: Optional[str] = None
    forecast_start: Optional[str] = None
    forecast_end: Optional[str] = None
    prediction_timestamp: Optional[str] = None
    valid_for_date: Optional[str] = None


class RiskPredictRequest(BaseModel):
    """Payload to trigger an on-demand risk prediction run."""
    region_id: str
    target_date: str
    force_recompute: bool = False
    model_name: Optional[str] = "risk-xgboost-v001"
    model_version: Optional[str] = None


class RiskPredictResponse(BaseModel):
    """Response returned upon triggering a prediction run."""
    job_id: str
    region_id: str
    target_date: str
    status: str
    cells_predicted: int
    mean_risk_probability: float
    completed_at: str
    model_version: Optional[str] = "risk-xgboost-v001"


class RiskSummaryDistribution(BaseModel):
    """Distribution counts across categorical risk tiers."""
    low: int = 0
    moderate: int = 0
    high: int = 0
    extreme: int = 0


class RiskSummaryResponse(BaseModel):
    """Summary metrics of risk predictions across an entire region."""
    region_id: str
    target_date: str
    total_cells: int
    high_risk_cells: int
    extreme_risk_cells: int
    mean_probability: float
    model_version: str
    risk_distribution: RiskSummaryDistribution
