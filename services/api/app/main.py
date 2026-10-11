"""FastAPI Application entrypoint."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .core.config import settings
from .core.logging import logger
from .core.middleware import RequestContextMiddleware
from .core.exceptions import ForestFireAppException
from .core.errors import (
    custom_app_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler,
)
from .core.model_manager import risk_model_manager
from .api.v1.router import api_v1_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context for startup and shutdown hooks."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} [{settings.APP_ENV}]")
    
    # Initialize active risk model in memory
    try:
        loaded = risk_model_manager.load_active_model()
        if loaded:
            logger.info(f"Risk model ready for inference: {risk_model_manager.active_version}")
        else:
            logger.warning("Risk model not available at startup. API operational with MODEL_UNAVAILABLE status.")
    except Exception as e:
        logger.warning(f"Error initializing risk model during startup: {e}")

    yield
    logger.info(f"Shutting down {settings.APP_NAME}")


app = FastAPI(
    title="Forest Fire Risk Prediction & Spread Simulation API",
    description="Enterprise Geospatial AI Platform for 24-hour fire risk and 12-hour spread simulation.",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Request ID & Logging Middleware
app.add_middleware(RequestContextMiddleware)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handlers
app.add_exception_handler(ForestFireAppException, custom_app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Register API Routers under /api/v1
app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["Root"])
async def root():
    """Root metadata discovery endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "api_v1_prefix": settings.API_V1_PREFIX,
    }
