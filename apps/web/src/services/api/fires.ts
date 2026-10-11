/**
 * Active Fires API service with contract normalization
 */

import { httpClient } from './client';
import { FireEventDetail, FireHotspotProperties } from '../../types/domain';
import { GeoJSONFeatureCollection, GeoJSONFeature, PointGeometry } from '../../types/geo';

export interface ActiveFireQueryParams {
  region_id?: string;
  min_confidence?: string;
  since_hours?: number;
  limit?: number;
}

export async function fetchActiveFires(
  params?: ActiveFireQueryParams
): Promise<GeoJSONFeatureCollection<PointGeometry, FireHotspotProperties>> {
  const query = new URLSearchParams();
  if (params?.region_id) query.set('region_id', params.region_id);
  if (params?.min_confidence) query.set('min_confidence', params.min_confidence);
  if (params?.since_hours) query.set('since_hours', params.since_hours.toString());
  if (params?.limit) query.set('limit', params.limit.toString());

  const queryString = query.toString();
  const path = `/fires/active${queryString ? `?${queryString}` : ''}`;
  const rawData = await httpClient.get<GeoJSONFeatureCollection<PointGeometry, Record<string, unknown>>>(path);

  // Normalize properties across API variations
  const normalizedFeatures: GeoJSONFeature<PointGeometry, FireHotspotProperties>[] = (
    rawData.features || []
  ).map((feat, index) => {
    const rawProps = feat.properties || {};

    const confidenceVal =
      rawProps.confidence ||
      (typeof rawProps.confidence_pct === 'number'
        ? rawProps.confidence_pct >= 80
          ? 'high'
          : rawProps.confidence_pct >= 50
          ? 'nominal'
          : 'low'
        : 'nominal');

    const detectionTimeVal =
      rawProps.detection_time ||
      rawProps.detected_at ||
      new Date().toISOString();

    const brightnessTempVal =
      typeof rawProps.brightness_temperature_kelvin === 'number'
        ? rawProps.brightness_temperature_kelvin
        : typeof rawProps.brightness_temp_k === 'number'
        ? rawProps.brightness_temp_k
        : null;

    const frpVal = typeof rawProps.frp_mw === 'number' ? rawProps.frp_mw : null;

    const normalizedProps: FireHotspotProperties = {
      id: String(feat.id || rawProps.id || `hotspot-${index + 1}`),
      detection_time: String(detectionTimeVal),
      satellite: String(rawProps.satellite || 'VIIRS NOAA-20'),
      confidence: String(confidenceVal),
      frp_mw: frpVal,
      brightness_temperature_kelvin: brightnessTempVal,
      status: String(rawProps.status || (rawProps.is_active ? 'active' : 'active')),
      region_id: rawProps.region_id ? String(rawProps.region_id) : null,
      raw_properties: rawProps,
    };

    return {
      ...feat,
      properties: normalizedProps,
    };
  });

  return {
    ...rawData,
    features: normalizedFeatures,
  };
}

export async function fetchFireById(fireId: string): Promise<FireEventDetail> {
  return httpClient.get<FireEventDetail>(`/fires/active/${encodeURIComponent(fireId)}`);
}
