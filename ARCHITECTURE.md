# Forest Fire Risk Prediction & Spread Simulation Platform
## System Architecture Specification

---

### 1. Project Overview
The Predictive Forest Fire Risk & Spread Simulation System is an enterprise-grade geospatial AI platform engineered to transition wildfire disaster management from reactive firefighting to proactive, data-driven prevention and containment. Inspired by the ISRO Forest Fire Prediction Technical Blueprint and international wildland fire science standards, the platform fuses multi-source satellite observations, real-time meteorological forecasts, vegetation/fuel moisture metrics, and topographical models into a standardized 500m × 500m spatial grid.

The system delivers three core operational capabilities:
1. **24-Hour Forest Fire Susceptibility Prediction**: Daily spatial probability mapping of wildfire occurrence across designated geographic jurisdictions.
2. **12-Hour Fire Spread Simulation**: Real-time physical/heuristic fire perimeter propagation modeling initialized from active satellite detections or simulated ignition points.
3. **Interactive GIS Command Dashboard**: A high-performance spatial interface for disaster management agencies, forest rangers, and emergency responders.

---

### 2. Problem & Domain Overview
Wildfires present severe ecological, human, and economic threats. Traditional operations suffer from fragmented data silos, delayed satellite reporting, and disparate computational models. To address this, the domain is split into two distinct computational paradigms:
- **Precursor Risk Forecasting (Static Time-Window)**: Evaluating whether environmental conditions (dry fuel, high temperatures, low humidity, steep topography, human proximity) make a grid cell susceptible to ignition over the next 24 hours.
- **Dynamic Spread Propagation (Time-Series Simulation)**: Given an active fire ignition, calculating how flame fronts propagate hour-by-hour across neighboring cells based on wind vectors, slope gradients, aspect, and fuel combustibility over a 12-hour operational window.

---

### 3. Architectural Style: Modular Monorepo
To maintain high velocity, atomic versioning, and strict separation of concerns without introducing premature microservices latency and deployment overhead, this platform uses a **modular monorepo** architecture.

- **Unified Repository**: Code, shared data contracts, spatial utilities, schemas, and infrastructure manifests live together in a single repository.
- **Strict Service Boundaries**: Computational algorithms, API routing, data ingestion adapters, and frontend visualization operate in dedicated directories with isolated dependency manifests.
- **No Monolithic Tangling**: Business logic does not leak across boundaries; the API does not execute heavy scientific calculations; the ML models do not directly handle HTTP requests; the frontend does not execute Python algorithms.

---

### 4. Overall System Architecture Diagram

