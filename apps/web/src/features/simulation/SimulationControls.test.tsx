import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { SimulationControls } from './components/SimulationControls';
import { IgnitionSelector } from './components/IgnitionSelector';

describe('Simulation Controls and Ignition Selector', () => {
  it('disables execution button when no ignition point is chosen', () => {
    const handleStart = vi.fn();
    render(
      <SimulationControls
        durationHours={6}
        onDurationChange={vi.fn()}
        stepMinutes={60}
        onStepMinutesChange={vi.fn()}
        hasIgnition={false}
        onStartSimulation={handleStart}
      />
    );

    const button = screen.getByRole('button', { name: /initialize 12h simulation/i });
    expect(button).toBeDisabled();
    expect(screen.getByText(/select an ignition point to begin simulation/i)).toBeInTheDocument();
  });

  it('enables execution button when ignition point is active', () => {
    const handleStart = vi.fn();
    render(
      <SimulationControls
        durationHours={6}
        onDurationChange={vi.fn()}
        stepMinutes={60}
        onStepMinutesChange={vi.fn()}
        hasIgnition={true}
        onStartSimulation={handleStart}
      />
    );

    const button = screen.getByRole('button', { name: /initialize 12h simulation/i });
    expect(button).not.toBeDisabled();
    fireEvent.click(button);
    expect(handleStart).toHaveBeenCalled();
  });

  it('renders and validates manual coordinates in IgnitionSelector', () => {
    const handleSetIgnition = vi.fn();
    render(
      <IgnitionSelector
        ignitionPoint={null}
        onSetIgnition={handleSetIgnition}
        onClearIgnition={vi.fn()}
      />
    );

    const latInput = screen.getByPlaceholderText(/30\.2241/i);
    const lonInput = screen.getByPlaceholderText(/78\.7842/i);
    const submitBtn = screen.getByRole('button', { name: /set coordinates/i });

    fireEvent.change(latInput, { target: { value: '30.1234' } });
    fireEvent.change(lonInput, { target: { value: '78.5678' } });
    fireEvent.click(submitBtn);

    expect(handleSetIgnition).toHaveBeenCalledWith({
      latitude: 30.1234,
      longitude: 78.5678,
    });
  });

  it('renders and adjusts environmental overrides when toggled', () => {
    const handleWindSpeed = vi.fn();
    const handleWindDir = vi.fn();

    render(
      <SimulationControls
        durationHours={6}
        onDurationChange={vi.fn()}
        stepMinutes={60}
        onStepMinutesChange={vi.fn()}
        windSpeedMs={10}
        onWindSpeedChange={handleWindSpeed}
        windDirectionDeg={270}
        onWindDirectionChange={handleWindDir}
        hasIgnition={true}
        onStartSimulation={vi.fn()}
      />
    );

    // Expand overrides
    const toggleBtn = screen.getByRole('button', { name: /weather & fuel overrides/i });
    fireEvent.click(toggleBtn);

    expect(screen.getByText(/10 m\/s \(36.0 km\/h\)/i)).toBeInTheDocument();
    expect(screen.getByText(/270° \(W\)/i)).toBeInTheDocument();
  });

  it('renders replay and reset buttons when simulation is complete and ignition is set', () => {
    const handleReplay = vi.fn();
    const handleClear = vi.fn();

    render(
      <SimulationControls
        durationHours={6}
        onDurationChange={vi.fn()}
        stepMinutes={60}
        onStepMinutesChange={vi.fn()}
        hasIgnition={true}
        hasCompletedSimulation={true}
        onReplaySimulation={handleReplay}
        onClearIgnition={handleClear}
        onStartSimulation={vi.fn()}
      />
    );

    const replayBtn = screen.getByRole('button', { name: /replay simulation/i });
    const clearBtn = screen.getByRole('button', { name: /reset ignition point/i });

    fireEvent.click(replayBtn);
    expect(handleReplay).toHaveBeenCalledTimes(1);

    fireEvent.click(clearBtn);
    expect(handleClear).toHaveBeenCalledTimes(1);
  });
});
