"""SQLAlchemy ORM model for grid cell environmental observations."""

import uuid
from sqlalchemy import Column, Numeric, DateTime, ForeignKey, func, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..core.database import Base


class EnvironmentalObservation(Base):
    """Meteorological, vegetation, and fuel moisture metrics on a grid cell."""
    __tablename__ = "environmental_observations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    grid_cell_id = Column(UUID(as_uuid=True), ForeignKey("grid_cells.id", ondelete="CASCADE"), nullable=False, index=True)
    observation_time = Column(DateTime(timezone=True), nullable=False, index=True)
    temperature_c = Column(Numeric(5, 2), nullable=True)
    relative_humidity_pct = Column(Numeric(5, 2), nullable=True)
    wind_speed_ms = Column(Numeric(6, 2), nullable=True)
    wind_direction_deg = Column(Numeric(5, 2), nullable=True)
    precipitation_mm = Column(Numeric(7, 2), nullable=True)
    ndvi = Column(Numeric(4, 3), nullable=True)
    ndwi = Column(Numeric(4, 3), nullable=True)
    fwi = Column(Numeric(6, 2), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    grid_cell = relationship("GridCell", back_populates="environmental_observations")

    __table_args__ = (
        UniqueConstraint("grid_cell_id", "observation_time", name="uq_cell_obs_time"),
        Index("idx_env_obs_cell_time", "grid_cell_id", "observation_time"),
    )
