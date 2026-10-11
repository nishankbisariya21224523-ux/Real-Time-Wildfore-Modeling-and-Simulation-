import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { OperationalAttentionBanner } from './OperationalAttentionBanner';

describe('OperationalAttentionBanner', () => {
  it('renders HIGH_ATTENTION advisory when extreme risk cells are detected', () => {
    render(
      <OperationalAttentionBanner
        regionName="Garhwal Himalaya"
        activeFireCount={2}
        highRiskCellCount={15}
        extremeRiskCellCount={8}
        maxProbability={0.88}
        onNavigateTab={vi.fn()}
      />
    );

    expect(screen.getByText(/high operational attention required/i)).toBeInTheDocument();
    expect(screen.getByText(/88%/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /inspect 24h risk layer/i })).toBeInTheDocument();
  });

  it('renders WARNING advisory when active fires exist without extreme risk cells', () => {
    render(
      <OperationalAttentionBanner
        regionName="Garhwal Himalaya"
        activeFireCount={4}
        highRiskCellCount={0}
        extremeRiskCellCount={0}
        maxProbability={0.25}
        onNavigateTab={vi.fn()}
      />
    );

    expect(screen.getByText(/active satellite thermal anomalies detected/i)).toBeInTheDocument();
    expect(screen.getByText(/4 thermal hotspots/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /view active hotspots/i })).toBeInTheDocument();
  });

  it('renders INFO status when no active fires or extreme cells exist', () => {
    render(
      <OperationalAttentionBanner
        regionName="Garhwal Himalaya"
        activeFireCount={0}
        highRiskCellCount={0}
        extremeRiskCellCount={0}
        maxProbability={0.12}
        onNavigateTab={vi.fn()}
      />
    );

    expect(screen.getByText(/sector operational baseline/i)).toBeInTheDocument();
    expect(screen.getByText(/normal baseline state for Garhwal Himalaya/i)).toBeInTheDocument();
  });

  it('calls onNavigateTab when action buttons are clicked', () => {
    const onNavigateTab = vi.fn();
    render(
      <OperationalAttentionBanner
        regionName="Garhwal Himalaya"
        activeFireCount={3}
        highRiskCellCount={10}
        extremeRiskCellCount={5}
        maxProbability={0.85}
        onNavigateTab={onNavigateTab}
      />
    );

    fireEvent.click(screen.getByRole('button', { name: /inspect 24h risk layer/i }));
    expect(onNavigateTab).toHaveBeenCalledWith('risk');
  });
});