```
+----------------------------------------------------------------------------------------------------+
|                                    GIS FRONTEND (React + TypeScript)                               |
|   +-------------------+  +-------------------+  +-------------------+  +-----------------------+   |
|   |   Map Viewport    |  |  Risk Overlays    |  |  Spread Timeline  |  |  Active Fire Monitor  |   |
|   |  (Leaflet/Mapbox) |  |   (GeoJSON 500m)  |  |   (0 - 12 Hours)  |  |    (VIIRS / MODIS)    |   |
|   +-------------------+  +-------------------+  +-------------------+  +-----------------------+   |
+--------------------------------------------------^-------------------------------------------------+
                                                   | HTTPS / JSON / GeoJSON
+--------------------------------------------------v-------------------------------------------------+
|                                    BACKEND API (FastAPI Gateway)                                   |
|   +--------------------------------------------------------------------------------------------+   |
|   |  Routers (/v1/health, /v1/regions, /v1/fires, /v1/risk, /v1/simulations, /v1/layers)      |   |
|   +--------------------------------------------------------------------------------------------+   |
|   |  Core Middleware (CORS, Structured Logging, Centralized Config, Request Tracing)          |   |
|   +--------------------------------------------------------------------------------------------+   |
|   |  Application Services & Repository Abstractions (Decoupled SQL / PostGIS queries)          |   |
|   +-----------------------+------------------------------------------+-------------------------+   |
+---------------------------|------------------------------------------|-----------------------------+
                            | Enqueue Jobs                             | Queries / Results
                            v                                          v
+---------------------------+-----------------------+   +--------------+-----------------------------+
|               TASK BROKER & ASYNC QUEUE           |   |            SPATIAL STORAGE                 |
|   +-------------------------------------------+   |   |   +------------------------------------+   |
|   |  Redis Broker & State Backend             |   |   |   |   PostgreSQL 16 + PostGIS 3.4      |   |
|   +---------------------+---------------------+   |   |   |   - regions & 500m grid_cells      |   |
|                         | Consume Tasks           |   |   |   - fire_events & active hotspots  |   |
|                         v                         |   |   |   - environmental_observations     |   |
|   +-------------------------------------------+   |   |   |   - risk_predictions               |   |
|   |  Celery Worker Process                    |   |   |   |   - simulations & simulation_steps |   |
|   |  (Async Execution & Job Orchestration)    |   |   |   +------------------------------------+   |
|   +---------------------+---------------------+   |   |   Object / File Storage (S3 / Local)       |   |
+-------------------------|-------------------------+   |   - Raw satellite rasters & GeoTIFFs       |   |
                          |                             +--------------------------------------------+
       +------------------+------------------+
       |                                     |
       v                                     v
+-------------------------------+ +----------------------------------+ +-----------------------------+
|       DATA PIPELINE           | |         RISK ENGINE              | |        SPREAD ENGINE        |
|  - Ingestion Adapters         | |  - Feature Validation            | |  - Cellular Automata Grid   |
|    (ISRO, NASA, IMD, DEM)     | |  - Training & Evaluation         | |  - Slope / Wind Vectors     |
|  - Spatial/Temporal Alignment | |  - Baseline XGBoost / RF         | |  - Rothermel Physics Layer  |
|  - Common 500m Grid Resampler | |  - Susceptibility Inference      | |  - Timestep Propagation     |
|  - Feature Engineering (FWI)  | |  - Model Registry & Metadata     | |  - Convex Hull / Perimeters |
+-------------------------------+ +----------------------------------+ +-----------------------------+
```

---

