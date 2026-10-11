"""SQLAlchemy ORM model for active and historical fire events."""

import uuid
from sqlalchemy import Column, String, Numeric, Boolean, DateTime, ForeignKey, func, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry

from ..core.database import Base


class FireEvent(Base):
    """Satellite thermal detection or ground active fire event."""
    __tablename__ = "fire_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    grid_cell_id = Column(UUID(as_uuid=True), ForeignKey("grid_cells.id", ondelete="SET NULL"), nullable=True, index=True)
    source = Column(String(50), nullable=False, index=True)  # MODIS, VIIRS, INSAT_3D
    detected_at = Column(DateTime(timezone=True), nullable=False, index=True)
    brightness_temp_k = Column(Numeric(6, 2), nullable=True)
    frp_mw = Column(Numeric(8, 2), nullable=True)
    confidence_pct = Column(Numeric(5, 2), nullable=False)
    location = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    grid_cell = relationship("GridCell", back_populates="fire_events")

    __table_args__ = (
        Index("idx_fire_events_location", "location", postgresql_using="gist"),
        Index("idx_fire_events_detected_at", "detected_at"),
    )
