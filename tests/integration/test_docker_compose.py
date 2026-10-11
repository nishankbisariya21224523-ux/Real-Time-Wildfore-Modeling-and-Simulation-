"""Validation test for docker-compose.yml and deployment configurations."""

import os
from pathlib import Path


def test_docker_compose_structure():
    """Verify docker-compose.yml contains all 5 required services and references valid files."""
    repo_root = Path(__file__).resolve().parent.parent.parent
    compose_path = repo_root / "docker-compose.yml"
    assert compose_path.exists(), "docker-compose.yml must exist at repository root"

    content = compose_path.read_text(encoding="utf-8")

    # Verify all 5 required services are declared
    required_services = ["postgres:", "redis:", "api:", "celery_worker:", "web:"]
    for svc in required_services:
        assert svc in content, f"Service '{svc}' must be declared in docker-compose.yml"

    # Verify networks and volumes
    assert "forest_fire_network:" in content, "Shared network must be declared"
    assert "postgres_data:" in content, "Postgres volume must be declared"
    assert "redis_data:" in content, "Redis volume must be declared"

    # Verify referenced files on disk
    assert (repo_root / "services" / "api" / "Dockerfile").exists(), "API Dockerfile must exist"
    assert (repo_root / "apps" / "web" / "Dockerfile").exists(), "Web Dockerfile must exist"
    assert (repo_root / "database" / "schema" / "initial_schema.sql").exists(), "Initial SQL schema must exist"
    assert (repo_root / "database" / "seed" / "sample_seed.sql").exists(), "Sample seed SQL must exist"


def test_environment_template():
    """Verify .env.example contains all required configuration keys."""
    repo_root = Path(__file__).resolve().parent.parent.parent
    env_example = repo_root / ".env.example"
    assert env_example.exists(), ".env.example must exist"

    content = env_example.read_text(encoding="utf-8")
    required_keys = [
        "APP_ENV",
        "DATABASE_URL",
        "REDIS_URL",
        "CELERY_BROKER_URL",
        "VITE_API_BASE_URL",
        "DEFAULT_GRID_RESOLUTION_METERS",
    ]
    for key in required_keys:
        assert key in content, f"Key '{key}' must be documented in .env.example"
