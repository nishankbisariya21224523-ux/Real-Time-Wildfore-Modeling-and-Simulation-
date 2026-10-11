# Platform Limitations & Operational Constraints

## 1. Overview

To maintain scientific integrity and operational transparency, this document details the functional, algorithmic, and data limitations of the Forest Fire Prediction and Spread Simulation Platform. Operational personnel and stakeholders must review these boundaries prior to interpreting model outputs.

---

## 2. Machine Learning Risk Model Limitations

### 2.1 Training Dataset Scope
- **Development Sample Slice**: The current machine learning model (`risk-xgboost-v001`) was trained and evaluated on a development sample dataset (dated 2026-05-15) covering monitored test regions (Uttarakhand and Western Ghats).
- **Subcontinent-Scale Data Ingestion**: The multi-year historical dataset spanning 2015–2025 across pan-India requires large-scale enterprise data warehouse infrastructure and petabyte-scale raster ingestion. The pipeline architecture is complete and ready, but full historical retraining remains an enterprise deployment phase.
- **Extreme Class Imbalance**: Wildfire occurrences represent approximately 0.1% of all spatial grid cells. While `scale_pos_weight = 999.0` successfully elevates recall to $> 84\%$, precision remains around $5.3\%$, resulting in false-positive warnings that require operational context when reviewing high-risk areas.

---

## 3. Cellular Automata Fire Spread Engine Limitations

### 3.1 Empirical / Heuristic Status
- **Engineering Simulation Model**: The `spread-ca-v001` engine is an 8-neighborhood Cellular Automata model utilizing empirical spread factors. It is **NOT** a calibrated numerical solver of the Rothermel surface fire equations or a CFD (Computational Fluid Dynamics) model.
- **Uncalibrated against Observed Wildfire Scars**: The engine has not yet been fitted against historical wildfire perimeters (e.g., Bandipur 2019 or Simlipal 2021 burn scars).

### 3.2 Unmodeled Wildland Fire Phenomena
- **Spotting & Firebrands**: The engine does not simulate lofting of embers by convection plumes and spotting ahead of the main fire perimeter.
- **Atmospheric Fire-Weather Coupling**: Fire-induced local winds, convective updrafts, and pyrocumulonimbus clouds are not dynamically coupled back into the meteorological field.
- **Crown Fires**: Canopy and crown fire transitions are modeled solely through fuel type multipliers rather than distinct vertical fuel stratification equations.
- **Suppression Tactics**: Active suppression (firebreaks, backburning, water bombing, mechanical bulldozer lines) is not incorporated into perimeter propagation.

---

## 4. Geospatial & Ingestion Latencies

### 4.1 Satellite Revisit & Observation Lag
- **Thermal Hotspot Refresh**: NASA FIRMS (MODIS and VIIRS) observations depend on polar-orbiting satellite passes, typically delivering updates every 3 to 6 hours. "Active Fire" markers reflect the timestamp of the latest orbital pass, not instantaneous real-time conditions.
- **Cloud Obscuration**: Heavy cloud cover, smoke plumes, or intense monsoonal conditions can obscure optical and thermal infrared sensors, potentially missing active surface fires.

### 4.2 Spatial Resolution Limitations
- **500m Common Spatial Grid**: While 500m resolution provides fast subcontinent-scale modeling, it does not resolve narrow firebreaks (< 50m), roads, or micro-topographical ravines that can act as natural barriers in the field.

---

## 5. Network & GIS Client Dependencies

- **Online Basemap Tiles**: The web dashboard relies on remote tile servers (OpenStreetMap or Mapbox) for cartographic basemaps. Offline deployment in remote field headquarters requires provisioning a local MBTiles or GeoServer raster tile service.