### 5. Repository Structure
```
forest-fire-platform/
├── apps/
│   └── web/                         # React 18 + TypeScript + Vite + Tailwind CSS Frontend
│       ├── public/                  # Static assets and icons
│       └── src/
│           ├── components/          # Reusable UI controls (Header, Sidebar, MapContainer, etc.)
│           ├── features/            # Feature domains (map, risk, fire, simulation, weather, dashboard)
│           ├── hooks/               # Custom React hooks
│           ├── layouts/             # App shell layouts
│           ├── lib/                 # Third-party wrapper utilities
│           ├── services/            # API client abstraction & fetchers
│           ├── types/               # Typed domain contracts
│           ├── utils/               # GIS formatters & math helpers
│           └── pages/               # Top-level view routes
├── services/
│   ├── api/                         # FastAPI Application & REST Endpoints
│   │   ├── app/
│   │   │   ├── api/v1/              # Versioned API routes
│   │   │   ├── core/                # Config, logging, errors, celery client, db session
│   │   │   ├── dependencies/        # FastAPI dependency injection
│   │   │   ├── models/              # SQLAlchemy spatial ORM models
│   │   │   ├── repositories/        # Database access layer
│   │   │   ├── schemas/             # Pydantic request/response schemas
│   │   │   ├── services/            # API business logic orchestration
│   │   │   └── main.py              # FastAPI application entrypoint
│   │   ├── tests/                   # API test suite
│   │   ├── requirements.txt         # API service dependencies
│   │   └── Dockerfile               # API container image
│   ├── data-pipeline/               # Data Ingestion, Preprocessing & Feature Engineering
│   │   ├── adapters/                # Modular data source adapters (Fire, Weather, Vegetation, DEM)
│   │   ├── common/                  # Pipeline exceptions and utilities
│   │   ├── features/                # Feature engineering (NDVI, NDWI, FWI, slope/aspect)
│   │   ├── ingestion/               # Extraction & staging orchestration
│   │   ├── preprocessing/           # 500m spatial resampling & temporal daily compositing
│   │   ├── validation/              # Raw data validation schemas & quality rules
│   │   ├── tests/                   # Pipeline test suite
│   │   ├── requirements.txt         # Pipeline dependencies
│   │   └── Dockerfile               # Pipeline container image
│   ├── risk-engine/                 # 24-Hour Fire Risk Machine Learning Engine
│   │   ├── common/                  # Model metadata, versioning & metrics
│   │   ├── evaluation/              # Precision, Recall, F1, ROC-AUC evaluators
│   │   ├── features/                # Pre-inference feature validators & normalizers
│   │   ├── inference/               # Abstract predictor & inference runner
│   │   ├── models/                  # Base risk model contracts & model registry
│   │   ├── training/                # Dataset preparation & training loops
│   │   ├── tests/                   # Risk engine unit tests
│   │   ├── requirements.txt         # Scikit-learn, XGBoost dependencies
│   │   └── Dockerfile               # Risk engine container image
│   └── spread-engine/               # 12-Hour Fire Spread Simulation Engine
│       ├── calibration/             # Fuel model parameters & calibration interfaces
│       ├── common/                  # Grid state constants and spread exceptions
│       ├── models/                  # Simulation configurations and input contracts
│       ├── physics/                 # Wind vectors, slope adjustment, Rothermel equations
│       ├── simulation/              # Cellular Automata runner, grid matrix, timesteps
│       ├── tests/                   # Spread engine unit tests
│       ├── requirements.txt         # NumPy / scientific dependencies
│       └── Dockerfile               # Spread engine container image
├── packages/
│   ├── shared-types/                # Shared JSON schemas, Python dataclasses & TypeScript types
│   ├── geo-utils/                   # Common GIS utilities (CRS transformation, bbox, 500m grid cell)
│   └── config/                      # Environment schema definitions
├── database/
│   ├── migrations/                  # Alembic database migrations
│   ├── schema/                      # Raw PostGIS DDL scripts
│   └── seed/                        # Initial regional reference geometries & seed data
├── data/                            # Local filesystem data directory
│   ├── raw/                         # Raw satellite and meteorological downloads
│   ├── processed/                   # Cleaned, standardized 500m rasters
│   └── sample/                      # Lightweight fixtures for unit testing
├── models/
│   ├── risk/                        # Serialized risk model artifacts (.joblib, .json)
│   └── spread/                      # Calibrated fuel lookups and spread configurations
├── scripts/                         # Operational helper scripts
├── tests/
│   ├── integration/                 # Cross-service integration tests
│   └── e2e/                         # End-to-end API & simulation flow verification
├── docker-compose.yml               # Multi-container local orchestration
├── .env.example                     # Environment variable specification template
├── .gitignore                       # Git repository exclusions
├── ARCHITECTURE.md                  # This document
├── API_CONTRACT.md                  # OpenAPI specification & endpoint contracts
├── DATABASE_SCHEMA.md               # PostGIS database schema specification
├── DATA_CONTRACTS.md                # Canonical data models & input/output contracts
├── DEVELOPMENT.md                   # Local setup, testing & contribution guide
├── IMPLEMENTATION_PLAN.md           # 10-Phase project roadmap
└── LICENSE                          # Apache 2.0 License
```

---

### 6. Service Responsibilities & Domain Ownership

