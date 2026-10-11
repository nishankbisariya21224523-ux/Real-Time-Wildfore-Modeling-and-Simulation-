/**
 * Fire Spread Simulation API service
 */

import { httpClient } from './client';
import {
  SimulationCreateRequest,
  SimulationJob,
  SimulationDetail,
  SimulationStepProperties,
} from '../../types/domain';
import { GeoJSONFeatureCollection, MultiPolygonGeometry } from '../../types/geo';

export async function createSimulation(
  payload: SimulationCreateRequest
): Promise<SimulationJob> {
  return httpClient.post<SimulationJob>('/simulations', payload);
}

export async function fetchSimulation(
  simulationId: string
): Promise<SimulationDetail> {
  return httpClient.get<SimulationDetail>(`/simulations/${encodeURIComponent(simulationId)}`);
}

export async function fetchSimulationSteps(
  simulationId: string
): Promise<GeoJSONFeatureCollection<MultiPolygonGeometry, SimulationStepProperties>> {
  return httpClient.get<GeoJSONFeatureCollection<MultiPolygonGeometry, SimulationStepProperties>>(
    `/simulations/${encodeURIComponent(simulationId)}/steps`
  );
}

export async function fetchSimulationTimeline(
  simulationId: string
): Promise<{
  simulation_id: string;
  total_steps: number;
  timeline: Array<{
    step_hour: number;
    burned_area_ha: number;
    spread_velocity_kmh: number;
    spread_direction_deg: number;
    intensity_mw: number;
  }>;
}> {
  return httpClient.get(`/simulations/${encodeURIComponent(simulationId)}/timeline`);
}

export async function fetchSimulationTimestep(
  simulationId: string,
  hour: number
) {
  return httpClient.get(`/simulations/${encodeURIComponent(simulationId)}/timesteps/${hour}`);
}
