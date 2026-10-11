import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { RiskLegend } from './components/RiskLegend';
import { RiskSummaryCard } from './components/RiskSummaryCard';
import { RiskSummary } from '../../types/domain';

describe('Risk Visualization Components', () => {
  it('renders all 4 risk classes in the legend', () => {
    render(<RiskLegend />);

    expect(screen.getByText(/susceptibility scale/i)).toBeInTheDocument();
    expect(screen.getByText(/low/i)).toBeInTheDocument();
    expect(screen.getByText(/moderate/i)).toBeInTheDocument();
    expect(screen.getByText(/high/i)).toBeInTheDocument();
    expect(screen.getByText(/extreme/i)).toBeInTheDocument();
  });

  it('renders regional risk breakdown in RiskSummaryCard', () => {
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

    render(<RiskSummaryCard summary={mockSummary} />);

    expect(screen.getByText('1,000')).toBeInTheDocument();
    expect(screen.getByText('200')).toBeInTheDocument(); // high + extreme
    expect(screen.getByText(/mean: 35\.0%/i)).toBeInTheDocument();
  });
});
