# Known Issues & Operational Considerations

## 1. Overview

This document catalogues known issues, behavioral quirks, and development constraints identified during Phase 10 verification of the Forest Fire Prediction and Spread Simulation Platform.

---

## 2. Machine Learning & Modeling

### 2.1 Low Precision from Severe Class Imbalance
- **Description**: Wildfire ignition is an extremely rare event (~0.1% positive cells). The XGBoost model was configured with `scale_pos_weight = 999.0` to prioritize recall ($84.4\%$).
- **Impact**: Precision is approximately $5.3\%$, meaning several cells predicted as "High Risk" will not experience actual fires.
- **Operational Guidance**: Operational teams should treat high risk classifications as areas requiring enhanced monitoring or patrol staging, rather than certain ignitions.

### 2.2 Development Sample Training Dataset
- **Description**: The packaged model artifact was trained on a curated representative sample dataset slice (2026-05-15) rather than the multi-year (2015–2025) historical dataset envisioned in the long-term blueprint.
- **Impact**: Model inference outside the monitored test regions (Uttarakhand and Western Ghats) may exhibit domain shift without retraining on local historical data.

---

## 3. Simulation Engine

### 3.1 Uncalibrated Heuristic Spread
- **Description**: The 12-hour Cellular Automata engine utilizes empirical factor weighting rather than calibrated Rothermel surface fire equations.
- **Impact**: While directional propagation aligned with wind and slope is qualitatively accurate and deterministic, absolute burned perimeter shapes have not been calibrated against real wildfire scars.

### 3.2 Simplified Spotting Dynamics
- **Description**: The simulation does not compute aerodynamic lofting of burning embers.
- **Impact**: Fires cannot "jump" wide rivers, reservoirs, or major mountain ridges if distance exceeds 1 grid cell (500m).

---

## 4. Frontend & GIS User Experience

### 4.1 Internet Dependency for Basemap Tiles
- **Description**: The web interface requests OpenStreetMap cartographic tiles directly from public CDNs.
- **Impact**: If running in an air-gapped field operations room without internet connectivity, the basemap will appear blank unless a local vector tile service (e.g. Martin / OpenMapTiles) is provisioned.

### 4.2 Browser Memory during Extended Simulation Playback
- **Description**: When rendering complex 12-hour MultiPolygon GeoJSON perimeters repeatedly, low-end mobile devices or older browsers may experience minor UI frame drops.
- **Mitigation**: Hourly perimeter coordinates are simplified using Douglas-Peucker tolerance in Shapely before transmission.
