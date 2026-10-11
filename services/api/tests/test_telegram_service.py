"""Tests for Telegram Emergency Wildfire Civil Alert Service & API endpoints."""
import asyncio
from fastapi.testclient import TestClient

from services.api.app.main import app
from services.api.app.services.telegram_service import TelegramService

client = TestClient(app)


def test_telegram_format_message():
    """Verify emergency alert message formatting contains key safety directives."""
    service = TelegramService(bot_token="", chat_id="")
    msg = service.format_alert_message(
        region_name="Garhwal Himalaya",
        threat_level="CRITICAL / EXTREME",
        fire_danger_index=88.5,
        evacuation_status="MANDATORY EVACUATION",
        custom_note="NH-58 roadway blocked due to heavy smoke downwind.",
    )

    assert "EMERGENCY WILDFIRE CIVIL ALERT" in msg
    assert "GARHWAL HIMALAYA" in msg
    assert "CRITICAL / EXTREME" in msg
    assert "MANDATORY EVACUATION" in msg
    assert "NH-58 roadway blocked" in msg
    assert "112 / 1077" in msg


def test_telegram_broadcast_simulation_mode():
    """Verify fallback simulation mode works without API keys configured."""
    service = TelegramService(bot_token="", chat_id="")
    result = asyncio.run(
        service.broadcast_alert(
            region_name="Kumaon Sector",
            threat_level="HIGH",
            fire_danger_index=72.0,
            evacuation_status="PRE-EVACUATION ADVISORY",
        )
    )

    assert result["status"] == "simulated_delivered"
    assert result["provider"] == "telegram_simulation_mode"
    assert "KUMAON SECTOR" in result["formatted_message"]
    assert "timestamp" in result


def test_telegram_status_endpoint():
    """Verify GET /api/v1/alerts/status returns 200 and operational status."""
    response = client.get("/api/v1/alerts/status")
    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "Telegram Emergency Alerts"
    assert "is_configured" in data
    assert "status" in data


def test_telegram_broadcast_endpoint():
    """Verify POST /api/v1/alerts/telegram triggers resident broadcast successfully."""
    payload = {
        "region_name": "Garhwal Division",
        "threat_level": "CRITICAL / EXTREME",
        "fire_danger_index": 85.0,
        "evacuation_status": "MANDATORY EVACUATION",
        "custom_note": "Stage Type-3 engines at southern perimeter interface.",
    }
    response = client.post("/api/v1/alerts/telegram", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["delivered", "simulated_delivered"]
    assert "GARHWAL DIVISION" in data["formatted_message"]
    assert "MANDATORY EVACUATION" in data["formatted_message"]
