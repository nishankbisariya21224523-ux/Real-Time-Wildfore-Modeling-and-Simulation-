# Data Card: Environmental & Geospatial Data Pipeline

## 1. Dataset & Pipeline Overview

The Forest Fire Prediction and Spread Simulation Platform integrates heterogeneous spatial and temporal observations from satellite, meteorological, topographical, and vegetation sources into a unified **500m × 500m Common Spatial Grid** (`EPSG:4326`).

---

## 2. Ingested Data Sources

| Domain | Source Provider | Primary Sensor / Dataset | Native Resolution | Update Frequency | Purpose in Pipeline |
|---|---|---|---|---|---|
| **Thermal Hotspots** | NASA FIRMS | MODIS (Terra/Aqua), VIIRS (S-NPP, NOAA-20) | 375m – 1km | 3–6 hours | Active fire ignition detection, historical fire labels |
| **Meteorology** | IMD / ECMWF ERA5 | Surface observations, ERA5 reanalysis / GFS | 0.1° – 0.25° | Hourly / 3-hourly | Temperature, Relative Humidity, Wind Speed, Wind Direction, Precipitation |
| **Topography** | ISRO CartoDEM / NASA SRTM | CartoDEM v3R1, SRTM GL1 | 30m | Static | Elevation, Slope (degrees), Aspect (compass degrees) |
| **Vegetation & Fuels** | ISRO Bhuvan / ESA Copernicus | Sentinel-2 MSI, Bhuvan LULC | 10m – 30m | 5-day / Seasonal | NDVI, Fuel Load Type, Moisture index, Canopy Cover |

---

## 3. Standardized Feature Space (30 Features)

The pipeline transforms raw spatial rasters and point observations into a 30-dimensional feature vector for each 500m grid cell:

### Meteorological Features (8)
1. `temp_celsius`: Air temperature at 2m (°C)
2. `relative_humidity`: Relative humidity at 2m (%)
3. `wind_speed_kmh`: Sustained wind velocity (km/h)
4. `wind_direction_deg`: Wind direction clockwise from North (0°–360°)
5. `wind_u`: Eastward wind vector component ($u = -v \sin \theta$)
6. `wind_v`: Northward wind vector component ($v = -v \cos \theta$)
7. `precip_24h_mm`: Cumulative rainfall over the preceding 24 hours (mm)
8. `fwi_proxy`: Canadian Fire Weather Index composite proxy

### Topographical Features (6)
9. `elevation_m`: Mean cell elevation (meters above sea level)
10. `slope_deg`: Terrain slope angle (0°–90°)
11. `aspect_deg`: Compass orientation of downhill slope (0°–360°)
12. `aspect_sin`: Sine transformation of aspect ($\sin \theta$)
13. `aspect_cos`: Cosine transformation of aspect ($\cos \theta$)
14. `roughness`: Terrain ruggedness index across neighboring cells

### Fuel & Vegetation Features (8)
15. `ndvi`: Normalized Difference Vegetation Index (-1.0 to 1.0)
16. `ndvi_anomaly`: Deviation from 30-day rolling baseline NDVI
17. `fuel_type_code`: Categorical fuel classification code (1–5)
18. `fuel_moisture_est`: Estimated 10-hour dead fuel moisture content (%)
19. `canopy_cover_pct`: Percentage of tree canopy closure (0%–100%)
20. `vegetation_stress`: Plant water stress index
21. `is_burnable`: Binary mask indicator (0 for water/rock/urban, 1 for burnable fuel)
22. `fuel_load_ton_per_ha`: Dry biomass fuel load density (tons/ha)

### Historical Fire & Spatial Features (8)
23. `fire_count_30d`: Count of thermal anomalies in cell over past 30 days
24. `fire_count_1y`: Count of thermal anomalies in cell over past 365 days
25. `dist_to_active_fire_km`: Euclidean distance to nearest active thermal hotspot (km)
26. `dist_to_road_km`: Distance to mapped road / human access corridor (km)
27. `dist_to_water_km`: Distance to nearest perennial water body (km)
28. `dist_to_settlement_km`: Distance to closest urban or rural settlement (km)
29. `cell_latitude`: Grid cell centroid latitude (decimal degrees)
30. `cell_longitude`: Grid cell centroid longitude (decimal degrees)

---

## 4. Data Leakage Prevention & Boundary Audit

A strict causal time boundary is enforced across all feature extractors:
- **Reference Time ($T_{\text{ref}}$)**: The instantaneous timestamp for which a 24-hour prediction is generated.
- **Feature Extraction Rule**: Any feature $f_i$ computed from meteorological, vegetation, or historical fire tables MUST strictly satisfy:
  $$\text{timestamp}(f_i) \le T_{\text{ref}}$$
- **Target Label Rule**: The binary label $y \in \{0, 1\}$ (indicating fire occurrence) is defined as:
  $$y = 1 \iff \exists \text{ hotspot in cell with timestamp} \in (T_{\text{ref}}, T_{\text{ref}} + 24\text{h}]$$
- **Verification**: Verified in `services/data-pipeline/features/fire_history.py` and `services/data-pipeline/features/target.py`. Zero lookahead features are admitted into the ML training or inference matrix.

---

## 5. Scope & Current Dataset Constraints

> [!IMPORTANT]
> **SAMPLE DATASET NOTICE**
> The current machine learning model (`risk-xgboost-v001`) and data validation tests were developed, validated, and trained on a **curated development sample slice** (dated 2026-05-15) covering monitored test regions (Uttarakhand Forest Division and Western Ghats).
>
> **Known Constraints:**
> 1. Multi-year continuous satellite feeds spanning 2015–2025 across the entire Indian subcontinent require enterprise data warehouse ingestion and petabyte-scale storage not present in this local containerized deployment.
> 2. The pipeline architecture and ingestion adapters are fully functional and production-structured, but historical training currently reflects the development sample dataset rather than a 10-year pan-India dataset.
