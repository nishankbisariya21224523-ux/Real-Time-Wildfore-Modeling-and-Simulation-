"""Master router aggregating all API v1 domain routers."""

from fastapi import APIRouter
from .health import router as health_router
from .regions import router as regions_router
from .fires import router as fires_router
from .risk import router as risk_router
from .simulations import router as simulations_router
from .layers import router as layers_router

api_v1_router = APIRouter()

# Register sub-routers
api_v1_router.include_router(health_router)
api_v1_router.include_router(regions_router)
api_v1_router.include_router(fires_router)
api_v1_router.include_router(risk_router)
api_v1_router.include_router(simulations_router)
api_v1_router.include_router(layers_router)
