import React from 'react';
import {
  Info,
  Workflow,
  Layers,
  Cpu,
  Database,
  ShieldCheck,
  RefreshCw,
  GitBranch,
  CheckCircle2,
  Code2,
  Award
} from 'lucide-react';

export default function AboutProjectPage() {
  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">About SupplyPrescript</h1>
          <p className="page-subtitle">
            AI-Powered Closed-Loop Prescriptive Supply Chain Analytics & Decision Intelligence Platform.
          </p>
        </div>
        <span className="badge" style={{ backgroundColor: 'var(--moonlight-soft)', color: 'var(--deep-indigo)', padding: '0.35rem 0.75rem', fontWeight: 700 }}>
          Enterprise Decision Intelligence • Production Tier
        </span>
      </div>

      {/* Hero Overview Card */}
      <div className="card" style={{ marginBottom: '1.75rem', padding: '1.5rem', backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem', alignItems: 'center' }}>
          <div>
            <span style={{ fontSize: '0.74rem', fontWeight: 700, color: 'var(--muted-indigo)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
              Project Specification
            </span>
            <h2 style={{ fontSize: '1.45rem', fontWeight: 800, color: 'var(--deep-indigo)', margin: '0.35rem 0 0.75rem' }}>
              SupplyPrescript Platform
            </h2>
            <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', lineHeight: '1.55', marginBottom: '1rem' }}>
              SupplyPrescript is an enterprise-grade decision intelligence framework that moves beyond descriptive telemetry into <strong>predictive risk classification</strong> and <strong>prescriptive mitigation recommendations</strong>. It establishes a verifiable human-in-the-loop audit ledger coupled with closed-loop outcome tracking and data drift supervision.
            </p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              <span className="badge badge-low">Closed-Loop Learning</span>
              <span className="badge" style={{ backgroundColor: 'var(--moonlight-soft)', color: 'var(--deep-indigo)' }}>Explainable AI (SHAP)</span>
              <span className="badge" style={{ backgroundColor: 'var(--bg-main)', color: 'var(--text-secondary)' }}>Dual Classification & Regression</span>
              <span className="badge" style={{ backgroundColor: '#FFF0F2', color: 'var(--critical)' }}>ISO Safety Invariants</span>
            </div>
          </div>

          <div style={{ padding: '1.25rem', backgroundColor: 'var(--moonlight-subtle)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--moonlight-lavender)' }}>
            <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--deep-indigo)', marginBottom: '0.65rem' }}>
              Primary System Objectives
            </h4>
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.55rem', fontSize: '0.8rem', color: 'var(--text-main)' }}>
              <li style={{ display: 'flex', alignItems: 'flex-start', gap: '0.45rem' }}>
                <CheckCircle2 size={15} color="var(--deep-indigo)" style={{ flexShrink: 0, marginTop: '2px' }} />
                <span><strong>Proactive Disruption Forecast:</strong> Dual-model inference predicting delay probability and expected slip days.</span>
              </li>
              <li style={{ display: 'flex', alignItems: 'flex-start', gap: '0.45rem' }}>
                <CheckCircle2 size={15} color="var(--deep-indigo)" style={{ flexShrink: 0, marginTop: '2px' }} />
                <span><strong>Explainable Root Causes:</strong> SHAP feature attributions explaining corridor distance, lead times, and weather severity.</span>
              </li>
              <li style={{ display: 'flex', alignItems: 'flex-start', gap: '0.45rem' }}>
                <CheckCircle2 size={15} color="var(--deep-indigo)" style={{ flexShrink: 0, marginTop: '2px' }} />
                <span><strong>Prescriptive Mitigation:</strong> Multi-option ranking with trade-off analysis (expedite, buffer, alternate supplier).</span>
              </li>
              <li style={{ display: 'flex', alignItems: 'flex-start', gap: '0.45rem' }}>
                <CheckCircle2 size={15} color="var(--deep-indigo)" style={{ flexShrink: 0, marginTop: '2px' }} />
                <span><strong>Continuous Monitoring Guardrails:</strong> Drift detection and automated learning signals preserving model integrity.</span>
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* Interactive Layered Architecture Diagram */}
      <div className="card" style={{ marginBottom: '1.75rem' }}>
        <div className="card-header">
          <div>
            <h3 className="card-title">
              <Workflow size={17} color="var(--deep-indigo)" />
              <span>Multi-Tier System Architecture</span>
            </h3>
            <p className="card-subtitle">Layered dataflow from telemetry ingestion to continuous closed-loop learning</p>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem', padding: '0.5rem 0' }}>

          {/* Layer 1: Ingestion & Preprocessing */}
          <div style={{ padding: '1rem', backgroundColor: 'var(--bg-main)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span style={{ fontSize: '0.74rem', fontWeight: 700, padding: '0.2rem 0.5rem', backgroundColor: 'var(--deep-indigo)', color: '#FFFFFF', borderRadius: 'var(--radius-xs)' }}>
                  LAYER 1
                </span>
                <span style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--deep-indigo)' }}>
                  Data Ingestion & Integrity Validation
                </span>
              </div>
              <span style={{ fontSize: '0.74rem', color: 'var(--text-secondary)' }}>CSV / Sensor Telemetry</span>
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              Validates schema constraints across 18 operational fields (distance, weather, inventory, supplier reliability). Cleans missing values, scales numerical features, and performs categorical encoding.
            </p>
          </div>

          <div style={{ textAlign: 'center', color: 'var(--muted-indigo)' }}>↓</div>

          {/* Layer 2: Machine Learning Inference Core */}
          <div style={{ padding: '1rem', backgroundColor: 'var(--moonlight-subtle)', borderRadius: 'var(--radius-md)', border: '1px solid var(--moonlight-lavender)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span style={{ fontSize: '0.74rem', fontWeight: 700, padding: '0.2rem 0.5rem', backgroundColor: 'var(--muted-indigo)', color: '#FFFFFF', borderRadius: 'var(--radius-xs)' }}>
                  LAYER 2
                </span>
                <span style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--deep-indigo)' }}>
                  Dual-Headed Predictive Intelligence Core
                </span>
              </div>
              <span style={{ fontSize: '0.74rem', color: 'var(--deep-indigo)' }}>Random Forest / XGBoost + SHAP</span>
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              Dual model pipelines: Classification Model outputs probability of delay (80% accuracy); Regression Model outputs expected delay duration (R²=0.912). Local SHAP explains key drivers per shipment.
            </p>
          </div>

          <div style={{ textAlign: 'center', color: 'var(--muted-indigo)' }}>↓</div>

          {/* Layer 3: Prescriptive Analytics & Decision Intelligence */}
          <div style={{ padding: '1rem', backgroundColor: 'var(--bg-main)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span style={{ fontSize: '0.74rem', fontWeight: 700, padding: '0.2rem 0.5rem', backgroundColor: 'var(--deep-indigo)', color: '#FFFFFF', borderRadius: 'var(--radius-xs)' }}>
                  LAYER 3
                </span>
                <span style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--deep-indigo)' }}>
                  Prescriptive Recommendations & Risk Aggregation
                </span>
              </div>
              <span style={{ fontSize: '0.74rem', color: 'var(--text-secondary)' }}>Rule & Heuristic Optimization</span>
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              Aggregates batch risk scores (75.37%), detects escalation patterns, and generates ranked candidate actions (Expedite, Buffer, Alternate supplier) paired with operational trade-offs and triggers.
            </p>
          </div>

          <div style={{ textAlign: 'center', color: 'var(--muted-indigo)' }}>↓</div>

          {/* Layer 4: Manager Decision & Closed-Loop Feedback */}
          <div style={{ padding: '1rem', backgroundColor: '#FDFBF7', borderRadius: 'var(--radius-md)', border: '1px solid var(--warning-border)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span style={{ fontSize: '0.74rem', fontWeight: 700, padding: '0.2rem 0.5rem', backgroundColor: 'var(--warning)', color: '#FFFFFF', borderRadius: 'var(--radius-xs)' }}>
                  LAYER 4
                </span>
                <span style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--deep-indigo)' }}>
                  Manager Decision Capture & Closed-Loop Feedback Loop
                </span>
              </div>
              <span style={{ fontSize: '0.74rem', color: 'var(--warning)', fontWeight: 600 }}>Human-in-the-Loop</span>
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              Manager reviews and commits decision with written rationale. Post-arrival delivery data tracks prediction accuracy, logs error metrics, checks feature drift, and feeds learning signals for guarded model retraining.
            </p>
          </div>

        </div>
      </div>

      {/* Technology Stack & AI Module Breakdown */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
        {/* Core Technologies */}
        <div className="card">
          <div className="card-header">
            <div>
              <h3 className="card-title">
                <Code2 size={17} color="var(--deep-indigo)" />
                <span>Technology Stack</span>
              </h3>
              <p className="card-subtitle">Enterprise frameworks and libraries</p>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem', fontSize: '0.82rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.4rem 0', borderBottom: '1px solid var(--border-subtle)' }}>
              <span style={{ color: 'var(--text-secondary)' }}>AI Engine Core:</span>
              <span style={{ fontWeight: 600 }}>Python 3.14 (Scikit-Learn, NumPy, Pandas)</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.4rem 0', borderBottom: '1px solid var(--border-subtle)' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Explainability:</span>
              <span style={{ fontWeight: 600 }}>SHAP (SHapley Additive exPlanations)</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.4rem 0', borderBottom: '1px solid var(--border-subtle)' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Backend REST API:</span>
              <span style={{ fontWeight: 600 }}>Python HTTP Server with CORS & JSON Endpoints</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.4rem 0', borderBottom: '1px solid var(--border-subtle)' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Frontend Architecture:</span>
              <span style={{ fontWeight: 600 }}>React 19 + Vite 8 + Vanilla CSS Design System</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.4rem 0' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Design System:</span>
              <span style={{ fontWeight: 600 }}>Under the Moonlight Palette & Tokens</span>
            </div>
          </div>
        </div>

        {/* Closed-Loop Learning Concept */}
        <div className="card">
          <div className="card-header">
            <div>
              <h3 className="card-title">
                <RefreshCw size={17} color="var(--muted-indigo)" />
                <span>Closed-Loop Learning Paradigm</span>
              </h3>
              <p className="card-subtitle">Preventing feedback degeneration</p>
            </div>
          </div>

          <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '0.75rem', lineHeight: '1.45' }}>
            <p>
              Traditional supply chain platforms operate as one-way dashboards where models generate numbers but never record human reactions or verify actual field outcomes.
            </p>
            <p>
              <strong>SupplyPrescript establishes a closed loop:</strong> When a manager acts upon an alert (e.g. expediting freight), the actual arrival timeline is matched back to the initial prediction. This produces a verified outcome signal:
            </p>
            <div style={{ padding: '0.65rem', backgroundColor: 'var(--bg-main)', borderRadius: 'var(--radius-sm)', borderLeft: '3px solid var(--deep-indigo)' }}>
              <code>Prediction → Manager Action → Physical Arrival → Error Measurement → Drift Analysis → Guarded Retraining</code>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