| Service Domain | Primary Responsibilities | Prohibited / Out-of-Scope Responsibilities |
| :--- | :--- | :--- |
| **Frontend / Web** | Interactive GIS rendering, layer toggling, time slider (0-12h), dashboard metrics, user notifications. | Direct execution of Python ML, database access, heavy raster calculations. |
| **Backend API** | HTTP routing, request/response validation, auth/permissions, job queueing, querying spatial results. | Running ML training, executing Cellular Automata simulation loops. |
| **Data Pipeline** | Data provider adapters (ISRO, NASA, IMD, SRTM), CRS projection, 500m raster resampling, daily compositing. | Serving HTTP requests, computing fire spread trajectories. |
| **Risk Engine** | Precursor feature validation, model registry, 24h probability scoring, susceptibility classification. | HTTP routing, database management, Celery task queueing. |
| **Spread Engine** | Fire grid state, cellular propagation, wind/slope vector factoring, boundary extraction, 12h timesteps. | Web framework coupling, database connection management. |
| **PostgreSQL + PostGIS** | Relational integrity, spatial indexing (GIST), region boundaries, 500m grid cells, queryable predictions. | Storing raw multi-gigabyte satellite imagery binaries (stored in object store). |
| **Redis + Celery** | Distributed asynchronous task queue, background job state tracking, non-blocking simulation execution. | Long-term spatial data persistence, complex relational queries. |

---

### 7. Dependency Boundaries
- **Unidirectional Flow**: FastAPI imports Domain Models & Task contracts; Celery Worker imports Risk/Spread engines; Engines have ZERO dependencies on Web/API frameworks.
- **Pure Domain Engines**: `risk-engine` and `spread-engine` are pure computational packages testable with simple in-memory matrices and dataclasses.
- **Shared Contracts**: Contracts in `packages/shared-types` and Pydantic schemas enforce compile-time and runtime type consistency across all services.

---

### 8. Frontend Architecture
- **Framework**: React 18, TypeScript (strict mode), Vite for bundling, Tailwind CSS for clean GIS controls.
- **Mapping Engine**: Leaflet with custom DOM container management and MapContext for high-performance direct vector rendering.
- **Layer Visual Hierarchy**:
  1. Base Map (CartoDB Dark Matter / Satellite / OpenStreetMap)
  2. Terrain & Environmental Raster Catalog (CartoDEM / IMD / Sentinel-2)
  3. 24-Hour Risk Susceptibility Choropleth (500m Grid Partitions)
  4. Active Satellite Thermal Hotspot Markers (VIIRS / MODIS)
  5. Fire Spread Simulation Perimeters & Ignition Point Marker (Cellular Automata)
  6. Region Boundary Highlight (EPSG:4326)
  7. Interactive UI Overlay Controls (MapControls, LayerControls, MapLegend, Timeline)
- **Feature Modularization**:
  - `features/map/`: Leaflet map lifecycle, tile controllers, GIS layer abstractions, and floating controls.
  - `features/regions/`: Monitored conservation reserves selector and boundary auto-fit.
  - `features/risk/`: 24h risk prediction choropleths, 500m cell inspector, and regional distribution cards.
  - `features/fire/`: Satellite hotspot markers, telemetry popups (FRP, brightness temp), and list-map bidirectional focus.
  - `features/simulation/`: Interactive map-click ignition selection, duration slider, and 0-12h scrub timeline controls.
  - `features/layers/`: Environmental and terrain raster catalogue (distinguishing active vs upcoming pipelines).
  - `features/dashboard/`: Operational metric cards and system health banners.
- **Typed API Integration**: Centralized HTTP client (`services/api/`) with RFC 7807 problem details parsing, typed contracts matching `DATA_CONTRACTS.md`, and deterministic fallback handling.

---

### 9. Backend Architecture
- **Framework**: FastAPI with asynchronous route handlers.
- **Validation**: Pydantic v2 schemas for strict contract enforcement.
- **Configuration**: `pydantic-settings` reading centralized environment variables.
- **Error Handling**: Global exception handler transforming application exceptions into standardized RFC-compliant error payloads.
- **Database Abstraction**: SQLAlchemy session factory with PostGIS geometry support (`GeoAlchemy2`).

---

### 10. Data Pipeline Architecture
- **Adapter Pattern**: Each data source implements an abstract base interface (`BaseDataSource`).
- **Data Harmonization**:
  - Resampling all incoming imagery/rasters to a common 500m × 500m grid cell resolution.
  - Reprojecting to geographic WGS 84 (EPSG:4326) or local UTM zones.
  - Computing daily composites for vegetation and weather precursor metrics.

