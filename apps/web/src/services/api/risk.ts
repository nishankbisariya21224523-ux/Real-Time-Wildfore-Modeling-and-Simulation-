/**
 * Risk Prediction API service
 */

import { httpClient } from './client';
import { RiskPredictionProperties, RiskSummary } from '../../types/domain';
import { GeoJSONFeatureCollection, PolygonGeometry } from '../../types/geo';

export async function fetchRiskPredictions(
  regionId: string,
  targetDate?: string
): Promise<GeoJSONFeatureCollection<PolygonGeometry, RiskPredictionProperties>> {
  const query = new URLSearchParams();
  if (targetDate) query.set('target_date', targetDate);

  const queryString = query.toString();
  const path = `/risk/${encodeURIComponent(regionId)}${queryString ? `?${queryString}` : ''}`;
  return httpClient.get<GeoJSONFeatureCollection<PolygonGeometry, RiskPredictionProperties>>(path);
}

export async function fetchRiskSummary(
  regionId: string,
  targetDate?: string
): Promise<RiskSummary> {
  const query = new URLSearchParams();
  if (targetDate) query.set('target_date', targetDate);

  const queryString = query.toString();
  const path = `/risk/${encodeURIComponent(regionId)}/summary${queryString ? `?${queryString}` : ''}`;
  return httpClient.get<RiskSummary>(path);
}

export interface RiskPredictResponse {
  job_id: string;
  region_id: string;
  target_date: string;
  status: string;
  cells_predicted: number;
  mean_risk_probability: number;
  completed_at: string;
  model_version?: string;
}

export async function triggerRiskPrediction(
  regionId: string,
  targetDate: string,
  forceRecompute: boolean = false
): Promise<RiskPredictResponse> {
  return httpClient.post<RiskPredictResponse>('/risk/predict', {
    region_id: regionId,
    target_date: targetDate,
    force_recompute: forceRecompute,
    model_name: 'risk-xgboost-v001',
  });
}

