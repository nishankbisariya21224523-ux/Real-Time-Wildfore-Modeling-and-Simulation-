/**
 * Backwards-compatibility wrapper delegating to modern services/api/
 */

import { fetchHealth, fetchRegions, fetchRegionById, fetchActiveFires } from './api';
import { SystemHealth, RegionSummary, RegionDetail } from '../types';

class ApiClient {
  async getHealth(): Promise<SystemHealth> {
    return fetchHealth();
  }

  async getRegions(): Promise<{ count: number; results: RegionSummary[] }> {
    const list = await fetchRegions();
    return { count: list.length, results: list };
  }

  async getRegionDetails(regionId: string): Promise<RegionDetail> {
    return fetchRegionById(regionId);
  }

  async getActiveFires(): Promise<{ type: string; features: unknown[] }> {
    return fetchActiveFires();
  }
}

export const apiClient = new ApiClient();
