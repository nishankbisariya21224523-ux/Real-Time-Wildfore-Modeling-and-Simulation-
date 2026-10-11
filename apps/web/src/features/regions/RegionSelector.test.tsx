import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { RegionSelector } from './components/RegionSelector';
import { RegionSummary } from '../../types/domain';

describe('RegionSelector Component', () => {
  const mockRegions: RegionSummary[] = [
    {
      id: 'reg-01',
      code: 'UTT-GARH-01',
      name: 'Uttarakhand Western Himalaya',
      state: 'Uttarakhand',
      area_sqkm: 2450.5,
    },
    {
      id: 'reg-02',
      code: 'OD-SIM-01',
      name: 'Similipal Biosphere Reserve',
      state: 'Odisha',
      area_sqkm: 2750.0,
    },
  ];

  it('renders region options correctly', () => {
    const handleSelect = vi.fn();
    render(
      <RegionSelector
        regions={mockRegions}
        selectedRegionId="reg-01"
        onSelectRegion={handleSelect}
      />
    );

    const select = screen.getByLabelText(/select monitored forest region/i) as HTMLSelectElement;
    expect(select).toBeInTheDocument();
    expect(select.children).toHaveLength(2);
    expect(select.value).toBe('reg-01');
  });

  it('triggers onSelectRegion callback when selection changes', () => {
    const handleSelect = vi.fn();
    render(
      <RegionSelector
        regions={mockRegions}
        selectedRegionId="reg-01"
        onSelectRegion={handleSelect}
      />
    );

    const select = screen.getByLabelText(/select monitored forest region/i);
    fireEvent.change(select, { target: { value: 'reg-02' } });

    expect(handleSelect).toHaveBeenCalledWith('reg-02');
  });

  it('shows loading state when regions are being fetched', () => {
    render(
      <RegionSelector
        regions={[]}
        selectedRegionId=""
        onSelectRegion={vi.fn()}
        isLoading={true}
      />
    );

    expect(screen.getByText(/loading regions\.\.\./i)).toBeInTheDocument();
  });
});
