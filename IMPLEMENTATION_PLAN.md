# 10-Phase Project Implementation Plan

This roadmap governs the end-to-end development of the **Predictive Forest Fire Risk & Spread Simulation Platform**, derived from the ISRO Forest Fire Prediction Technical Blueprint and modern geospatial software architecture standards.

---

### Phase 1: Architecture, Project Foundation & Development Setup [COMPLETED]
- **Objectives**: Establish modular monorepo architecture, formal documentation, typed API and data contracts, PostGIS database schema, React shell, FastAPI skeleton, Celery configuration, Docker Compose environment, and automated test foundation.
- **Deliverables**:
  - `ARCHITECTURE.md`, `API_CONTRACT.md`, `DATA_CONTRACTS.md`, `DATABASE_SCHEMA.md`, `DEVELOPMENT.md`, `IMPLEMENTATION_PLAN.md`.
  - Directory structure and service boundaries.
  - FastAPI `/api/v1/health` endpoint and core middlewares.
  - React + TypeScript application shell with GIS map container and navigation.
  - Data pipeline, Risk engine, Spread engine abstract interfaces.
  - PostGIS DDL script and sample seed data.
  - Docker Compose configuration and automated tests.

---

### Phase 2: Backend, Database & API Implementation [COMPLETED]
- **Objectives**: Implement full relational data models, SQLAlchemy / GeoAlchemy2 integration, repositories, service layer, and concrete REST endpoints.
- **Deliverables**:
  - Region querying and spatial bounding endpoints (`/api/v1/regions`).
  - Active fire hotspots ingestion and querying endpoints (`/api/v1/fires/active`).
  - Simulation job submission and lifecycle tracking endpoints (`/api/v1/simulations`).
  - 24-hour risk prediction endpoints and GIS layer metadata (`/api/v1/risk`, `/api/v1/layers`).
  - Alembic migrations (`0001_initial_postgis_schema.py`) and programmatic database seeding (`python -m services.api.app.seed`).
  - RFC 7807-compliant error handlers, `X-Request-ID` tracing, and GeoJSON spatial response serialization.

---

### Phase 3: Frontend & GIS Foundation [COMPLETED]
- **Objectives**: Build high-performance interactive GIS client using React, Leaflet, Tailwind CSS, and feature-driven architecture.
- **Deliverables**:
  - Modular feature architecture (`src/features/map`, `risk`, `fire`, `simulation`, `regions`, `layers`, `dashboard`).
  - Interactive Leaflet GIS map with Basemap switcher (Dark Matter, Satellite, OSM), MapControls, LayerControls, and MapLegend.
  - Monitored region selector integrated with backend (`/api/v1/regions`, `/api/v1/regions/{id}/boundary`) with automatic viewport centering.
  - Active satellite fire hotspots visualization (`/api/v1/fires/active`) with animated pulse markers, FRP telemetry popups, and list-map bidirectional selection.
  - 24-hour risk susceptibility visualization (`/api/v1/risk/{region_id}`) with 500m grid cell inspection and regional summary distributions.
  - 12-hour Cellular Automata simulation interface with map-click ignition point selection, duration scrub slider, and 0-12h timeline playback controls.
  - Environmental layers catalog (`/api/v1/layers`) distinguishing operational layers from upcoming Phase 4 pipelines.
  - Typed central API client layer with RFC 7807 problem details parsing and timeout management.
  - Comprehensive unit and integration test suite (25/25 tests passing in Vitest).


---