---

### 11. Risk Engine Architecture
- **Model Baseline**: Tabular/pixel-wise models (Random Forest, XGBoost) mapping 500m cell precursor features to a fire susceptibility probability in `[0.0, 1.0]`.
- **Classification Bands**:
  - `0.00 - 0.25`: LOW
  - `0.25 - 0.50`: MODERATE
  - `0.50 - 0.75`: HIGH
  - `0.75 - 1.00`: EXTREME
- **Extensibility**: Future interfaces reserve slots for U-Net or Spatio-Temporal Graph Convolutional Networks (ST-GCN) to capture spatial autocorrelation among adjacent grid cells.

---

### 12. Spread Engine Architecture
- **Cellular Automata (CA) Core**: The simulation space is represented as a 2D discrete cell grid where each cell exists in one of three canonical states: `UNBURNED (0)`, `BURNING (1)`, or `BURNED (2)`.
- **Spread Influence Factors**:
  - **Wind Vector**: Wind speed ($m/s$) and direction ($\theta^\circ$) bias propagation toward downwind neighbor cells.
  - **Slope & Aspect**: Uphill fire spread accelerates dramatically according to topographical gradient ($S$).
  - **Fuel Model**: Land cover combustibility coefficients modulate transition probability.
- **Physics Integration (Advanced)**: Interface hooks for Rothermel surface fire spread rate calculations and Physics-Informed Neural Networks (PINN).

---

### 13. Database Architecture
- **Database Engine**: PostgreSQL 16 with PostGIS 3.4 spatial extension.
- **Spatial Indexing**: `GIST` indexes on all spatial geometry columns (`geometry(Polygon, 4326)`, `geometry(Point, 4326)`, `geometry(MultiPolygon, 4326)`).
- **Partitioning & Granularity**: High-volume tables (`grid_cells`, `environmental_observations`, `risk_predictions`) are keyed by `region_id` and indexed temporally.

---

### 14. Asynchronous Processing Architecture
- **Task Queue**: Celery backed by Redis.
- **Job Lifecycle**:
  1. Client sends `POST /api/v1/simulations` with ignition coordinates and simulation parameters.
  2. API validates request, creates a simulation record in database with status `PENDING`, and dispatches task `simulate_fire_spread` to Celery.
  3. API immediately responds with `202 Accepted` returning `simulation_id` and polling URI.
  4. Celery worker picks up job, executes the spread engine simulation step-by-step, writes intermediate timesteps to PostGIS, and updates status to `COMPLETED`.
  5. Frontend polls `GET /api/v1/simulations/{id}` or retrieves the final boundary layers.

---

### 15. Asynchronous Job Flow Diagram

```
+----------+             +---------+          +-------+          +---------------+          +-----------+
| React UI |             | FastAPI |          | Redis |          | Celery Worker |          |  PostGIS  |
+----+-----+             +----+----+          +---+---+          +-------+-------+          +-----+-----+
     |                        |                   |                      |                        |
     | POST /simulations      |                   |                      |                        |
     |----------------------->|                   |                      |                        |
     |                        | Save Pending      |                      |                        |
     |                        |------------------------------------------------------------------>|
     |                        | Enqueue Job       |                      |                        |
     |                        |------------------>|                      |                        |
     | 202 Accepted {id}      |                   |                      |                        |
     |<-----------------------|                   |                      |                        |
     |                        |                   | Fetch Task           |                        |
     |                        |                   |--------------------->|                        |
     |                        |                   |                      | Update status: RUNNING |
     |                        |                   |                      |----------------------->|
     |                        |                   |                      | Run Spread Engine (CA) |
     |                        |                   |                      | (Hours 1 to 12)        |
     |                        |                   |                      |                        |
     |                        |                   |                      | Write Timesteps        |
     |                        |                   |                      |----------------------->|
     |                        |                   |                      | Update: COMPLETED      |
     |                        |                   |                      |----------------------->|
     | GET /simulations/{id}  |                   |                      |                        |
     |----------------------->| Query status      |                      |                        |
     |                        |------------------------------------------------------------------>|
     | 200 OK (COMPLETED)     |<------------------------------------------------------------------|
     |<-----------------------|                   |                      |                        |
```

