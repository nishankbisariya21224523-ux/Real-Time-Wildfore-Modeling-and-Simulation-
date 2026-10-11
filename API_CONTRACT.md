# API Contract Specification

This document defines the formal REST API contract for the Predictive Forest Fire Risk & Spread Simulation Platform (`/api/v1`).
All endpoints adhere to strict versioning, standardized JSON/GeoJSON payload structures, and unified error envelopes.

---

## 1. Global Standards & Error Structure

### 1.1 Content Types & Spatial Standards
- Standard API responses use `application/json`.
- Spatial geometries use RFC 7946 GeoJSON format (`Point`, `Polygon`, `MultiPolygon`, `Feature`, `FeatureCollection`) with coordinates in `[longitude, latitude]` order (WGS 84 / EPSG:4326).

### 1.2 Unified Error Response
Whenever an HTTP error code (4xx, 5xx) is returned, the response body always follows this schema:

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "The requested entity was not found.",
    "details": {
      "field": "region_id",
      "value": "invalid-uuid-or-code"
    },
    "request_id": "req-a4f18d72-9b2c-4903-8d0f-4886b71f98d1"
  }
}
```

#### Standard Error Codes:
- `VALIDATION_ERROR` (422 / 400): Request parameters or JSON payload failed schema validation.
- `RESOURCE_NOT_FOUND` (404): The requested region, fire event, or simulation record does not exist.
- `SIMULATION_STILL_RUNNING` (409): Timestep details requested before simulation processing completed.
- `INTERNAL_SERVER_ERROR` (500): Unexpected server failure.
- `SERVICE_UNAVAILABLE` (503): Downstream queue or database connectivity failure.

---

## 2. API Endpoints

### 2.1 System Health
`GET /api/v1/health`

- **Purpose**: Verify that the API application is running, healthy, and report connectivity status of dependencies.
- **Path Parameters**: None.
- **Query Parameters**: None.
- **Request Body**: None.
- **Success Status**: `200 OK`
- **Error Status**: `503 Service Unavailable`
- **Example Response**:
```json
{
  "status": "healthy",
  "timestamp": "2026-10-05T18:00:00Z",
  "version": "1.0.0",
  "environment": "development",
  "services": {
    "database": "connected",
    "redis": "connected",
    "celery_broker": "connected"
  }
}
```

---

### 2.2 List Monitored Regions
`GET /api/v1/regions`

- **Purpose**: Retrieve a list of all forest monitoring jurisdictions/regions.
- **Path Parameters**: None.
- **Query Parameters**:
  - `state` (optional, string): Filter regions by administrative state (e.g. `Uttarakhand`, `Karnataka`).
  - `limit` (optional, integer, default 50): Pagination limit.
  - `offset` (optional, integer, default 0): Pagination offset.
- **Request Body**: None.
- **Success Status**: `200 OK`
- **Error Status**: `400 Bad Request`, `500 Internal Server Error`
- **Example Response**:
```json
{
  "count": 2,
  "results": [
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "code": "UTTARAKHAND_GARHWAL",
      "name": "Garhwal Forest Division",
      "state": "Uttarakhand",
      "area_sqkm": 2840.5,
      "centroid": {
        "type": "Point",
        "coordinates": [78.7842, 30.2241]
      },
      "created_at": "2026-01-15T00:00:00Z"
    },
    {
      "id": "7ca85f64-5717-4562-b3fc-2c963f66afa7",
      "code": "WESTERN_GHATS_WAYANAD",
      "name": "Wayanad Wildlife Sanctuary",
      "state": "Kerala",
      "area_sqkm": 344.4,
      "centroid": {
        "type": "Point",
        "coordinates": [76.2418, 11.6854]
      },
      "created_at": "2026-01-15T00:00:00Z"
    }
  ]
}
```

---

### 2.3 Get Region Details & GeoJSON Boundary
`GET /api/v1/regions/{region_id}`

- **Purpose**: Retrieve detailed metadata and full boundary polygon for a specific region.
- **Path Parameters**:
  - `region_id` (string / UUID): Unique identifier or region code.
- **Query Parameters**: None.
- **Request Body**: None.
- **Success Status**: `200 OK`
- **Error Status**: `404 Not Found`
- **Example Response**:
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "code": "UTTARAKHAND_GARHWAL",
  "name": "Garhwal Forest Division",
  "state": "Uttarakhand",
  "area_sqkm": 2840.5,
  "boundary": {
    "type": "Feature",
    "geometry": {
      "type": "Polygon",
      "coordinates": [
        [
          [78.50, 30.10],
          [79.10, 30.10],
          [79.10, 30.40],
          [78.50, 30.40],
          [78.50, 30.10]
        ]
      ]
    },
    "properties": {
      "code": "UTTARAKHAND_GARHWAL",
      "name": "Garhwal Forest Division"
    }
  },
  "grid_resolution_meters": 500,
  "total_cells": 11362
}
```

