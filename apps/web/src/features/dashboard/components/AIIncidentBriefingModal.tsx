import React, { useState } from 'react';
import { generateAIAdvisory, IncidentBriefingResult } from '../../../services/api/ai';
import { broadcastTelegramAlert, TelegramAlertResult } from '../../../services/api/alerts';

export interface AIIncidentBriefingModalProps {
  regionName: string;
  fireDangerIndex: number;
  temperatureC?: number;
  relativeHumidity?: number;
  windSpeedKmh?: number;
  windDirectionDeg?: number;
  activeHotspots: number;
}

export const AIIncidentBriefingModal: React.FC<AIIncidentBriefingModalProps> = ({
  regionName,
  fireDangerIndex,
  temperatureC = 34.5,
  relativeHumidity = 18.0,
  windSpeedKmh = 28.0,
  windDirectionDeg = 210.0,
  activeHotspots,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [advisory, setAdvisory] = useState<IncidentBriefingResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [telegramSending, setTelegramSending] = useState(false);
  const [telegramResult, setTelegramResult] = useState<TelegramAlertResult | null>(null);
  const [telegramError, setTelegramError] = useState<string | null>(null);


  const handleOpenAndFetch = async () => {
    setIsOpen(true);
    setLoading(true);
    setError(null);
    try {
      const data = await generateAIAdvisory({
        region_name: regionName,
        fire_danger_index: fireDangerIndex,
        temperature_c: temperatureC,
        relative_humidity: relativeHumidity,
        wind_speed_kmh: windSpeedKmh,
        wind_direction_deg: windDirectionDeg,
        active_hotspots: activeHotspots,
        slope_pct: 14.0,
        fuel_type: 'Timber / Mixed Conifer',
        evacuation_status: activeHotspots > 0 ? 'WARNING' : 'ADVISORY',
      });
      setAdvisory(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to generate advisory';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleBroadcastTelegram = async () => {
    if (!advisory) return;
    setTelegramSending(true);
    setTelegramError(null);
    try {
      const res = await broadcastTelegramAlert({
        region_name: regionName,
        threat_level: advisory.threat_level,
        fire_danger_index: advisory.fire_danger_index,
        evacuation_status: advisory.evacuation_directive,
        safety_instructions: advisory.tactical_actions,
        custom_note: `Civil emergency alert for ${regionName}. Follow directives from Incident Command.`,
      });
      setTelegramResult(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to broadcast Telegram alert';
      setTelegramError(msg);
    } finally {
      setTelegramSending(false);
    }
  };

  return (
    <>
      <button
        onClick={handleOpenAndFetch}
        title="Generate AI-driven Incident Commander SITREP via DigitalOcean GenAI"
        className="px-2.5 py-1 rounded-[2px] bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 border border-blue-500/40 transition-colors font-mono text-[11px] font-semibold flex items-center space-x-1"
      >
        <span>⚡</span>
        <span>DO AI SITREP</span>
      </button>

      {isOpen && (
        <div className="fixed inset-0 z-[1000] flex items-center justify-center bg-black/75 backdrop-blur-xs p-4 pointer-events-auto">
          <div className="bg-ops-panel border border-ops-border rounded-[4px] max-w-2xl w-full p-5 text-txt-primary shadow-2xl font-mono flex flex-col max-h-[88vh]">
            {/* Header */}
            <div className="flex justify-between items-center border-b border-ops-border pb-3 shrink-0">
              <div className="flex items-center space-x-2">
                <span className="text-base text-blue-400">🌊</span>
                <div>
                  <h3 className="text-sm font-bold text-txt-primary uppercase tracking-wide">
                    DigitalOcean AI · Wildfire SITREP
                  </h3>
                  <div className="text-[10px] text-txt-muted">
                    SECTOR: {regionName.toUpperCase()} · TELEMETRY SYNTHESIS
                  </div>
                </div>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="text-txt-muted hover:text-txt-primary text-base font-bold px-2 py-0.5 rounded border border-transparent hover:border-ops-border transition-colors"
              >
                ✕
              </button>
            </div>

            {/* Content Body */}
            <div className="py-4 overflow-y-auto flex-1 space-y-4">
              {loading && (
                <div className="py-12 flex flex-col items-center justify-center space-y-3">
                  <div className="w-7 h-7 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
                  <p className="text-xs text-txt-muted">
                    Synthesizing real-time telemetry via DigitalOcean GenAI...
                  </p>
                </div>
              )}

              {error && (
                <div className="p-3 bg-danger/10 border border-danger/30 rounded text-danger text-xs">
                  {error}
                </div>
              )}

              {!loading && advisory && (
                <>
                  {/* Status Badges */}
                  <div className="grid grid-cols-2 gap-2 bg-ops-surface p-2.5 rounded border border-ops-border text-xs">
                    <div>
                      <span className="text-[10px] text-txt-muted uppercase">Threat Level</span>
                      <p className="font-bold text-danger text-sm">{advisory.threat_level}</p>
                    </div>
                    <div className="text-right">
                      <span className="text-[10px] text-txt-muted uppercase">Civil Directive</span>
                      <p className="font-semibold text-amber text-xs">{advisory.evacuation_directive}</p>
                    </div>
                  </div>

                  {/* Summary */}
                  <div>
                    <div className="text-[11px] font-bold text-txt-secondary uppercase tracking-wider mb-1">
                      Incident Commander Briefing
                    </div>
                    <div className="bg-ops-bg p-3 rounded border border-ops-border text-xs text-txt-secondary whitespace-pre-line leading-relaxed">
                      {advisory.summary}
                    </div>
                  </div>

                  {/* Tactical Directives */}
                  <div>
                    <div className="text-[11px] font-bold text-txt-secondary uppercase tracking-wider mb-1.5">
                      Tactical Containment Directives
                    </div>
                    <div className="space-y-1.5">
                      {advisory.tactical_actions.map((action, idx) => (
                        <div
                          key={idx}
                          className="flex items-start space-x-2 bg-ops-surface/60 p-2 rounded border border-ops-border/60 text-xs text-txt-primary"
                        >
                          <span className="text-blue-400 font-bold shrink-0">▸</span>
                          <span>{action}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Telegram Civil Alert Broadcasting Panel */}
                  <div className="bg-ops-surface p-3 rounded border border-sky-500/30 space-y-2">
                    <div className="flex justify-between items-center">
                      <div className="flex items-center space-x-2">
                        <span className="text-base text-sky-400">✈️</span>
                        <div>
                          <div className="text-[11px] font-bold text-txt-primary uppercase">
                            Telegram Resident Civil Alert
                          </div>
                          <div className="text-[10px] text-txt-muted">
                            Broadcast real-time evacuation notice to local residents
                          </div>
                        </div>
                      </div>
                      <button
                        onClick={handleBroadcastTelegram}
                        disabled={telegramSending}
                        className="px-3 py-1 rounded-[2px] bg-sky-600 hover:bg-sky-500 text-white font-mono text-[11px] font-semibold flex items-center space-x-1.5 transition-colors disabled:opacity-50"
                      >
                        <span>📢</span>
                        <span>{telegramSending ? 'Broadcasting...' : 'Broadcast to Telegram'}</span>
                      </button>
                    </div>

                    {telegramError && (
                      <div className="p-2 bg-danger/10 border border-danger/30 rounded text-danger text-[11px]">
                        {telegramError}
                      </div>
                    )}

                    {telegramResult && (
                      <div className="p-2.5 bg-sky-950/40 border border-sky-500/40 rounded text-sky-300 text-xs space-y-1.5">
                        <div className="font-bold flex items-center gap-1.5 text-[11px]">
                          <span>✅</span>
                          <span>Dispatched to {telegramResult.channel} ({telegramResult.provider})</span>
                        </div>
                        <pre className="p-2 bg-black/60 rounded text-[10px] text-slate-300 font-mono whitespace-pre-wrap max-h-32 overflow-y-auto border border-ops-border/60">
                          {telegramResult.formatted_message}
                        </pre>
                      </div>
                    )}
                  </div>

                  {/* Metadata Footer */}
                  <div className="pt-2 text-[10px] text-txt-muted flex justify-between items-center border-t border-ops-border">
                    <span>
                      ENGINE: {advisory.provider} ({advisory.model})
                    </span>
                    <span>
                      {new Date(advisory.timestamp).toLocaleTimeString()} UTC
                    </span>
                  </div>
                </>
              )}
            </div>

            {/* Footer Buttons */}
            <div className="pt-3 border-t border-ops-border flex justify-end space-x-2 shrink-0">
              <button
                onClick={() => setIsOpen(false)}
                className="px-3 py-1.5 rounded-[2px] bg-ops-surface hover:bg-ops-hover text-txt-primary border border-ops-border text-xs"
              >
                Close
              </button>
              <button
                onClick={handleOpenAndFetch}
                disabled={loading}
                className="px-3 py-1.5 rounded-[2px] bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold"
              >
                Refresh SITREP
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
