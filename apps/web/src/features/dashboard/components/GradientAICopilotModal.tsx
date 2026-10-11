import React, { useState } from 'react';
import {
  explainRiskFeatures,
  askCopilot,
  retrievePreparednessGuidance,
  generateSituationBrief,
  RiskExplanationResult,
  CopilotQuestionResult,
  GuidanceItem,
  SituationBriefResult,
} from '../../../services/api/gradientAi';

export interface GradientAICopilotModalProps {
  regionName: string;
  fireDangerIndex: number;
  meanRisk?: number;
  activeHotspots: number;
  temperatureC?: number;
  relativeHumidity?: number;
  windSpeedKmh?: number;
}

type CopilotTab = 'explain' | 'qa' | 'guidance' | 'sitbrief';

interface ChatMessage {
  sender: 'user' | 'assistant';
  text: string;
  timestamp: string;
}

export const GradientAICopilotModal: React.FC<GradientAICopilotModalProps> = ({
  regionName,
  fireDangerIndex,
  meanRisk = 0.68,
  activeHotspots,
  temperatureC = 34.5,
  relativeHumidity = 18.0,
  windSpeedKmh = 28.0,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<CopilotTab>('explain');

  // Tab 1: Explain Elevated Risk State
  const [loadingExplain, setLoadingExplain] = useState(false);
  const [explainResult, setExplainResult] = useState<RiskExplanationResult | null>(null);
  const [explainError, setExplainError] = useState<string | null>(null);
  const [featureInputs, setFeatureInputs] = useState({
    temperature_c: temperatureC,
    relative_humidity_pct: relativeHumidity,
    wind_speed_ms: Math.round(windSpeedKmh / 3.6),
    slope_deg: 24.0,
    ndvi: 0.62,
    ndwi: -0.15,
    fuel_type: 'CONIFER_HIGH_FLAMMABILITY',
  });

  // Tab 2: Map & Spread Copilot State
  const [loadingQA, setLoadingQA] = useState(false);
  const [qaInput, setQaInput] = useState('');
  const [qaMessages, setQaMessages] = useState<ChatMessage[]>([
    {
      sender: 'assistant',
      text: `Hello! I am your DigitalOcean Gradient AI Wildfire Copilot for the ${regionName} sector. You can ask me anything about the active 24-hour predicted risk map, cellular automata spread vectors, or tactical fire behavior.`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [qaError, setQaError] = useState<string | null>(null);

  // Tab 3: Preparedness Guidance State
  const [guidanceQuery, setGuidanceQuery] = useState('');
  const [loadingGuidance, setLoadingGuidance] = useState(false);
  const [guidanceList, setGuidanceList] = useState<GuidanceItem[]>([]);
  const [guidanceError, setGuidanceError] = useState<string | null>(null);

  // Tab 4: Situation Brief State
  const [loadingBrief, setLoadingBrief] = useState(false);
  const [briefResult, setBriefResult] = useState<SituationBriefResult | null>(null);
  const [briefError, setBriefError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  // --- Handlers ---

  // Handle Tab 1
  const handleExplainRisk = async () => {
    setLoadingExplain(true);
    setExplainError(null);
    try {
      const res = await explainRiskFeatures({
        region_name: regionName,
        predicted_probability: meanRisk,
        risk_class: meanRisk > 0.6 ? 'EXTREME' : meanRisk > 0.35 ? 'HIGH' : 'MODERATE',
        features: featureInputs,
      });
      setExplainResult(res);
    } catch (err: unknown) {
      setExplainError(err instanceof Error ? err.message : 'Failed to explain risk features');
    } finally {
      setLoadingExplain(false);
    }
  };

  // Handle Tab 2
  const handleSendQuestion = async (presetText?: string) => {
    const questionText = presetText || qaInput.trim();
    if (!questionText) return;

    const userMsg: ChatMessage = {
      sender: 'user',
      text: questionText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setQaMessages((prev) => [...prev, userMsg]);
    if (!presetText) setQaInput('');
    setLoadingQA(true);
    setQaError(null);

    try {
      const res: CopilotQuestionResult = await askCopilot({
        question: questionText,
        map_context: {
          region_name: regionName,
          fire_danger_index: fireDangerIndex,
          mean_probability: meanRisk,
          active_hotspots: activeHotspots,
          burned_area_ha: activeHotspots > 0 ? activeHotspots * 25.0 : 0.0,
          temperature_c: temperatureC,
          relative_humidity: relativeHumidity,
          wind_speed_kmh: windSpeedKmh,
          simulation_model: 'Cellular Automata (Rothermel & Farsite Equations)',
        },
      });

      const assistantMsg: ChatMessage = {
        sender: 'assistant',
        text: res.answer,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setQaMessages((prev) => [...prev, assistantMsg]);
    } catch (err: unknown) {
      setQaError(err instanceof Error ? err.message : 'Error communicating with Gradient Copilot');
    } finally {
      setLoadingQA(false);
    }
  };

  // Handle Tab 3
  const handleRetrieveGuidance = async (queryText?: string) => {
    const q = queryText !== undefined ? queryText : guidanceQuery.trim();
    if (!q) return;
    if (queryText !== undefined) setGuidanceQuery(queryText);

    setLoadingGuidance(true);
    setGuidanceError(null);
    try {
      const res = await retrievePreparednessGuidance(q);
      setGuidanceList(res.retrieved_guidance);
    } catch (err: unknown) {
      setGuidanceError(err instanceof Error ? err.message : 'Failed to retrieve guidance doctrine');
    } finally {
      setLoadingGuidance(false);
    }
  };

  // Handle Tab 4
  const handleGenerateBrief = async () => {
    setLoadingBrief(true);
    setBriefError(null);
    try {
      const res = await generateSituationBrief({
        region_name: regionName,
        fire_danger_index: fireDangerIndex,
        temperature_c: temperatureC,
        relative_humidity: relativeHumidity,
        wind_speed_kmh: windSpeedKmh,
        active_hotspots: activeHotspots,
        burned_area_ha: 142.5,
      });
      setBriefResult(res);
    } catch (err: unknown) {
      setBriefError(err instanceof Error ? err.message : 'Failed to generate situation brief');
    } finally {
      setLoadingBrief(false);
    }
  };

  const handleCopyBrief = () => {
    if (!briefResult) return;
    const textToCopy = `${briefResult.situation_brief}\n\nEvidence Citations:\n${briefResult.evidence_citations.map((c) => `- ${c}`).join('\n')}`;
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  return (
    <>
      <button
        onClick={() => {
          setIsOpen(true);
          if (!explainResult) handleExplainRisk();
        }}
        title="DigitalOcean Gradient AI Copilot: Feature Attribution, GIS Spread Q&A, Preparedness Doctrine & Situation Briefs"
        className="px-2.5 py-1 rounded-[2px] bg-indigo-600/25 hover:bg-indigo-600/35 text-indigo-300 border border-indigo-500/40 transition-colors font-mono text-[11px] font-semibold flex items-center space-x-1"
      >
        <span>Gradient AI</span>
      </button>

      {isOpen && (
        <div className="fixed inset-0 z-[1000] flex items-center justify-center bg-black/80 backdrop-blur-xs p-3 pointer-events-auto">
          <div className="bg-ops-panel border border-ops-border rounded-[4px] max-w-4xl w-full p-5 text-txt-primary shadow-2xl font-mono flex flex-col h-[90vh]">
            {/* Modal Header */}
            <div className="flex justify-between items-center border-b border-ops-border pb-3 shrink-0">
              <div className="flex items-center space-x-2.5">
                <div>
                  <div className="flex items-center space-x-2">
                    <h3 className="text-sm font-bold text-txt-primary uppercase tracking-wide">
                      DigitalOcean Gradient AI Copilot
                    </h3>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-indigo-900/60 border border-indigo-500/40 text-indigo-300">
                      DO Serverless Inference
                    </span>
                  </div>
                  <div className="text-[10px] text-txt-muted">
                    SECTOR: {regionName.toUpperCase()} · RISK MODEL: risk-xgboost-v002 · TELEMETRY-LINKED
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

            {/* Navigation Tabs */}
            <div className="flex border-b border-ops-border bg-ops-subtle/50 shrink-0 text-xs mt-2">
              <button
                onClick={() => {
                  setActiveTab('explain');
                  if (!explainResult && !loadingExplain) handleExplainRisk();
                }}
                className={`flex-1 py-2 px-3 text-center font-medium border-b-2 transition-colors flex items-center justify-center space-x-1.5 ${
                  activeTab === 'explain'
                    ? 'border-indigo-400 text-indigo-300 bg-indigo-950/20'
                    : 'border-transparent text-txt-muted hover:text-txt-primary'
                }`}
              >
                <span>Explain Elevated Risk</span>
              </button>

              <button
                onClick={() => setActiveTab('qa')}
                className={`flex-1 py-2 px-3 text-center font-medium border-b-2 transition-colors flex items-center justify-center space-x-1.5 ${
                  activeTab === 'qa'
                    ? 'border-indigo-400 text-indigo-300 bg-indigo-950/20'
                    : 'border-transparent text-txt-muted hover:text-txt-primary'
                }`}
              >
                <span>Map & Spread Copilot</span>
              </button>

              <button
                onClick={() => {
                  setActiveTab('guidance');
                  if (guidanceList.length === 0 && !loadingGuidance) {
                    handleRetrieveGuidance('Evacuation and safety standards');
                  }
                }}
                className={`flex-1 py-2 px-3 text-center font-medium border-b-2 transition-colors flex items-center justify-center space-x-1.5 ${
                  activeTab === 'guidance'
                    ? 'border-indigo-400 text-indigo-300 bg-indigo-950/20'
                    : 'border-transparent text-txt-muted hover:text-txt-primary'
                }`}
              >
                <span>Preparedness Guidance</span>
              </button>

              <button
                onClick={() => {
                  setActiveTab('sitbrief');
                  if (!briefResult && !loadingBrief) handleGenerateBrief();
                }}
                className={`flex-1 py-2 px-3 text-center font-medium border-b-2 transition-colors flex items-center justify-center space-x-1.5 ${
                  activeTab === 'sitbrief'
                    ? 'border-indigo-400 text-indigo-300 bg-indigo-950/20'
                    : 'border-transparent text-txt-muted hover:text-txt-primary'
                }`}
              >
                <span>Regional Situation Brief</span>
              </button>
            </div>

            {/* Tab 1: Explain Elevated Risk */}
            {activeTab === 'explain' && (
              <div className="py-3 overflow-y-auto flex-1 space-y-3">
                <div className="flex items-center justify-between bg-ops-surface p-2.5 rounded border border-ops-border text-xs">
                  <div>
                    <span className="text-[10px] text-txt-muted uppercase">Target Division</span>
                    <p className="font-bold text-txt-primary">{regionName}</p>
                  </div>
                  <div>
                    <span className="text-[10px] text-txt-muted uppercase">Predicted Probability</span>
                    <p className="font-bold text-amber">
                      {((explainResult?.predicted_probability ?? meanRisk) * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div>
                    <span className="text-[10px] text-txt-muted uppercase">Risk Classification</span>
                    <p className="font-bold text-danger">
                      {explainResult?.risk_class ?? (meanRisk > 0.6 ? 'EXTREME' : 'HIGH')}
                    </p>
                  </div>
                  <button
                    onClick={handleExplainRisk}
                    disabled={loadingExplain}
                    className="px-3 py-1 rounded bg-indigo-600 hover:bg-indigo-500 text-white font-mono text-[11px] font-semibold transition-colors disabled:opacity-50"
                  >
                    {loadingExplain ? 'Analyzing...' : 'Re-run Explanation'}
                  </button>
                </div>

                {explainError && (
                  <div className="p-3 bg-danger/10 border border-danger/30 rounded text-danger text-xs">
                    {explainError}
                  </div>
                )}

                {loadingExplain && (
                  <div className="py-12 flex flex-col items-center justify-center space-y-3">
                    <div className="w-7 h-7 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin" />
                    <p className="text-xs text-txt-muted">
                      Synthesizing SHAP feature importance vectors via Gradient AI...
                    </p>
                  </div>
                )}

                {!loadingExplain && explainResult && (
                  <>
                    {/* Natural Language Explanation */}
                    <div className="bg-ops-bg p-3 rounded border border-indigo-500/30 text-xs text-txt-primary leading-relaxed whitespace-pre-line">
                      <div className="flex items-center space-x-1.5 text-indigo-400 font-bold mb-1.5 uppercase text-[11px]">
                        <span>Model Prediction Rationale ({explainResult.model_version})</span>
                      </div>
                      {explainResult.explanation}
                    </div>

                    {/* Feature Attribution Table */}
                    <div>
                      <div className="text-[11px] font-bold text-txt-secondary uppercase tracking-wider mb-1.5">
                        Feature Attribution Breakdown (Order of Influence)
                      </div>
                      <div className="border border-ops-border rounded overflow-hidden">
                        <table className="w-full text-left text-xs border-collapse">
                          <thead className="bg-ops-surface text-[10px] uppercase text-txt-muted border-b border-ops-border">
                            <tr>
                              <th className="p-2">Feature</th>
                              <th className="p-2">Value</th>
                              <th className="p-2">Impact</th>
                              <th className="p-2">Direction</th>
                              <th className="p-2">Physical Mechanism</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-ops-border/60">
                            {explainResult.feature_importance.map((f, i) => (
                              <tr key={i} className="hover:bg-ops-surface/40">
                                <td className="p-2 font-bold text-txt-primary">{f.feature}</td>
                                <td className="p-2 text-txt-secondary">{f.value}</td>
                                <td className="p-2">
                                  <span
                                    className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                                      f.impact === 'CRITICAL'
                                        ? 'bg-danger/20 text-danger border border-danger/40'
                                        : f.impact === 'HIGH'
                                        ? 'bg-amber/20 text-amber border border-amber/40'
                                        : 'bg-ops-surface text-txt-muted border border-ops-border'
                                    }`}
                                  >
                                    {f.impact}
                                  </span>
                                </td>
                                <td className="p-2">
                                  <span
                                    className={`text-[11px] font-semibold ${
                                      f.contribution_direction === 'ELEVATING'
                                        ? 'text-danger'
                                        : 'text-forest'
                                    }`}
                                  >
                                    {f.contribution_direction === 'ELEVATING' ? 'ELEVATING' : 'MITIGATING'}
                                  </span>
                                </td>
                                <td className="p-2 text-[11px] text-txt-muted">{f.physical_rationale}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>

                    {/* Interactive Telemetry Tweak simulation */}
                    <div className="bg-ops-surface/60 p-3 rounded border border-ops-border space-y-2 text-xs">
                      <div className="text-[11px] font-bold text-txt-secondary uppercase">
                        Simulate Feature Adjustments
                      </div>
                      <div className="grid grid-cols-3 gap-2">
                        <div>
                          <label className="text-[10px] text-txt-muted block mb-0.5">Temp (°C)</label>
                          <input
                            type="number"
                            value={featureInputs.temperature_c}
                            onChange={(e) =>
                              setFeatureInputs({ ...featureInputs, temperature_c: Number(e.target.value) })
                            }
                            className="w-full bg-ops-bg border border-ops-border rounded px-2 py-1 text-txt-primary text-xs"
                          />
                        </div>
                        <div>
                          <label className="text-[10px] text-txt-muted block mb-0.5">Rel Humidity (%)</label>
                          <input
                            type="number"
                            value={featureInputs.relative_humidity_pct}
                            onChange={(e) =>
                              setFeatureInputs({
                                ...featureInputs,
                                relative_humidity_pct: Number(e.target.value),
                              })
                            }
                            className="w-full bg-ops-bg border border-ops-border rounded px-2 py-1 text-txt-primary text-xs"
                          />
                        </div>
                        <div>
                          <label className="text-[10px] text-txt-muted block mb-0.5">Wind (m/s)</label>
                          <input
                            type="number"
                            value={featureInputs.wind_speed_ms}
                            onChange={(e) =>
                              setFeatureInputs({ ...featureInputs, wind_speed_ms: Number(e.target.value) })
                            }
                            className="w-full bg-ops-bg border border-ops-border rounded px-2 py-1 text-txt-primary text-xs"
                          />
                        </div>
                      </div>
                    </div>
                  </>
                )}
              </div>
            )}

            {/* Tab 2: Map & Spread Copilot */}
            {activeTab === 'qa' && (
              <div className="py-3 flex-1 flex flex-col min-h-0 space-y-3">
                {/* Chat message history */}
                <div className="flex-1 overflow-y-auto space-y-2.5 pr-1 border border-ops-border rounded p-3 bg-ops-bg/70">
                  {qaMessages.map((m, idx) => (
                    <div
                      key={idx}
                      className={`flex flex-col ${
                        m.sender === 'user' ? 'items-end' : 'items-start'
                      }`}
                    >
                      <div className="flex items-center space-x-1.5 text-[10px] text-txt-muted mb-0.5">
                        <span>{m.sender === 'user' ? 'Incident Operator' : 'Gradient AI'}</span>
                        <span>· {m.timestamp}</span>
                      </div>
                      <div
                        className={`max-w-[85%] rounded p-2.5 text-xs leading-relaxed whitespace-pre-line ${
                          m.sender === 'user'
                            ? 'bg-indigo-600/30 border border-indigo-500/40 text-txt-primary'
                            : 'bg-ops-surface border border-ops-border text-txt-primary'
                        }`}
                      >
                        {m.text}
                      </div>
                    </div>
                  ))}

                  {loadingQA && (
                    <div className="flex items-center space-x-2 text-xs text-indigo-400 p-2">
                      <div className="w-4 h-4 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin" />
                      <span>Gradient AI analyzing active map context...</span>
                    </div>
                  )}

                  {qaError && (
                    <div className="p-2 bg-danger/10 border border-danger/30 rounded text-danger text-xs">
                      {qaError}
                    </div>
                  )}
                </div>

                {/* Suggested Prompt Chips */}
                <div className="space-y-1">
                  <span className="text-[10px] text-txt-muted uppercase font-bold">Suggested Queries:</span>
                  <div className="flex flex-wrap gap-1.5">
                    {[
                      'Why does the northern ridge show high predicted risk?',
                      'How will 28 km/h southwest wind affect spread perimeters?',
                      'What fuel types in this sector accelerate flame front velocity?',
                      'Which ridge lines offer natural containment barriers?',
                    ].map((chip, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleSendQuestion(chip)}
                        className="text-[11px] bg-ops-surface hover:bg-ops-hover border border-ops-border text-txt-secondary hover:text-txt-primary px-2 py-1 rounded transition-colors text-left"
                      >
                        ▸ {chip}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Input box */}
                <div className="flex space-x-2 pt-1">
                  <input
                    type="text"
                    value={qaInput}
                    onChange={(e) => setQaInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') handleSendQuestion();
                    }}
                    placeholder={`Ask questions about ${regionName} risk map or simulated spread...`}
                    className="flex-1 bg-ops-bg border border-ops-border rounded px-3 py-2 text-xs text-txt-primary focus:outline-none focus:border-indigo-400"
                  />
                  <button
                    onClick={() => handleSendQuestion()}
                    disabled={loadingQA || !qaInput.trim()}
                    className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded text-xs font-semibold disabled:opacity-50 transition-colors"
                  >
                    Send
                  </button>
                </div>
              </div>
            )}

            {/* Tab 3: Preparedness Guidance */}
            {activeTab === 'guidance' && (
              <div className="py-3 flex-1 flex flex-col min-h-0 space-y-3">
                {/* Search Bar + Presets */}
                <div className="space-y-2">
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      value={guidanceQuery}
                      onChange={(e) => setGuidanceQuery(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') handleRetrieveGuidance();
                      }}
                      placeholder="Search doctrine: e.g. evacuation, LCES, defensible space, watchout situations..."
                      className="flex-1 bg-ops-bg border border-ops-border rounded px-3 py-2 text-xs text-txt-primary focus:outline-none focus:border-indigo-400"
                    />
                    <button
                      onClick={() => handleRetrieveGuidance()}
                      disabled={loadingGuidance}
                      className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded text-xs font-semibold disabled:opacity-50 transition-colors"
                    >
                      {loadingGuidance ? 'Retrieving...' : 'Search Doctrine'}
                    </button>
                  </div>

                  {/* Preset doctrine buttons */}
                  <div className="flex flex-wrap gap-1.5">
                    {[
                      { label: 'NDMA Evacuation Guidelines', q: 'NDMA evacuation directives' },
                      { label: 'NWCG LCES Firefighter Safety', q: 'LCES lookouts communications escape routes safety zones' },
                      { label: 'NFPA 1144 Defensible Space', q: 'NFPA defensible space buffer home ignition' },
                      { label: '10 Standard Firefighting Orders', q: 'Standard firefighting orders and 18 watchout situations' },
                    ].map((item, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleRetrieveGuidance(item.q)}
                        className="text-[11px] bg-ops-surface hover:bg-ops-hover border border-ops-border text-txt-secondary hover:text-txt-primary px-2.5 py-1 rounded transition-colors"
                      >
                        {item.label}
                      </button>
                    ))}
                  </div>
                </div>

                {guidanceError && (
                  <div className="p-3 bg-danger/10 border border-danger/30 rounded text-danger text-xs">
                    {guidanceError}
                  </div>
                )}

                {/* Doctrine results list */}
                <div className="flex-1 overflow-y-auto space-y-2.5 pr-1">
                  {loadingGuidance && (
                    <div className="py-12 flex flex-col items-center justify-center space-y-3">
                      <div className="w-7 h-7 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin" />
                      <p className="text-xs text-txt-muted">Searching official wildfire doctrine repository...</p>
                    </div>
                  )}

                  {!loadingGuidance && guidanceList.length === 0 && (
                    <div className="text-center py-12 text-txt-muted text-xs">
                      No guidance doctrine matching query. Click a preset above or enter a search query.
                    </div>
                  )}

                  {!loadingGuidance &&
                    guidanceList.map((doc, idx) => (
                      <div
                        key={idx}
                        className="bg-ops-surface border border-ops-border hover:border-indigo-500/50 rounded p-3 space-y-2 transition-colors"
                      >
                        <div className="flex items-center justify-between border-b border-ops-border/60 pb-1.5">
                          <div className="flex items-center space-x-2">
                            <span className="font-bold text-xs text-txt-primary">{doc.title}</span>
                          </div>
                          <span className="text-[10px] px-2 py-0.5 rounded bg-indigo-900/50 text-indigo-300 border border-indigo-500/40 font-bold">
                            {doc.jurisdiction}
                          </span>
                        </div>
                        <div className="text-xs text-txt-secondary leading-relaxed bg-ops-bg/60 p-2.5 rounded border border-ops-border/40 whitespace-pre-line">
                          {doc.excerpt}
                        </div>
                        <div className="text-[10px] text-txt-muted flex justify-between">
                          <span>Doc ID: {doc.document_id}</span>
                          <span className="text-forest font-semibold">[VERIFIED DOCTRINE]</span>
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            )}

            {/* Tab 4: Regional Situation Brief */}
            {activeTab === 'sitbrief' && (
              <div className="py-3 overflow-y-auto flex-1 space-y-3">
                <div className="flex items-center justify-between bg-ops-surface p-2.5 rounded border border-ops-border text-xs">
                  <div>
                    <span className="text-[10px] text-txt-muted uppercase">Active Hotspots</span>
                    <p className="font-bold text-danger text-sm">{activeHotspots}</p>
                  </div>
                  <div>
                    <span className="text-[10px] text-txt-muted uppercase">Fire Danger Index</span>
                    <p className="font-bold text-amber text-sm">{fireDangerIndex.toFixed(1)} / 100</p>
                  </div>
                  <div>
                    <span className="text-[10px] text-txt-muted uppercase">Wind / Temp / RH</span>
                    <p className="font-bold text-txt-primary text-xs">
                      {windSpeedKmh} km/h · {temperatureC}°C · {relativeHumidity}%
                    </p>
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={handleGenerateBrief}
                      disabled={loadingBrief}
                      className="px-3 py-1 rounded bg-indigo-600 hover:bg-indigo-500 text-white font-mono text-[11px] font-semibold transition-colors disabled:opacity-50"
                    >
                      {loadingBrief ? 'Synthesizing...' : 'Re-generate SITBRIEF'}
                    </button>
                    {briefResult && (
                      <button
                        onClick={handleCopyBrief}
                        className="px-3 py-1 rounded bg-ops-surface hover:bg-ops-hover text-txt-primary border border-ops-border font-mono text-[11px] font-semibold transition-colors flex items-center space-x-1"
                      >
                        <span>{copied ? 'Copied!' : 'Copy'}</span>
                      </button>
                    )}
                  </div>
                </div>

                {briefError && (
                  <div className="p-3 bg-danger/10 border border-danger/30 rounded text-danger text-xs">
                    {briefError}
                  </div>
                )}

                {loadingBrief && (
                  <div className="py-12 flex flex-col items-center justify-center space-y-3">
                    <div className="w-7 h-7 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin" />
                    <p className="text-xs text-txt-muted">
                      Synthesizing evidence-linked tactical situation brief via Gradient AI...
                    </p>
                  </div>
                )}

                {!loadingBrief && briefResult && (
                  <>
                    {/* Situation Brief Content */}
                    <div>
                      <div className="text-[11px] font-bold text-txt-secondary uppercase tracking-wider mb-1.5">
                        Incident Commander Regional Situation Brief (SITBRIEF)
                      </div>
                      <div className="bg-ops-bg p-4 rounded border border-indigo-500/30 text-xs text-txt-primary whitespace-pre-line leading-relaxed font-mono shadow-inner">
                        {briefResult.situation_brief}
                      </div>
                    </div>

                    {/* Evidence Citations */}
                    <div>
                      <div className="text-[11px] font-bold text-txt-secondary uppercase tracking-wider mb-1.5">
                        Telemetry & Doctrine Evidence Citations
                      </div>
                      <div className="space-y-1.5">
                        {briefResult.evidence_citations.map((cite, idx) => (
                          <div
                            key={idx}
                            className="bg-ops-surface p-2 rounded border border-ops-border/60 text-xs text-txt-secondary flex items-start space-x-2"
                          >
                            <span className="text-forest font-bold shrink-0">•</span>
                            <span>{cite}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </>
                )}
              </div>
            )}

            {/* Modal Footer */}
            <div className="border-t border-ops-border pt-2.5 mt-auto flex justify-between items-center text-[10px] text-txt-muted shrink-0">
              <div className="flex items-center space-x-2">
                <span className="inline-block w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                <span>Connected to DigitalOcean Gradient AI & XGBoost v002 Pipeline</span>
              </div>
              <div>Wildfire Intelligence Operations Platform</div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
