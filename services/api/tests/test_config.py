"""Unit tests for configuration loading."""

from services.api.app.core.config import Settings


def test_settings_defaults():
    """Verify default configuration values."""
    s = Settings()
    assert s.APP_NAME == "forest-fire-platform"
    assert s.API_PORT == 8000
    assert s.API_V1_PREFIX == "/api/v1"
    assert "http://localhost:5173" in s.cors_origin_list