---

### 16. System Data Flow Overview
Data flows through systematic validation, alignment, model inference, persistence, and display stages. Both risk and spread engines consume uniform spatial data products.

---

### 17. Prediction Data Flow Diagram

```
+----------------------------------------------------------------------------------------------------+
|                                        EXTERNAL DATA SOURCES                                       |
|     +------------------+  +------------------+  +------------------+  +----------------------+     |
|     | Satellite/Hotspot|  |   Meteorology    |  | Vegetation/Fuel  |  |   Topography (DEM)   |     |
|     |  (MODIS / VIIRS) |  |   (IMD / ERA5)   |  |   (Sentinel-2)   |  | (CartoDEM / SRTM 30m)|     |
|     +--------+---------+  +--------+---------+  +--------+---------+  +----------+-----------+     |
+--------------|---------------------|---------------------|-----------------------|-----------------+
               v                     v                     v                       v
+----------------------------------------------------------------------------------------------------+
|                                    DATA PIPELINE (INGESTION)                                       |
|  - Ingestion Adapters -> Raw Validation -> CRS Harmonization (EPSG:4326 / UTM)                     |
|  - 500m x 500m Resampling -> Daily Temporal Composites -> Feature Calculation (NDVI, NDWI, FWI)    |
+--------------------------------------------------+-------------------------------------------------+
                                                   v
+----------------------------------------------------------------------------------------------------+
|                                        RISK ENGINE (24-HOUR)                                       |
|  - Feature Vector Assembly: [NDVI, NDWI, Temp, Humidity, Wind, Slope, Aspect, FuelClass, BurnHist] |
|  - Pre-inference Validation -> XGBoost / Random Forest Inference -> Probability [0.0 - 1.0]        |
|  - Risk Classification: LOW | MODERATE | HIGH | EXTREME                                            |
+--------------------------------------------------+-------------------------------------------------+
                                                   v
+----------------------------------------------------------------------------------------------------+
|                                         POSTGRESQL + POSTGIS                                       |
|  - Persist risk_predictions linked to grid_cell_id and region_id with prediction_timestamp         |
+--------------------------------------------------+-------------------------------------------------+
                                                   v
+----------------------------------------------------------------------------------------------------+
|                                     FASTAPI -> REACT GIS CLIENT                                    |
|  - GET /api/v1/risk/{region_id} returns GeoJSON FeatureCollection of 500m cells with risk levels   |
+----------------------------------------------------------------------------------------------------+
```

---

### 18. Simulation Data Flow Diagram

```
+----------------------------------------------------------------------------------------------------+
|                                      IGNITION POINT SELECTION                                      |
|  - User clicks on map OR active satellite hotspot detected: (Latitude, Longitude, Ignition Time)   |
+--------------------------------------------------+-------------------------------------------------+
                                                   v
+----------------------------------------------------------------------------------------------------+
|                                       FASTAPI SIMULATION ENDPOINT                                  |
|  - POST /api/v1/simulations -> Validates coordinates, simulation hours (1-12), wind overrides      |
|  - Creates simulation record -> Dispatches Celery job -> Returns 202 Accepted                      |
+--------------------------------------------------+-------------------------------------------------+
                                                   v
+----------------------------------------------------------------------------------------------------+
|                                  SPREAD ENGINE (CELLULAR AUTOMATA)                                 |
|  - Initializes grid bounding box around ignition point (500m cell matrix)                          |
|  - Loads cell parameters: fuel type, slope, aspect, wind speed & direction                         |
|  - For t = 1 to 12 hours:                                                                          |
|      * Calculates burn transition probability for unburned neighbor cells                          |
|      * Updates state matrix: UNBURNED -> BURNING -> BURNED                                         |
|      * Computes metrics: burned area (ha), spread velocity (km/h), intensity                       |
|      * Generates perimeter polygon boundary (GeoJSON Polygon)                                      |
+--------------------------------------------------+-------------------------------------------------+
                                                   v
+----------------------------------------------------------------------------------------------------+
|                                      DATABASE PERSISTENCE                                          |
|  - Writes simulation_steps records with step hour, metrics, and geometry                           |
+--------------------------------------------------+-------------------------------------------------+
                                                   v
+----------------------------------------------------------------------------------------------------+
|                                    INTERACTIVE TIMELINE & GIS                                      |
|  - React slider animates fire perimeter propagation from Hour 1 through Hour 12                    |
+----------------------------------------------------------------------------------------------------+
```

