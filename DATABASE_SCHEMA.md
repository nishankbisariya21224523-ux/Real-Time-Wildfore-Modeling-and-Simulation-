# Database Architecture & PostGIS Schema Specification

This document details the spatial relational database architecture for the Forest Fire Risk Prediction & Spread Simulation Platform.

---

## 1. Spatial Database Design Principles

1. **PostGIS Native Geometries**: All geographical boundaries, centroids, perimeters, and active hotspot points are stored as PostGIS `GEOMETRY` objects in `EPSG:4326` (WGS 84 coordinate reference system: `[longitude, latitude]`).
2. **Spatial Indexing**: Every spatial column is indexed using Generalized Search Trees (`GIST`) to support high-performance spatial predicates (`ST_Intersects`, `ST_Within`, `ST_DWithin`, `ST_Contains`).
3. **Decoupled Raster Strategy**: Multi-spectral satellite rasters (MODIS, VIIRS, Sentinel-2 GeoTIFFs) and large elevation rasters (SRTM/CartoDEM) are stored in cloud object storage (S3 / MinIO / GCS). PostgreSQL stores normalized 500m vector cells, extracted zonal statistics, and spatial indices.
4. **Coordinate Reference System (CRS) Strategy**:
   - Ingestion & Storage: All public APIs and PostGIS tables standardize on `EPSG:4326` (WGS 84).
   - Metric Calculations: Spatial measurements (area in hectares, buffer distances, rate of spread) leverage `ST_Transform` to local UTM zones (e.g. `EPSG:32643` / `EPSG:32644` for Northern/Central India, `EPSG:32643` for Western Ghats) or PostGIS `GEOGRAPHY` cast for spherical distance calculations.

---

## 2. Table Specifications

### 2.1 Table: `regions`
- **Purpose**: Defines administrative and geographical forest monitoring divisions.
- **Primary Key**: `id` (UUID, DEFAULT `gen_random_uuid()`)
- **Important Columns**:
  - `code` (VARCHAR(50), UNIQUE, NOT NULL): Human-readable unique division slug.
  - `name` (VARCHAR(150), NOT NULL): Official name.
  - `state` (VARCHAR(100), NOT NULL): Indian state or territory.
  - `boundary` (GEOMETRY(Polygon, 4326), NOT NULL): Regional perimeter.
  - `area_sqkm` (NUMERIC(10, 2), NOT NULL): Total territorial area.
  - `created_at` (TIMESTAMPTZ, DEFAULT NOW())
  - `updated_at` (TIMESTAMPTZ, DEFAULT NOW())
- **Indexes**:
  - `idx_regions_code` (B-Tree on `code`)
  - `idx_regions_boundary` (GIST on `boundary`)

---

### 2.2 Table: `grid_cells`
- **Purpose**: Discrete 500m × 500m spatial cells tiling a monitored region.
- **Primary Key**: `id` (UUID, DEFAULT `gen_random_uuid()`)
- **Foreign Keys**:
  - `region_id` -> `regions(id)` ON DELETE CASCADE
- **Important Columns**:
  - `cell_code` (VARCHAR(100), UNIQUE, NOT NULL): Region-prefixed index slug.
  - `centroid` (GEOMETRY(Point, 4326), NOT NULL): Center coordinate.
  - `geometry` (GEOMETRY(Polygon, 4326), NOT NULL): Exact 500m cell polygon.
  - `resolution_meters` (INTEGER, DEFAULT 500)
  - `elevation_m` (NUMERIC(8, 2)): Mean elevation above sea level.
  - `slope_deg` (NUMERIC(5, 2)): Slope inclination in degrees [0 to 90].
  - `aspect_deg` (NUMERIC(5, 2)): Aspect azimuth [0 to 360].
  - `fuel_type` (VARCHAR(50)): Standardized fuel classification code.
- **Indexes**:
  - `idx_grid_cells_region` (B-Tree on `region_id`)
  - `idx_grid_cells_geom` (GIST on `geometry`)
  - `idx_grid_cells_centroid` (GIST on `centroid`)

---

### 2.3 Table: `fire_events`
- **Purpose**: Satellite active thermal detections (MODIS / VIIRS / INSAT-3D) and verified ground ignitions.
- **Primary Key**: `id` (UUID, DEFAULT `gen_random_uuid()`)
- **Foreign Keys**:
  - `grid_cell_id` -> `grid_cells(id)` ON DELETE SET NULL
- **Important Columns**:
  - `source` (VARCHAR(50), NOT NULL): Satellite sensor (`MODIS`, `VIIRS_NOAA20`, `VIIRS_SNPP`, `INSAT_3D`).
  - `detected_at` (TIMESTAMPTZ, NOT NULL): Acquisition timestamp.
  - `brightness_temp_k` (NUMERIC(6, 2)): Channel brightness temperature.
  - `frp_mw` (NUMERIC(8, 2)): Fire Radiative Power in MW.
  - `confidence_pct` (NUMERIC(5, 2), NOT NULL): Detection confidence [0 - 100].
  - `location` (GEOMETRY(Point, 4326), NOT NULL): Detection coordinate.
  - `created_at` (TIMESTAMPTZ, DEFAULT NOW())
- **Indexes**:
  - `idx_fire_events_detected_at` (B-Tree on `detected_at DESC`)
  - `idx_fire_events_location` (GIST on `location`)
  - `idx_fire_events_grid_cell` (B-Tree on `grid_cell_id`)

---

