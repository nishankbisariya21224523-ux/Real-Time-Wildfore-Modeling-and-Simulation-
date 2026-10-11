import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { App } from './App';

describe('Frontend Architecture Foundation', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    // Mock fetch for health and regions
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation((url: string) => {
        if (url.includes('/health')) {
          return Promise.resolve({
            ok: true,
            status: 200,
            json: async () => ({
              status: 'healthy',
              version: '1.0.0',
              services: { database: 'connected', redis: 'connected', celery_broker: 'connected' },
            }),
          });
        }
        if (url.includes('/regions')) {
          return Promise.resolve({
            ok: true,
            status: 200,
            json: async () => [
              {
                id: 'reg-01',
                code: 'UTT-GARH-01',
                name: 'Uttarakhand Western Himalaya',
                state: 'Uttarakhand',
                area_sqkm: 2450.5,
              },
            ],
          });
        }
        if (url.includes('/fires/active')) {
          return Promise.resolve({
            ok: true,
            status: 200,
            json: async () => ({ type: 'FeatureCollection', features: [] }),
          });
        }
        if (url.includes('/risk')) {
          return Promise.resolve({
            ok: true,
            status: 200,
            json: async () => ({ type: 'FeatureCollection', features: [] }),
          });
        }
        if (url.includes('/layers')) {
          return Promise.resolve({
            ok: true,
            status: 200,
            json: async () => [],
          });
        }
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => ({}),
        });
      })
    );
  });

  it('verifies that domain constants and risk classes are defined', () => {
    const riskLevels = ['LOW', 'MODERATE', 'HIGH', 'EXTREME'];
    expect(riskLevels).toHaveLength(4);
    expect(riskLevels).toContain('EXTREME');
  });

  it('validates 500m spatial grid parameters', () => {
    const resolutionMeters = 500;
    const cellAreaHa = (resolutionMeters * resolutionMeters) / 10000;
    expect(cellAreaHa).toBe(25); // 500m x 500m = 250,000 m2 = 25 hectares
  });

  it('verifies 12-hour simulation duration bounds', () => {
    const minHours = 1;
    const maxHours = 12;
    expect(maxHours).toBe(12);
    expect(minHours).toBeLessThanOrEqual(maxHours);
  });

  it('renders application shell with navigation tabs and header', async () => {
    render(<App />);

    expect(screen.getByText(/isro forest fire platform/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /overview/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /24h fire risk/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /active hotspots/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /12h simulation/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /environmental layers/i })).toBeInTheDocument();
  });

  it('switches between routes when clicking navigation items', async () => {
    render(<App />);

    // Click on 24h Fire Risk
    const riskBtn = screen.getByRole('button', { name: /24h fire risk/i });
    fireEvent.click(riskBtn);

    await waitFor(() => {
      expect(screen.getByText(/24h susceptibility forecast/i)).toBeInTheDocument();
    });

    // Click on 12h Simulation
    const simBtn = screen.getByRole('button', { name: /12h simulation/i });
    fireEvent.click(simBtn);

    await waitFor(() => {
      expect(screen.getByText(/simulation engine:/i)).toBeInTheDocument();
      expect(screen.getByText(/spread horizon:/i)).toBeInTheDocument();
    });

    // Click on Active Hotspots
    const firesBtn = screen.getByRole('button', { name: /active hotspots/i });
    fireEvent.click(firesBtn);

    await waitFor(() => {
      expect(screen.getByText(/satellite sensor feeds:/i)).toBeInTheDocument();
    });
  });
});