---

### 19. Database Entity-Relationship Diagram

```
+------------------------------------+
|              regions               |
+------------------------------------+
| id (PK, UUID)                      |
| code (VARCHAR(50), UNIQUE)         |
| name (VARCHAR(150))                |
| state (VARCHAR(100))               |
| boundary (GEOMETRY(Polygon, 4326)) |
| area_sqkm (NUMERIC)                |
| created_at, updated_at             |
+-----------------+------------------+
                  | 1
                  |
                  | N
+-----------------v------------------+       N      +-----------------------------------------+
|             grid_cells             |------------->|              fire_events                |
+------------------------------------+              +-----------------------------------------+
| id (PK, UUID)                      |              | id (PK, UUID)                           |
| region_id (FK, UUID)               |              | grid_cell_id (FK, UUID, NULL)           |
| cell_code (VARCHAR(100), UNIQUE)   |              | source (VARCHAR(50)) [MODIS, VIIRS]     |
| centroid (GEOMETRY(Point, 4326))   |              | detected_at (TIMESTAMPTZ)               |
| geometry (GEOMETRY(Polygon, 4326)) |              | brightness_temp_k (NUMERIC)             |
| resolution_meters (INT=500)        |              | frp_mw (NUMERIC)                        |
| elevation_m (NUMERIC)              |              | confidence_pct (NUMERIC)                |
| slope_deg (NUMERIC)                |              | location (GEOMETRY(Point, 4326))        |
| aspect_deg (NUMERIC)               |              +-----------------------------------------+
| fuel_type (VARCHAR(50))            |
+--------+---------------------+-----+
         | 1                   | 1
         |                     |
         | N                   | N
+--------v-------------------+ +v--------------------------------------+
| risk_predictions           | |     environmental_observations        |
+----------------------------+ +---------------------------------------+
| id (PK, UUID)              | | id (PK, UUID)                         |
| grid_cell_id (FK, UUID)    | | grid_cell_id (FK, UUID)               |
| region_id (FK, UUID)       | | observation_time (TIMESTAMPTZ)        |
| valid_for_date (DATE)      | | temperature_c (NUMERIC)               |
| risk_probability (NUMERIC) | | relative_humidity_pct (NUMERIC)       |
| risk_class (VARCHAR(20))   | | wind_speed_ms (NUMERIC)               |
| model_version (VARCHAR(50))| | wind_direction_deg (NUMERIC)          |
| generated_at (TIMESTAMPTZ) | | precipitation_mm (NUMERIC)            |
+----------------------------+ | ndvi (NUMERIC), ndwi (NUMERIC)        |
                               | fwi (NUMERIC)                         |
                               +---------------------------------------+

+-----------------------------------------+
|               simulations               |
+-----------------------------------------+
| id (PK, UUID)                           |
| region_id (FK, UUID)                    |
| ignition_location (GEOMETRY(Pt, 4326))  |
| ignition_time (TIMESTAMPTZ)             |
| duration_hours (INT)                    |
| status (VARCHAR(20)) [PENDING, ...]     |
| total_area_burned_ha (NUMERIC)          |
| created_at, completed_at                |
+--------------------+--------------------+
                     | 1
                     |
                     | N
+--------------------v--------------------+
|            simulation_steps             |
+-----------------------------------------+
| id (PK, UUID)                           |
| simulation_id (FK, UUID)                |
| step_hour (INT, 1 to 12)                |
| burned_area_ha (NUMERIC)                |
| spread_velocity_kmh (NUMERIC)           |
| spread_direction_deg (NUMERIC)          |
| intensity_mw (NUMERIC)                  |
| perimeter_geom (GEOMETRY(MultiPoly,4326)|
| created_at                              |
+-----------------------------------------+
```

