"""System health check endpoint."""

from datetime import datetime, timezone
from fastapi import APIRouter, status
from ...core.config import settings
from ...core.database import check_db_connection
from ...core.celery_app import check_celery_broker
from ...schemas.common import HealthResponse, ServiceStatus

from ...core.model_manager import risk_model_manager

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="System Health & Dependency Connectivity Check"
)
async def get_health() -> HealthResponse:
    """
    Verify API service operational status, software version, environment,
    and connectivity to backing infrastructure (PostGIS, Redis, Celery).
    Distinguishes application operational status from dependency health.
    """
    db_status = check_db_connection()
    celery_status = check_celery_broker()
    if not risk_model_manager.is_available:
        risk_model_manager.load_active_model()
    model_status = "available" if risk_model_manager.is_available else "unavailable"


    overall_db = "healthy" if db_status == "connected" else ("unhealthy" if db_status == "unreachable" else "not_configured")

    return HealthResponse(
        status="healthy",
        service=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.APP_ENV,
        timestamp=datetime.now(timezone.utc).isoformat(),
        database=overall_db,
        services=ServiceStatus(
            database=db_status,
            redis=celery_status,
            celery_broker=celery_status,
            risk_model=model_status,
        ),
    )

