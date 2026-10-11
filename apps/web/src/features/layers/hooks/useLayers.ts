import { useState, useEffect, useCallback } from 'react';
import { fetchLayers } from '../../../services/api/layers';
import { LayerMetadata } from '../../../types/domain';

export function useLayers() {
  const [layers, setLayers] = useState<LayerMetadata[]>([]);
  const [selectedLayerId, setSelectedLayerId] = useState<string>('risk_layer');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadLayers = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await fetchLayers();
      setLayers(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch layers catalogue');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadLayers();
  }, [loadLayers]);

  const selectedLayer = layers.find((l) => l.id === selectedLayerId) || null;

  return {
    layers,
    selectedLayerId,
    setSelectedLayerId,
    selectedLayer,
    isLoading,
    error,
    reload: loadLayers,
  };
}
