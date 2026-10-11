# Release & Production Readiness Checklist

## 1. Codebase & Dependency Verification

- [x] Python virtual environment cleanly builds with zero dependency conflicts.
- [x] Node.js dependencies (`npm ci`) install cleanly with zero peer dependency errors.
- [x] Monorepo imports audited: zero circular dependencies across `services.api`, `services.data_pipeline`, `services.risk_engine`, and `services.spread_engine`.
- [x] Static type checking and bundle build pass cleanly in `apps/web` (`npm run build`).

---

## 2. Test Execution & Coverage

- [x] Full Pytest suite passes: 141 of 141 tests passing.
- [x] Full Vitest suite passes: 39 of 39 tests passing across 11 test suites.
- [x] Integration tests pass: database models, relationships, and docker-compose configurations.
- [x] Edge case handling tested: missing weather parameters, database disconnects, Redis disconnects.

---

## 3. Data Integrity & Machine Learning Governance

- [x] Data leakage audited: Strict temporal boundary at $T_{\text{ref}}$ enforced; no lookahead features in training or inference.
- [x] ML Model Artifact: `models/risk/risk-xgboost-v001` serialized with complete `metadata.json`.
- [x] ML Model Performance: ROC-AUC = 0.8658, Recall = 0.8438 on test split.
- [x] Extreme class imbalance accounted for: `scale_pos_weight = 999.0`.
- [x] Spread Engine Determinism: Identical outputs verified across multiple simulation runs on 40×40 test grids.

---

## 4. Security & Hardening

- [x] Automated secret scanning completed: zero hardcoded tokens, passwords, or private keys.
- [x] Production environment template `.env.production.example` prepared with strong dummy placeholders.
- [x] SQL injection prevention: SQLAlchemy parameterized queries and GeoAlchemy2 bindings utilized exclusively.
- [x] Cross-Origin Resource Sharing (CORS) configured and restrictable to authorized domains.
- [x] Input sanitization: Pydantic v2 schemas reject malformed bodies with HTTP 422.

---

## 5. Performance & Operational SLAs

- [x] Risk model single-cell inference: 7.69 ms (target: < 50 ms).
- [x] Risk model batch 1,000-cell inference: 67.50 ms (target: < 500 ms).
- [x] 12-hour Cellular Automata simulation (40×40 grid): 331.80 ms (target: < 2.0 s).
- [x] Frontend bundle footprint: 447.7 kB uncompressed / 127 kB gzipped (target: < 1.0 MB).
- [x] API health and metadata endpoints respond in < 60 ms.

---

## 6. Documentation & Release Collateral

- [x] `CHANGELOG.md` documents all features from v0.1.0 through v1.0.0.
- [x] `DEMO.md` provides complete step-by-step walkthrough script.
- [x] Model Cards created: `docs/SPREAD_ENGINE_CARD.md` and `docs/DATA_CARD.md`.
- [x] Reports generated: `docs/VALIDATION_REPORT.md`, `docs/PERFORMANCE_REPORT.md`, `docs/SECURITY_REVIEW.md`.
- [x] Operational transparency: `docs/LIMITATIONS.md` and `docs/FUTURE_WORK.md`.
- [x] Deployment instructions: `docs/DEPLOYMENT.md`.