---

### 2.4 Active Fire Hotspots
`GET /api/v1/fires/active`

- **Purpose**: Retrieve near real-time thermal anomalies and active fire hotspots (from MODIS/VIIRS).
- **Path Parameters**: None.
- **Query Parameters**:
  - `region_id` (optional, UUID): Filter by region.
  - `hours` (optional, integer, default 24, max 72): Time window of detections.
  - `min_confidence` (optional, float, default 50.0): Filter by detection confidence percentage.
- **Request Body**: None.
- **Success Status**: `200 OK`
- **Error Status**: `422 Validation Error`
- **Example Response**:
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "id": "f8a9e712-4523-41a3-b3c1-019283746554",
      "geometry": {
        "type": "Point",
        "coordinates": [78.7523, 30.2104]
      },
      "properties": {
        "satellite": "VIIRS_NOAA20",
        "detected_at": "2026-10-05T14:30:00Z",
        "brightness_temp_k": 348.6,
        "frp_mw": 42.1,
        "confidence_pct": 88.0,
        "day_night": "D"
      }
    }
  ]
}
```

---

### 2.5 Get 24-Hour Fire Risk Layer for Region
`GET /api/v1/risk/{region_id}`

- **Purpose**: Retrieve pre-computed 24-hour fire susceptibility grid predictions for a region.
- **Path Parameters**:
  - `region_id` (string / UUID): Region identifier.
- **Query Parameters**:
  - `date` (optional, ISO date `YYYY-MM-DD`): Target forecast date (defaults to today).
  - `min_risk` (optional, string enum `LOW | MODERATE | HIGH | EXTREME`): Filter cells above a threshold.
- **Request Body**: None.
- **Success Status**: `200 OK`
- **Error Status**: `404 Not Found`, `422 Validation Error`
- **Example Response**:
```json
{
  "type": "FeatureCollection",
  "properties": {
    "region_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "forecast_date": "2026-10-06",
    "model_version": "rf-baseline-v1.0.0",
    "generated_at": "2026-10-05T06:00:00Z"
  },
  "features": [
    {
      "type": "Feature",
      "id": "cell-gar-00129",
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [78.750, 30.200],
            [78.755, 30.200],
            [78.755, 30.205],
            [78.750, 30.205],
            [78.750, 30.200]
          ]
        ]
      },
      "properties": {
        "grid_cell_id": "9bc12345-0000-0000-0000-000000000129",
        "risk_probability": 0.82,
        "risk_class": "EXTREME",
        "fwi": 28.4,
        "fuel_type": "Chir_Pine",
        "elevation_m": 1420
      }
    }
  ]
}
```

---

### 2.6 Trigger On-Demand 24-Hour Risk Prediction
`POST /api/v1/risk/predict`

- **Purpose**: Run or refresh a 24-hour risk inference calculation for a specific region.
- **Path Parameters**: None.
- **Query Parameters**: None.
- **Request Body**:
```json
{
  "region_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "target_date": "2026-10-06",
  "force_recompute": false,
  "model_name": "xgboost-baseline"
}
```
- **Success Status**: `200 OK` (if cached/computed immediately) or `202 Accepted`
- **Error Status**: `404 Not Found`, `422 Validation Error`
- **Example Response**:
```json
{
  "job_id": "risk-job-90182",
  "region_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "target_date": "2026-10-06",
  "status": "COMPLETED",
  "cells_predicted": 11362,
  "mean_risk_probability": 0.34,
  "completed_at": "2026-10-05T18:02:10Z"
}
```

---

### 2.7 Create / Initiate Fire Spread Simulation
`POST /api/v1/simulations`

- **Purpose**: Initiate a 12-hour Cellular Automata fire spread simulation from an ignition point.
- **Path Parameters**: None.
- **Query Parameters**: None.
- **Request Body**:
```json
{
  "region_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "ignition_point": {
    "latitude": 30.2104,
    "longitude": 78.7523
  },
  "ignition_time": "2026-10-05T18:00:00Z",
  "duration_hours": 12,
  "weather_scenario": {
    "wind_speed_ms": 7.5,
    "wind_direction_deg": 245.0,
    "temperature_c": 32.0,
    "relative_humidity_pct": 22.0
  }
}
```
- **Success Status**: `202 Accepted`
- **Error Status**: `400 Bad Request`, `422 Validation Error`
- **Example Response**:
```json
{
  "simulation_id": "99e1234a-89bc-43de-b821-fa123456789a",
  "status": "PENDING",
  "created_at": "2026-10-05T18:05:00Z",
  "duration_hours": 12,
  "poll_url": "/api/v1/simulations/99e1234a-89bc-43de-b821-fa123456789a"
}
```

---

### 2.8 Get Simulation Job Status & Summary
`GET /api/v1/simulations/{simulation_id}`

- **Purpose**: Check simulation progress, status (`PENDING`, `RUNNING`, `COMPLETED`, `FAILED`), and final summary metrics.
- **Path Parameters**:
  - `simulation_id` (UUID): Simulation identifier.
- **Query Parameters**: None.
- **Request Body**: None.
- **Success Status**: `200 OK`
- **Error Status**: `404 Not Found`
- **Example Response**:
```json
{
  "simulation_id": "99e1234a-89bc-43de-b821-fa123456789a",
  "status": "COMPLETED",
  "progress_pct": 100.0,
  "duration_hours": 12,
  "created_at": "2026-10-05T18:05:00Z",
  "completed_at": "2026-10-05T18:05:15Z",
  "ignition_point": {
    "type": "Point",
    "coordinates": [78.7523, 30.2104]
  },
  "metrics": {
    "total_area_burned_ha": 412.5,
    "peak_spread_velocity_kmh": 1.45,
    "dominant_spread_direction_deg": 65.0
  }
}
```

---

### 2.9 Get Simulation 12-Hour Timeline
`GET /api/v1/simulations/{simulation_id}/timeline`

- **Purpose**: Retrieve summary progression statistics for each of the 12 simulation hours.
- **Path Parameters**:
  - `simulation_id` (UUID): Simulation identifier.
- **Query Parameters**: None.
- **Request Body**: None.
- **Success Status**: `200 OK`
- **Error Status**: `404 Not Found`, `409 Conflict` (if still running)
- **Example Response**:
```json
{
  "simulation_id": "99e1234a-89bc-43de-b821-fa123456789a",
  "total_steps": 12,
  "timeline": [
    {
      "step_hour": 1,
      "burned_area_ha": 12.5,
      "spread_velocity_kmh": 0.85,
      "spread_direction_deg": 62.0,
      "intensity_mw": 8.2
    },
    {
      "step_hour": 2,
      "burned_area_ha": 35.0,
      "spread_velocity_kmh": 0.95,
      "spread_direction_deg": 64.0,
      "intensity_mw": 11.5
    }
  ]
}
```

---

### 2.10 Get Specific Simulation Timestep Spatial Boundary
`GET /api/v1/simulations/{simulation_id}/timesteps/{hour}`

- **Purpose**: Retrieve the exact GeoJSON perimeter and burning cell matrix for a specific simulation hour (1 to 12).
- **Path Parameters**:
  - `simulation_id` (UUID): Simulation identifier.
  - `hour` (integer, 1 to 12): Simulation timestep hour.
- **Query Parameters**: None.
- **Request Body**: None.
- **Success Status**: `200 OK`
- **Error Status**: `404 Not Found`, `422 Validation Error`
- **Example Response**:
```json
{
  "simulation_id": "99e1234a-89bc-43de-b821-fa123456789a",
  "step_hour": 3,
  "metrics": {
    "burned_area_ha": 72.8,
    "spread_velocity_kmh": 1.10,
    "spread_direction_deg": 65.0,
    "intensity_mw": 14.3
  },
  "perimeter": {
    "type": "Feature",
    "geometry": {
      "type": "Polygon",
      "coordinates": [
        [
          [78.752, 30.210],
          [78.761, 30.218],
          [78.768, 30.222],
          [78.759, 30.215],
          [78.752, 30.210]
        ]
      ]
    },
    "properties": {
      "hour": 3,
      "area_ha": 72.8
    }
  }
}
```

---

### 2.11 Get Static / Environmental GIS Layers
`GET /api/v1/layers/{layer_type}`

- **Purpose**: Retrieve reference GIS vector or metadata layers (e.g. `elevation`, `slope`, `fuel`, `weather`).
- **Path Parameters**:
  - `layer_type` (string enum: `elevation | slope | fuel | weather | fire-history`).
- **Query Parameters**:
  - `region_id` (required, UUID): Region to filter layer for.
- **Request Body**: None.
- **Success Status**: `200 OK`
- **Error Status**: `404 Not Found`, `422 Validation Error`
- **Example Response**:
```json
{
  "layer_type": "fuel",
  "region_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "resolution_meters": 500,
  "legend": {
    "1": "Dense Pine Forest",
    "2": "Deciduous Broadleaf",
    "3": "Dry Shrubland",
    "4": "Grassland / Agricultural"
  },
  "source": "ISRO Bhuvan Land Cover 2024"
}
```
