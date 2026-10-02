import React from 'react';
import {
  X,
  AlertTriangle,
  TrendingUp,
  Clock,
  MapPin,
  Truck,
  ShieldCheck,
  FileText,
  BarChart2,
  CheckCircle2,
  AlertOctagon,
  ArrowRight
} from 'lucide-react';

export default function ShipmentDrawer({ shipment, intelligence, onClose, onSelectForDecision }) {
  if (!shipment) return null;

  const pred = intelligence?.prediction || {};
  const conf = intelligence?.confidence || {};
  const intel = intelligence?.intelligence || {};
  const drivers = intelligence?.risk_drivers || [];
  const shapList = intelligence?.shap_explanation || [];
  const hist = intelligence?.historical_evidence || {};

  const riskLevel = pred.risk_level || shipment.risk_level || 'LOW';
  const delayProb = typeof pred.delay_probability === 'number'
    ? (pred.delay_probability * 100).toFixed(1)
    : (shipment.delay_probability ? (shipment.delay_probability * 100).toFixed(1) : '28.0');

  const expectedDelay = typeof pred.expected_delay_days === 'number'
    ? pred.expected_delay_days.toFixed(1)
    : (shipment.expected_delay_days || 0.5);

  const getRiskBadgeClass = (lvl) => {
    switch (String(lvl).toUpperCase()) {
      case 'CRITICAL': return 'badge-critical';
      case 'HIGH': return 'badge-high';
      case 'MEDIUM': return 'badge-medium';
      default: return 'badge-low';
    }
  };

  return (
    <div className="drawer-backdrop" onClick={onClose}>
      <div className="drawer-panel" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="drawer-header">
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.2rem' }}>
              <span className="drawer-title">{shipment.shipment_id}</span>
              <span className={`badge ${getRiskBadgeClass(riskLevel)}`}>{riskLevel} RISK</span>
            </div>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
              {shipment.origin} → {shipment.destination} • {shipment.transport_mode}
            </div>
          </div>
          <button className="drawer-close-btn" onClick={onClose} aria-label="Close drawer">
            <X size={20} />
          </button>
        </div>

        {/* Body */}
        <div className="drawer-body">
          {/* AI Prediction Summary Card */}
          <div className="card" style={{ backgroundColor: 'var(--moonlight-subtle)', borderColor: 'var(--moonlight-lavender)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
              <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--deep-indigo)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                AI Prediction Engine Output
              </span>
              <span className="badge" style={{ backgroundColor: '#FFFFFF', color: 'var(--deep-indigo)' }}>
                {pred.prediction || (shipment.delay_status === 'DELAYED' ? 'DELAYED' : 'ON_TIME')}
              </span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '0.85rem' }}>
              <div>
                <span style={{ fontSize: '0.74rem', color: 'var(--text-secondary)', display: 'block' }}>Delay Probability</span>
                <span style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--deep-indigo)' }}>{delayProb}%</span>
              </div>
              <div>
                <span style={{ fontSize: '0.74rem', color: 'var(--text-secondary)', display: 'block' }}>Expected Delay</span>
                <span style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--deep-indigo)' }}>{expectedDelay} days</span>
              </div>
            </div>

            {/* Risk Meter */}
            <div style={{ marginBottom: '0.4rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: 'var(--text-secondary)', marginBottom: '0.2rem' }}>
                <span>Risk Exposure</span>
                <span>{riskLevel}</span>
              </div>
              <div className="risk-meter">
                <div
                  className="risk-meter-fill"
                  style={{
                    width: `${Math.min(100, Math.max(10, delayProb))}%`,
                    backgroundColor: riskLevel === 'CRITICAL' ? 'var(--critical)' : riskLevel === 'HIGH' ? 'var(--warning)' : 'var(--success)'
                  }}
                />
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.74rem', color: 'var(--text-secondary)', marginTop: '0.5rem', paddingTop: '0.5rem', borderTop: '1px solid rgba(41, 41, 102, 0.1)' }}>
              <span>Confidence Score: <strong>{conf.score ? (conf.score * 100).toFixed(1) + '%' : '45.0%'}</strong> ({conf.level || 'MEDIUM'})</span>
              <span>Intelligence Level: <strong>{intel.level || 'HIGH'}</strong></span>
            </div>
          </div>

          {/* Key Risk Drivers */}
          <div className="card">
            <h4 className="card-title" style={{ marginBottom: '0.75rem' }}>
              <AlertTriangle size={16} color="var(--warning)" />
              <span>Primary Risk Drivers</span>
            </h4>
            {drivers.length > 0 ? (
              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.45rem' }}>
                {drivers.map((driver, idx) => (
                  <li key={idx} style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    fontSize: '0.82rem',
                    padding: '0.45rem 0.65rem',
                    backgroundColor: 'var(--bg-main)',
                    borderRadius: 'var(--radius-sm)',
                    borderLeft: '3px solid var(--muted-indigo)'
                  }}>
                    <span>{driver}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>No active risk escalation triggers detected for this route.</p>
            )}
          </div>

          {/* Explainability / SHAP Feature Attributions */}
          {shapList.length > 0 && (
            <div className="card">
              <h4 className="card-title" style={{ marginBottom: '0.75rem' }}>
                <BarChart2 size={16} color="var(--muted-indigo)" />
                <span>Feature Importance & Attributions (SHAP)</span>
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
                {shapList.map((item, idx) => (
                  <div key={idx} style={{ fontSize: '0.8rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.2rem' }}>
                      <span style={{ fontWeight: 500 }}>{item.description || item.feature}</span>
                      <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: 'var(--deep-indigo)' }}>
                        +{item.shap_value.toFixed(3)}
                      </span>
                    </div>
                    <div style={{ height: '6px', backgroundColor: 'var(--border-subtle)', borderRadius: '3px', overflow: 'hidden' }}>
                      <div
                        style={{
                          height: '100%',
                          width: `${Math.min(100, Math.abs(item.shap_value) * 200)}%`,
                          backgroundColor: 'var(--muted-indigo)',
                          borderRadius: '3px'
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Available Operational Features */}
          <div className="card">
            <h4 className="card-title" style={{ marginBottom: '0.85rem' }}>
              <FileText size={16} color="var(--deep-indigo)" />
              <span>Available Shipment Features</span>
            </h4>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', fontSize: '0.8rem' }}>
              <div style={{ padding: '0.5rem', backgroundColor: 'var(--bg-main)', borderRadius: 'var(--radius-sm)' }}>
                <span style={{ color: 'var(--text-secondary)', display: 'block', fontSize: '0.72rem' }}>Supplier ID</span>
                <span style={{ fontWeight: 600 }}>{shipment.supplier_id || 'N/A'}</span>
              </div>
              <div style={{ padding: '0.5rem', backgroundColor: 'var(--bg-main)', borderRadius: 'var(--radius-sm)' }}>
                <span style={{ color: 'var(--text-secondary)', display: 'block', fontSize: '0.72rem' }}>Supplier Reliability</span>
                <span style={{ fontWeight: 600 }}>{shipment.supplier_reliability ? `${(shipment.supplier_reliability * 100).toFixed(0)}%` : 'N/A'}</span>
              </div>
              <div style={{ padding: '0.5rem', backgroundColor: 'var(--bg-main)', borderRadius: 'var(--radius-sm)' }}>
                <span style={{ color: 'var(--text-secondary)', display: 'block', fontSize: '0.72rem' }}>Distance</span>
                <span style={{ fontWeight: 600 }}>{shipment.distance_km ? `${shipment.distance_km} km` : 'N/A'}</span>
              </div>
              <div style={{ padding: '0.5rem', backgroundColor: 'var(--bg-main)', borderRadius: 'var(--radius-sm)' }}>
                <span style={{ color: 'var(--text-secondary)', display: 'block', fontSize: '0.72rem' }}>Lead Time</span>
                <span style={{ fontWeight: 600 }}>{shipment.lead_time_days ? `${shipment.lead_time_days} days` : 'N/A'}</span>
              </div>
              <div style={{ padding: '0.5rem', backgroundColor: 'var(--bg-main)', borderRadius: 'var(--radius-sm)' }}>
                <span style={{ color: 'var(--text-secondary)', display: 'block', fontSize: '0.72rem' }}>Weather Severity</span>
                <span style={{ fontWeight: 600 }}>{shipment.weather_severity || 'Low'}</span>
              </div>
              <div style={{ padding: '0.5rem', backgroundColor: 'var(--bg-main)', borderRadius: 'var(--radius-sm)' }}>
                <span style={{ color: 'var(--text-secondary)', display: 'block', fontSize: '0.72rem' }}>Traffic Level</span>
                <span style={{ fontWeight: 600 }}>{shipment.traffic_level || 'Low'}</span>
              </div>
              <div style={{ padding: '0.5rem', backgroundColor: 'var(--bg-main)', borderRadius: 'var(--radius-sm)' }}>
                <span style={{ color: 'var(--text-secondary)', display: 'block', fontSize: '0.72rem' }}>Order Priority</span>
                <span style={{ fontWeight: 600 }}>{shipment.priority || 'Standard'}</span>
              </div>
              <div style={{ padding: '0.5rem', backgroundColor: 'var(--bg-main)', borderRadius: 'var(--radius-sm)' }}>
                <span style={{ color: 'var(--text-secondary)', display: 'block', fontSize: '0.72rem' }}>Warehouse Load</span>
                <span style={{ fontWeight: 600 }}>{shipment.warehouse_load ? `${(shipment.warehouse_load * 100).toFixed(0)}%` : 'N/A'}</span>
              </div>
            </div>
          </div>

          {/* Historical Evidence */}
          <div className="card">
            <h4 className="card-title" style={{ marginBottom: '0.75rem' }}>
              <Clock size={16} color="var(--text-secondary)" />
              <span>Historical Similarity Evidence</span>
            </h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.5rem', textAlign: 'center', marginBottom: '0.5rem' }}>
              <div style={{ padding: '0.5rem', backgroundColor: 'var(--bg-main)', borderRadius: 'var(--radius-sm)' }}>
                <span style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--deep-indigo)' }}>{hist.similar_shipments || 10}</span>
                <span style={{ fontSize: '0.68rem', color: 'var(--text-secondary)', display: 'block' }}>Similar Routes</span>
              </div>
              <div style={{ padding: '0.5rem', backgroundColor: 'var(--bg-main)', borderRadius: 'var(--radius-sm)' }}>
                <span style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--critical)' }}>{hist.delayed_shipments || 8}</span>
                <span style={{ fontSize: '0.68rem', color: 'var(--text-secondary)', display: 'block' }}>Hist. Delayed</span>
              </div>
              <div style={{ padding: '0.5rem', backgroundColor: 'var(--bg-main)', borderRadius: 'var(--radius-sm)' }}>
                <span style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--deep-indigo)' }}>{hist.historical_delay_rate ? (hist.historical_delay_rate * 100).toFixed(0) + '%' : '80%'}</span>
                <span style={{ fontSize: '0.68rem', color: 'var(--text-secondary)', display: 'block' }}>Delay Rate</span>
              </div>
            </div>
            <p style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
              Nearest-neighbor clustering identifies historical shipments matching distance corridor, transport mode, and weather pressure.
            </p>
          </div>

          {/* Action button */}
          <div style={{ paddingTop: '0.5rem' }}>
            <button
              className="btn btn-primary"
              style={{ width: '100%' }}
              onClick={() => onSelectForDecision(shipment)}
            >
              <span>Review in Decision Center</span>
              <ArrowRight size={16} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
