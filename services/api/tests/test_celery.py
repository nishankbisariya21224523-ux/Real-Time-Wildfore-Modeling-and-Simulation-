"""Unit tests for Celery task discovery and configuration."""

from services.api.app.core.celery_app import celery_app


def test_celery_task_discovery():
    """Verify that Celery worker discovers and registers simulation tasks."""
    celery_app.loader.import_default_modules()
    registered = list(celery_app.tasks.keys())
    assert "services.api.app.tasks.simulation_tasks.run_fire_spread_simulation" in registered
    assert "services.api.app.tasks.simulation_tasks.ping_task" in registered