### Phase 4: Data Ingestion & Preprocessing Pipeline [COMPLETED]
- **Objectives**: Implement automated adapters for satellite, meteorological, vegetation, and terrain datasets, normalizing all inputs to a 500m × 500m common spatial grid without temporal leakage.
- **Deliverables**:
  - Source Adapters: NASA MODIS (`ModisFireAdapter`), VIIRS (`ViirsFireAdapter`), ISRO INSAT-3D (`InsatFireAdapter`), ECMWF ERA5 (`Era5WeatherAdapter`), IMD (`ImdWeatherAdapter`), Sentinel-2 (`SentinelVegetationAdapter`), Landsat-8 (`LandsatVegetationAdapter`), ISRO Bhuvan (`BhuvanVegetationAdapter`), NASA SRTM (`SrtmTerrainAdapter`), ISRO CartoDEM (`CartoDemTerrainAdapter`).
  - Spatial Reference & Grid: Dynamic UTM metric CRS projection discovery (`CrsManager`), regular 500m × 500m cell generator (`GridGenerator`), and R-tree spatial indexing (`SpatialGridIndex`).
  - Spatial & Temporal Alignment: IDW spatial interpolation (`SpatialAligner`), daily temporal compositing, and strict anti-leakage guards raising `DataLeakageError` on future observations (`TemporalAligner`).
  - Feature Engineering: Spectral indices (NDVI, NDWI), fuel categorization (`standardize_fuel_class`), continuous cyclical aspect sin/cos, orthogonal U/V wind decomposition, and full Canadian Fire Weather Index equations (`FwiCalculator`).
  - Missing Data & Auditing: Traceable imputation with flags (`imputed_fields`), out-of-bounds physical clamping, and automated quality reporting (`QualityReport`, `QualityReportWriter`).
  - Model-Ready Outputs & Provenance: CSV, Parquet, and GeoJSON writers (`DatasetWriter`), reproducible run manifest (`ManifestBuilder`), and deterministic sample datasets for Uttarakhand/Garhwal.
  - End-to-end CLI & Test Suite: Command-line runner (`services.data_pipeline.cli`), 22 comprehensive pipeline tests (60/60 total monorepo tests passing).

---

### Phase 5: 24-Hour Fire Risk Machine Learning Model [COMPLETED]
- **Objectives**: Develop, train, evaluate, and serialize baseline tabular/pixel-wise machine learning models for 24-hour fire susceptibility prediction on the 500m × 500m canonical spatial grid without temporal leakage.
- **Deliverables**:
  - Standalone Risk Engine Service (`services/risk-engine/`) completely decoupled from FastAPI/PostGIS/Celery.
  - Strict Feature Contracts (`RiskFeatureSchema`, `FeatureSpec`, `RiskFeatureValidator`) enforcing physical bounds and rejecting non-finite anomalies across 20 numerical and 10 fuel categories.
  - Temporal Splitter (`TemporalSplitter`) guaranteeing strict chronological separation ($\max(T_{\text{train}}) \le \min(T_{\text{val}})$) with zero future data leakage.
  - Preprocessor (`FeaturePreprocessor`) with deterministic fuel one-hot matrix encoding and automatic cyclical/vector geometric feature derivation.
  - Machine Learning Trainers: Native XGBoost (`XGBoostRiskTrainer`) with dynamic `scale_pos_weight` rare-event imbalance scaling, plus comparative Random Forest baseline (`RandomForestRiskTrainer`).
  - Evaluation & Model Cards: Comprehensive metrics computation (`metrics.json`), human-readable Markdown evaluation report (`evaluation_report.md`), and complete production `MODEL_CARD.md`.
  - Model Registry & Safe Serialization (`ModelRegistry`, `ModelArtifactSerializer`) using native `model.json` (no insecure pickles) and versioned tracking under `models/risk/<version>/`.
  - High-Performance Inference (`ModelLoader`, `RiskPredictor`) supporting single-cell, batch, and vectorized DataFrame inference with standardized Pydantic contracts (`RiskPrediction`).
  - Unified CLI (`python -m services.risk_engine.cli` with `train`, `evaluate`, `predict`, `info` subcommands).
  - Test Suite: 30 new unit and integration tests across features, splits, trainers, evaluation, edge cases, and inference contracts (85/85 total monorepo tests passing).

---

