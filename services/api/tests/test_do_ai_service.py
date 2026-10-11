"""Tests for DigitalOcean AI Service and /api/v1/ai endpoints."""
import asyncio
import pytest
from fastapi.testclient import TestClient

from services.api.app.main import app
from services.api.app.services.do_ai_service import DigitalOceanAIService

client = TestClient(app)


def test_do_ai_service_heuristic_fallback():
    """Verify that DigitalOceanAIService falls back to deterministic heuristic without API key."""
    service = DigitalOceanAIService(api_key="")
    assert not service.is_configured

    briefing = asyncio.run(
        service.generate_incident_briefing(
            region_name="Garhwal Division",
            fire_danger_index=85.0,
            temperature_c=39.0,
            relative_humidity=11.5,
            wind_speed_kmh=52.0,
            wind_direction_deg=225.0,
            active_hotspots=12,
            slope_pct=25.0,
            fuel_type="Mixed Conifer",
        )
    )

    assert briefing["region_name"] == "Garhwal Division"
    assert briefing["threat_level"] == "CRITICAL / EXTREME"
    assert briefing["fire_danger_index"] == 85.0
    assert "MANDATORY EVACUATION" in briefing["evacuation_directive"]
    assert len(briefing["tactical_actions"]) >= 3
    assert briefing["provider"] == "digitalocean_genai_heuristic_engine"


def test_ai_status_endpoint():
    """Verify GET /api/v1/ai/status returns 200 and valid DigitalOcean AI status."""
    response = client.get("/api/v1/ai/status")
    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "DigitalOcean GenAI"
    assert "is_configured" in data
    assert "default_model" in data
    assert "status" in data


def test_ai_advisory_endpoint():
    """Verify POST /api/v1/ai/advisory generates incident briefing successfully."""
    payload = {
        "region_name": "Garhwal Division",
        "fire_danger_index": 72.0,
        "temperature_c": 34.0,
        "relative_humidity": 18.0,
        "wind_speed_kmh": 32.0,
        "wind_direction_deg": 190.0,
        "active_hotspots": 4,
        "slope_pct": 15.0,
        "fuel_type": "Chaparral / Dry Grass",
        "evacuation_status": "ADVISORY",
    }
    response = client.post("/api/v1/ai/advisory", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["region_name"] == "Garhwal Division"
    assert data["threat_level"] in ["HIGH", "CRITICAL / EXTREME"]
    assert len(data["tactical_actions"]) > 0
    assert "summary" in data
    assert "provider" in data
