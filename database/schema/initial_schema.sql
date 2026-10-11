-- PostGIS Initial Schema for Forest Fire Risk Prediction & Spread Simulation Platform
-- Coordinate Reference System: EPSG:4326 (WGS 84)

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";

-- 1. Regions
CREATE TABLE IF NOT EXISTS regions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(150) NOT NULL,
    state VARCHAR(100) NOT NULL,
    boundary GEOMETRY(Polygon, 4326) NOT NULL,
    area_sqkm NUMERIC(10, 2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_regions_code ON regions(code);
CREATE INDEX IF NOT EXISTS idx_regions_boundary ON regions USING GIST(boundary);

-- 2. 500m Grid Cells
CREATE TABLE IF NOT EXISTS grid_cells (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    region_id UUID NOT NULL REFERENCES regions(id) ON DELETE CASCADE,
    cell_code VARCHAR(100) UNIQUE NOT NULL,
    centroid GEOMETRY(Point, 4326) NOT NULL,
    geometry GEOMETRY(Polygon, 4326) NOT NULL,
    resolution_meters INTEGER DEFAULT 500,
    elevation_m NUMERIC(8, 2),
    slope_deg NUMERIC(5, 2),
    aspect_deg NUMERIC(5, 2),
    fuel_type VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_grid_cells_region ON grid_cells(region_id);
CREATE INDEX IF NOT EXISTS idx_grid_cells_geom ON grid_cells USING GIST(geometry);
CREATE INDEX IF NOT EXISTS idx_grid_cells_centroid ON grid_cells USING GIST(centroid);

-- 3. Fire Events (Satellite Thermal Anomalies)
CREATE TABLE IF NOT EXISTS fire_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    grid_cell_id UUID REFERENCES grid_cells(id) ON DELETE SET NULL,
    source VARCHAR(50) NOT NULL,
    detected_at TIMESTAMPTZ NOT NULL,
    brightness_temp_k NUMERIC(6, 2),
    frp_mw NUMERIC(8, 2),
    confidence_pct NUMERIC(5, 2) NOT NULL,
    location GEOMETRY(Point, 4326) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_fire_events_detected_at ON fire_events(detected_at DESC);
CREATE INDEX IF NOT EXISTS idx_fire_events_location ON fire_events USING GIST(location);
CREATE INDEX IF NOT EXISTS idx_fire_events_grid_cell ON fire_events(grid_cell_id);

-- 4. Environmental Observations
CREATE TABLE IF NOT EXISTS environmental_observations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    grid_cell_id UUID NOT NULL REFERENCES grid_cells(id) ON DELETE CASCADE,
    observation_time TIMESTAMPTZ NOT NULL,
    temperature_c NUMERIC(5, 2),
    relative_humidity_pct NUMERIC(5, 2),
    wind_speed_ms NUMERIC(6, 2),
    wind_direction_deg NUMERIC(5, 2),
    precipitation_mm NUMERIC(7, 2),
    ndvi NUMERIC(4, 3),
    ndwi NUMERIC(4, 3),
    fwi NUMERIC(6, 2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_cell_obs_time UNIQUE (grid_cell_id, observation_time)
);

CREATE INDEX IF NOT EXISTS idx_env_obs_cell_time ON environmental_observations(grid_cell_id, observation_time DESC);
CREATE INDEX IF NOT EXISTS idx_env_obs_time ON environmental_observations(observation_time);

-- 5. Risk Predictions (24-Hour)
CREATE TABLE IF NOT EXISTS risk_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    grid_cell_id UUID NOT NULL REFERENCES grid_cells(id) ON DELETE CASCADE,
    region_id UUID NOT NULL REFERENCES regions(id) ON DELETE CASCADE,
    valid_for_date DATE NOT NULL,
    risk_probability NUMERIC(4, 3) NOT NULL CHECK (risk_probability >= 0.0 AND risk_probability <= 1.0),
    risk_class VARCHAR(20) NOT NULL CHECK (risk_class IN ('LOW', 'MODERATE', 'HIGH', 'EXTREME')),
    model_version VARCHAR(50) NOT NULL,
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_cell_risk_pred UNIQUE (grid_cell_id, valid_for_date, model_version)
);

CREATE INDEX IF NOT EXISTS idx_risk_pred_region_date ON risk_predictions(region_id, valid_for_date);
CREATE INDEX IF NOT EXISTS idx_risk_pred_cell ON risk_predictions(grid_cell_id);

-- 6. Simulations (12-Hour Cellular Automata Jobs)
CREATE TABLE IF NOT EXISTS simulations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    region_id UUID NOT NULL REFERENCES regions(id) ON DELETE CASCADE,
    ignition_location GEOMETRY(Point, 4326) NOT NULL,
    ignition_time TIMESTAMPTZ NOT NULL,
    duration_hours INTEGER DEFAULT 12,
    status VARCHAR(20) NOT NULL CHECK (status IN ('PENDING', 'RUNNING', 'COMPLETED', 'FAILED')),
    total_area_burned_ha NUMERIC(10, 2) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ NULL
);

CREATE INDEX IF NOT EXISTS idx_simulations_status ON simulations(status);
CREATE INDEX IF NOT EXISTS idx_simulations_region ON simulations(region_id);
CREATE INDEX IF NOT EXISTS idx_simulations_ignition ON simulations USING GIST(ignition_location);

-- 7. Simulation Timesteps
CREATE TABLE IF NOT EXISTS simulation_steps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    simulation_id UUID NOT NULL REFERENCES simulations(id) ON DELETE CASCADE,
    step_hour INTEGER NOT NULL CHECK (step_hour >= 1 AND step_hour <= 12),
    burned_area_ha NUMERIC(10, 2) NOT NULL,
    spread_velocity_kmh NUMERIC(6, 2) NOT NULL,
    spread_direction_deg NUMERIC(5, 2) NOT NULL,
    intensity_mw NUMERIC(8, 2) NOT NULL,
    perimeter_geom GEOMETRY(Polygon, 4326) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_sim_step UNIQUE (simulation_id, step_hour)
);

CREATE INDEX IF NOT EXISTS idx_sim_steps_sim_hour ON simulation_steps(simulation_id, step_hour);
CREATE INDEX IF NOT EXISTS idx_sim_steps_geom ON simulation_steps USING GIST(perimeter_geom);
