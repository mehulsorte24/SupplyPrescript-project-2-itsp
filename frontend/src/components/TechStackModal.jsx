import React from 'react';
import {
  X,
  Cpu,
  Layers,
  Server,
  Layout,
  Palette,
  ShieldCheck,
  CheckCircle2,
  ArrowRight,
  ExternalLink,
  Code2,
  Terminal,
  Activity
} from 'lucide-react';

export default function TechStackModal({ isOpen, onClose, onNavigateToPage }) {
  if (!isOpen) return null;

  const stackItems = [
    {
      id: 'ai-engine',
      title: 'AI Engine Core',
      spec: 'Python 3.14 (Scikit-Learn, NumPy, Pandas)',
      tag: 'Core Machine Learning',
      color: '#4F46E5',
      icon: Cpu,
      summary: 'Dual-model predictive intelligence architecture utilizing an ensemble Gradient Boosting Classifier for delay probability and Random Forest Regressor for arrival timeline impact estimation.',
      capabilities: [
        'Non-linear interaction modeling for route corridor & terminal bottlenecks',
        'Multi-factor normalization across weather, traffic, and supplier reliability',
        'Real-time confidence level estimation (High / Medium / Low)'
      ]
    },
    {
      id: 'explainability',
      title: 'Explainability (XAI)',
      spec: 'SHAP (SHapley Additive exPlanations)',
      tag: 'Local & Global Attributions',
      color: '#0284C7',
      icon: Activity,
      summary: 'Grounded Game-Theoretic TreeExplainer generating exact Shapley values to pinpoint the key drivers behind each individual shipment risk assessment.',
      capabilities: [
        'Local driver breakdowns (Weather severity, Congestion, Buffer depletion)',
        'Positive & negative delay contributor scoring per consignment',
        'Transparent auditable rationale for supply chain compliance'
      ]
    },
    {
      id: 'backend',
      title: 'Backend REST API',
      spec: 'Python HTTP Server with CORS & JSON Endpoints',
      tag: 'Microservice Engine',
      color: '#059669',
      icon: Server,
      summary: 'Zero-overhead, high-performance native Python server implementing RESTful JSON APIs, CORS pre-flight negotiation, and live SQLite database persistence.',
      capabilities: [
        'Port 8000 unified service serving both REST endpoints and frontend SPA',
        'Live SQLite WAL database storing real-time telemetry events and audit logs',
        'Interactive scenario injector (Weather Shock, Port Congestion, Supplier Strike)'
      ]
    },
    {
      id: 'frontend',
      title: 'Frontend Architecture',
      spec: 'React 19 + Vite 8 + Vanilla CSS Design System',
      tag: 'Mission-Control Console',
      color: '#7C3AED',
      icon: Layout,
      summary: 'State-of-the-art single-page web console built on React 19 and Vite 8, featuring reactive live streams, auto-sync intervals, and tactile inspection drawers.',
      capabilities: [
        'Sub-second hot-reloading & production-optimized asset bundling',
        'Modular workspace pages: Overview, Shipments, Risks, Recommendations, Decisions, Feedback',
        'Live 16:9 Presentation mode and seamless instant theme switching'
      ]
    },
    {
      id: 'design-system',
      title: 'Design System',
      spec: 'Under the Moonlight Palette & Tokens',
      tag: 'Obsidian & Moonlight',
      color: '#D97706',
      icon: Palette,
      summary: 'Bespoke enterprise theme inspired by Obsidian Slate (#0F172A), deep indigo accents (#4F46E5), and moonlight lavender tints calibrated for maximum data readability.',
      capabilities: [
        'Curated semantic status tokens (Critical, Warning, Low Risk, Verified)',
        'Obsidian Dark & Clean Light high-contrast WCAG AAA compliance',
        'Glassmorphic headers and responsive micro-animations'
      ]
    },
    {
      id: 'guardrails',
      title: 'Operational Safety & Guardrails',
      spec: 'Human-in-the-Loop Decision Ledger',
      tag: 'Enterprise Governance',
      color: '#10B981',
      icon: ShieldCheck,
      summary: 'Safety architecture ensuring AI remains strictly advisory: automated predictions require Human-in-the-Loop (HITL) authorization for high-value logistics mitigations.',
      capabilities: [
        'Manager decision capture with justification logging (Mehul Sorte, Ops Lead)',
        'Closed-loop outcome tracking to prevent model degeneration',
        'Automated drift telemetry monitoring and retraining alerts'
      ]
    }
  ];

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div
        className="modal-content tech-stack-modal"
        onClick={(e) => e.stopPropagation()}
        style={{ maxWidth: '980px', width: '92vw', maxHeight: '90vh', overflowY: 'auto' }}
      >
        {/* Modal Header */}
        <div className="modal-header" style={{ borderBottom: '1px solid var(--border-color)', padding: '1.25rem 1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
            <div style={{
              width: '38px',
              height: '38px',
              borderRadius: 'var(--radius-md)',
              background: 'var(--brand-gradient)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#FFFFFF'
            }}>
              <Layers size={20} />
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
                <h2 style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--text-main)' }}>
                  Enterprise Frameworks & Architecture
                </h2>
                <span className="badge badge-low" style={{ fontSize: '0.68rem', fontWeight: 700 }}>
                  SupplyPrescript v1.0
                </span>
              </div>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.15rem' }}>
                Technical stack specification, AI engine capabilities, and architectural guardrails
              </p>
            </div>
          </div>
          <button
            className="sidebar-toggle-btn"
            onClick={onClose}
            aria-label="Close modal"
          >
            <X size={18} />
          </button>
        </div>

        {/* Modal Body: Cards Grid */}
        <div style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '1rem'
          }}>
            {stackItems.map((item) => {
              const ItemIcon = item.icon;
              return (
                <div
                  key={item.id}
                  style={{
                    backgroundColor: 'var(--bg-main)',
                    border: '1px solid var(--border-color)',
                    borderRadius: 'var(--radius-lg)',
                    padding: '1.15rem 1.25rem',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                    boxShadow: 'var(--shadow-xs)'
                  }}
                >
                  <div>
                    {/* Top Row: Tag & Icon */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.65rem' }}>
                      <span style={{
                        fontSize: '0.68rem',
                        fontWeight: 700,
                        color: item.color,
                        backgroundColor: 'var(--moonlight-soft)',
                        padding: '0.2rem 0.5rem',
                        borderRadius: 'var(--radius-sm)'
                      }}>
                        {item.tag}
                      </span>
                      <ItemIcon size={18} color={item.color} />
                    </div>

                    {/* Title */}
                    <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.25rem' }}>
                      {item.title}
                    </h3>

                    {/* Spec string */}
                    <div style={{
                      fontSize: '0.8rem',
                      fontFamily: 'var(--font-mono)',
                      fontWeight: 600,
                      color: 'var(--brand-primary)',
                      marginBottom: '0.65rem'
                    }}>
                      {item.spec}
                    </div>

                    {/* Summary */}
                    <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: '1.45', marginBottom: '0.85rem' }}>
                      {item.summary}
                    </p>

                    {/* Bullet Points */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', borderTop: '1px dashed var(--border-subtle)', paddingTop: '0.65rem' }}>
                      {item.capabilities.map((cap, idx) => (
                        <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '0.45rem', fontSize: '0.72rem', color: 'var(--text-secondary)' }}>
                          <CheckCircle2 size={12} color="var(--success)" style={{ marginTop: '2px', flexShrink: 0 }} />
                          <span>{cap}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Quick Navigations */}
          <div style={{
            backgroundColor: 'var(--moonlight-subtle)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-md)',
            padding: '1rem 1.25rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '0.75rem'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
              <Code2 size={16} color="var(--brand-primary)" />
              <span style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-main)' }}>
                Want to examine the full AI lifecycle or design specs?
              </span>
            </div>
            <div style={{ display: 'flex', gap: '0.6rem' }}>
              <button
                className="btn btn-secondary btn-sm"
                onClick={() => {
                  onClose();
                  onNavigateToPage('pipeline');
                }}
                style={{ fontSize: '0.78rem' }}
              >
                <span>View 16-Stage Pipeline</span>
                <ArrowRight size={13} />
              </button>
              <button
                className="btn btn-primary btn-sm"
                onClick={() => {
                  onClose();
                  onNavigateToPage('about');
                }}
                style={{ fontSize: '0.78rem' }}
              >
                <span>System Design & Specs</span>
                <ArrowRight size={13} />
              </button>
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="modal-footer" style={{ borderTop: '1px solid var(--border-color)', padding: '0.85rem 1.5rem', display: 'flex', justifyContent: 'flex-end' }}>
          <button className="btn btn-secondary btn-sm" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