### Phase 6: 24-Hour Risk Model -> FastAPI -> PostGIS -> GIS [COMPLETED]
- **Objectives**: Connect the Phase 5 trained 24-hour XGBoost fire risk model to the FastAPI backend, PostGIS spatial persistence layer, and the React GIS dashboard.
- **Deliverables**:
  - In-Memory Model Manager (`RiskModelManager`) loading and caching active model (`risk-xgboost-v001`) at startup with graceful fallback to `MODEL_UNAVAILABLE` status without crashing the API.
  - End-to-End Orchestrator (`RiskService`) integrating Phase 4 canonical features, Phase 5 XGBoost vector inference (`RiskPredictor`), PostGIS `risk_predictions` and `grid_cells` persistence, and GeoJSON conversion.
  - Thin REST Endpoints:
    - `GET /api/v1/risk/{region_id}` returning GeoJSON FeatureCollection of 500m cells with exact probability, risk class, 24h forecast window, model version, and environmental telemetry.
    - `GET /api/v1/risk/{region_id}/summary` providing real regional risk distributions (`low`, `moderate`, `high`, `extreme`) and mean probabilities.
    - `POST /api/v1/risk/predict` triggering synchronous on-demand batch inference with strict idempotency guards (`force_recompute`).
  - Spatial Persistence & Idempotency: `RiskRepository` supporting spatial joins with `grid_cells`, duplicate prevention on `(grid_cell_id, valid_for_date, model_version)`, and recompute overrides.
  - Enhanced GIS Frontend:
    - Real model layer rendered across 2,668 500m spatial cells with threshold styling.
    - Interactive 500m cell inspector rendering fire probability, risk class badge, FWI rating, elevation, slope, fuel classification, model version, forecast window, and generation timestamp.
    - Regional summary card powered by live `/summary` endpoint.
    - "Run Prediction" on-demand trigger button integrated directly into the map controls bar.
  - Automated Verification: 11 new integration tests in `test_risk_integration.py` (96/96 monorepo backend tests passing, 25/25 frontend tests passing, clean TypeScript build).

---

### Phase 7: 12-Hour Cellular Automata Spread Engine [COMPLETED]
- **Objectives**: Implement physical/heuristic Cellular Automata fire spread simulation engine incorporating wind vectors, slope, aspect, and fuel types.
- **Deliverables**:
  - Standalone Cellular Automata Engine: High-performance NumPy-backed 2D spatial grid representation (`UNBURNED`, `BURNING`, `BURNED`, `NON_BURNABLE`) in `services/spread-engine/`.
  - Moore 8-Neighbourhood Dynamics: Clockwise directional offsets, spherical distance weighting ($1.0$ orthogonal, $1/\sqrt{2}$ diagonal), and boundary-safe neighbor evaluation.
  - Directional Environmental Factors:
    - Wind vector amplification downwind and retardation upwind with circular angle diff handling ($359^\circ \leftrightarrow 1^\circ$).
    - Topographic slope uphill exponential acceleration and downhill retardation via Noble/McArthur scaling.
    - Solar aspect insolation modulation for the Northern Hemisphere (peak heating on south-facing slopes ~180°).
    - Indian forest fuel flammability classes (`CONIFER_HIGH_FLAMMABILITY` to `NON_BURNABLE_WATER`/`BARREN` with 0 combustibility).
  - Double-Buffered Simultaneous Transitions: State updates and burning timer countdowns committed order-independently.
  - Shapely Geometric Boundary Extraction: Dissolving active and burned cells into RFC 7946 GeoJSON Polygons / MultiPolygons.
  - Hourly Timestep Metrics: Cumulative burned area (ha), spread velocity (km/h), centroid spread direction (deg), and radiative fire intensity (MW).
  - Full Deterministic Reproducibility: Bit-for-bit identical outputs when executed with identical inputs.
  - Standalone CLI & Programmatic API: `services.spread_engine.cli` supporting standalone execution and GeoJSON exports.
  - Comprehensive Verification: 42 new unit, factor, boundary, and integration tests with 100% pass rate.

---

