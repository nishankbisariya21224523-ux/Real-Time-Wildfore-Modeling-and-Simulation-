import { useState, useEffect, useCallback } from 'react';
import { fetchActiveFires } from '../../../services/api/fires';
import { FireHotspotProperties } from '../../../types/domain';
import { GeoJSONFeatureCollection, GeoJSONFeature, PointGeometry } from '../../../types/geo';

export function useActiveFires(regionId?: string) {
  const [firesData, setFiresData] = useState<
    GeoJSONFeatureCollection<PointGeometry, FireHotspotProperties> | null
  >(null);
  const [selectedFire, setSelectedFire] = useState<FireHotspotProperties | null>(null);
  const [confidenceFilter, setConfidenceFilter] = useState<string>('all');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadFires = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const params = {
        region_id: regionId || undefined,
        min_confidence: confidenceFilter !== 'all' ? confidenceFilter : undefined,
      };
      const data = await fetchActiveFires(params);
      setFiresData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load active fire detections');
    } finally {
      setIsLoading(false);
    }
  }, [regionId, confidenceFilter]);

  useEffect(() => {
    loadFires();
  }, [loadFires]);

  // Derived filtered features
  const filteredFeatures: GeoJSONFeature<PointGeometry, FireHotspotProperties>[] = (
    firesData?.features || []
  )
    .filter((f: GeoJSONFeature<PointGeometry, FireHotspotProperties>) => {
      if (confidenceFilter === 'all') return true;
      return f.properties.confidence?.toLowerCase() === confidenceFilter.toLowerCase();
    })
    .map((f) => ({
      ...f,
      properties: {
        ...f.properties,
        longitude: f.properties.longitude ?? f.geometry?.coordinates?.[0] ?? 0,
        latitude: f.properties.latitude ?? f.geometry?.coordinates?.[1] ?? 0,
      },
    }));

  return {
    firesData,
    filteredFeatures,
    totalCount: firesData?.features?.length || 0,
    selectedFire,
    setSelectedFire,
    confidenceFilter,
    setConfidenceFilter,
    isLoading,
    error,
    reload: loadFires,
  };
}
