import { useState, useEffect, useCallback, useRef } from 'react';
import {
  createSimulation,
  fetchSimulation,
  fetchSimulationSteps,
} from '../../../services/api/simulations';
import {
  IgnitionPoint,
  SimulationJob,
  SimulationDetail,
  SimulationStepProperties,
} from '../../../types/domain';
import { GeoJSONFeatureCollection, MultiPolygonGeometry } from '../../../types/geo';

export function useSimulation(regionId: string, initialIgnition?: IgnitionPoint | null) {
  const [ignitionPoint, setIgnitionPoint] = useState<IgnitionPoint | null>(initialIgnition || null);
  const [durationHours, setDurationHours] = useState<number>(6);
  const [stepMinutes, setStepMinutes] = useState<number>(60);
  const [windSpeedMs, setWindSpeedMs] = useState<number>(7.5);
  const [windDirectionDeg, setWindDirectionDeg] = useState<number>(225.0);
  const [fuelType, setFuelType] = useState<string>('CONIFER_HIGH_FLAMMABILITY');
  const [activeJob, setActiveJob] = useState<SimulationJob | null>(null);
  const [simulationDetail, setSimulationDetail] = useState<SimulationDetail | null>(null);

  // Synchronize initial ignition if provided from parent (e.g. cross-navigation from fire/risk)
  useEffect(() => {
    if (initialIgnition) {
      setIgnitionPoint(initialIgnition);
    }
  }, [initialIgnition]);
  const [stepsData, setStepsData] = useState<
    GeoJSONFeatureCollection<MultiPolygonGeometry, SimulationStepProperties> | null
  >(null);
  const [currentStepIndex, setCurrentStepIndex] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const playbackTimerRef = useRef<number | null>(null);
  const pollingTimerRef = useRef<number | null>(null);

  // Synchronize simulation ID from URL on mount
  useEffect(() => {
    if (typeof window === 'undefined') return;
    const params = new URLSearchParams(window.location.search);
    const urlSimId = params.get('simulationId');
    if (urlSimId && !activeJob) {
      setActiveJob({
        simulation_id: urlSimId,
        status: 'RUNNING',
        created_at: new Date().toISOString(),
      });
    }
  }, [activeJob]);

  // Status Polling Effect
  useEffect(() => {
    const simId = activeJob?.simulation_id;
    if (!simId) return;

    // Terminal check
    if (activeJob.status === 'COMPLETED' || activeJob.status === 'FAILED') {
      if (pollingTimerRef.current) clearInterval(pollingTimerRef.current);
      return;
    }

    const pollStatus = async () => {
      try {
        const detail = await fetchSimulation(simId);
        setSimulationDetail(detail);

        if (detail.status === 'COMPLETED') {
          if (pollingTimerRef.current) clearInterval(pollingTimerRef.current);
          setActiveJob((prev) => (prev ? { ...prev, status: 'COMPLETED' } : null));

          // Fetch complete timestep boundaries
          const steps = await fetchSimulationSteps(simId);
          if (steps && steps.features?.length) {
            setStepsData(steps);
            setCurrentStepIndex(0);
          }
        } else if (detail.status === 'FAILED') {
          if (pollingTimerRef.current) clearInterval(pollingTimerRef.current);
          setActiveJob((prev) => (prev ? { ...prev, status: 'FAILED' } : null));
          setError(detail.error_message || 'Fire spread simulation failed.');
        } else {
          setActiveJob((prev) => (prev ? { ...prev, status: detail.status } : null));
        }
      } catch (err: unknown) {
        // Polling retry: don't crash on transient network error
      }
    };

    // Immediate initial poll
    pollStatus();
    pollingTimerRef.current = window.setInterval(pollStatus, 1500);

    return () => {
      if (pollingTimerRef.current) clearInterval(pollingTimerRef.current);
    };
  }, [activeJob?.simulation_id, activeJob?.status]);

  // Playback timer loop
  useEffect(() => {
    if (!isPlaying) {
      if (playbackTimerRef.current) clearInterval(playbackTimerRef.current);
      return;
    }

    const totalSteps = stepsData?.features?.length || 0;
    if (totalSteps <= 1) {
      setIsPlaying(false);
      return;
    }

    playbackTimerRef.current = window.setInterval(() => {
      setCurrentStepIndex((prev) => {
        if (prev >= totalSteps - 1) {
          setIsPlaying(false);
          return prev; // Stop at final step
        }
        return prev + 1;
      });
    }, 1200);

    return () => {
      if (playbackTimerRef.current) clearInterval(playbackTimerRef.current);
    };
  }, [isPlaying, stepsData]);

  // Submit new simulation
  const handleStartSimulation = async (name: string = 'Operational Spread Run') => {
    if (!ignitionPoint) {
      setError('Please select an ignition point on the map or enter coordinates.');
      return;
    }

    setIsSubmitting(true);
    setError(null);
    setIsPlaying(false);

    try {
      const job = await createSimulation({
        region_id: regionId,
        name,
        ignition_point: ignitionPoint,
        ignition_points: [ignitionPoint],
        duration_hours: durationHours,
        max_duration_hours: durationHours,
        temporal_step_minutes: stepMinutes,
        weather_scenario: {
          wind_speed_ms: windSpeedMs,
          wind_direction_deg: windDirectionDeg,
        },
        fuel_type: fuelType,
      });
      setActiveJob(job);

      // Persist active simulation in URL query parameter
      if (typeof window !== 'undefined' && window.history) {
        const url = new URL(window.location.href);
        url.searchParams.set('simulationId', job.simulation_id);
        window.history.replaceState(null, '', url.toString());
      }

      // Fetch simulation details and steps immediately (covers eager execution)
      const [detail, steps] = await Promise.all([
        fetchSimulation(job.simulation_id).catch(() => null),
        fetchSimulationSteps(job.simulation_id).catch(() => null),
      ]);

      if (detail) {
        setSimulationDetail(detail);
        if (detail.status === 'COMPLETED') {
          setActiveJob((prev) => (prev ? { ...prev, status: 'COMPLETED' } : null));
        }
      }
      if (steps && steps.features?.length) {
        setStepsData(steps);
        setCurrentStepIndex(0);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Simulation submission failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClearIgnition = useCallback(() => {
    setIgnitionPoint(null);
  }, []);

  const handleStepForward = useCallback(() => {
    const totalSteps = stepsData?.features?.length || 0;
    setCurrentStepIndex((prev) => Math.min(prev + 1, Math.max(totalSteps - 1, 0)));
  }, [stepsData]);

  const handleStepBackward = useCallback(() => {
    setCurrentStepIndex((prev) => Math.max(prev - 1, 0));
  }, []);

  const handleReplay = useCallback(() => {
    setCurrentStepIndex(0);
    setIsPlaying(true);
  }, []);

  return {
    ignitionPoint,
    setIgnitionPoint,
    durationHours,
    setDurationHours,
    stepMinutes,
    setStepMinutes,
    windSpeedMs,
    setWindSpeedMs,
    windDirectionDeg,
    setWindDirectionDeg,
    fuelType,
    setFuelType,
    activeJob,
    simulationDetail,
    stepsData,
    currentStepIndex,
    setCurrentStepIndex,
    isPlaying,
    setIsPlaying,
    isSubmitting,
    error,
    startSimulation: handleStartSimulation,
    clearIgnition: handleClearIgnition,
    stepForward: handleStepForward,
    stepBackward: handleStepBackward,
    replaySimulation: handleReplay,
  };
}