---

### 20. Error Handling Strategy
- **Centralized Handling**: All custom errors inherit from `ForestFireAppException` with structured error codes.
- **Consistent API Format**: Errors always return JSON conforming to the API Contract:
  ```json
  {
    "error": {
      "code": "RESOURCE_NOT_FOUND",
      "message": "Region not found with code 'WESTERN_GHATS_01'",
      "details": {},
      "request_id": "req-987a-b65c"
    }
  }
  ```
- **No Leaked Stack Traces**: Production logs record tracebacks; clients receive sanitized error payloads.

---

### 21. Logging Strategy
- **Structured JSON Logging**: Logs emit timestamp, level, logger name, message, request ID, and context metadata.
- **Security Sanitization**: Passwords, connection URIs, tokens, and authorization headers are strictly excluded from logs.
- **Traceability**: Every HTTP request receives a unique `X-Request-ID` passed through downstream logging.

---

### 22. Configuration Strategy
- **Single Source of Truth**: All configuration is managed via `pydantic-settings` in `core/config.py`.
- **Environment Driven**: Every setting has a default for local development and can be overridden via `.env`.
- **Validation**: Improperly formatted database URLs or port numbers fail fail-fast on startup.

---

### 23. Testing Strategy
- **Unit Testing**: Pytest for domain engines, repositories, and API endpoints without relying on live external networks.
- **Mock Interfaces**: Adapters, Celery workers, and database connections are mocked during unit tests.
- **Frontend Testing**: Vitest and React Testing Library verifying component rendering, layout structure, and state changes.
- **Deterministic Assertions**: Tests assert deterministic mathematical formulas, boundary geometries, and contracts.

---

### 24. Security Considerations
- **Environment Secrets**: No credentials, tokens, or private keys committed to source control.
- **CORS Protection**: Restricted to allowed origins.
- **Input Validation**: Coordinate boundaries validated against legitimate latitude/longitude bounds and region envelopes.
- **SQL Injection Prevention**: Parameterized queries via SQLAlchemy and GeoAlchemy2.

---

### 25. Scalability Considerations
- **Raster Decoupling**: Large GeoTIFF files remain in object storage; only indexed vector boundaries and cell aggregates are stored in PostGIS.
- **Asynchronous Workflows**: Heavy 12-hour Cellular Automata calculations run off the main event loop in Celery workers.
- **Spatial Tiling**: Future raster tile services (e.g., MVT / GeoServer / TiTiler) can serve 500m grid overlays efficiently.

---

### 26. Extensibility Considerations
- **Swappable Adapters**: Adding an active fire sensor (e.g., Sentinel-3 SLSTR) simply requires implementing `BaseFireAdapter`.
- **Model Registry**: Upgrading the risk engine from Random Forest to XGBoost or a PyTorch U-Net requires no changes to API schemas or frontend.
- **Spread Engine Physics**: Rothermel equations and PINNs plug directly into the spread runner without rewriting the grid representation.

---

### 27. MVP Boundaries & Future Architecture
- **Phase 1 (Current)**: Architectural blueprint, modular monorepo structure, API and data contracts, database schema, React layout shell, FastAPI skeleton, Celery configuration, and automated test foundation.
- **Phases 2-10 (Future)**: Real machine learning training, live data ingestion, Cellular Automata physics simulation, GIS layer rendering, and production hardening.
