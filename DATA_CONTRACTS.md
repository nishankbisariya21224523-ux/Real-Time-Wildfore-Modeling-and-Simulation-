# Shared Data Contracts Specification

This document defines the canonical domain models, schemas, and input/output interfaces for the Predictive Forest Fire Risk & Spread Simulation Platform.
These contracts are language-agnostic specifications mirrored in Python Pydantic models (`packages/shared-types` and service schemas) and TypeScript interfaces (`apps/web/src/types`).

---

## 1. Canonical Domain Entities

### 1.1 Region
Represents a recognized forest division, sanctuary, or administrative monitoring jurisdiction.

```json
{
  "$id": "https://forestfire.platform/schemas/region.json",
  "type": "object",
  "required": ["id", "code", "name", "state", "boundary", "area_sqkm"],
  "properties": {
    "id": { "type": "string", "format": "uuid" },
    "code": { "type": "string", "pattern": "^[A-Z0-9_]+$" },
    "name": { "type": "string" },
    "state": { "type": "string" },
    "area_sqkm": { "type": "number", "minimum": 0 },
    "boundary": {
      "type": "object",
      "description": "GeoJSON Polygon or MultiPolygon representing the regional border in EPSG:4326"
    },
    "created_at": { "type": "string", "format": "date-time" },
    "updated_at": { "type": "string", "format": "date-time" }
  }
}
```

---

### 1.2 GridCell
Represents a discrete standardized 500m × 500m spatial partition within a monitored region.

```json
{
  "$id": "https://forestfire.platform/schemas/grid_cell.json",
  "type": "object",
  "required": ["id", "region_id", "cell_code", "centroid", "geometry", "resolution_meters"],
  "properties": {
    "id": { "type": "string", "format": "uuid" },
    "region_id": { "type": "string", "format": "uuid" },
    "cell_code": { "type": "string" },
    "centroid": {
      "type": "object",
      "description": "GeoJSON Point [longitude, latitude] in EPSG:4326"
    },
    "geometry": {
      "type": "object",
      "description": "GeoJSON Polygon (500m x 500m boundary) in EPSG:4326"
    },
    "resolution_meters": { "type": "integer", "default": 500 },
    "elevation_m": { "type": "number", "description": "Mean elevation in meters above sea level" },
    "slope_deg": { "type": "number", "minimum": 0, "maximum": 90, "description": "Topographical slope in degrees" },
    "aspect_deg": { "type": "number", "minimum": 0, "maximum": 360, "description": "Compass aspect facing in degrees" },
    "fuel_type": { "type": "string", "description": "Standardized Indian fuel category code" }
  }
}
```

---

### 1.3 FireEvent
Represents an active or historical thermal anomaly detected via satellite instruments (MODIS, VIIRS, INSAT-3D).

```json
{
  "$id": "https://forestfire.platform/schemas/fire_event.json",
  "type": "object",
  "required": ["id", "source", "detected_at", "location", "confidence_pct"],
  "properties": {
    "id": { "type": "string", "format": "uuid" },
    "grid_cell_id": { "type": ["string", "null"], "format": "uuid" },
    "source": { "type": "string", "enum": ["MODIS", "VIIRS", "INSAT_3D", "GROUND_REPORT"] },
    "detected_at": { "type": "string", "format": "date-time" },
    "brightness_temp_k": { "type": "number", "description": "Brightness temperature in Kelvin" },
    "frp_mw": { "type": "number", "description": "Fire Radiative Power in MegaWatts" },
    "confidence_pct": { "type": "number", "minimum": 0, "maximum": 100 },
    "location": {
      "type": "object",
      "description": "GeoJSON Point [longitude, latitude] in EPSG:4326"
    }
  }
}
```

---

### 1.4 EnvironmentalObservation
Represents daily or hourly meteorology, vegetation moisture, and drought precursor indices aggregated onto a grid cell.

```json
{
  "$id": "https://forestfire.platform/schemas/environmental_observation.json",
  "type": "object",
  "required": ["id", "grid_cell_id", "observation_time"],
  "properties": {
    "id": { "type": "string", "format": "uuid" },
    "grid_cell_id": { "type": "string", "format": "uuid" },
    "observation_time": { "type": "string", "format": "date-time" },
    "temperature_c": { "type": "number", "description": "Surface ambient temperature in Celsius" },
    "relative_humidity_pct": { "type": "number", "minimum": 0, "maximum": 100 },
    "wind_speed_ms": { "type": "number", "minimum": 0, "description": "Wind velocity in meters per second" },
    "wind_direction_deg": { "type": "number", "minimum": 0, "maximum": 360, "description": "Wind vector azimuth (0 = North, 90 = East)" },
    "precipitation_mm": { "type": "number", "minimum": 0, "description": "24h accumulated rainfall in millimeters" },
    "ndvi": { "type": "number", "minimum": -1.0, "maximum": 1.0, "description": "Normalized Difference Vegetation Index" },
    "ndwi": { "type": "number", "minimum": -1.0, "maximum": 1.0, "description": "Normalized Difference Water Index" },
    "fwi": { "type": "number", "minimum": 0, "description": "Canadian Fire Weather Index composite" }
  }
}
```

---

### 1.5 RiskPrediction
Represents the 24-hour fire susceptibility probability and categorical classification for a grid cell.

