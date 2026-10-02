import React, { useState } from 'react';
import {
  AlertTriangle,
  ShieldAlert,
  TrendingUp,
  MapPin,
  Truck,
  BarChart2,
  Layers,
  ChevronRight,
  Info,
  CheckCircle,
  AlertOctagon,
  ExternalLink
} from 'lucide-react';

export default function RiskAnalysisPage({
  riskData,
  isLoading,
  onSelectShipment
}) {
  const [selectedRoute, setSelectedRoute] = useState(null);

  if (isLoading || !riskData) {
    return (
      <div className="page-container">
        <div style={{ height: '30px', width: '250px', backgroundColor: 'var(--border-color)', marginBottom: '1.5rem' }}></div>
        <div className="card" style={{ height: '300px' }}></div>
      </div>
    );
  }

  const { batch_risk, decision_intelligence, escalation, supplier_comparison, route_comparison } = riskData;

  const riskExposure = batch_risk?.batch_risk?.risk_exposure_score || 75.37;
  const overallRisk = batch_risk?.batch_risk?.overall_risk_level || 'CRITICAL';
  const escalationScore = decision_intelligence?.risk_context?.escalation_score || 95.0;
  const highRiskList = batch_risk?.highest_risk_shipments || [];

  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Risk Analysis Workspace</h1>
          <p className="page-subtitle">
            Comprehensive evaluation of batch risk exposure, supplier vulnerabilities, corridor congestion, and escalation patterns.
          </p>
        </div>
      </div>

      {/* Visual Risk Scale (Low to Critical) */}
      <div className="card" style={{ marginBottom: '2rem', padding: '1.4rem 1.65rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
          <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-main)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Enterprise Operational Risk Calibration Scale
          </span>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Multi-factor weighted calibration</span>
        </div>

        {/* Multi-segment Scale */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
          {/* Low */}
          <div style={{
            padding: '1rem 1.15rem',
            borderRadius: 'var(--radius-lg)',
            backgroundColor: 'var(--success-bg)',
            border: '1px solid var(--success-border)',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.4rem'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--success)' }}>LOW RISK</span>
              <span style={{ fontSize: '0.74rem', color: 'var(--success)', fontWeight: 700 }}>0% – 30%</span>
            </div>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>Normal operations, standard automated tracking</span>
          </div>

          {/* Medium */}
          <div style={{
            padding: '1rem 1.15rem',
            borderRadius: 'var(--radius-lg)',
            backgroundColor: 'var(--moonlight-soft)',
            border: '1px solid var(--moonlight-lavender)',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.4rem'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--brand-primary)' }}>MEDIUM RISK</span>
              <span style={{ fontSize: '0.74rem', color: 'var(--brand-primary)', fontWeight: 700 }}>31% – 50%</span>
            </div>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>Elevated lead time, automated proactive notice</span>
          </div>

          {/* High */}
          <div style={{
            padding: '1rem 1.15rem',
            borderRadius: 'var(--radius-lg)',
            backgroundColor: 'var(--warning-bg)',
            border: '1px solid var(--warning-border)',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.4rem'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--warning)' }}>HIGH RISK</span>
              <span style={{ fontSize: '0.74rem', color: 'var(--warning)', fontWeight: 700 }}>51% – 70%</span>
            </div>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>Expedition candidate, buffer corridor deployment</span>
          </div>

          {/* Critical (Current Active State) */}
          <div style={{
            padding: '1rem 1.15rem',
            borderRadius: 'var(--radius-lg)',
            backgroundColor: 'var(--critical-bg)',
            border: '2px solid var(--critical)',
            boxShadow: '0 4px 14px rgba(225, 29, 72, 0.18)',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.4rem'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.82rem', fontWeight: 800, color: 'var(--critical)' }}>CRITICAL RISK [ACTIVE]</span>
              <span style={{ fontSize: '0.74rem', color: 'var(--critical)', fontWeight: 800 }}>71% – 100%</span>
            </div>
            <span style={{ fontSize: '0.78rem', color: 'var(--critical)', fontWeight: 600 }}>
              Immediate managerial decision action required
            </span>
          </div>
        </div>
      </div>

      {/* Top Risk Exposure Summary Metrics */}
      <div className="kpi-grid">
        <div className="kpi-card" style={{ borderLeft: '4px solid var(--critical)' }}>
          <span className="kpi-label">Batch Risk Exposure</span>
          <div className="kpi-value-row">
            <span className="kpi-value" style={{ color: 'var(--critical)' }}>{riskExposure}%</span>
            <span className="kpi-unit">({overallRisk})</span>
          </div>
          <p className="kpi-subtext">Composite batch vulnerability score</p>
        </div>

        <div className="kpi-card" style={{ borderLeft: '4px solid var(--critical)' }}>
          <span className="kpi-label">Risk Escalation Score</span>
          <div className="kpi-value-row">
            <span className="kpi-value" style={{ color: 'var(--critical)' }}>{escalationScore}%</span>
            <span className="kpi-unit">CRITICAL</span>
          </div>
          <p className="kpi-subtext">Multi-condition escalation intensity</p>
        </div>

        <div className="kpi-card">
          <span className="kpi-label">Delay Probability</span>
          <div className="kpi-value-row">
            <span className="kpi-value">{batch_risk?.average_metrics?.delay_probability ? (batch_risk.average_metrics.delay_probability * 100).toFixed(1) : '71.9'}%</span>
          </div>
          <p className="kpi-subtext">Average probability of delivery disruption</p>
        </div>

        <div className="kpi-card">
          <span className="kpi-label">Expected Delay Duration</span>
          <div className="kpi-value-row">
            <span className="kpi-value">+{batch_risk?.average_metrics?.expected_delay_days?.toFixed(2) || '3.42'}</span>
            <span className="kpi-unit">days</span>
          </div>
          <p className="kpi-subtext">Regression model predicted lead time slip</p>
        </div>
      </div>

      {/* High-Risk Shipment Cluster & Escalation Signals */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '1.25rem', marginBottom: '1.75rem' }}>
        {/* Critical & High Risk Shipments List */}
        <div className="card">
          <div className="card-header">
            <div>
              <h3 className="card-title">
                <AlertOctagon size={17} color="var(--critical)" />
                <span>Critical-Risk Shipment Cohort</span>
              </h3>
              <p className="card-subtitle">Top priority shipments facing imminent timeline disruption</p>
            </div>
            <span className="badge badge-critical">{highRiskList.length} Flagged</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
            {highRiskList.map((item, idx) => (
              <div
                key={item.shipment_id}
                onClick={() => onSelectShipment(item.shipment_id)}
                style={{
                  padding: '0.75rem 0.95rem',
                  borderRadius: 'var(--radius-md)',
                  border: '1px solid var(--border-color)',
                  backgroundColor: 'var(--bg-main)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  cursor: 'pointer',
                  transition: 'background-color var(--transition-fast)'
                }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--moonlight-subtle)'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'var(--bg-main)'}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <span style={{
                    width: '24px',
                    height: '24px',
                    borderRadius: '50%',
                    backgroundColor: 'var(--critical-bg)',
                    color: 'var(--critical)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '0.74rem',
                    fontWeight: 700
                  }}>
                    {idx + 1}
                  </span>
                  <div>
                    <span style={{ fontWeight: 700, fontSize: '0.88rem', color: 'var(--deep-indigo)' }}>
                      {item.shipment_id}
                    </span>
                    <span style={{ fontSize: '0.74rem', color: 'var(--text-secondary)', display: 'block' }}>
                      Delay Prob: <strong>{(item.delay_probability * 100).toFixed(1)}%</strong> • Risk Score: {item.risk_score?.toFixed(1)}
                    </span>
                  </div>
                </div>

                <div style={{ textAlign: 'right' }}>
                  <span style={{ fontWeight: 700, color: 'var(--critical)', fontSize: '0.9rem' }}>
                    +{item.expected_delay_days}d
                  </span>
                  <span className="badge badge-critical" style={{ display: 'block', marginTop: '0.2rem', fontSize: '0.65rem' }}>
                    {item.risk_level}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* AI Escalation Signals Context */}
        <div className="card">
          <div className="card-header">
            <div>
              <h3 className="card-title">
                <ShieldAlert size={17} color="var(--deep-indigo)" />
                <span>AI Escalation Evidence & Signals</span>
              </h3>
              <p className="card-subtitle">Decision intelligence rule triggers</p>
            </div>
            <span className="badge" style={{ backgroundColor: 'var(--moonlight-soft)', color: 'var(--deep-indigo)' }}>
              7 Active Triggers
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
            {(decision_intelligence?.risk_context?.escalation_signals || [
              "Overall batch risk level is CRITICAL.",
              "Critical-risk predictions represent at least half of the batch (70.0%).",
              "High and critical predictions represent a large majority of the batch (80.0%).",
              "A high percentage of predictions are delayed (80.0%).",
              "Batch risk exposure score is at or above the critical threshold (75.37%).",
              "Average AI confidence is below the healthy threshold (46.72%).",
              "Only one historical batch is available; risk trend requires additional batches."
            ]).map((sig, idx) => (
              <div
                key={idx}
                style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '0.6rem',
                  fontSize: '0.82rem',
                  padding: '0.5rem 0.75rem',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: 'var(--bg-main)'
                }}
              >
                <AlertTriangle size={15} color="var(--warning)" style={{ flexShrink: 0, marginTop: '2px' }} />
                <span>{sig}</span>
              </div>
            ))}
          </div>

          <div style={{ marginTop: '1rem', padding: '0.75rem', backgroundColor: 'var(--moonlight-subtle)', borderRadius: 'var(--radius-md)', fontSize: '0.76rem', color: 'var(--deep-indigo)' }}>
            <strong>Trend State: BASELINE (INSUFFICIENT_HISTORY)</strong> — Temporal classification requires subsequent observation batches to establish recurring seasonal or supplier trend trajectories.
          </div>
        </div>
      </div>

      {/* Supplier Risk Comparison Table */}
      <div className="card" style={{ marginBottom: '1.75rem' }}>
        <div className="card-header">
          <div>
            <h3 className="card-title">Supplier Risk & Reliability Comparison</h3>
            <p className="card-subtitle">Historical performance and delay incident rates per supplier</p>
          </div>
        </div>

        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Supplier ID</th>
                <th>Shipments Handled</th>
                <th>Delay Incident Rate</th>
                <th>Critical Delayed Units</th>
                <th>Contract Reliability Score</th>
                <th>Composite Risk Category</th>
              </tr>
            </thead>
            <tbody>
              {supplier_comparison?.map((sup) => (
                <tr key={sup.supplier_id}>
                  <td style={{ fontWeight: 600, color: 'var(--deep-indigo)' }}>{sup.supplier_id}</td>
                  <td>{sup.total_shipments} shipments</td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span style={{ fontWeight: 600 }}>{sup.delay_rate}%</span>
                      <div style={{ width: '60px', height: '6px', backgroundColor: 'var(--border-subtle)', borderRadius: '3px', overflow: 'hidden' }}>
                        <div style={{ width: `${sup.delay_rate}%`, height: '100%', backgroundColor: sup.delay_rate >= 80 ? 'var(--critical)' : 'var(--warning)' }} />
                      </div>
                    </div>
                  </td>
                  <td>{sup.critical_shipments} units</td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{(sup.supplier_reliability * 100).toFixed(0)}%</td>
                  <td>
                    <span className={`badge ${
                      sup.risk_level === 'CRITICAL' ? 'badge-critical' :
                      sup.risk_level === 'HIGH' ? 'badge-high' :
                      sup.risk_level === 'MEDIUM' ? 'badge-medium' : 'badge-low'
                    }`}>
                      {sup.risk_level}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Route & Corridor Risk Comparison */}
      <div className="card">
        <div className="card-header">
          <div>
            <h3 className="card-title">Top High-Exposure Transportation Corridors</h3>
            <p className="card-subtitle">Origin to Destination analysis sorted by delay severity</p>
          </div>
        </div>

        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Corridor Route</th>
                <th>Mode</th>
                <th>Active Volume</th>
                <th>Avg Distance</th>
                <th>Delay Occurrence Rate</th>
                <th>Average Delay Duration</th>
                <th>Vulnerability Rating</th>
              </tr>
            </thead>
            <tbody>
              {route_comparison?.map((rc) => (
                <tr key={rc.route_key}>
                  <td style={{ fontWeight: 600, color: 'var(--deep-indigo)' }}>
                    {rc.route}
                  </td>
                  <td>
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem' }}>
                      <Truck size={13} color="var(--muted-indigo)" />
                      {rc.transport_mode}
                    </span>
                  </td>
                  <td>{rc.shipment_count} shipments</td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{rc.avg_distance_km} km</td>
                  <td>
                    <span style={{ fontWeight: 600, color: rc.delay_rate >= 80 ? 'var(--critical)' : 'var(--text-main)' }}>
                      {rc.delay_rate}%
                    </span>
                  </td>
                  <td>
                    <span style={{ fontWeight: 600 }}>+{rc.avg_delay_days} days</span>
                  </td>
                  <td>
                    <span className={`badge ${
                      rc.risk_level === 'CRITICAL' ? 'badge-critical' :
                      rc.risk_level === 'HIGH' ? 'badge-high' : 'badge-medium'
                    }`}>
                      {rc.risk_level}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
