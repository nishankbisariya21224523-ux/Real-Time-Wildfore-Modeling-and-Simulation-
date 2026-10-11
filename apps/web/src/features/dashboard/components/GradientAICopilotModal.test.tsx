import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { GradientAICopilotModal } from './GradientAICopilotModal';
import * as gradientAiApi from '../../../services/api/gradientAi';

describe('GradientAICopilotModal', () => {
  it('renders Gradient AI button', () => {
    render(
      <GradientAICopilotModal
        regionName="Garhwal Division"
        fireDangerIndex={75.0}
        meanRisk={0.65}
        activeHotspots={3}
      />
    );

    expect(screen.getByRole('button', { name: /Gradient AI/i })).toBeInTheDocument();
  });

  it('opens modal and renders all 4 Gradient AI feature tabs', async () => {
    const mockExplain: gradientAiApi.RiskExplanationResult = {
      region_name: 'Garhwal Division',
      predicted_probability: 0.72,
      risk_class: 'EXTREME',
      explanation: 'Elevated risk driven by low humidity and high slope.',
      feature_importance: [
        {
          feature: 'relative_humidity_pct',
          value: '18.0%',
          impact: 'CRITICAL',
          contribution_direction: 'ELEVATING',
          physical_rationale: 'Desiccates 1-hr dead fuel moisture.',
        },
      ],
      model_version: 'risk-xgboost-v002',
      provider: 'digitalocean_gradient_ai',
      timestamp: new Date().toISOString(),
    };

    vi.spyOn(gradientAiApi, 'explainRiskFeatures').mockResolvedValue(mockExplain);

    render(
      <GradientAICopilotModal
        regionName="Garhwal Division"
        fireDangerIndex={78.0}
        meanRisk={0.72}
        activeHotspots={4}
      />
    );

    fireEvent.click(screen.getByRole('button', { name: /Gradient AI/i }));

    expect(screen.getByText(/Explain Elevated Risk/i)).toBeInTheDocument();
    expect(screen.getByText(/Map & Spread Copilot/i)).toBeInTheDocument();
    expect(screen.getByText(/Preparedness Guidance/i)).toBeInTheDocument();
    expect(screen.getByText(/Regional Situation Brief/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText(/Elevated risk driven by low humidity/i)).toBeInTheDocument();
      expect(screen.getByText(/relative_humidity_pct/i)).toBeInTheDocument();
    });
  });

  it('answers questions in Map & Spread Copilot tab', async () => {
    const mockQA: gradientAiApi.CopilotQuestionResult = {
      question: 'How does wind affect spread?',
      answer: 'Southwest winds increase flame front forward velocity along ridges.',
      context_region: 'Garhwal Division',
      provider: 'digitalocean_gradient_ai',
      timestamp: new Date().toISOString(),
    };

    vi.spyOn(gradientAiApi, 'askCopilot').mockResolvedValue(mockQA);

    render(
      <GradientAICopilotModal
        regionName="Garhwal Division"
        fireDangerIndex={78.0}
        meanRisk={0.72}
        activeHotspots={4}
      />
    );

    fireEvent.click(screen.getByRole('button', { name: /Gradient AI/i }));
    fireEvent.click(screen.getByText(/Map & Spread Copilot/i));

    const input = screen.getByPlaceholderText(/Ask questions about Garhwal Division/i);
    fireEvent.change(input, { target: { value: 'How does wind affect spread?' } });
    fireEvent.click(screen.getByRole('button', { name: /Send/i }));

    await waitFor(() => {
      expect(screen.getByText(/Southwest winds increase flame front forward velocity/i)).toBeInTheDocument();
    });
  });

  it('retrieves preparedness guidance doctrine', async () => {
    const mockGuidance: gradientAiApi.GuidanceRetrievalResult = {
      query: 'Evacuation',
      total_documents_searched: 4,
      retrieved_guidance: [
        {
          document_id: 'DOC-NDMA-2020',
          title: 'NDMA Forest Fire Evacuation Protocol',
          jurisdiction: 'NDMA / Ministry of Environment & Forests (India)',
          excerpt: 'Tier 1 alert requires clearing perimeter access routes.',
        },
      ],
      timestamp: new Date().toISOString(),
    };

    vi.spyOn(gradientAiApi, 'retrievePreparednessGuidance').mockResolvedValue(mockGuidance);

    render(
      <GradientAICopilotModal
        regionName="Garhwal Division"
        fireDangerIndex={78.0}
        meanRisk={0.72}
        activeHotspots={4}
      />
    );

    fireEvent.click(screen.getByRole('button', { name: /Gradient AI/i }));
    fireEvent.click(screen.getByText(/Preparedness Guidance/i));

    await waitFor(() => {
      expect(screen.getByText(/NDMA Forest Fire Evacuation Protocol/i)).toBeInTheDocument();
      expect(screen.getByText(/Tier 1 alert requires clearing perimeter access routes/i)).toBeInTheDocument();
    });
  });

  it('generates regional situation brief', async () => {
    const mockBrief: gradientAiApi.SituationBriefResult = {
      region_name: 'Garhwal Division',
      fire_danger_index: 85.0,
      active_hotspots: 5,
      situation_brief: 'URGENT: Active flame perimeters expanding northeast.',
      evidence_citations: [
        'Satellite Sensor: MODIS / VIIRS confirmed 5 thermal anomalies',
        'Numerical Telemetry: FDI 85.0/100',
      ],
      provider: 'digitalocean_gradient_ai',
      timestamp: new Date().toISOString(),
    };

    vi.spyOn(gradientAiApi, 'generateSituationBrief').mockResolvedValue(mockBrief);

    render(
      <GradientAICopilotModal
        regionName="Garhwal Division"
        fireDangerIndex={85.0}
        meanRisk={0.8}
        activeHotspots={5}
      />
    );

    fireEvent.click(screen.getByRole('button', { name: /Gradient AI/i }));
    fireEvent.click(screen.getByText(/Regional Situation Brief/i));

    await waitFor(() => {
      expect(screen.getByText(/URGENT: Active flame perimeters expanding northeast/i)).toBeInTheDocument();
      expect(screen.getByText(/MODIS \/ VIIRS confirmed 5 thermal anomalies/i)).toBeInTheDocument();
    });
  });
});
