# Development Guide & Local Setup

Welcome to the **Predictive Forest Fire Risk & Spread Simulation Platform** developer documentation.
This guide outlines local environment setup, dependency management, commands for running services and tests, and troubleshooting workflows.

---

## 1. Prerequisites

Before starting local development, ensure the following tools are installed:
- **Python**: 3.11+ (Python 3.12 or 3.14 supported)
- **Node.js**: 20+ (LTS) or 24+
- **npm**: 10+
- **Docker & Docker Compose**: (Recommended for full multi-container local stack)
- **Git**

---

## 2. Environment Configuration

1. Copy the example environment file to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Review the core environment variables in `.env`:

| Variable | Description | Default |
| :--- | :--- | :--- |
| `APP_ENV` | Application environment (`development`, `testing`, `production`) | `development` |
| `DEBUG` | Enable debug mode and hot-reloading | `true` |
| `LOG_LEVEL` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) | `INFO` |
| `SECRET_KEY` | Application secret key for cryptography | Development string |
| `API_HOST` | FastAPI listener bind IP | `0.0.0.0` |
| `API_PORT` | FastAPI listener port | `8000` |
| `API_V1_PREFIX` | Versioned route prefix | `/api/v1` |
| `CORS_ORIGINS` | Comma-separated list of allowed origins | `http://localhost:5173,http://localhost:3000` |
| `POSTGRES_USER` | PostgreSQL superuser | `postgres` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `postgres` |
| `POSTGRES_DB` | PostgreSQL database name | `forest_fire_db` |
| `POSTGRES_PORT` | PostgreSQL port | `5432` |
| `DATABASE_URL` | PostgreSQL connection URI | `postgresql://postgres:postgres@localhost:5432/forest_fire_db` |
| `REDIS_URL` | Redis broker and state store URI | `redis://localhost:6379/0` |
| `CELERY_BROKER_URL` | Celery task queue broker URI | `redis://localhost:6379/0` |
| `CELERY_RESULT_BACKEND` | Celery task result backend URI | `redis://localhost:6379/1` |
| `DEFAULT_GRID_RESOLUTION_METERS` | Common spatial grid resolution | `500` |
| `VITE_API_BASE_URL` | Frontend REST API base URL | `http://localhost:8000/api/v1` |
| `VITE_MAPBOX_ACCESS_TOKEN` | Optional Mapbox GL JS access token | Empty (uses Leaflet OSM tiles) |

---

## 3. Running with Docker Compose

To launch all infrastructure services (FastAPI backend, Celery worker, PostGIS database, Redis broker, and React frontend) simultaneously:

```bash
# Build and start all services
docker compose up --build

# Run in background
docker compose up -d

# View service logs
docker compose logs -f api
docker compose logs -f celery_worker
docker compose logs -f web

# Stop services
docker compose down
```

### Exposed Endpoints in Docker:
- **Web Frontend**: `http://localhost:5173`
- **FastAPI Backend**: `http://localhost:8000`
- **API Interactive Swagger Docs**: `http://localhost:8000/docs`
- **PostgreSQL / PostGIS**: `localhost:5432`
- **Redis**: `localhost:6379`

---

## 4. Running Services Locally Without Docker

### 4.1 Python Virtual Environment Setup

```bash
# 1. Create and activate a Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies for the API service
pip install -r services/api/requirements.txt

# 3. Install testing dependencies
pip install pytest httpx
```

### 4.2 Start the FastAPI Backend

```bash
source .venv/bin/activate
uvicorn services.api.app.main:app --host 0.0.0.0 --port 8000 --reload
```
Test the health endpoint:
```bash
curl http://localhost:8000/api/v1/health
```

### 4.3 Start Celery Worker

```bash
source .venv/bin/activate
celery -A services.api.app.core.celery_app.celery_app worker --loglevel=INFO
```

### 4.4 Start the React Frontend

```bash
cd apps/web
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 5. Testing Guide

### 5.1 Python Automated Tests
Run the complete automated test suite across all services:

```bash
source .venv/bin/activate

# Run all unit tests
pytest

# Run API tests specifically
pytest services/api/tests -v

# Run Data Pipeline tests
pytest services/data-pipeline/tests -v

# Run Risk Engine tests
pytest services/risk-engine/tests -v

# Run Spread Engine tests
pytest services/spread-engine/tests -v
```

### 5.2 Frontend Automated Tests & Build

The frontend uses Vitest with React Testing Library and JSDOM for component and integration testing:

```bash
cd apps/web

# Run all 25 frontend tests across all feature modules
npm test

# Verify TypeScript typechecking and production Vite build
npm run build

# Preview production build locally
npm run preview
```

### 5.3 Frontend Feature Architecture
The frontend codebase in `apps/web/src` is organized into domain-specific features:
- `features/map/`: Leaflet GIS container, TileLayer providers, MapControls, LayerControls, and MapLegend.
- `features/regions/`: Monitored region selector and boundary rendering.
- `features/fire/`: Satellite thermal detections list, animated pulse markers, and FRP telemetry details.
- `features/risk/`: 24-hour fire risk susceptibility choropleth (500m cells) and cell inspection.
- `features/simulation/`: 12-hour Cellular Automata ignition placement, duration slider, and timeline scrubber.
- `features/layers/`: Environmental and terrain raster catalogue (distinguishing active vs upcoming pipelines).
- `services/api/`: Centralized HTTP client parsing RFC 7807 problem details with typed contracts.

---

## 6. Database & Migration Workflow

### 6.1 Alembic Database Migrations
PostGIS spatial schema migrations are managed via Alembic:

```bash
source .venv/bin/activate

# Check current revision
alembic current

# Run all migrations up to head (creates all 7 PostGIS tables and GIST indexes)
alembic upgrade head

# Rollback one migration revision
alembic downgrade -1
```

### 6.2 Programmatic Database Seeding
To populate the database with reference Indian forest regions (Uttarakhand, Similipal, Bandipur) and initial baseline grid cells:

```bash
source .venv/bin/activate

# Execute Python database seed script
python -m services.api.app.seed
```

### 6.3 Manual SQL Schema Execution (Alternative)
To manually execute the schema on an active PostgreSQL database:

```bash
psql -h localhost -U postgres -d forest_fire_db -f database/schema/initial_schema.sql
```

### 6.4 Manual SQL Seed (Alternative)
```bash
psql -h localhost -U postgres -d forest_fire_db -f database/seed/sample_seed.sql
```

---

## 7. Troubleshooting

- **CORS Errors**: Verify that your frontend port is included in `CORS_ORIGINS` in `.env`.
- **Database Connection Refused**: Ensure PostgreSQL is running and port `5432` is reachable. In local execution outside Docker, change the hostname in `DATABASE_URL` from `postgres` to `localhost`.
- **Redis Connection Refused**: Verify Redis is active on port `6379`. For local runs outside Docker, ensure `REDIS_URL` points to `localhost`.
- **Port In Use (8000 / 5173)**: Kill any dangling process via `lsof -ti :8000 | xargs kill -9` or configure a different port in `.env`.
