"""DigitalOcean GenAI Service for Wildfire Modeling & Simulation.
Utilizes DigitalOcean GenAI serverless inference endpoints (e.g. Llama 3.3 70B / 3.1 8B)
with intelligent heuristic fallback when DO_GENAI_API_KEY is not configured.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import httpx

from ..core.config import settings

logger = logging.getLogger(__name__)


class DigitalOceanAIService:
    """Service interfacing with DigitalOcean GenAI Serverless Inference."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = api_key if api_key is not None else settings.DO_GENAI_API_KEY
        self.base_url = base_url if base_url is not None else settings.DO_GENAI_BASE_URL
        self.model = model if model is not None else settings.DO_GENAI_MODEL

    @property
    def is_configured(self) -> bool:
        """Indicates if an active DigitalOcean GenAI API key is provided."""
        return bool(self.api_key and self.api_key.strip())

    async def generate_incident_briefing(
        self,
        region_name: str,
        fire_danger_index: float,
        temperature_c: float,
        relative_humidity: float,
        wind_speed_kmh: float,
        wind_direction_deg: float,
        active_hotspots: int,
        slope_pct: float = 0.0,
        fuel_type: str = "Timber / Mixed Conifer",
        evacuation_status: str = "ADVISORY",
    ) -> Dict[str, Any]:
        """
        Generates a comprehensive wildfire incident command briefing (SITREP)
        synthesizing real-time telemetry, threat level, and containment tactics.
        """
        # Determine threat level category
        if fire_danger_index >= 80 or (wind_speed_kmh > 45 and relative_humidity < 15):
            threat_level = "CRITICAL / EXTREME"
        elif fire_danger_index >= 60:
            threat_level = "HIGH"
        elif fire_danger_index >= 40:
            threat_level = "MODERATE"
        else:
            threat_level = "LOW"

        # If DO GenAI API key is configured, invoke DigitalOcean GenAI endpoint
        if self.is_configured:
            try:
                return await self._call_do_genai(
                    region_name=region_name,
                    threat_level=threat_level,
                    fire_danger_index=fire_danger_index,
                    temperature_c=temperature_c,
                    relative_humidity=relative_humidity,
                    wind_speed_kmh=wind_speed_kmh,
                    wind_direction_deg=wind_direction_deg,
                    active_hotspots=active_hotspots,
                    slope_pct=slope_pct,
                    fuel_type=fuel_type,
                    evacuation_status=evacuation_status,
                )
            except Exception as exc:
                logger.warning(
                    "DigitalOcean GenAI call failed (%s). Falling back to heuristic tactical engine.",
                    exc,
                )

        # Fallback to deterministic heuristic tactical briefing engine
        return self._heuristic_tactical_briefing(
            region_name=region_name,
            threat_level=threat_level,
            fire_danger_index=fire_danger_index,
            temperature_c=temperature_c,
            relative_humidity=relative_humidity,
            wind_speed_kmh=wind_speed_kmh,
            wind_direction_deg=wind_direction_deg,
            active_hotspots=active_hotspots,
            slope_pct=slope_pct,
            fuel_type=fuel_type,
            evacuation_status=evacuation_status,
        )

    async def _call_do_genai(
        self,
        region_name: str,
        threat_level: str,
        fire_danger_index: float,
        temperature_c: float,
        relative_humidity: float,
        wind_speed_kmh: float,
        wind_direction_deg: float,
        active_hotspots: int,
        slope_pct: float,
        fuel_type: str,
        evacuation_status: str,
    ) -> Dict[str, Any]:
        """Calls DigitalOcean GenAI OpenAI-compatible chat completions endpoint."""
        prompt = (
            f"You are the Wildfire Incident Command AI Officer. Analyze the following real-time telemetry:\n"
            f"- Region: {region_name}\n"
            f"- Threat Level: {threat_level}\n"
            f"- Fire Danger Index: {fire_danger_index:.1f}/100\n"
            f"- Weather: {temperature_c:.1f}°C, RH {relative_humidity:.1f}%, Wind {wind_speed_kmh:.1f} km/h @ {wind_direction_deg:.0f}°\n"
            f"- Active Hotspots: {active_hotspots}\n"
            f"- Terrain/Fuel: Slope {slope_pct:.1f}%, Fuel: {fuel_type}\n"
            f"- Evacuation Status: {evacuation_status}\n\n"
            f"Provide an authoritative tactical briefing with:\n"
            f"1. Executive SITREP\n"
            f"2. Rate of Spread & Weather Dynamics\n"
            f"3. Containment & Suppression Strategy\n"
            f"4. Evacuation & Public Safety Directives"
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert wildfire intelligence system providing structured tactical advisories.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 800,
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(
                f"{self.base_url.rstrip('/')}/chat/completions",
                json=payload,
                headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()
            analysis_text = data["choices"][0]["message"]["content"]

        return {
            "region_name": region_name,
            "threat_level": threat_level,
            "fire_danger_index": fire_danger_index,
            "summary": analysis_text,
            "tactical_actions": [
                f"Establish primary aerial retardant drop along bearing {wind_direction_deg:.0f}°",
                "Deploy ground crews to reinforce ridge firebreaks ahead of advancing front",
                "Maintain continuous sensor surveillance over active thermal anomalies",
            ],
            "evacuation_directive": evacuation_status,
            "provider": "digitalocean_genai",
            "model": self.model,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _heuristic_tactical_briefing(
        self,
        region_name: str,
        threat_level: str,
        fire_danger_index: float,
        temperature_c: float,
        relative_humidity: float,
        wind_speed_kmh: float,
        wind_direction_deg: float,
        active_hotspots: int,
        slope_pct: float,
        fuel_type: str,
        evacuation_status: str,
    ) -> Dict[str, Any]:
        """Provides deterministic tactical SITREP when offline or unconfigured."""
        summary_paragraphs = [
            f"WILDFIRE SITREP FOR {region_name.upper()} | STATUS: {threat_level}",
            f"Current conditions register a Fire Danger Index of {fire_danger_index:.1f}/100 with {active_hotspots} detected thermal hotspots. "
            f"Dry-bulb temperature is {temperature_c:.1f}°C with relative humidity at {relative_humidity:.1f}%.",
            f"Surface winds are tracking from {wind_direction_deg:.0f}° at {wind_speed_kmh:.1f} km/h over {fuel_type} with a {slope_pct:.1f}% terrain slope.",
        ]

        tactical_actions: List[str] = []
        if threat_level == "CRITICAL / EXTREME":
            tactical_actions.extend([
                "Order immediate mandatory evacuation for downwind sectors within a 15km perimeter.",
                f"Concentrate heavy aerial water/retardant tankers along bearing {wind_direction_deg:.0f}°.",
                "Withdraw hand crews from direct flame front on steep slopes to avoid entrapment.",
            ])
        elif threat_level == "HIGH":
            tactical_actions.extend([
                "Establish secondary bulldozer firebreaks 500m ahead of the active advancing flank.",
                "Stage structural protection engines at interfaces downwind.",
                "Activate local public emergency broadcasting and pre-evacuation notices.",
            ])
        else:
            tactical_actions.extend([
                "Maintain perimeter containment patrol and monitor satellite thermal anomalies.",
                "Deploy thermal drone surveillance to detect sub-surface smoldering.",
                "Ensure local water hydrants and relay tanker drafting points are operational.",
            ])

        return {
            "region_name": region_name,
            "threat_level": threat_level,
            "fire_danger_index": fire_danger_index,
            "summary": "\n\n".join(summary_paragraphs),
            "tactical_actions": tactical_actions,
            "evacuation_directive": (
                "MANDATORY EVACUATION" if threat_level == "CRITICAL / EXTREME" else evacuation_status
            ),
            "provider": "digitalocean_genai_heuristic_engine",
            "model": "rule-based-tactical-v1",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# Singleton service instance
do_ai_service = DigitalOceanAIService()
