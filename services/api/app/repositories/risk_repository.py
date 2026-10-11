"""Repository for 24-hour fire risk predictions with PostGIS spatial join support."""

import uuid
from datetime import date
from typing import List, Optional, Any, Dict, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models.risk_prediction import RiskPrediction
from ..models.grid_cell import GridCell
from .base_repository import BaseRepository


class RiskRepository(BaseRepository[RiskPrediction]):
    """Database repository for risk predictions and spatial cell joins."""

    def __init__(self, db: Session):
        super().__init__(db, RiskPrediction)

    def get_predictions_with_cells(
        self,
        region_id: Any,
        target_date: Optional[date] = None,
        min_risk: Optional[str] = None,
        model_version: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Tuple[RiskPrediction, GridCell]]:
        """
        Query risk predictions joined with their corresponding GridCell geometry.
        """
        query = (
            self.db.query(RiskPrediction, GridCell)
            .join(GridCell, RiskPrediction.grid_cell_id == GridCell.id)
            .filter(RiskPrediction.region_id == region_id)
        )

        if target_date:
            query = query.filter(RiskPrediction.valid_for_date == target_date)

        if model_version:
            query = query.filter(RiskPrediction.model_version == model_version)

        if min_risk:
            risk_order = {"LOW": 0.0, "MODERATE": 0.25, "HIGH": 0.50, "EXTREME": 0.75}
            threshold = risk_order.get(min_risk.upper(), 0.0)
            query = query.filter(RiskPrediction.risk_probability >= threshold)

        query = query.order_by(RiskPrediction.risk_probability.desc())
        if limit:
            query = query.limit(limit)

        return query.all()

    def get_predictions_by_region(
        self,
        region_id: Any,
        target_date: Optional[date] = None,
        min_risk: Optional[str] = None,
        limit: int = 500,
    ) -> List[RiskPrediction]:
        """Fetch prediction records by region, optionally filtered by date and threshold."""
        query = self.db.query(RiskPrediction).filter(RiskPrediction.region_id == region_id)

        if target_date:
            query = query.filter(RiskPrediction.valid_for_date == target_date)

        if min_risk:
            risk_order = {"LOW": 0.0, "MODERATE": 0.25, "HIGH": 0.50, "EXTREME": 0.75}
            threshold = risk_order.get(min_risk.upper(), 0.0)
            query = query.filter(RiskPrediction.risk_probability >= threshold)

        return query.order_by(RiskPrediction.risk_probability.desc()).limit(limit).all()

    def count_predictions_for_date(
        self,
        region_id: Any,
        target_date: date,
        model_version: Optional[str] = None,
    ) -> int:
        """Count existing predictions for idempotency verification."""
        query = self.db.query(func.count(RiskPrediction.id)).filter(
            RiskPrediction.region_id == region_id,
            RiskPrediction.valid_for_date == target_date,
        )
        if model_version:
            query = query.filter(RiskPrediction.model_version == model_version)
        return query.scalar() or 0

    def delete_predictions_for_date(
        self,
        region_id: Any,
        target_date: date,
        model_version: Optional[str] = None,
    ) -> int:
        """Remove existing predictions to support force_recompute replacement."""
        query = self.db.query(RiskPrediction).filter(
            RiskPrediction.region_id == region_id,
            RiskPrediction.valid_for_date == target_date,
        )
        if model_version:
            query = query.filter(RiskPrediction.model_version == model_version)
        count = query.delete(synchronize_session="fetch")
        self.db.commit()
        return count

    def save_predictions_batch(self, predictions: List[RiskPrediction]) -> None:
        """Persist a batch of RiskPrediction records atomically."""
        if not predictions:
            return
        self.db.add_all(predictions)
        self.db.commit()
