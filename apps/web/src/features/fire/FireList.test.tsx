import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { FireList } from './components/FireList';
import { FireHotspotProperties } from '../../types/domain';

describe('FireList Component', () => {
  const mockFires: FireHotspotProperties[] = [
    {
      id: 'fire-001',
      detection_time: '2026-10-06T12:00:00Z',
      satellite: 'VIIRS NOAA-20',
      confidence: 'high',
      frp_mw: 42.5,
      brightness_temperature_kelvin: 345.2,
      status: 'active',
    },
    {
      id: 'fire-002',
      detection_time: '2026-10-06T13:30:00Z',
      satellite: 'MODIS Aqua',
      confidence: 'nominal',
      frp_mw: 18.0,
      brightness_temperature_kelvin: 312.0,
      status: 'active',
    },
  ];

  it('renders fire hotspot items with FRP and sensor metadata', () => {
    render(
      <FireList
        fires={mockFires}
        selectedFireId={null}
        onSelectFire={vi.fn()}
      />
    );

    expect(screen.getByText('VIIRS NOAA-20')).toBeInTheDocument();
    expect(screen.getByText('42.5 MW')).toBeInTheDocument();
    expect(screen.getByText('MODIS Aqua')).toBeInTheDocument();
    expect(screen.getByText('18.0 MW')).toBeInTheDocument();
  });

  it('invokes onSelectFire when a hotspot card is clicked', () => {
    const handleSelect = vi.fn();
    render(
      <FireList
        fires={mockFires}
        selectedFireId={null}
        onSelectFire={handleSelect}
      />
    );

    fireEvent.click(screen.getByText('VIIRS NOAA-20'));
    expect(handleSelect).toHaveBeenCalledWith(mockFires[0]);
  });

  it('renders an empty state when no active fires are present', () => {
    render(
      <FireList
        fires={[]}
        selectedFireId={null}
        onSelectFire={vi.fn()}
      />
    );

    expect(screen.getByText(/no active fires/i)).toBeInTheDocument();
  });
});
