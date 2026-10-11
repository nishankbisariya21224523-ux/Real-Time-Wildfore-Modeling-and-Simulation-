import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Timeline } from './components/Timeline';
import { SimulationStepProperties } from '../../types/domain';
import { GeoJSONFeatureCollection, MultiPolygonGeometry } from '../../types/geo';

describe('Timeline Scrubber Component', () => {
  it('displays empty/disabled state when no simulation perimeters exist', () => {
    render(
      <Timeline
        stepsData={null}
        currentStepIndex={0}
        onSelectStep={vi.fn()}
        isPlaying={false}
        onTogglePlay={vi.fn()}
        onStepForward={vi.fn()}
        onStepBackward={vi.fn()}
      />
    );

    expect(screen.getByText(/no active timestep/i)).toBeInTheDocument();
    expect(
      screen.getByText(/timeline scrub disabled until a simulation job is executed/i)
    ).toBeInTheDocument();
  });

  it('renders step progression slider and controls when steps exist', () => {
    const mockSteps: GeoJSONFeatureCollection<MultiPolygonGeometry, SimulationStepProperties> = {
      type: 'FeatureCollection',
      features: [
        {
          type: 'Feature',
          geometry: { type: 'MultiPolygon', coordinates: [] },
          properties: {
            step_number: 1,
            elapsed_minutes: 60,
            cumulative_burned_area_ha: 25.4,
            active_front_cells_count: 12,
          },
        },
        {
          type: 'Feature',
          geometry: { type: 'MultiPolygon', coordinates: [] },
          properties: {
            step_number: 2,
            elapsed_minutes: 120,
            cumulative_burned_area_ha: 52.8,
            active_front_cells_count: 24,
          },
        },
      ],
    };

    const handleTogglePlay = vi.fn();
    const handleStepForward = vi.fn();

    render(
      <Timeline
        stepsData={mockSteps}
        currentStepIndex={0}
        onSelectStep={vi.fn()}
        isPlaying={false}
        onTogglePlay={handleTogglePlay}
        onStepForward={handleStepForward}
        onStepBackward={vi.fn()}
      />
    );

    expect(screen.getByText('25.4 ha')).toBeInTheDocument();
    expect(screen.getByText(/t\+60m \(step 1\)/i)).toBeInTheDocument();

    const playBtn = screen.getByRole('button', { name: /play/i });
    fireEvent.click(playBtn);
    expect(handleTogglePlay).toHaveBeenCalled();

    const nextBtn = screen.getByRole('button', { name: /next step/i });
    fireEvent.click(nextBtn);
    expect(handleStepForward).toHaveBeenCalled();
  });

  it('triggers onReplay when replay button is clicked', () => {
    const handleReplay = vi.fn();
    const mockSteps: GeoJSONFeatureCollection<MultiPolygonGeometry, SimulationStepProperties> = {
      type: 'FeatureCollection',
      features: [
        {
          type: 'Feature',
          geometry: { type: 'MultiPolygon', coordinates: [] },
          properties: {
            step_number: 1,
            elapsed_minutes: 60,
            cumulative_burned_area_ha: 15.0,
            spread_velocity_kmh: 1.2,
            active_front_cells_count: 5,
          },
        },
      ],
    };

    render(
      <Timeline
        stepsData={mockSteps}
        currentStepIndex={0}
        onSelectStep={vi.fn()}
        isPlaying={false}
        onTogglePlay={vi.fn()}
        onStepForward={vi.fn()}
        onStepBackward={vi.fn()}
        onReplay={handleReplay}
      />
    );

    const replayBtn = screen.getByRole('button', { name: /replay/i });
    fireEvent.click(replayBtn);
    expect(handleReplay).toHaveBeenCalledTimes(1);
    expect(screen.getByText(/1.2 km\/h/i)).toBeInTheDocument();
  });
});
