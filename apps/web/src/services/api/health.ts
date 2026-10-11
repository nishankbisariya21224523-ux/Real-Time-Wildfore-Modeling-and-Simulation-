/**
 * System Health API service
 */

import { httpClient } from './client';
import { SystemHealth } from '../../types/api';

export async function fetchHealth(): Promise<SystemHealth> {
  return httpClient.get<SystemHealth>('/health');
}

export async function fetchLiveness(): Promise<{ status: string }> {
  return httpClient.get<{ status: string }>('/health/liveness');
}

export async function fetchReadiness(): Promise<{ status: string; checks?: Record<string, string> }> {
  return httpClient.get<{ status: string; checks?: Record<string, string> }>('/health/readiness');
}
