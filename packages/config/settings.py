"""Centralized configuration definitions for Forest Fire Platform."""

import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class BasePlatformSettings(BaseSettings):
    """Platform-wide settings shared across services."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_ENV: str = "development"
    APP_NAME: str = "forest-fire-platform"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "dev-secret-key-forest-fire-simulation-change-in-prod-32chars"

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/forest_fire_db"

    # Redis & Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # Spatial defaults
    DEFAULT_GRID_RESOLUTION_METERS: int = 500
    DEFAULT_CRS: str = "EPSG:4326"