### Phase 8: Asynchronous Simulation & Live GIS Visualization [COMPLETED]
- **Objectives**: Integrate the spread engine into Celery background workers and provide interactive animated playback on the GIS frontend.
- **Deliverables**:
  - Celery background task `run_fire_spread_simulation` executing the Phase 7 Cellular Automata Spread Engine asynchronously.
  - Robust worker context management supporting both production Celery broker (Redis) and thread pool fallback in detached/testing modes.
  - Lifecycle state tracking: `QUEUED` $\to$ `RUNNING` $\to$ `COMPLETED` (or `FAILED`), with progress percentage and runtime telemetry.
  - Spatial validation of ignition points against region boundary polygons, preventing out-of-boundary runs with HTTP 422 `IGNITION_OUTSIDE_REGION`.
  - Database schema and PostGIS persistence of hourly progression perimeters (`simulation_steps`) as `GEOMETRY(4326)` supporting `Polygon` and `MultiPolygon`.
  - Rich FastAPI endpoints:
    - `POST /api/v1/simulations`: Enqueue 1h to 12h simulation with optional environmental/weather overrides.
    - `GET /api/v1/simulations/{id}`: Poll status, progress %, metrics, and engine version.
    - `GET /api/v1/simulations/{id}/timeline`: Retrieve hourly burned area, velocity, direction, and intensity.
    - `GET /api/v1/simulations/{id}/timesteps/{hour}`: Retrieve single hour perimeter GeoJSON feature and metrics.
    - `GET /api/v1/simulations/{id}/steps`: Retrieve full GeoJSON FeatureCollection of all hourly perimeters.
  - Interactive GIS Timeline Animation in React:
    - Play / Pause (▶ / ⏸), step forward / backward (⏮ / ⏭), scrub slider (0h to 12h), and replay (🔁).
    - Real-time telemetry displaying Hour $N$, elapsed minutes, burned area (ha), spread velocity (km/h), and active burning front cells.
    - Environmental scenario adjustment controls (wind speed slider, wind direction compass/degree slider, fuel classification).
    - Map click boundary containment check with friendly warning alert if clicked outside active region.
    - Multi-temporal Leaflet GIS perimeter rendering with distinct styling for active front (rose-500) vs burned history (dashed orange-400), plus click popups and tooltips.
  - Comprehensive verification: 40/40 API tests passing, 141/141 backend monorepo tests passing, 28/28 web tests passing, and clean production build.

---

### Phase 9: Operational GIS Dashboard, Analytics, Alerts & UX Productization [COMPLETED]
- **Objectives**: Transform the platform into an operational, battle-ready GIS intelligence dashboard with unified information hierarchy, live operational telemetries, cross-module workflows, actionable advisories, and burn analytics.
- **Deliverables**:
  - Operational Attention Advisory System:
    - Dynamic priority banner (`OperationalAttentionBanner`) calculating three operational readiness tiers (`HIGH_ATTENTION`, `WARNING`, `INFO`).
    - Multi-factor evaluation across active satellite thermal hotspots, elevated/extreme risk cell totals, and peak fire probabilities.
    - Contextual operational cross-links directly navigating responders to active fire clusters or 24h risk layers with zero manual searching.
  - Enhanced Operational Header & Status Telemetry:
    - Real-time digital clock displaying UTC timestamp and local operational time.
    - Sub-system health monitoring with tooltip telemetry for PostGIS, Celery workers, and machine learning models.
    - Regional selector with live name, state, and code search filter and accessible reset.
    - Data freshness and operational horizon badge (`24h Horizon Forecast`).
  - Real Operational Metrics (`MetricGrid`):
    - Replaced mock/static data with real live counts: Active Hotspots (24h observation window), High & Extreme Risk Cells (500m resolution), Peak Fire Susceptibility (regional maximum probability), and 500m Grid Partitions.
    - Direct quick action dispatch buttons in `OverviewPage` (`24h Risk →`, `Fires (N) →`, `Simulate →`).
  - 24h Fire Risk Analytics & Distribution (`RiskDistributionChart`):
    - Accessible bar breakdown of LOW, MODERATE, HIGH, and EXTREME risk tiers with exact cell counts and float percentages.
    - Click-to-filter capability linking distribution bars directly to the Leaflet choropleth layer.
    - `🎯 Focus Highest Risk` action identifying the single most vulnerable 500m cell in the active region.
    - `RiskCellInspector` updated with 3 structured operational panels (Risk Classification, Forecast & Model Metadata, Environmental Inputs) and model transparency disclaimers.
  - Seamless Cross-Module Simulation Dispatch:
    - Direct "Simulate Spread" action from any inspected risk cell (`onSimulateFromCell`) and any thermal hotspot card (`onSimulateFromFire`).
    - Cross-page state synchronization via `prefilledIgnition` automatically setting the CA ignition source and opening the simulation workspace.
  - 12h Spread Curve Analytics (`SimulationMetricChart`):
    - Visual bar & line progression chart displaying Cumulative Burned Area (ha) and Spread Velocity (km/h) for every simulation timestep.
    - Interactive timestep inspection synchronized with the timeline slider.
    - Keyboard controls for operational timeline playback (`Space` for Play/Pause, `ArrowLeft` / `ArrowRight` for timestep scrub).
    - Map focus tools (`SimulationFocusControls`) providing one-click recentering on ignition coordinates and region boundary.
  - Environmental Layer Catalog Polish:
    - Canonical measurement units (°C, m/s, %, m, °, MW) consistently documented across catalog and inspection cards.
    - Explicit operational status tags distinguishing operational GIS rasters from future data ingestion pipelines.
  - Fullscreen GIS Mode:
    - MapControls updated with one-click HTML5 Fullscreen GIS toggle (`⛶` / `🗗`).
  - Comprehensive Verification:
    - 39/39 frontend unit and integration tests passing (`npm test -- --run`).
    - Clean production frontend build (`npm run build`).
    - 141/141 backend monorepo tests passing with zero regressions.

