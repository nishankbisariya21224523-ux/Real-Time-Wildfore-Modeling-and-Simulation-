import { useState, useEffect, useCallback } from 'react';
import { fetchRiskPredictions, fetchRiskSummary, triggerRiskPrediction } from '../../../services/api/risk';
import { RiskPredictionProperties, RiskSummary } from '../../../types/domain';

import { GeoJSONFeatureCollection, GeoJSONFeature, PolygonGeometry } from '../../../types/geo';

export function useRisk(regionId?: string, targetDate?: string) {
  const [riskData, setRiskData] = useState<
    GeoJSONFeatureCollection<PolygonGeometry, RiskPredictionProperties> | null
  >(null);
  const [summary, setSummary] = useState<RiskSummary | null>(null);
  const [selectedCell, setSelectedCell] = useState<RiskPredictionProperties | null>(null);
  const [selectedClassFilter, setSelectedClassFilter] = useState<string>('ALL');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadRisk = useCallback(async () => {
    if (!regionId) return;

    setIsLoading(true);
    setError(null);

    try {
      const [gridData, summaryData] = await Promise.all([
        fetchRiskPredictions(regionId, targetDate),
        fetchRiskSummary(regionId, targetDate).catch((err: unknown) => {
          console.warn('Risk summary unavailable:', err);
          return null;
        }),
      ]);

      setRiskData(gridData);
      setSummary(summaryData);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load risk prediction layer');
    } finally {
      setIsLoading(false);
    }
  }, [regionId, targetDate]);

  const recomputeRisk = useCallback(async () => {
    if (!regionId) return;

    setIsLoading(true);
    setError(null);

    try {
      const dateToUse = targetDate || new Date().toISOString().slice(0, 10);
      await triggerRiskPrediction(regionId, dateToUse, true);
      await loadRisk();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to execute risk model inference');
    } finally {
      setIsLoading(false);
    }
  }, [regionId, targetDate, loadRisk]);

  useEffect(() => {
    loadRisk();
  }, [loadRisk]);


  // Filter features based on risk class
  const filteredFeatures: GeoJSONFeature<PolygonGeometry, RiskPredictionProperties>[] = (
    riskData?.features || []
  ).filter((f: GeoJSONFeature<PolygonGeometry, RiskPredictionProperties>) => {
    if (selectedClassFilter === 'ALL') return true;
    return f.properties.risk_class.toUpperCase() === selectedClassFilter.toUpperCase();
  });

  const filteredRiskData: GeoJSONFeatureCollection<PolygonGeometry, RiskPredictionProperties> | null =
    riskData
      ? {
          ...riskData,
          features: filteredFeatures,
        }
      : null;

  return {
    riskData: filteredRiskData,
    rawRiskData: riskData,
    summary,
    selectedCell,
    setSelectedCell,
    selectedClassFilter,
    setSelectedClassFilter,
    isLoading,
    error,
    reload: loadRisk,
    recomputeRisk,
  };
}

