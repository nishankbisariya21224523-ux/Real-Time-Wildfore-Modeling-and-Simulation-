"""FastAPI dependencies providing instantiated application services."""

from typing import Optional
from fastapi import Depends
from sqlalchemy.orm import Session

from .database import get_db
from ..services.region_service import RegionService
from ..services.fire_service import FireService
from ..services.risk_service import RiskService
from ..services.simulation_service import SimulationService
from ..services.layer_service import LayerService


def get_region_service(db: Optional[Session] = Depends(get_db)) -> RegionService:
    return RegionService(db=db)


def get_fire_service(db: Optional[Session] = Depends(get_db)) -> FireService:
    return FireService(db=db)


def get_risk_service(db: Optional[Session] = Depends(get_db)) -> RiskService:
    return RiskService(db=db)


def get_simulation_service(db: Optional[Session] = Depends(get_db)) -> SimulationService:
    return SimulationService(db=db)


def get_layer_service() -> LayerService:
    return LayerService()