---

### Phase 10: Validation, Hardening & Production Deployment
- **Status**: **COMPLETED (Phase 10 — Final Release)**
- **Release Decision**: **READY FOR DEMO**
- **Objectives**: Execute validation audits, benchmark testing, security review, production containerization, CI configuration, and complete release documentation.
- **Completed Deliverables**:
  - **Full Automated Testing**:
    - Backend Pytest suite: **141/141 passing** (unit, integration, DB models, edge cases).
    - Frontend Vitest suite: **39/39 passing** across 11 test suites.
    - Total test coverage: **180/180 passing**.
  - **Machine Learning & Spread Governance**:
    - `risk-xgboost-v001` validated on holdout data: ROC-AUC **0.8658**, Recall **0.8438**, `scale_pos_weight = 999.0`.
    - Spread Engine `spread-ca-v001` determinism verified: bit-for-bit identical burned areas and GeoJSON perimeters across repeated 12h runs on 40×40 grids.
    - Model and Data Cards established: `docs/SPREAD_ENGINE_CARD.md`, `docs/DATA_CARD.md`.
  - **Performance Benchmarks & SLAs**:
    - Risk inference: **7.69 ms/cell** (single), **0.067 ms/cell** (1,000-cell batch).
    - 12h Cellular Automata spread: **331.8 ms** (40×40 grid, 1,600 cells).
    - Frontend production bundle: **447.7 kB** uncompressed / **127 kB** gzipped (`npm run build`).
  - **Security & Infrastructure Hardening**:
    - Secret scanning: 0 hardcoded credentials or keys found in repo.
    - Production template created: `.env.production.example`.
    - GitHub Actions CI workflow implemented: `.github/workflows/ci.yml`.
    - SQL injection protected via SQLAlchemy parameterized queries; CORS configurable.
  - **Operational Documentation & Runbooks**:
    - `docs/VALIDATION_REPORT.md`, `docs/PERFORMANCE_REPORT.md`, `docs/SECURITY_REVIEW.md`.
    - `docs/LIMITATIONS.md`, `docs/KNOWN_ISSUES.md`, `docs/FUTURE_WORK.md`.
    - `docs/DEPLOYMENT.md`, `docs/RELEASE_CHECKLIST.md`, `docs/PROJECT_STATUS.md`.
    - `CHANGELOG.md`, `DEMO.md`, and updated `README.md`.
