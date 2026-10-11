"""Repository for active and historical fire events."""

import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.fire_event import FireEvent
from ..models.region import Region
from ..models.grid_cell import GridCell
from .base_repository import BaseRepository


class FireRepository(BaseRepository[FireEvent]):
    """Database repository for fire events."""

    def __init__(self, db: Session):
        super().__init__(db, FireEvent)

    def get_active_fires(
        self,
        region_id: Optional[str] = None,
        hours: int = 24,
        min_confidence: float = 50.0,
        limit: int = 100
    ) -> List[FireEvent]:
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        query = self.db.query(FireEvent).filter(
            FireEvent.is_active == True,
            FireEvent.detected_at >= cutoff_time,
            FireEvent.confidence_pct >= min_confidence
        )

        if region_id:
            # Spatial filter using PostGIS ST_Intersects if region exists
            try:
                reg_uuid = uuid.UUID(region_id)
                region = self.db.query(Region).filter(Region.id == reg_uuid).first()
            except (ValueError, AttributeError):
                region = self.db.query(Region).filter(Region.code == region_id).first()

            if region is not None:
                query = query.filter(func.ST_Intersects(FireEvent.location, region.boundary))

        return query.order_by(FireEvent.detected_at.desc()).limit(limit).all()
