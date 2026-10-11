"""Repository for fire spread simulation sessions and timesteps."""

import uuid
from datetime import datetime, timezone
from typing import List, Optional, Any
from sqlalchemy.orm import Session
from ..models.simulation import Simulation
from ..models.simulation_step import SimulationStep
from .base_repository import BaseRepository


class SimulationRepository(BaseRepository[Simulation]):
    """Database repository for simulations."""

    def __init__(self, db: Session):
        super().__init__(db, Simulation)

    def get_by_id(self, simulation_id: Any) -> Optional[Simulation]:
        try:
            sim_uuid = uuid.UUID(str(simulation_id))
            return self.db.query(Simulation).filter(Simulation.id == sim_uuid).first()
        except (ValueError, AttributeError):
            return None

    def get_steps(self, simulation_id: Any) -> List[SimulationStep]:
        try:
            sim_uuid = uuid.UUID(str(simulation_id))
            return (
                self.db.query(SimulationStep)
                .filter(SimulationStep.simulation_id == sim_uuid)
                .order_by(SimulationStep.step_hour.asc())
                .all()
            )
        except (ValueError, AttributeError):
            return []

    def get_step(self, simulation_id: Any, hour: int) -> Optional[SimulationStep]:
        try:
            sim_uuid = uuid.UUID(str(simulation_id))
            return (
                self.db.query(SimulationStep)
                .filter(SimulationStep.simulation_id == sim_uuid, SimulationStep.step_hour == hour)
                .first()
            )
        except (ValueError, AttributeError):
            return None

    def add_step(self, step: SimulationStep) -> SimulationStep:
        self.db.add(step)
        self.db.flush()
        return step

    def save_steps(self, steps: List[SimulationStep]) -> List[SimulationStep]:
        """Save a list of simulation timesteps in batch."""
        for step in steps:
            self.db.add(step)
        self.db.flush()
        return steps

    def delete_steps(self, simulation_id: Any) -> int:
        """Remove any existing steps for the simulation."""
        try:
            sim_uuid = uuid.UUID(str(simulation_id))
            count = self.db.query(SimulationStep).filter(SimulationStep.simulation_id == sim_uuid).delete()
            self.db.flush()
            return count
        except (ValueError, AttributeError):
            return 0

    def update_simulation_status(
        self,
        simulation_id: Any,
        status: str,
        total_area_burned_ha: Optional[float] = None,
        model_version: Optional[str] = None,
        completed_at: Optional[datetime] = None,
    ) -> Optional[Simulation]:
        sim = self.get_by_id(simulation_id)
        if sim is None:
            return None
        sim.status = status
        if total_area_burned_ha is not None:
            sim.total_area_burned_ha = total_area_burned_ha
        if model_version is not None:
            sim.model_version = model_version
        if completed_at is not None:
            sim.completed_at = completed_at
        elif status == "COMPLETED" and sim.completed_at is None:
            sim.completed_at = datetime.now(timezone.utc)
        self.db.flush()
        return sim
