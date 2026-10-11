"""SQLAlchemy ORM model for 12-hour fire spread simulation sessions."""

import uuid
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey, func, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry

from ..core.database import Base


class Simulation(Base):
    """Execution session for a 12-hour Cellular Automata fire spread simulation."""
    __tablename__ = "simulations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    region_id = Column(UUID(as_uuid=True), ForeignKey("regions.id", ondelete="CASCADE"), nullable=False, index=True)
    ignition_location = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    ignition_time = Column(DateTime(timezone=True), nullable=False)
    duration_hours = Column(Integer, default=12, nullable=False)
    status = Column(String(20), default="QUEUED", nullable=False, index=True)
    total_area_burned_ha = Column(Numeric(10, 2), default=0.0, nullable=False)
    model_version = Column(String(50), default="ca-baseline-v1.0", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    region = relationship("Region", back_populates="simulations")
    steps = relationship("SimulationStep", back_populates="simulation", cascade="all, delete-orphan", order_by="SimulationStep.step_hour")

    __table_args__ = (
        CheckConstraint(
            "status IN ('QUEUED', 'PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED')",
            name="chk_simulation_status"
        ),
        Index("idx_simulations_ignition", "ignition_location", postgresql_using="gist"),
    )
