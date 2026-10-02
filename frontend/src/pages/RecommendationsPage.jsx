import React from 'react';
import {
  Lightbulb,
  ShieldCheck,
  ArrowRight,
  CheckCircle,
  AlertTriangle,
  Clock,
  Scale,
  Zap,
  Info,
  Layers,
  ChevronRight
} from 'lucide-react';

export default function RecommendationsPage({
  recommendationData,
  isLoading,
  onSelectActionForDecision
}) {
  if (isLoading || !recommendationData) {
    return (
      <div className="page-container">
        <div style={{ height: '30px', width: '320px', backgroundColor: 'var(--border-color)', marginBottom: '1.5rem' }}></div>
        <div className="kpi-grid">
          {[1, 2, 3].map(i => (
            <div key={i} className="card" style={{ height: '180px' }}></div>
          ))}
        </div>
      </div>
    );
  }

  const { decision_context, recommendation, manager_guidance, operational_safety } = recommendationData;
  const candidateActions = recommendation?.candidate_actions || [];
  const rankedActions = recommendation?.ranked_actions || [];

  // Merge ranked action details with candidate action full rationale
  const enrichedActions = candidateActions.map(action => {
    const rankInfo = rankedActions.find(r => r.action_id === action.action_id) || {};
    return {
      ...action,
      rank: rankInfo.rank || 99,
      relevance_score: rankInfo.relevance_score || 50,
      ranking_reasons: rankInfo.ranking_reasons || []
    };
  }).sort((a, b) => a.rank - b.rank);

  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">AI Action Recommendations</h1>
          <p className="page-subtitle">
            Prescriptive decision support mitigating delay severity across active high-exposure shipment clusters.
          </p>
        </div>
      </div>

      {/* Decision Support Advisory & Safety Notice */}
      <div style={{
        backgroundColor: 'var(--moonlight-subtle)',
        border: '1px solid var(--moonlight-lavender)',
        borderRadius: 'var(--radius-lg)',
        padding: '1.15rem 1.35rem',
        marginBottom: '1.75rem',
        display: 'flex',
        alignItems: 'flex-start',
        gap: '1rem'
      }}>
        <div style={{
          width: '36px',
          height: '36px',
          borderRadius: 'var(--radius-md)',
          backgroundColor: 'var(--deep-indigo)',
          color: 'var(--moonlight-lavender)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0
        }}>
          <ShieldCheck size={20} />
        </div>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
            <span style={{ fontWeight: 700, fontSize: '0.92rem', color: 'var(--deep-indigo)' }}>
              Operational Boundary: Decision Support Mode
            </span>
            <span className="badge" style={{ backgroundColor: '#FFFFFF', color: 'var(--deep-indigo)' }}>
              MANAGER REVIEW MANDATORY
            </span>
          </div>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: '0.25rem', lineHeight: '1.45' }}>
            {manager_guidance || 'These are AI-generated candidate actions for manager evaluation. The engine does not execute business decisions, modify shipments, change suppliers, purchase capacity, or alter inventory.'}
          </p>
        </div>
      </div>

      {/* Decision Context Bar */}
      <div className="card" style={{ marginBottom: '1.75rem', padding: '1rem 1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.85rem' }}>
          <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Prescriptive Trigger Context
          </span>
          <span className="badge badge-critical">ATTENTION: {decision_context?.attention_level || 'IMMEDIATE'}</span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem' }}>
          <div>
            <span style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', display: 'block' }}>Overall Risk Level</span>
            <span style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--critical)' }}>{decision_context?.overall_risk_level || 'CRITICAL'}</span>
          </div>
          <div>
            <span style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', display: 'block' }}>Risk Exposure Score</span>
            <span style={{ fontSize: '1.15rem', fontWeight: 700 }}>{decision_context?.risk_exposure || 75.37}%</span>
          </div>
          <div>
            <span style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', display: 'block' }}>Batch Delay Probability</span>
            <span style={{ fontSize: '1.15rem', fontWeight: 700 }}>{decision_context?.delay_probability || 71.85}%</span>
          </div>
          <div>
            <span style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', display: 'block' }}>Mean Expected Delay</span>
            <span style={{ fontSize: '1.15rem', fontWeight: 700 }}>+{decision_context?.expected_delay_days || 3.42} days</span>
          </div>
          <div>
            <span style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', display: 'block' }}>Escalation Intensity</span>
            <span style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--critical)' }}>{decision_context?.escalation_score || 95.0}%</span>
          </div>
        </div>
      </div>

      {/* Recommendation Summary Statement */}
      <div style={{ marginBottom: '1.25rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)' }}>
          Ranked Prescriptive Mitigation Options ({enrichedActions.length})
        </h3>
        <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
          Sorted by AI Relevance Score & Risk Reduction Potential
        </span>
      </div>

      {/* Cards List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', marginBottom: '2rem' }}>
        {enrichedActions.map((rec) => {
          const isRank1 = rec.rank === 1;

          return (
            <div
              key={rec.action_id}
              className="card"
              style={{
                border: isRank1 ? '2px solid var(--deep-indigo)' : '1px solid var(--border-color)',
                boxShadow: isRank1 ? '0 6px 18px rgba(41, 41, 102, 0.08)' : 'var(--shadow-sm)',
                position: 'relative',
                overflow: 'hidden'
              }}
            >
              {isRank1 && (
                <div style={{
                  position: 'absolute',
                  top: 0,
                  right: 0,
                  backgroundColor: 'var(--deep-indigo)',
                  color: '#FFFFFF',
                  padding: '0.3rem 0.95rem',
                  fontSize: '0.72rem',
                  fontWeight: 700,
                  borderBottomLeftRadius: 'var(--radius-md)',
                  letterSpacing: '0.05em'
                }}>
                  PRIMARY RECOMMENDATION
                </div>
              )}

              {/* Card Header */}
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '1rem', paddingRight: isRank1 ? '160px' : '0' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
                  <div style={{
                    width: '38px',
                    height: '38px',
                    borderRadius: 'var(--radius-md)',
                    backgroundColor: isRank1 ? 'var(--deep-indigo)' : 'var(--moonlight-soft)',
                    color: isRank1 ? '#FFFFFF' : 'var(--deep-indigo)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontWeight: 800,
                    fontSize: '1rem'
                  }}>
                    #{rec.rank}
                  </div>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <h4 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)' }}>
                        {rec.action_name}
                      </h4>
                      <span className="badge" style={{ backgroundColor: 'var(--bg-main)', color: 'var(--text-secondary)' }}>
                        {rec.action_id}
                      </span>
                      <span className="badge" style={{ backgroundColor: 'var(--moonlight-soft)', color: 'var(--deep-indigo)' }}>
                        {rec.category}
                      </span>
                    </div>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                      Urgency: <strong>{rec.urgency}</strong> • Status: <strong>{rec.execution_status}</strong>
                    </span>
                  </div>
                </div>

                {/* Relevance Score Pill */}
                <div style={{ textAlign: 'right' }}>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', display: 'block' }}>Relevance Score</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    <span style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--deep-indigo)' }}>
                      {rec.relevance_score}/100
                    </span>
                  </div>
                </div>
              </div>

              {/* Details Grid */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem', marginBottom: '1.25rem' }}>
                {/* Rationale & Trigger */}
                <div style={{ padding: '0.85rem', backgroundColor: 'var(--bg-main)', borderRadius: 'var(--radius-md)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.75rem', fontWeight: 600, color: 'var(--deep-indigo)', marginBottom: '0.35rem' }}>
                    <Lightbulb size={14} />
                    <span>AI RATIONALE & TRIGGER</span>
                  </div>
                  <p style={{ fontSize: '0.82rem', color: 'var(--text-main)', marginBottom: '0.4rem', lineHeight: '1.4' }}>
                    {rec.rationale}
                  </p>
                  <span style={{ fontSize: '0.74rem', color: 'var(--text-secondary)', display: 'block' }}>
                    <strong>Trigger Condition:</strong> {rec.trigger}
                  </span>
                </div>

                {/* Expected Impact */}
                <div style={{ padding: '0.85rem', backgroundColor: 'var(--success-bg)', borderRadius: 'var(--radius-md)', border: '1px solid var(--success-border)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.75rem', fontWeight: 600, color: 'var(--success)', marginBottom: '0.35rem' }}>
                    <Zap size={14} />
                    <span>EXPECTED OPERATIONAL EFFECT</span>
                  </div>
                  <p style={{ fontSize: '0.82rem', color: 'var(--text-main)', lineHeight: '1.4' }}>
                    {rec.expected_effect}
                  </p>
                </div>

                {/* Trade-offs & Limitations */}
                <div style={{ padding: '0.85rem', backgroundColor: 'var(--warning-bg)', borderRadius: 'var(--radius-md)', border: '1px solid var(--warning-border)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.75rem', fontWeight: 600, color: 'var(--warning)', marginBottom: '0.35rem' }}>
                    <Scale size={14} />
                    <span>OPERATIONAL TRADE-OFFS</span>
                  </div>
                  <p style={{ fontSize: '0.82rem', color: 'var(--text-main)', lineHeight: '1.4' }}>
                    {rec.trade_off}
                  </p>
                </div>
              </div>

              {/* Supporting Reasons */}
              {rec.ranking_reasons?.length > 0 && (
                <div style={{ marginBottom: '1.15rem' }}>
                  <span style={{ fontSize: '0.74rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.04em', display: 'block', marginBottom: '0.35rem' }}>
                    Ranking Justification Drivers:
                  </span>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.45rem' }}>
                    {rec.ranking_reasons.map((r, i) => (
                      <span key={i} style={{
                        fontSize: '0.75rem',
                        padding: '0.25rem 0.55rem',
                        backgroundColor: 'var(--bg-main)',
                        borderRadius: 'var(--radius-sm)',
                        border: '1px solid var(--border-subtle)'
                      }}>
                        • {r}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Bottom Card Action */}
              <div style={{ display: 'flex', justifyContent: 'flex-end', paddingTop: '0.85rem', borderTop: '1px solid var(--border-subtle)' }}>
                <button
                  className={isRank1 ? 'btn btn-primary btn-sm' : 'btn btn-secondary btn-sm'}
                  onClick={() => onSelectActionForDecision(rec)}
                >
                  <span>Select & Evaluate in Decision Center</span>
                  <ArrowRight size={14} />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
