import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { RiskDistributionChart } from './RiskDistributionChart';
import { RiskSummary } from '../../../types/domain';

describe('RiskDistributionChart', () => {
  const mockSummary: RiskSummary = {
    region_id: 'reg-01',
    target_date: '2026-10-06',
    total_cells: 1000,
    high_risk_cells: 150,
    extreme_risk_cells: 50,
    mean_probability: 0.35,
    risk_distribution: {
      low: 500,
      moderate: 300,
      high: 150,
      extreme: 50,
    },
  };

  it('renders loading placeholder when summary is null', () => {
    render(<RiskDistributionChart summary={null} />);
    expect(screen.getByText(/risk distribution/i)).toBeInTheDocument();
    expect(screen.getByText(/awaiting risk prediction summary/i)).toBeInTheDocument();
  });

  it('renders 4 distribution tiers with cell counts and percentages', () => {
    render(<RiskDistributionChart summary={mockSummary} />);

    expect(screen.getByText(/500m cell breakdown/i)).toBeInTheDocument();
    expect(screen.getByText(/EXTREME/i)).toBeInTheDocument();
    expect(screen.getByText('50')).toBeInTheDocument();
    expect(screen.getByText('(5.0%)')).toBeInTheDocument();

    expect(screen.getByText(/HIGH/i)).toBeInTheDocument();
    expect(screen.getByText('150')).toBeInTheDocument();
    expect(screen.getByText('(15.0%)')).toBeInTheDocument();

    expect(screen.getByText(/MODERATE/i)).toBeInTheDocument();
    expect(screen.getByText('300')).toBeInTheDocument();
    expect(screen.getByText('(30.0%)')).toBeInTheDocument();

    expect(screen.getByText(/LOW/i)).toBeInTheDocument();
    expect(screen.getByText('500')).toBeInTheDocument();
    expect(screen.getByText('(50.0%)')).toBeInTheDocument();
  });

  it('triggers onSelectFilter when a risk tier row is clicked', () => {
    const onSelectFilter = vi.fn();
    render(
      <RiskDistributionChart
        summary={mockSummary}
        selectedFilter="ALL"
        onSelectFilter={onSelectFilter}
      />
    );

    const extremeBtn = screen.getByRole('button', { name: /filter map by extreme risk tier/i });
    fireEvent.click(extremeBtn);
    expect(onSelectFilter).toHaveBeenCalledWith('EXTREME');

    const lowBtn = screen.getByRole('button', { name: /filter map by low risk tier/i });
    fireEvent.click(lowBtn);
    expect(onSelectFilter).toHaveBeenCalledWith('LOW');
  });

  it('toggles filter back to ALL when clicking already selected filter', () => {
    const onSelectFilter = vi.fn();
    render(
      <RiskDistributionChart
        summary={mockSummary}
        selectedFilter="HIGH"
        onSelectFilter={onSelectFilter}
      />
    );

    const highBtn = screen.getByRole('button', { name: /filter map by high risk tier/i });
    fireEvent.click(highBtn);
    expect(onSelectFilter).toHaveBeenCalledWith('ALL');
  });
});
