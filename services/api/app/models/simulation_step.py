"""SQLAlchemy ORM model for simulation progression timesteps."""

import uuid
from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey, func, Index, UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry

from ..core.database import Base


class SimulationStep(Base):
    """Hourly progression snapshot of fire spread (Hour 0 to 12)."""
    __tablename__ = "simulation_steps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    simulation_id = Column(UUID(as_uuid=True), ForeignKey("simulations.id", ondelete="CASCADE"), nullable=False, index=True)
    step_hour = Column(Integer, nullable=False)
    burned_area_ha = Column(Numeric(10, 2), nullable=False)
    spread_velocity_kmh = Column(Numeric(6, 2), nullable=False)
    spread_direction_deg = Column(Numeric(5, 2), nullable=False)
    intensity_mw = Column(Numeric(8, 2), nullable=False)
    perimeter_geom = Column(Geometry(geometry_type="GEOMETRY", srid=4326), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    simulation = relationship("Simulation", back_populates="steps")

    __table_args__ = (
        CheckConstraint("step_hour >= 0 AND step_hour <= 12", name="chk_sim_step_hour_range"),
        UniqueConstraint("simulation_id", "step_hour", name="uq_sim_step_hour"),
        Index("idx_sim_steps_geom", "perimeter_geom", postgresql_using="gist"),
    )
