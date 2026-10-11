import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { SimulationMetricChart } from './SimulationMetricChart';
import { GeoJSONFeatureCollection, MultiPolygonGeometry } from '../../../types/geo';
import { SimulationStepProperties } from '../../../types/domain';

describe('SimulationMetricChart', () => {
  const mockStepsData: GeoJSONFeatureCollection<MultiPolygonGeometry, SimulationStepProperties> = {
    type: 'FeatureCollection',
    features: [
      {
        type: 'Feature',
        geometry: { type: 'MultiPolygon', coordinates: [] },
        properties: {
          step_number: 0,
          step_hour: 0,
          elapsed_minutes: 0,
          cumulative_burned_area_ha: 0.5,
          spread_velocity_kmh: 0.2,
        },
      },
      {
        type: 'Feature',
        geometry: { type: 'MultiPolygon', coordinates: [] },
        properties: {
          step_number: 1,
          step_hour: 3,
          elapsed_minutes: 180,
          cumulative_burned_area_ha: 15.4,
          spread_velocity_kmh: 1.8,
        },
      },
      {
        type: 'Feature',
        geometry: { type: 'MultiPolygon', coordinates: [] },
        properties: {
          step_number: 2,
          step_hour: 6,
          elapsed_minutes: 360,
          cumulative_burned_area_ha: 42.1,
          spread_velocity_kmh: 2.4,
        },
      },
    ],
  };

  it('renders placeholder message when no steps data is provided', () => {
    render(<SimulationMetricChart stepsData={null} currentStepIndex={0} />);
    expect(screen.getByText(/spread analytics/i)).toBeInTheDocument();
    expect(screen.getByText(/run or load a simulation to view cumulative burned area/i)).toBeInTheDocument();
  });

  it('renders timesteps with burned area and velocity', () => {
    render(<SimulationMetricChart stepsData={mockStepsData} currentStepIndex={1} />);

    expect(screen.getByText(/spread metrics/i)).toBeInTheDocument();
    expect(screen.getByText(/3 timesteps/i)).toBeInTheDocument();
    expect(screen.getByText('15.4 ha')).toBeInTheDocument();
    expect(screen.getByText('1.8 km/h')).toBeInTheDocument();
    expect(screen.getByText('T+0h')).toBeInTheDocument();
    expect(screen.getByText('T+3h')).toBeInTheDocument();
    expect(screen.getByText('T+6h')).toBeInTheDocument();
    expect(screen.getByText(/max area: 42\.1 ha/i)).toBeInTheDocument();
  });

  it('triggers onSelectStep when clicking a timestep column', () => {
    const onSelectStep = vi.fn();
    render(
      <SimulationMetricChart
        stepsData={mockStepsData}
        currentStepIndex={0}
        onSelectStep={onSelectStep}
      />
    );

    const step2Btn = screen.getByRole('button', { name: /step 2: t\+6h/i });
    fireEvent.click(step2Btn);
    expect(onSelectStep).toHaveBeenCalledWith(2);
  });
});
