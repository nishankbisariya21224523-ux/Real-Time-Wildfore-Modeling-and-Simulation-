"""SQLAlchemy ORM model for discrete 500m spatial grid cells."""

import uuid
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey, func, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry

from ..core.database import Base


class GridCell(Base):
    """Discrete 500m x 500m spatial partition within a region."""
    __tablename__ = "grid_cells"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    region_id = Column(UUID(as_uuid=True), ForeignKey("regions.id", ondelete="CASCADE"), nullable=False, index=True)
    cell_code = Column(String(100), unique=True, nullable=False, index=True)
    centroid = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    geometry = Column(Geometry(geometry_type="POLYGON", srid=4326), nullable=False)
    resolution_meters = Column(Integer, default=500, nullable=False)
    elevation_m = Column(Numeric(8, 2), nullable=True)
    slope_deg = Column(Numeric(5, 2), nullable=True)
    aspect_deg = Column(Numeric(5, 2), nullable=True)
    fuel_type = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    region = relationship("Region", back_populates="grid_cells")
    environmental_observations = relationship("EnvironmentalObservation", back_populates="grid_cell", cascade="all, delete-orphan")
    risk_predictions = relationship("RiskPrediction", back_populates="grid_cell", cascade="all, delete-orphan")
    fire_events = relationship("FireEvent", back_populates="grid_cell")

    __table_args__ = (
        Index("idx_grid_cells_geom", "geometry", postgresql_using="gist"),
        Index("idx_grid_cells_centroid", "centroid", postgresql_using="gist"),
    )
