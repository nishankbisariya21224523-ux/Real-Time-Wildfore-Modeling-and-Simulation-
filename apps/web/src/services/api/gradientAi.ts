/**
 * DigitalOcean Gradient AI Service Client for Frontend.
 */
import { httpClient } from './client';

export interface FeatureImpactItem {
  feature: string;
  value: string;
  impact: string;
  contribution_direction: string;
  physical_rationale: string;
}

export interface RiskExplanationPayload {
  region_name: string;
  predicted_probability: number;
  risk_class: string;
  features?: Record<string, any>;
}

export interface RiskExplanationResult {
  region_name: string;
  predicted_probability: number;
  risk_class: string;
  explanation: string;
  feature_importance: FeatureImpactItem[];
  model_version: string;
  provider: string;
  timestamp: string;
}

export interface CopilotQuestionPayload {
  question: string;
  map_context?: Record<string, any>;
}

export interface CopilotQuestionResult {
  question: string;
  answer: string;
  context_region: string;
  provider: string;
  timestamp: string;
}

export interface GuidanceItem {
  document_id: string;
  title: string;
  jurisdiction: string;
  excerpt: string;
}

export interface GuidanceRetrievalResult {
  query: string;
  total_documents_searched: number;
  retrieved_guidance: GuidanceItem[];
  timestamp: string;
}

export interface SituationBriefPayload {
  region_name: string;
  fire_danger_index: number;
  temperature_c: number;
  relative_humidity: number;
  wind_speed_kmh: number;
  active_hotspots: number;
  burned_area_ha?: number;
}

export interface SituationBriefResult {
  region_name: string;
  fire_danger_index: number;
  active_hotspots: number;
  situation_brief: string;
  evidence_citations: string[];
  provider: string;
  timestamp: string;
}

export async function explainRiskFeatures(
  payload: RiskExplanationPayload
): Promise<RiskExplanationResult> {
  return httpClient.request<RiskExplanationResult>('/ai/explain-risk', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function askCopilot(
  payload: CopilotQuestionPayload
): Promise<CopilotQuestionResult> {
  return httpClient.request<CopilotQuestionResult>('/ai/ask-copilot', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function retrievePreparednessGuidance(
  query: string
): Promise<GuidanceRetrievalResult> {
  return httpClient.request<GuidanceRetrievalResult>('/ai/retrieve-guidance', {
    method: 'POST',
    body: JSON.stringify({ query }),
  });
}

export async function generateSituationBrief(
  payload: SituationBriefPayload
): Promise<SituationBriefResult> {
  return httpClient.request<SituationBriefResult>('/ai/situation-brief', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}
