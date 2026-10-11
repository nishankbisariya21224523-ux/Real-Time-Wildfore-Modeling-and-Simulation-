/**
 * DigitalOcean GenAI Service Client
 */
import { httpClient } from './client';

export interface IncidentBriefingPayload {
  region_name: string;
  fire_danger_index: number;
  temperature_c: number;
  relative_humidity: number;
  wind_speed_kmh: number;
  wind_direction_deg: number;
  active_hotspots: number;
  slope_pct?: number;
  fuel_type?: string;
  evacuation_status?: string;
}

export interface IncidentBriefingResult {
  region_name: string;
  threat_level: string;
  fire_danger_index: number;
  summary: string;
  tactical_actions: string[];
  evacuation_directive: string;
  provider: string;
  model: string;
  timestamp: string;
}

export interface AIStatusResult {
  provider: string;
  is_configured: boolean;
  default_model: string;
  status: string;
}

export async function fetchAIStatus(): Promise<AIStatusResult> {
  return httpClient.request<AIStatusResult>('/ai/status');
}

export async function generateAIAdvisory(
  payload: IncidentBriefingPayload
): Promise<IncidentBriefingResult> {
  return httpClient.request<IncidentBriefingResult>('/ai/advisory', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}