### 2.4 Table: `environmental_observations`
- **Purpose**: Meteorological feeds, moisture indices, and vegetation indicators aggregated to grid cells.
- **Primary Key**: `id` (UUID, DEFAULT `gen_random_uuid()`)
- **Foreign Keys**:
  - `grid_cell_id` -> `grid_cells(id)` ON DELETE CASCADE
- **Important Columns**:
  - `observation_time` (TIMESTAMPTZ, NOT NULL): Date/time of observation composite.
  - `temperature_c` (NUMERIC(5, 2)): Ambient surface temperature (°C).
  - `relative_humidity_pct` (NUMERIC(5, 2)): Relative humidity [0 - 100%].
  - `wind_speed_ms` (NUMERIC(6, 2)): Wind velocity (m/s).
  - `wind_direction_deg` (NUMERIC(5, 2)): Wind compass azimuth [0 - 360°].
  - `precipitation_mm` (NUMERIC(7, 2)): 24-hour rainfall accumulation.
  - `ndvi` (NUMERIC(4, 3)): Normalized Difference Vegetation Index [-1.0 to 1.0].
  - `ndwi` (NUMERIC(4, 3)): Normalized Difference Water Index [-1.0 to 1.0].
  - `fwi` (NUMERIC(6, 2)): Canadian Fire Weather Index rating.
- **Constraints**:
  - UNIQUE(`grid_cell_id`, `observation_time`)
- **Indexes**:
  - `idx_env_obs_cell_time` (B-Tree on `grid_cell_id`, `observation_time DESC`)
  - `idx_env_obs_time` (B-Tree on `observation_time`)

---

### 2.5 Table: `risk_predictions`
- **Purpose**: Pre-computed 24-hour fire susceptibility predictions for each 500m grid cell.
- **Primary Key**: `id` (UUID, DEFAULT `gen_random_uuid()`)
- **Foreign Keys**:
  - `grid_cell_id` -> `grid_cells(id)` ON DELETE CASCADE
  - `region_id` -> `regions(id)` ON DELETE CASCADE
- **Important Columns**:
  - `valid_for_date` (DATE, NOT NULL): Forecast date.
  - `risk_probability` (NUMERIC(4, 3), NOT NULL): Susceptibility score [0.000 - 1.000].
  - `risk_class` (VARCHAR(20), NOT NULL): Enum (`LOW`, `MODERATE`, `HIGH`, `EXTREME`).
  - `model_version` (VARCHAR(50), NOT NULL): Tracking tag of model artifact.
  - `generated_at` (TIMESTAMPTZ, DEFAULT NOW())
- **Constraints**:
  - UNIQUE(`grid_cell_id`, `valid_for_date`, `model_version`)
- **Indexes**:
  - `idx_risk_pred_region_date` (B-Tree on `region_id`, `valid_for_date`)
  - `idx_risk_pred_cell` (B-Tree on `grid_cell_id`)

---

### 2.6 Table: `simulations`
- **Purpose**: Records metadata and global state of 12-hour Cellular Automata fire spread jobs.
- **Primary Key**: `id` (UUID, DEFAULT `gen_random_uuid()`)
- **Foreign Keys**:
  - `region_id` -> `regions(id)` ON DELETE CASCADE
- **Important Columns**:
  - `ignition_location` (GEOMETRY(Point, 4326), NOT NULL): Origin point of the fire.
  - `ignition_time` (TIMESTAMPTZ, NOT NULL): Starting timestamp.
  - `duration_hours` (INTEGER, DEFAULT 12)
  - `status` (VARCHAR(20), NOT NULL): Enum (`PENDING`, `RUNNING`, `COMPLETED`, `FAILED`).
  - `total_area_burned_ha` (NUMERIC(10, 2), DEFAULT 0)
  - `created_at` (TIMESTAMPTZ, DEFAULT NOW())
  - `completed_at` (TIMESTAMPTZ, NULL)
- **Indexes**:
  - `idx_simulations_status` (B-Tree on `status`)
  - `idx_simulations_region` (B-Tree on `region_id`)
  - `idx_simulations_ignition` (GIST on `ignition_location`)

---

### 2.7 Table: `simulation_steps`
- **Purpose**: Hourly progression snapshots (hours 1 through 12) for an active or completed simulation.
- **Primary Key**: `id` (UUID, DEFAULT `gen_random_uuid()`)
- **Foreign Keys**:
  - `simulation_id` -> `simulations(id)` ON DELETE CASCADE
- **Important Columns**:
  - `step_hour` (INTEGER, NOT NULL): Simulation timestep [1 to 12].
  - `burned_area_ha` (NUMERIC(10, 2), NOT NULL): Cumulative burned area in hectares.
  - `spread_velocity_kmh` (NUMERIC(6, 2), NOT NULL): Rate of front spread.
  - `spread_direction_deg` (NUMERIC(5, 2), NOT NULL): Dominant fire front azimuth.
  - `intensity_mw` (NUMERIC(8, 2), NOT NULL): Fireline intensity.
  - `perimeter_geom` (GEOMETRY(Polygon, 4326), NOT NULL): Outer boundary polygon of the burned footprint.
  - `created_at` (TIMESTAMPTZ, DEFAULT NOW())
- **Constraints**:
  - UNIQUE(`simulation_id`, `step_hour`)
- **Indexes**:
  - `idx_sim_steps_sim_hour` (B-Tree on `simulation_id`, `step_hour`)
  - `idx_sim_steps_geom` (GIST on `perimeter_geom`)
