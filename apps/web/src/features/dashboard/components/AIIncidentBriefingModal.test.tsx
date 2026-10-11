import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { AIIncidentBriefingModal } from './AIIncidentBriefingModal';
import * as aiApi from '../../../services/api/ai';
import * as alertsApi from '../../../services/api/alerts';

describe('AIIncidentBriefingModal', () => {
  it('renders DO AI SITREP button', () => {
    render(
      <AIIncidentBriefingModal
        regionName="Garhwal Division"
        fireDangerIndex={75.0}
        activeHotspots={3}
      />
    );

    expect(screen.getByRole('button', { name: /DO AI SITREP/i })).toBeInTheDocument();
  });

  it('opens modal and displays briefing on click', async () => {
    const mockAdvisory: aiApi.IncidentBriefingResult = {
      region_name: 'Garhwal Division',
      threat_level: 'CRITICAL / EXTREME',
      fire_danger_index: 82.0,
      summary: 'Wildfire threat elevated due to dry winds.',
      tactical_actions: [
        'Deploy heavy retardant tankers',
        'Establish bulldozer firebreaks',
      ],
      evacuation_directive: 'MANDATORY EVACUATION',
      provider: 'digitalocean_genai',
      model: 'meta-llama/llama-3.3-70b-instruct',
      timestamp: new Date().toISOString(),
    };

    vi.spyOn(aiApi, 'generateAIAdvisory').mockResolvedValue(mockAdvisory);

    render(
      <AIIncidentBriefingModal
        regionName="Garhwal Division"
        fireDangerIndex={82.0}
        activeHotspots={5}
      />
    );

    fireEvent.click(screen.getByRole('button', { name: /DO AI SITREP/i }));

    await waitFor(() => {
      expect(screen.getByText(/Wildfire threat elevated due to dry winds/i)).toBeInTheDocument();
      expect(screen.getByText(/CRITICAL \/ EXTREME/i)).toBeInTheDocument();
      expect(screen.getByText(/Deploy heavy retardant tankers/i)).toBeInTheDocument();
    });
  });

  it('broadcasts emergency alert to Telegram when button clicked', async () => {
    const mockAdvisory: aiApi.IncidentBriefingResult = {
      region_name: 'Garhwal Division',
      threat_level: 'CRITICAL / EXTREME',
      fire_danger_index: 85.0,
      summary: 'Extreme fire danger.',
      tactical_actions: ['Evacuate immediate sector'],
      evacuation_directive: 'MANDATORY EVACUATION',
      provider: 'digitalocean_genai',
      model: 'meta-llama/llama-3.3-70b-instruct',
      timestamp: new Date().toISOString(),
    };
    vi.spyOn(aiApi, 'generateAIAdvisory').mockResolvedValue(mockAdvisory);

    const mockAlertResult = {
      status: 'simulated_delivered',
      provider: 'telegram_simulation_mode',
      channel: '@WildfireAlerts',
      message_id: 12345,
      formatted_message: '🚨 EMERGENCY WILDFIRE CIVIL ALERT 🚨',
      timestamp: new Date().toISOString(),
    };
    vi.spyOn(alertsApi, 'broadcastTelegramAlert').mockResolvedValue(mockAlertResult);

    render(
      <AIIncidentBriefingModal
        regionName="Garhwal Division"
        fireDangerIndex={85.0}
        activeHotspots={6}
      />
    );

    fireEvent.click(screen.getByRole('button', { name: /DO AI SITREP/i }));
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Broadcast to Telegram/i })).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('button', { name: /Broadcast to Telegram/i }));
    await waitFor(() => {
      expect(screen.getByText(/Dispatched to @WildfireAlerts/i)).toBeInTheDocument();
    });
  });
});

