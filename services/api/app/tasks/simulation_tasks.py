"""Celery background tasks for fire spread simulation and batch preprocessing."""

import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from shapely.geometry import shape
from geoalchemy2.shape import from_shape

from ..core.celery_app import celery_app
from ..core.logging import logger
from ..core.database import SessionLocal, check_db_connection
from ..models.simulation import Simulation
from ..models.simulation_step import SimulationStep
from ..repositories.simulation_repository import SimulationRepository

from services.spread_engine.models.inputs import (
    SpreadSimulationInput,
    IgnitionPoint,
    WindCondition,
    TerrainCondition,
)
from services.spread_engine.simulation.engine import SpreadSimulationEngine
from services.spread_engine.common.config import ENGINE_VERSION
from packages.geo_utils.grid import create_500m_cell_polygon


# In-memory execution cache for detached/test execution environments
SIMULATION_CACHE: Dict[str, Dict[str, Any]] = {}


@celery_app.task(name="services.api.app.tasks.simulation_tasks.run_fire_spread_simulation", bind=True)
def run_fire_spread_simulation(self, simulation_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Celery task executing the Phase 7 Cellular Automata fire spread simulation engine,
    persisting hourly steps in PostGIS, and updating lifecycle status.
    """
    task_id = getattr(self.request, "id", None) if hasattr(self, "request") and self.request else None
    logger.info(f"Starting async simulation task {task_id or 'local'} for job: {simulation_id}")
    start_time = time.time()

    # Unpack parameters
    lat = float(payload["ignition_lat"])
    lon = float(payload["ignition_lon"])
    duration_hours = int(payload.get("duration_hours", 12))
    wind_speed = float(payload.get("wind_speed_ms", 7.5))
    wind_dir = float(payload.get("wind_direction_deg", 225.0))
    fuel_type = str(payload.get("fuel_type", "CONIFER_HIGH_FLAMMABILITY"))
    slope_deg = float(payload.get("slope_deg", 0.0))
    aspect_deg = float(payload.get("aspect_deg", 180.0))

    # Initialize cache record
    SIMULATION_CACHE[simulation_id] = {
        "simulation_id": simulation_id,
        "status": "RUNNING",
        "duration_hours": duration_hours,
        "ignition": {"latitude": lat, "longitude": lon},
        "created_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None,
        "total_area_burned_ha": 0.0,
        "peak_spread_velocity_kmh": 0.0,
        "dominant_spread_direction_deg": (wind_dir + 180.0) % 360.0,
        "engine_version": ENGINE_VERSION,
        "timesteps": [],
        "steps_features": [],
        "error": None,
    }

    is_db_connected = check_db_connection() == "connected"
    db = SessionLocal() if (is_db_connected and SessionLocal is not None) else None
    repo = SimulationRepository(db) if db is not None else None

    # Step 1: Transition database status to RUNNING
    if repo is not None and db is not None:
        try:
            repo.update_simulation_status(simulation_id, status="RUNNING")
            db.commit()
        except Exception as e:
            db.rollback()
            logger.warning(f"Could not update status to RUNNING in DB for {simulation_id}: {e}")

    # Update Celery state if running in active Celery worker context
    if task_id and hasattr(self, "update_state"):
        try:
            self.update_state(state="RUNNING", meta={"simulation_id": simulation_id, "progress_pct": 10.0})
        except Exception as e:
            logger.debug(f"Could not update Celery task state: {e}")

    try:
        # Step 2: Invoke Phase 7 Cellular Automata Spread Engine
        engine = SpreadSimulationEngine()
        sim_input = SpreadSimulationInput(
            simulation_id=str(simulation_id),
            ignition=IgnitionPoint(lat=lat, lon=lon),
            duration_hours=duration_hours,
            wind=WindCondition(speed_ms=wind_speed, direction_deg=wind_dir),
            terrain=TerrainCondition(
                slope_deg=slope_deg,
                aspect_deg=aspect_deg,
                fuel_type=fuel_type,
            ),
            deterministic=True,
        )

        sim_result = engine.execute(sim_input)
        elapsed_sec = round(time.time() - start_time, 3)
        logger.info(
            f"Phase 7 engine executed in {elapsed_sec}s for job {simulation_id}: "
            f"burned {sim_result.total_area_burned_ha} ha, peak vel {sim_result.peak_spread_velocity_kmh} km/h"
        )

        # Step 3: Prepare Hour 0 (Initial Ignition State)
        hour_0_boundary = create_500m_cell_polygon(center_lat=lat, center_lon=lon, resolution_meters=500.0)
        hour_0_feature = {
            "type": "Feature",
            "id": f"sim-{simulation_id}-step-0",
            "geometry": hour_0_boundary,
            "properties": {
                "step_hour": 0,
                "step_number": 0,
                "elapsed_minutes": 0,
                "burned_area_ha": 0.0,
                "cumulative_burned_area_ha": 0.0,
                "spread_velocity_kmh": 0.0,
                "spread_direction_deg": round((wind_dir + 180.0) % 360.0, 1),
                "intensity_mw": 4.0,
                "active_front_cells_count": 1,
            },
        }

        all_features = [hour_0_feature]
        all_timeline_items = []

        # Step 4: Prepare Hours 1 through duration_hours
        db_steps = []
        if repo is not None and db is not None:
            try:
                db_steps.append(
                    SimulationStep(
                        id=uuid.uuid4(),
                        simulation_id=uuid.UUID(str(simulation_id)),
                        step_hour=0,
                        burned_area_ha=0.0,
                        spread_velocity_kmh=0.0,
                        spread_direction_deg=round((wind_dir + 180.0) % 360.0, 1),
                        intensity_mw=4.0,
                        perimeter_geom=from_shape(shape(hour_0_boundary), srid=4326),
                    )
                )
            except Exception as e:
                logger.debug(f"Could not construct hour 0 DB step: {e}")

        for ts in sim_result.timesteps:
            ts_feature = {
                "type": "Feature",
                "id": f"sim-{simulation_id}-step-{ts.step_hour}",
                "geometry": ts.boundary_polygon,
                "properties": {
                    "step_hour": ts.step_hour,
                    "step_number": ts.step_hour,
                    "elapsed_minutes": ts.step_hour * 60,
                    "burned_area_ha": ts.burned_area_ha,
                    "cumulative_burned_area_ha": ts.burned_area_ha,
                    "spread_velocity_kmh": ts.spread_velocity_kmh,
                    "spread_direction_deg": ts.spread_direction_deg,
                    "intensity_mw": ts.intensity_mw,
                    "active_front_cells_count": ts.active_burning_cells,
                },
            }
            all_features.append(ts_feature)
            all_timeline_items.append(
                {
                    "step_hour": ts.step_hour,
                    "burned_area_ha": ts.burned_area_ha,
                    "spread_velocity_kmh": ts.spread_velocity_kmh,
                    "spread_direction_deg": ts.spread_direction_deg,
                    "intensity_mw": ts.intensity_mw,
                }
            )

            if repo is not None and db is not None:
                try:
                    db_steps.append(
                        SimulationStep(
                            id=uuid.uuid4(),
                            simulation_id=uuid.UUID(str(simulation_id)),
                            step_hour=ts.step_hour,
                            burned_area_ha=ts.burned_area_ha,
                            spread_velocity_kmh=ts.spread_velocity_kmh,
                            spread_direction_deg=ts.spread_direction_deg,
                            intensity_mw=ts.intensity_mw,
                            perimeter_geom=from_shape(shape(ts.boundary_polygon), srid=4326),
                        )
                    )
                except Exception as e:
                    logger.debug(f"Could not construct hour {ts.step_hour} DB step: {e}")

        # Step 5: Persist steps in PostGIS and update status to COMPLETED
        now_iso = datetime.now(timezone.utc).isoformat()
        if repo is not None and db is not None and db_steps:
            try:
                repo.delete_steps(simulation_id)
                repo.save_steps(db_steps)
                repo.update_simulation_status(
                    simulation_id,
                    status="COMPLETED",
                    total_area_burned_ha=sim_result.total_area_burned_ha,
                    model_version=sim_result.engine_version,
                    completed_at=datetime.now(timezone.utc),
                )
                db.commit()
                logger.info(f"Persisted {len(db_steps)} timesteps in PostGIS for job {simulation_id}")
            except Exception as e:
                db.rollback()
                logger.warning(f"Failed to persist timesteps to DB: {e}")

        # Update cache
        dominant_dir = sim_result.timesteps[-1].spread_direction_deg if sim_result.timesteps else (wind_dir + 180.0) % 360.0
        SIMULATION_CACHE[simulation_id].update(
            {
                "status": "COMPLETED",
                "completed_at": now_iso,
                "total_area_burned_ha": sim_result.total_area_burned_ha,
                "peak_spread_velocity_kmh": sim_result.peak_spread_velocity_kmh,
                "dominant_spread_direction_deg": dominant_dir,
                "timesteps": all_timeline_items,
                "steps_features": all_features,
            }
        )

        return {
            "simulation_id": simulation_id,
            "status": "COMPLETED",
            "total_area_burned_ha": sim_result.total_area_burned_ha,
            "peak_spread_velocity_kmh": sim_result.peak_spread_velocity_kmh,
            "timesteps_count": len(all_timeline_items),
            "processed_by": "celery_worker" if task_id else "local_engine",
            "runtime_seconds": elapsed_sec,
        }

    except Exception as exc:
        logger.error(f"Simulation execution failed for job {simulation_id}: {exc}", exc_info=True)
        if repo is not None and db is not None:
            try:
                repo.update_simulation_status(simulation_id, status="FAILED")
                db.commit()
            except Exception:
                db.rollback()

        if simulation_id in SIMULATION_CACHE:
            SIMULATION_CACHE[simulation_id]["status"] = "FAILED"
            SIMULATION_CACHE[simulation_id]["error"] = str(exc)
        raise exc

    finally:
        if db is not None:
            db.close()


@celery_app.task(name="services.api.app.tasks.simulation_tasks.ping_task")
def ping_task() -> str:
    """Simple verification task to confirm worker connectivity and discovery."""
    return "pong"
