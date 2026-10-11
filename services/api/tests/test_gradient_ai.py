"""Tests for DigitalOcean Gradient AI Core Intelligence endpoints."""
from fastapi.testclient import TestClient
from services.api.app.main import app

client = TestClient(app)


def test_explain_risk_features_endpoint():
    """Verify POST /api/v1/ai/explain-risk explains ML features."""
    payload = {
        "region_name": "Garhwal Himalayan Sector",
        "predicted_probability": 0.885,
        "risk_class": "CRITICAL / EXTREME",
        "features": {
            "ndvi": 0.38,
            "ndwi": -0.18,
            "temperature_c": 37.0,
            "relative_humidity_pct": 14.5,
            "wind_speed_kmh": 32.0,
            "slope_deg": 26.5,
            "fuel_type": "CONIFER_HIGH_FLAMMABILITY",
            "fwi": 74.0,
        },
    }
    response = client.post("/api/v1/ai/explain-risk", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["region_name"] == "Garhwal Himalayan Sector"
    assert "explanation" in data
    assert len(data["feature_importance"]) >= 4
    assert data["model_version"] == "risk-xgboost-v002"
    assert "provider" in data


def test_ask_copilot_endpoint():
    """Verify POST /api/v1/ai/ask-copilot answers questions about map & simulation."""
    payload = {
        "question": "Which valleys are at highest risk if wind gusts shift North-East?",
        "map_context": {
            "region_name": "Garhwal Division",
            "active_fires_count": 4,
            "mean_risk": 0.058,
            "current_sim_step": 6,
            "burned_area_ha": 182.4,
            "wind_direction_deg": 220,
            "wind_speed_kmh": 35,
        },
    }
    response = client.post("/api/v1/ai/ask-copilot", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert data["context_region"] == "Garhwal Division"


def test_retrieve_guidance_endpoint():
    """Verify POST /api/v1/ai/retrieve-guidance retrieves trusted doctrine from NDMA/NWCG/NFPA."""
    payload = {"query": "evacuation defensible space firebreak"}
    response = client.post("/api/v1/ai/retrieve-guidance", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_documents_searched"] >= 4
    assert len(data["retrieved_guidance"]) >= 1
    first_doc = data["retrieved_guidance"][0]
    assert "title" in first_doc
    assert "excerpt" in first_doc


def test_situation_brief_endpoint():
    """Verify POST /api/v1/ai/situation-brief generates evidence-linked SITBRIEF."""
    payload = {
        "region_name": "Garhwal Himalayan Division",
        "fire_danger_index": 84.0,
        "temperature_c": 36.5,
        "relative_humidity": 15.0,
        "wind_speed_kmh": 30.0,
        "active_hotspots": 7,
        "burned_area_ha": 95.0,
    }
    response = client.post("/api/v1/ai/situation-brief", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "situation_brief" in data
    assert len(data["evidence_citations"]) >= 3
    assert data["region_name"] == "Garhwal Himalayan Division"
