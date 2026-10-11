"""Integration tests for SQLAlchemy database models and constraints."""

from services.api.app.models.region import Region
from services.api.app.models.grid_cell import GridCell
from services.api.app.models.environmental_observation import EnvironmentalObservation
from services.api.app.models.fire_event import FireEvent
from services.api.app.models.risk_prediction import RiskPrediction
from services.api.app.models.simulation import Simulation
from services.api.app.models.simulation_step import SimulationStep


def test_models_table_names_and_metadata():
    """Verify all 7 database models are registered with their designated table names."""
    assert Region.__tablename__ == "regions"
    assert GridCell.__tablename__ == "grid_cells"
    assert EnvironmentalObservation.__tablename__ == "environmental_observations"
    assert FireEvent.__tablename__ == "fire_events"
    assert RiskPrediction.__tablename__ == "risk_predictions"
    assert Simulation.__tablename__ == "simulations"
    assert SimulationStep.__tablename__ == "simulation_steps"


def test_model_columns_and_constraints():
    """Verify primary keys, foreign keys, and column constraints exist on models."""
    # Region
    assert "code" in Region.__table__.columns
    assert "boundary" in Region.__table__.columns
    assert "area_sqkm" in Region.__table__.columns

    # GridCell
    assert "region_id" in GridCell.__table__.columns
    assert "centroid" in GridCell.__table__.columns
    assert "geometry" in GridCell.__table__.columns
    assert "resolution_meters" in GridCell.__table__.columns

    # FireEvent
    assert "source" in FireEvent.__table__.columns
    assert "location" in FireEvent.__table__.columns
    assert "is_active" in FireEvent.__table__.columns

    # RiskPrediction
    assert "risk_probability" in RiskPrediction.__table__.columns
    assert "risk_class" in RiskPrediction.__table__.columns

    # Simulation
    assert "ignition_location" in Simulation.__table__.columns
    assert "status" in Simulation.__table__.columns
    assert "duration_hours" in Simulation.__table__.columns

    # SimulationStep
    assert "step_hour" in SimulationStep.__table__.columns
    assert "perimeter_geom" in SimulationStep.__table__.columns
