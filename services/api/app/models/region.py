"""SQLAlchemy ORM model for monitored forest regions."""

import uuid
from sqlalchemy import Column, String, Numeric, DateTime, func, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry

from ..core.database import Base


class Region(Base):
    """Monitored forest division / regional jurisdiction."""
    __tablename__ = "regions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(150), nullable=False)
    state = Column(String(100), nullable=False, index=True)
    boundary = Column(Geometry(geometry_type="POLYGON", srid=4326), nullable=False)
    area_sqkm = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    grid_cells = relationship("GridCell", back_populates="region", cascade="all, delete-orphan")
    risk_predictions = relationship("RiskPrediction", back_populates="region", cascade="all, delete-orphan")
    simulations = relationship("Simulation", back_populates="region", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_regions_boundary", "boundary", postgresql_using="gist"),
    )
