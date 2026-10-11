# Changelog

All notable changes to the Forest Fire Risk & Spread Simulation Platform are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-10-06 (Phase 10 — Production Readiness, Testing & Security)

### Added
- Comprehensive test suite verification: 141 backend Pytest tests and 39 frontend Vitest tests fully passing.
- GitHub Actions CI pipeline (`.github/workflows/ci.yml`) for automated backend testing, frontend testing, and production bundle builds.
- Production environment configuration template (`.env.production.example`) with externalized secrets and security guidelines.
- Model and Data Governance documentation:
  - `docs/SPREAD_ENGINE_CARD.md`: Specifications, mechanics, and limitations of `spread-ca-v001`.
  - `docs/DATA_CARD.md`: Catalog of 4 earth observation sources, 30 features, and causal time boundary validation.
  - `docs/VALIDATION_REPORT.md`: Comprehensive test matrix, ML metrics (ROC-AUC 0.8658), and CA determinism verification.
  - `docs/PERFORMANCE_REPORT.md`: Empirical latency baselines for inference (7.69 ms/cell), simulation (331.8 ms), and frontend bundle (447 kB).
  - `docs/SECURITY_REVIEW.md`: Secret scanning audit, CORS policies, SQL injection protection, and container security.
  - `docs/LIMITATIONS.md`: Explicit operational boundaries, sample training scope, and lack of field calibration.
  - `docs/FUTURE_WORK.md`: Research roadmap covering ST-GCN, PINNs, and high-frequency geostationary satellite ingestion.
  - `docs/DEPLOYMENT.md` & `docs/RELEASE_CHECKLIST.md`: Step-by-step production runbooks and verification gates.
  - `DEMO.md`: End-to-end user evaluation script.

### Changed
- Standardized Layer catalog endpoint (`GET /api/v1/layers`) to match frontend contracts.
- Enhanced fallback region service to support human-readable alias lookups.

---

## [0.9.0] - 2026-10-06 (Phase 9 — Operational Dashboard, Analytics & Alerts)

### Added
- Operational Attention Banner displaying real-time high-risk cell counts and active fire summaries.
- Interactive Recharts analytics panels:
  - Risk class distribution histogram (Low, Moderate, High, Very High, Extreme).
  - 12-hour simulation progression chart (cumulative burned area and front advancement velocity).
- Toast notification and user feedback alert system with error boundaries.

---

## [0.8.0] - 2026-10-06 (Phase 8 — Asynchronous Fire Simulation & Celery Integration)

### Added
- Celery worker task execution for long-running 12-hour fire spread simulations.
- Redis-backed task queue and simulation result cache.
- Interactive 12-hour simulation scrubber and animated timeline controls in React GIS dashboard.
- Hourly GeoJSON polygon dissolving and perimeter simplification.

---

## [0.7.0] - 2026-10-06 (Phase 7 — 12-Hour Fire Spread Simulation Engine)

### Added
- Discrete Cellular Automata (CA) propagation engine (`spread-ca-v001`) with Moore 8-neighborhood.
- Environmental spread factor multipliers: wind direction/velocity, terrain slope/aspect, fuel combustibility, and fuel moisture.
- Burned area calculation (hectares) and rate of spread velocity tracking.

---

## [0.6.0] - 2026-10-06 (Phase 6 — Risk Model Integration & GIS Choropleths)

### Added
- Backend integration of `risk-xgboost-v001` with FastAPI endpoint (`GET /api/v1/regions/{id}/risk`).
- Real-time feature matrix extraction from PostGIS environmental tables.
- Interactive 500m risk grid choropleth rendering on Leaflet map with standard color ramp legend.

---

## [0.5.0] - 2026-10-06 (Phase 5 — 24-Hour Fire Risk Machine Learning Model)

### Added
- Machine learning risk engine training pipeline with XGBoost classifier.
- Severe class imbalance calibration (`scale_pos_weight = 999.0`).
- Strict temporal train/validation/test split preventing data leakage.
- Serialized model artifact registry (`models/risk/risk-xgboost-v001`).

---

## [0.4.0] - 2026-10-06 (Phase 4 — Data Ingestion & Preprocessing Pipeline)

### Added
- Multi-source ingestion adapters: NASA FIRMS, ECMWF ERA5 / IMD, CartoDEM / SRTM, and Bhuvan / Sentinel-2.
- Geospatial resampling engine generating standardized 500m × 500m Common Spatial Grid (`EPSG:4326`).
- 30-feature vector extraction across meteorological, topographical, fuel, and historical fire domains.

---

## [0.3.0] - 2026-10-06 (Phase 3 — Frontend GIS Foundation)

### Added
- React 18 + TypeScript + Vite application shell with dark-themed GIS interface.
- Leaflet map integration with custom tile layers, zoom/pan controls, and region boundary rendering.
- State management for active regions, layer toggles, and simulation parameters.

---

## [0.2.0] - 2026-10-06 (Phase 2 — Backend, PostGIS Database & API)

### Added
- FastAPI application structure with versioned `/api/v1` REST endpoints.
- PostgreSQL 16 + PostGIS 3.4 relational spatial schema and Alembic migrations.
- SQLAlchemy ORM models with GeoAlchemy2 spatial geometry fields.
- Reference region seeding scripts and mock/fallback services.

---

## [0.1.0] - 2026-10-05 (Phase 1 — Foundation & Monorepo Setup)

### Added
- Initial monorepo layout (`apps/web`, `services/`, `packages/`, `database/`).
- Architecture specification, data contracts, and REST API specification documents.
- Docker Compose configuration for local development container orchestration.