```json
{
  "$id": "https://forestfire.platform/schemas/risk_prediction.json",
  "type": "object",
  "required": ["grid_cell_id", "probability", "risk_class", "model_version"],
  "properties": {
    "id": { "type": "string", "format": "uuid" },
    "grid_cell_id": { "type": "string", "format": "uuid" },
    "region_id": { "type": "string", "format": "uuid" },
    "valid_for_date": { "type": "string", "format": "date" },
    "probability": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
    "risk_class": { "type": "string", "enum": ["LOW", "MODERATE", "HIGH", "EXTREME"] },
    "model_version": { "type": "string" },
    "generated_at": { "type": "string", "format": "date-time" }
  }
}
```

---

### 1.6 Simulation
Represents a 12-hour Cellular Automata fire spread simulation execution session.

```json
{
  "$id": "https://forestfire.platform/schemas/simulation.json",
  "type": "object",
  "required": ["id", "region_id", "ignition_point", "duration_hours", "status"],
  "properties": {
    "id": { "type": "string", "format": "uuid" },
    "region_id": { "type": "string", "format": "uuid" },
    "ignition_point": {
      "type": "object",
      "description": "GeoJSON Point [longitude, latitude] of ignition"
    },
    "ignition_time": { "type": "string", "format": "date-time" },
    "duration_hours": { "type": "integer", "minimum": 1, "maximum": 12, "default": 12 },
    "status": { "type": "string", "enum": ["PENDING", "RUNNING", "COMPLETED", "FAILED"] },
    "total_area_burned_ha": { "type": "number", "minimum": 0 },
    "created_at": { "type": "string", "format": "date-time" },
    "completed_at": { "type": ["string", "null"], "format": "date-time" }
  }
}
```

---

### 1.7 SimulationTimestep
Represents a discrete 1-hour interval slice of fire spread progression.

```json
{
  "$id": "https://forestfire.platform/schemas/simulation_timestep.json",
  "type": "object",
  "required": ["simulation_id", "hour", "burned_area", "spread_velocity", "spread_direction", "intensity", "boundary"],
  "properties": {
    "simulation_id": { "type": "string", "format": "uuid" },
    "hour": { "type": "integer", "minimum": 1, "maximum": 12 },
    "burned_area": { "type": "number", "minimum": 0, "description": "Cumulative burned area in hectares" },
    "spread_velocity": { "type": "number", "minimum": 0, "description": "Rate of spread in km/h" },
    "spread_direction": { "type": "number", "minimum": 0, "maximum": 360, "description": "Heading of leading fire front in degrees" },
    "intensity": { "type": "number", "minimum": 0, "description": "Relative fireline intensity in MW/m" },
    "boundary": {
      "type": "object",
      "description": "GeoJSON Polygon or MultiPolygon representing active fire perimeter"
    }
  }
}
```

---

## 2. Computational Engine Input/Output Contracts

### 2.1 Risk Engine Contracts

#### RiskModelInput
Contract for tabular / pixel-wise feature records fed into the 24-hour risk model.
```json
{
  "grid_cell_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "features": {
    "elevation_m": 1250.0,
    "slope_deg": 18.5,
    "aspect_deg": 145.0,
    "temperature_c": 36.2,
    "relative_humidity_pct": 21.0,
    "wind_speed_ms": 6.8,
    "precipitation_7d_mm": 0.0,
    "ndvi": 0.32,
    "ndwi": -0.15,
    "fwi": 29.4,
    "historical_fire_frequency": 3
  }
}
```

#### RiskModelOutput
Canonical result produced by `predict_risk(input: RiskModelInput)`.
```json
{
  "grid_cell_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "probability": 0.78,
  "risk_class": "EXTREME",
  "model_version": "xgboost-v1.0.0",
  "feature_importances": {
    "fwi": 0.35,
    "relative_humidity_pct": 0.28,
    "temperature_c": 0.20
  }
}
```

---

### 2.2 Spread Engine Contracts

#### SpreadSimulationInput
Contract for initializing the 12-hour Cellular Automata propagation.
```json
{
  "simulation_id": "99e1234a-89bc-43de-b821-fa123456789a",
  "region_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "ignition": {
    "latitude": 30.2104,
    "longitude": 78.7523,
    "ignition_radius_meters": 250
  },
  "duration_hours": 12,
  "grid_resolution_meters": 500,
  "environmental_conditions": {
    "wind_speed_ms": 8.0,
    "wind_direction_deg": 240.0,
    "ambient_temperature_c": 34.0,
    "relative_humidity_pct": 18.0
  },
  "use_rothermel_physics": false
}
```

#### SpreadSimulationOutput
Canonical result returned by `run_simulation(input: SpreadSimulationInput)`.
```json
{
  "simulation_id": "99e1234a-89bc-43de-b821-fa123456789a",
  "total_area_burned_ha": 384.5,
  "duration_hours": 12,
  "peak_spread_velocity_kmh": 1.25,
  "timesteps": [
    {
      "simulation_id": "99e1234a-89bc-43de-b821-fa123456789a",
      "hour": 1,
      "burned_area": 14.2,
      "spread_velocity": 0.65,
      "spread_direction": 60.0,
      "intensity": 6.5,
      "boundary": { "type": "Polygon", "coordinates": [] }
    }
  ]
}
```
