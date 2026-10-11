"""SQLAlchemy ORM model for 24-hour fire risk predictions."""

import uuid
from sqlalchemy import Column, String, Numeric, Date, DateTime, ForeignKey, func, Index, UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..core.database import Base


class RiskPrediction(Base):
    """Pre-computed 24-hour fire susceptibility probability and class."""
    __tablename__ = "risk_predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    grid_cell_id = Column(UUID(as_uuid=True), ForeignKey("grid_cells.id", ondelete="CASCADE"), nullable=False, index=True)
    region_id = Column(UUID(as_uuid=True), ForeignKey("regions.id", ondelete="CASCADE"), nullable=False, index=True)
    valid_for_date = Column(Date, nullable=False, index=True)
    risk_probability = Column(Numeric(4, 3), nullable=False)
    risk_class = Column(String(20), nullable=False)
    model_version = Column(String(50), nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    grid_cell = relationship("GridCell", back_populates="risk_predictions")
    region = relationship("Region", back_populates="risk_predictions")

    __table_args__ = (
        CheckConstraint("risk_probability >= 0.0 AND risk_probability <= 1.0", name="chk_risk_prob_range"),
        CheckConstraint("risk_class IN ('LOW', 'MODERATE', 'HIGH', 'EXTREME')", name="chk_risk_class_valid"),
        UniqueConstraint("grid_cell_id", "valid_for_date", "model_version", name="uq_cell_risk_pred"),
        Index("idx_risk_pred_region_date", "region_id", "valid_for_date"),
    )
