"""Repository for region database queries and spatial filters."""

import uuid
from typing import List, Optional, Tuple, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.region import Region
from ..models.grid_cell import GridCell
from ..schemas.geojson import to_geojson_geometry
from .base_repository import BaseRepository


class RegionRepository(BaseRepository[Region]):
    """Database repository for regions."""

    def __init__(self, db: Session):
        super().__init__(db, Region)

    def list_regions(self, state: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[Region]:
        query = self.db.query(Region)
        if state:
            query = query.filter(func.lower(Region.state) == state.lower())
        return query.order_by(Region.name.asc()).offset(offset).limit(limit).all()

    def count_regions(self, state: Optional[str] = None) -> int:
        query = self.db.query(func.count(Region.id))
        if state:
            query = query.filter(func.lower(Region.state) == state.lower())
        return query.scalar() or 0

    def get_by_id_or_code(self, identifier: str) -> Optional[Region]:
        # Try UUID parse
        try:
            val_uuid = uuid.UUID(identifier)
            reg = self.db.query(Region).filter(Region.id == val_uuid).first()
            if reg:
                return reg
        except (ValueError, AttributeError):
            pass

        # Try region code
        return self.db.query(Region).filter(Region.code == identifier).first()

    def count_grid_cells(self, region_id: Any) -> int:
        return self.db.query(func.count(GridCell.id)).filter(GridCell.region_id == region_id).scalar() or 0
