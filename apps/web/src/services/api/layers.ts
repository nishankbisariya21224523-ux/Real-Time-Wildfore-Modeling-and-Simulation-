/**
 * GIS Layers API service
 */

import { httpClient } from './client';
import { LayerMetadata } from '../../types/domain';

export async function fetchLayers(): Promise<LayerMetadata[]> {
  return httpClient.get<LayerMetadata[]>('/layers');
}
