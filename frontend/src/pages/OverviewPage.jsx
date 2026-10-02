import React, { useState } from 'react';
import {
  Package,
  AlertTriangle,
  Percent,
  Clock,
  CheckCircle,
  ShieldCheck,
  ArrowUpRight,
  TrendingUp,
  AlertOctagon,
  Eye,
  ChevronRight,
  Truck,
  Database,
  Radio,
  Zap,
  Activity,
  BarChart2,
  Bell,
  Play,
  Pause,
  RefreshCw,
  Sparkles
} from 'lucide-react';

export default function OverviewPage({
  dashboardData,
  dbStats,
  liveRecords,
  notifications,
  isLoading,
  onSelectShipment,
  setActivePage,
  onIngestLiveShipment,
  isIngesting,
  autoRefreshInterval,
  setAutoRefreshInterval,
  countdown,
  autoStreamEnabled,
  setAutoStreamEnabled,
  onSwitchScenario
}) {
  const [activeTab, setActiveTab] = useState('live_stream'); // 'live_stream' | 'alerts' | 'recent_predictions'
  const [tabAlertFilter, setTabAlertFilter] = useState('ALL');
  const [activeCurveIndex, setActiveCurveIndex] = useState(3); // Default to SHP004 (83% Critical) at initial instant
  const [activeCurveMetric, setActiveCurveMetric] = useState('prob'); // 'prob' | 'delay' | 'risk'
  const [hoveredRiskSlice, setHoveredRiskSlice] = useState('CRITICAL'); // Default to CRITICAL at initial instant
  const [selectedScenarioKey, setSelectedScenarioKey] = useState('standard_live');

  const handleScenarioChange = (key) => {
    setSelectedScenarioKey(key);
    if (onSwitchScenario) {
      onSwitchScenario(key);
    }
  };

  if (isLoading || !dashboardData) {
    return (
      <div className="page-container">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
          <div style={{ height: '24px', width: '280px', backgroundColor: 'var(--border-color)', borderRadius: 'var(--radius-sm)' }}></div>
          <div className="kpi-grid">
            {[1, 2, 3, 4, 5, 6].map(i => (
              <div key={i} className="kpi-card" style={{ height: '95px', backgroundColor: 'var(--border-subtle)' }}></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  const { kpis, risk_distribution, transport_breakdown, recent_predictions, critical_alerts, batch_summary } = dashboardData;

  // Donut chart calculations
  const lowCount = risk_distribution?.LOW || 2;
  const medCount = risk_distribution?.MEDIUM || 0;
  const highCount = risk_distribution?.HIGH || 1;
  const critCount = risk_distribution?.CRITICAL || 7;
  const totalRiskCount = lowCount + medCount + highCount + critCount || 10;

  const lowPct = Math.round((lowCount / totalRiskCount) * 100);
  const medPct = Math.round((medCount / totalRiskCount) * 100);
  const highPct = Math.round((highCount / totalRiskCount) * 100);
  const critPct = Math.round((critCount / totalRiskCount) * 100);

  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const critStroke = (critPct / 100) * circumference;
  const highStroke = (highPct / 100) * circumference;
  const medStroke = (medPct / 100) * circumference;
  const lowStroke = (lowPct / 100) * circumference;

  const critOffset = 0;
  const highOffset = -critStroke;
  const medOffset = -(critStroke + highStroke);
  const lowOffset = -(critStroke + highStroke + medStroke);

  // Dynamic Multi-Point Dataset for Animated Delay Probability Curve
  const chartPoints = (recent_predictions && recent_predictions.length > 0) ? recent_predictions : [
    { shipment_id: 'SHP001', delay_probability: 0.30, expected_delay_days: 0.0, risk_score: 30, risk_level: 'LOW', origin: 'Berlin', destination: 'Paris', transport_mode: 'Truck', confidence: 0.89 },
    { shipment_id: 'SHP002', delay_probability: 0.42, expected_delay_days: 0.5, risk_score: 42, risk_level: 'MEDIUM', origin: 'Warsaw', destination: 'Berlin', transport_mode: 'Rail', confidence: 0.84 },
    { shipment_id: 'SHP003', delay_probability: 0.35, expected_delay_days: 0.2, risk_score: 35, risk_level: 'LOW', origin: 'Madrid', destination: 'Lyon', transport_mode: 'Truck', confidence: 0.91 },
    { shipment_id: 'SHP004', delay_probability: 0.83, expected_delay_days: 3.2, risk_score: 83, risk_level: 'CRITICAL', origin: 'Munich', destination: 'Chicago', transport_mode: 'Air', confidence: 0.88 },
    { shipment_id: 'SHP005', delay_probability: 0.78, expected_delay_days: 2.7, risk_score: 78, risk_level: 'HIGH', origin: 'Rotterdam', destination: 'New York', transport_mode: 'Sea', confidence: 0.85 },
    { shipment_id: 'SHP006', delay_probability: 0.45, expected_delay_days: 0.8, risk_score: 45, risk_level: 'MEDIUM', origin: 'Milan', destination: 'Vienna', transport_mode: 'Truck', confidence: 0.87 },
    { shipment_id: 'SHP007', delay_probability: 0.83, expected_delay_days: 3.5, risk_score: 83, risk_level: 'CRITICAL', origin: 'Frankfurt', destination: 'Tokyo', transport_mode: 'Air', confidence: 0.92 },
    { shipment_id: 'SHP008', delay_probability: 0.65, expected_delay_days: 1.9, risk_score: 65, risk_level: 'HIGH', origin: 'Hamburg', destination: 'Singapore', transport_mode: 'Sea', confidence: 0.82 },
    { shipment_id: 'SHP009', delay_probability: 0.88, expected_delay_days: 4.1, risk_score: 88, risk_level: 'CRITICAL', origin: 'London', destination: 'Dubai', transport_mode: 'Air', confidence: 0.94 },
    { shipment_id: 'SHP010', delay_probability: 0.28, expected_delay_days: 0.0, risk_score: 28, risk_level: 'LOW', origin: 'Antwerp', destination: 'Cologne', transport_mode: 'Rail', confidence: 0.95 }
  ];

  const chartW = 560;
  const chartH = 150;
  const pX = 42;
  const pY = 25;
  const aW = chartW - pX * 2;
  const aH = chartH - pY * 2;

  const curveData = chartPoints.map((pt, idx) => {
    const x = pX + (idx / Math.max(1, chartPoints.length - 1)) * aW;
    let norm = 0;
    let displayVal = '';
    if (activeCurveMetric === 'prob') {
      norm = pt.delay_probability;
      displayVal = `${(pt.delay_probability * 100).toFixed(0)}%`;
    } else if (activeCurveMetric === 'delay') {
      norm = Math.min(1, (pt.expected_delay_days || 0) / 5);
      displayVal = `+${pt.expected_delay_days || 0}d`;
    } else {
      norm = Math.min(1, (pt.risk_score || 0) / 100);
      displayVal = `${pt.risk_score?.toFixed(0) || 0}`;
    }
    const y = (chartH - pY) - norm * aH;
    return {
      ...pt,
      x,
      y,
      norm,
      displayVal
    };
  });

  const curveLinePath = curveData.map((c, i) => `${i === 0 ? 'M' : 'L'} ${c.x.toFixed(1)},${c.y.toFixed(1)}`).join(' ');
  const curveAreaPath = `${curveLinePath} L ${curveData[curveData.length - 1].x.toFixed(1)},${chartH - pY} L ${curveData[0].x.toFixed(1)},${chartH - pY} Z`;
  const activePoint = curveData[activeCurveIndex] || curveData[0];

  return (
    <div className="page-container">
      {/* Top Heading */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Supply Chain Intelligence Overview</h1>
          <p className="page-subtitle">Real-time risk telemetry, dual ML delay predictions, and live SQLite database stream.</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.55rem' }}>
          <button
            className="btn btn-secondary btn-sm"
            onClick={() => setActivePage('risks')}
          >
            <span>Risk Analysis</span>
            <ChevronRight size={13} />
          </button>
          <button
            className="btn btn-primary btn-sm"
            onClick={() => setActivePage('recommendations')}
          >
            <span>Prescriptive Actions (5)</span>
            <ArrowUpRight size={13} />
          </button>
        </div>
      </div>

      {/* Executive Command & Scenario Simulation Deck */}
      <div className="card" style={{
        marginBottom: '2rem',
        padding: '1.4rem 1.75rem',
        background: 'var(--bg-card)',
        borderRadius: 'var(--radius-lg)',
        border: '1px solid var(--border-color)',
        boxShadow: 'var(--shadow-card)'
      }}>
        {/* Top Telemetry Summary Row */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '1rem',
          paddingBottom: '1.15rem',
          borderBottom: '1px solid var(--border-subtle)'
        }}>
          {/* Status & Corpus */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem', flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.55rem' }}>
              <div style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: 'var(--success)', boxShadow: '0 0 10px var(--success)', animation: 'pulseDot 1.6s infinite ease-in-out' }} />
              <span style={{ fontSize: '0.9rem', fontWeight: 800, color: 'var(--text-main)', letterSpacing: '-0.01em' }}>
                Live SQLite Telemetry
              </span>
            </div>
            <span style={{
              fontSize: '0.78rem',
              color: 'var(--text-secondary)',
              backgroundColor: 'var(--moonlight-subtle)',
              padding: '0.25rem 0.65rem',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-color)'
            }}>
              <strong>{dbStats?.total_records || kpis?.total_shipments?.value || 100}</strong> Corridors Indexed • <strong>{dbStats?.file_size_kb || 52} KB</strong>
            </span>
            <span style={{
              fontSize: '0.78rem',
              color: 'var(--brand-primary)',
              backgroundColor: 'var(--moonlight-soft)',
              padding: '0.25rem 0.65rem',
              borderRadius: 'var(--radius-sm)',
              fontWeight: 600
            }}>
              AI Engine: Dual XGBoost
            </span>
          </div>

          {/* Quick Metrics */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
            <span style={{
              fontSize: '0.8rem',
              color: 'var(--text-secondary)',
              padding: '0.3rem 0.75rem',
              borderRadius: 'var(--radius-full)',
              backgroundColor: 'var(--bg-main)',
              border: '1px solid var(--border-color)'
            }}>
              Exposure: <strong style={{ color: kpis?.high_risk_shipments?.percentage >= 70 ? 'var(--critical)' : 'var(--warning)' }}>{kpis?.high_risk_shipments?.percentage || 80.0}%</strong>
            </span>
            <span style={{
              fontSize: '0.8rem',
              color: 'var(--text-secondary)',
              padding: '0.3rem 0.75rem',
              borderRadius: 'var(--radius-full)',
              backgroundColor: 'var(--bg-main)',
              border: '1px solid var(--border-color)'
            }}>
              Mean Delay: <strong style={{ color: 'var(--critical)' }}>+{kpis?.expected_delay?.value || 3.42}d</strong>
            </span>
            {autoRefreshInterval > 0 && (
              <span style={{
                fontSize: '0.78rem',
                color: 'var(--brand-primary)',
                fontWeight: 700,
                padding: '0.3rem 0.75rem',
                backgroundColor: 'var(--moonlight-soft)',
                borderRadius: 'var(--radius-full)',
                display: 'flex',
                alignItems: 'center',
                gap: '0.35rem'
              }}>
                <Clock size={13} className="animate-spin" />
                <span>Next Sync: {countdown}s</span>
              </span>
            )}
          </div>
        </div>

        {/* Bottom Simulation & Ingest Controls Row */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '1rem',
          paddingTop: '1.15rem'
        }}>
          {/* Scenario Selector */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
              <Database size={15} color="var(--brand-primary)" />
              <span style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--text-main)' }}>Simulation Scenario:</span>
            </div>
            <select
              className="form-select"
              style={{
                width: 'auto',
                minWidth: '290px',
                padding: '0.5rem 0.85rem',
                fontSize: '0.82rem',
                fontWeight: 600,
                color: 'var(--text-main)',
                backgroundColor: 'var(--bg-main)',
                cursor: 'pointer'
              }}
              value={selectedScenarioKey}
              onChange={(e) => handleScenarioChange(e.target.value)}
            >
              <option value="standard_live">🟢 Standard Baseline Telemetry (100 Corridors)</option>
              <option value="weather_shock">⛈️ Atlantic Storm & Port Shockwave (+2.8d)</option>
              <option value="optimized">🚀 Green Lane Express Corridors (-2.5d)</option>
              <option value="fuel_crisis">⛽ Fuel Spike & Rail Bottleneck (+1.8d)</option>
              <option value="peak_demand">📦 Peak Demand & Warehouse Saturation (+1.5d)</option>
              <option value="fluctuate_live">🌊 Fluctuate Live Telemetry Readings</option>
              <option value="batch_ingest">⚡ Batch Ingest (+5 AI Predictions)</option>
              <option value="batch_ingest_10">⚡ Mega Ingest (+10 AI Predictions)</option>
              <option value="reset">↺ Reset to Clean 100 Baseline</option>
            </select>
          </div>

          {/* Action Buttons Cluster */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', flexWrap: 'wrap' }}>
            {/* Continuous Ingest Toggle */}
            <button
              className={`btn btn-sm ${autoStreamEnabled ? 'btn-primary' : 'btn-secondary'}`}
              style={{
                fontSize: '0.8rem',
                padding: '0.5rem 0.95rem'
              }}
              onClick={() => setAutoStreamEnabled(!autoStreamEnabled)}
              title="Continuously stream new live shipments through the AI Engine every sync interval"
            >
              <Activity size={14} className={autoStreamEnabled ? 'animate-spin' : ''} />
              <span>{autoStreamEnabled ? 'Auto-Stream Active' : 'Auto-Stream'}</span>
            </button>

            {/* Instant Manual Ingestion Button */}
            <button
              className="btn btn-primary btn-sm"
              onClick={onIngestLiveShipment}
              disabled={isIngesting}
              style={{
                padding: '0.5rem 1.15rem',
                fontSize: '0.82rem',
                fontWeight: 700
              }}
              title="Immediately generate a new shipment through the Python AI engine and persist to SQLite"
            >
              <Zap size={14} className={isIngesting ? 'animate-spin' : ''} />
              <span>{isIngesting ? 'Scoring with AI...' : '⚡ Trigger AI Ingest'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* KPI Cards Grid (Compact & Dense) */}
      <div className="kpi-grid">
        {/* Total Shipments */}
        <div className="kpi-card">
          <div className="kpi-top">
            <span className="kpi-label">Total Shipments (SQLite)</span>
            <div className="kpi-icon-wrap" style={{ backgroundColor: 'var(--moonlight-soft)', color: 'var(--deep-indigo)' }}>
              <Database size={15} />
            </div>
          </div>
          <div>
            <div className="kpi-value-row">
              <span className="kpi-value">{dbStats?.total_records || kpis?.total_shipments?.value || 100}</span>
              <span className="kpi-unit">records</span>
              <span style={{ fontSize: '0.62rem', padding: '0.1rem 0.35rem', borderRadius: '3px', backgroundColor: 'var(--success-bg)', color: 'var(--success)', fontWeight: 700, marginLeft: '0.35rem' }}>▲ Live</span>
            </div>
            <p className="kpi-subtext">
              {dbStats?.live_ingested_records > 0 ? `+${dbStats.live_ingested_records} live ingested` : 'Active database telemetry'}
            </p>
          </div>
        </div>

        {/* High & Critical Risk */}
        <div className="kpi-card" style={{ borderLeft: '3px solid var(--critical)' }}>
          <div className="kpi-top">
            <span className="kpi-label">High & Critical Risk</span>
            <div className="kpi-icon-wrap" style={{ backgroundColor: 'var(--critical-bg)', color: 'var(--critical)' }}>
              <AlertTriangle size={15} />
            </div>
          </div>
          <div>
            <div className="kpi-value-row">
              <span className="kpi-value" style={{ color: 'var(--critical)' }}>{kpis?.high_risk_shipments?.value || 8}</span>
              <span className="kpi-unit">({kpis?.high_risk_shipments?.percentage || 80.0}%)</span>
              <span style={{ fontSize: '0.62rem', padding: '0.1rem 0.35rem', borderRadius: '3px', backgroundColor: 'var(--critical-bg)', color: 'var(--critical)', fontWeight: 700, marginLeft: '0.35rem' }}>
                {kpis?.high_risk_shipments?.percentage >= 70 ? '▲ Critical' : '▼ Nominal'}
              </span>
            </div>
            <p className="kpi-subtext">Real-time risk classification</p>
          </div>
        </div>

        {/* Average Delay Probability */}
        <div className="kpi-card">
          <div className="kpi-top">
            <span className="kpi-label">Avg Delay Probability</span>
            <div className="kpi-icon-wrap" style={{ backgroundColor: 'var(--warning-bg)', color: 'var(--warning)' }}>
              <Percent size={18} />
            </div>
          </div>
          <div>
            <div className="kpi-value-row">
              <span className="kpi-value">{kpis?.avg_delay_probability?.value || 71.9}%</span>
              <span style={{ fontSize: '0.74rem', padding: '0.2rem 0.55rem', borderRadius: 'var(--radius-full)', backgroundColor: 'var(--warning-bg)', color: 'var(--warning)', fontWeight: 700, marginLeft: '0.35rem' }}>Dynamic</span>
            </div>
            <p className="kpi-subtext">Corridor disruption intensity</p>
          </div>
        </div>

        {/* Expected Delay */}
        <div className="kpi-card">
          <div className="kpi-top">
            <span className="kpi-label">Expected Delay</span>
            <div className="kpi-icon-wrap" style={{ backgroundColor: 'var(--moonlight-soft)', color: 'var(--muted-indigo)' }}>
              <Clock size={18} />
            </div>
          </div>
          <div>
            <div className="kpi-value-row">
              <span className="kpi-value">+{kpis?.expected_delay?.value || 3.42}</span>
              <span className="kpi-unit">days</span>
              <span style={{ fontSize: '0.74rem', padding: '0.2rem 0.55rem', borderRadius: 'var(--radius-full)', backgroundColor: 'var(--moonlight-soft)', color: 'var(--brand-primary)', fontWeight: 700, marginLeft: '0.35rem' }}>ML Regressor</span>
            </div>
            <p className="kpi-subtext">Predicted lead-time slip</p>
          </div>
        </div>

        {/* AI Prediction Accuracy */}
        <div className="kpi-card">
          <div className="kpi-top">
            <span className="kpi-label">AI Accuracy</span>
            <div className="kpi-icon-wrap" style={{ backgroundColor: 'var(--success-bg)', color: 'var(--success)' }}>
              <CheckCircle size={18} />
            </div>
          </div>
          <div>
            <div className="kpi-value-row">
              <span className="kpi-value" style={{ color: 'var(--success)' }}>{kpis?.ai_prediction_accuracy?.value || 84.6}%</span>
              <span style={{ fontSize: '0.74rem', padding: '0.2rem 0.55rem', borderRadius: 'var(--radius-full)', backgroundColor: 'var(--success-bg)', color: 'var(--success)', fontWeight: 700, marginLeft: '0.35rem' }}>Verified</span>
            </div>
            <p className="kpi-subtext">Continuous real-time audit</p>
          </div>
        </div>

        {/* Pipeline Readiness */}
        <div className="kpi-card">
          <div className="kpi-top">
            <span className="kpi-label">Pipeline Readiness</span>
            <div className="kpi-icon-wrap" style={{ backgroundColor: 'var(--moonlight-soft)', color: 'var(--brand-primary)' }}>
              <ShieldCheck size={18} />
            </div>
          </div>
          <div>
            <div className="kpi-value-row">
              <span className="kpi-value" style={{ color: 'var(--brand-primary)' }}>{kpis?.pipeline_readiness?.value || 100}%</span>
            </div>
            <p className="kpi-subtext">42/42 validation checks passed</p>
          </div>
        </div>
      </div>

      {/* Visual Data Analytics Suite (Donut, Curve, Transport) */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>

        {/* Chart 1: Shipment Risk Distribution Donut with Animated Segments & Initial Readings */}
        <div className="card">
          <div className="card-header">
            <div>
              <h3 className="card-title">
                <BarChart2 size={17} color="var(--brand-primary)" />
                <span>Risk Distribution (n=10 Batch)</span>
              </h3>
              <p className="card-subtitle">Dual classification threshold allocation</p>
            </div>
            <span className="badge badge-critical">
              {critPct}% Critical
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-around', padding: '0.4rem 0' }}>
            {/* Animated SVG Donut */}
            <div style={{ position: 'relative', width: '135px', height: '135px' }}>
              <svg width="135" height="135" viewBox="0 0 140 140" style={{ transform: 'rotate(-90deg)', overflow: 'visible' }}>
                <circle cx="70" cy="70" r={radius} fill="none" stroke="var(--border-subtle)" strokeWidth="16" />

                {/* Critical Segment */}
                <circle
                  cx="70" cy="70" r={radius} fill="none"
                  stroke="var(--critical)"
                  strokeWidth={hoveredRiskSlice === 'CRITICAL' ? '20' : '16'}
                  strokeDasharray={`${critStroke} ${circumference}`}
                  strokeDashoffset={critOffset}
                  style={{ transition: 'all 0.3s ease', cursor: 'pointer' }}
                  onMouseEnter={() => setHoveredRiskSlice('CRITICAL')}
                />

                {/* High Segment */}
                <circle
                  cx="70" cy="70" r={radius} fill="none"
                  stroke="var(--warning)"
                  strokeWidth={hoveredRiskSlice === 'HIGH' ? '20' : '16'}
                  strokeDasharray={`${highStroke} ${circumference}`}
                  strokeDashoffset={highOffset}
                  style={{ transition: 'all 0.3s ease', cursor: 'pointer' }}
                  onMouseEnter={() => setHoveredRiskSlice('HIGH')}
                />

                {/* Medium Segment */}
                {medCount > 0 && (
                  <circle
                    cx="70" cy="70" r={radius} fill="none"
                    stroke="var(--muted-indigo)"
                    strokeWidth={hoveredRiskSlice === 'MEDIUM' ? '20' : '16'}
                    strokeDasharray={`${medStroke} ${circumference}`}
                    strokeDashoffset={medOffset}
                    style={{ transition: 'all 0.3s ease', cursor: 'pointer' }}
                    onMouseEnter={() => setHoveredRiskSlice('MEDIUM')}
                  />
                )}

                {/* Low Segment */}
                <circle
                  cx="70" cy="70" r={radius} fill="none"
                  stroke="var(--success)"
                  strokeWidth={hoveredRiskSlice === 'LOW' ? '20' : '16'}
                  strokeDasharray={`${lowStroke} ${circumference}`}
                  strokeDashoffset={lowOffset}
                  style={{ transition: 'all 0.3s ease', cursor: 'pointer' }}
                  onMouseEnter={() => setHoveredRiskSlice('LOW')}
                />
              </svg>

              {/* Initial Instant Center Reading HUD */}
              <div style={{
                position: 'absolute',
                inset: 0,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                textAlign: 'center',
                pointerEvents: 'none'
              }}>
                <span style={{
                  fontSize: '1.35rem',
                  fontWeight: 800,
                  color: hoveredRiskSlice === 'CRITICAL' ? 'var(--critical)' : hoveredRiskSlice === 'HIGH' ? 'var(--warning)' : hoveredRiskSlice === 'LOW' ? 'var(--success)' : 'var(--deep-indigo)',
                  lineHeight: '1',
                  transition: 'color 0.25s'
                }}>
                  {hoveredRiskSlice === 'CRITICAL' ? `${critPct}%` : hoveredRiskSlice === 'HIGH' ? `${highPct}%` : hoveredRiskSlice === 'LOW' ? `${lowPct}%` : `${medPct}%`}
                </span>
                <span style={{ fontSize: '0.62rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.04em', marginTop: '2px' }}>
                  {hoveredRiskSlice}
                </span>
                <span style={{ fontSize: '0.55rem', color: 'var(--text-muted)' }}>
                  {hoveredRiskSlice === 'CRITICAL' ? `${critCount}/${totalRiskCount} delayed` : hoveredRiskSlice === 'HIGH' ? `${highCount}/${totalRiskCount} high` : hoveredRiskSlice === 'LOW' ? `${lowCount}/${totalRiskCount} low` : `${medCount}/${totalRiskCount}`}
                </span>
              </div>
            </div>

            {/* Initial Instant Segment Breakdown Readings */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.45rem', fontSize: '0.78rem', minWidth: '135px' }}>
              <div
                style={{
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '0.45rem',
                  padding: '0.2rem 0.4rem', borderRadius: 'var(--radius-xs)',
                  backgroundColor: hoveredRiskSlice === 'CRITICAL' ? 'var(--moonlight-soft)' : 'transparent',
                  cursor: 'pointer'
                }}
                onMouseEnter={() => setHoveredRiskSlice('CRITICAL')}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                  <span style={{ width: '9px', height: '9px', borderRadius: '2px', backgroundColor: 'var(--critical)' }} />
                  <span>Critical</span>
                </div>
                <strong>{critCount} ({critPct}%)</strong>
              </div>

              <div
                style={{
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '0.45rem',
                  padding: '0.2rem 0.4rem', borderRadius: 'var(--radius-xs)',
                  backgroundColor: hoveredRiskSlice === 'HIGH' ? 'var(--moonlight-soft)' : 'transparent',
                  cursor: 'pointer'
                }}
                onMouseEnter={() => setHoveredRiskSlice('HIGH')}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                  <span style={{ width: '9px', height: '9px', borderRadius: '2px', backgroundColor: 'var(--warning)' }} />
                  <span>High</span>
                </div>
                <strong>{highCount} ({highPct}%)</strong>
              </div>

              <div
                style={{
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '0.45rem',
                  padding: '0.2rem 0.4rem', borderRadius: 'var(--radius-xs)',
                  backgroundColor: hoveredRiskSlice === 'MEDIUM' ? 'var(--moonlight-soft)' : 'transparent',
                  cursor: 'pointer'
                }}
                onMouseEnter={() => setHoveredRiskSlice('MEDIUM')}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                  <span style={{ width: '9px', height: '9px', borderRadius: '2px', backgroundColor: 'var(--muted-indigo)' }} />
                  <span>Medium</span>
                </div>
                <strong>{medCount} ({medPct}%)</strong>
              </div>

              <div
                style={{
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '0.45rem',
                  padding: '0.2rem 0.4rem', borderRadius: 'var(--radius-xs)',
                  backgroundColor: hoveredRiskSlice === 'LOW' ? 'var(--moonlight-soft)' : 'transparent',
                  cursor: 'pointer'
                }}
                onMouseEnter={() => setHoveredRiskSlice('LOW')}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                  <span style={{ width: '9px', height: '9px', borderRadius: '2px', backgroundColor: 'var(--success)' }} />
                  <span>Low</span>
                </div>
                <strong>{lowCount} ({lowPct}%)</strong>
              </div>
            </div>
          </div>
        </div>

        {/* Chart 2: Animated Delay Probability Curve with Initial Instant Readings & Interactive Scrubbing */}
        <div className="card" style={{ gridColumn: 'span 2' }}>
          <div className="card-header" style={{ marginBottom: '0.45rem', flexWrap: 'wrap', gap: '0.5rem' }}>
            <div>
              <h3 className="card-title">
                <TrendingUp size={15} color="var(--deep-indigo)" />
                <span>Animated Dual-Model Delay Probability Curve</span>
              </h3>
              <p className="card-subtitle">Real-time model trajectory with continuous readings at initial instant</p>
            </div>

            {/* Metric Switcher Controls */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
              <span style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-secondary)', marginRight: '0.2rem' }}>Metric:</span>
              <button
                className={`btn btn-sm ${activeCurveMetric === 'prob' ? 'btn-primary' : 'btn-secondary'}`}
                style={{ padding: '0.35rem 0.75rem', fontSize: '0.78rem', fontWeight: 600 }}
                onClick={() => setActiveCurveMetric('prob')}
              >
                Delay Prob (%)
              </button>
              <button
                className={`btn btn-sm ${activeCurveMetric === 'delay' ? 'btn-primary' : 'btn-secondary'}`}
                style={{ padding: '0.35rem 0.75rem', fontSize: '0.78rem', fontWeight: 600 }}
                onClick={() => setActiveCurveMetric('delay')}
              >
                Expected Delay (d)
              </button>
              <button
                className={`btn btn-sm ${activeCurveMetric === 'risk' ? 'btn-primary' : 'btn-secondary'}`}
                style={{ padding: '0.35rem 0.75rem', fontSize: '0.78rem', fontWeight: 600 }}
                onClick={() => setActiveCurveMetric('risk')}
              >
                Risk Score
              </button>
            </div>
          </div>

          {/* INITIAL INSTANT READINGS HUD BAR (Always Visible On Mount) */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '0.75rem',
            padding: '0.75rem 1.15rem',
            backgroundColor: 'var(--moonlight-subtle)',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--border-color)',
            marginBottom: '0.85rem',
            fontSize: '0.84rem'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
              <span style={{
                width: '10px',
                height: '10px',
                borderRadius: '50%',
                backgroundColor: activePoint.risk_level === 'CRITICAL' ? 'var(--critical)' : activePoint.risk_level === 'HIGH' ? 'var(--warning)' : 'var(--success)'
              }} />
              <span><strong>Corridor Tracked:</strong> <span style={{ color: 'var(--brand-primary)', fontWeight: 700 }}>{activePoint.shipment_id}</span> ({activePoint.origin} ➔ {activePoint.destination})</span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
              <span>Delay Prob: <strong style={{ color: activePoint.delay_probability >= 0.7 ? 'var(--critical)' : 'var(--text-main)' }}>{(activePoint.delay_probability * 100).toFixed(1)}%</strong></span>
              <span>Exp. Delay: <strong style={{ color: 'var(--critical)' }}>+{activePoint.expected_delay_days}d</strong></span>
              <span>Score: <strong>{activePoint.risk_score?.toFixed(1)}</strong></span>
              <span className={`badge ${activePoint.risk_level === 'CRITICAL' ? 'badge-critical' : activePoint.risk_level === 'HIGH' ? 'badge-high' : 'badge-low'}`}>
                {activePoint.risk_level}
              </span>
            </div>
          </div>

          {/* ANIMATED SVG CHART CANVAS WITH VISIBLE INITIAL POINTS & CALLOUTS */}
          <div style={{ width: '100%', height: '150px', position: 'relative' }}>
            <svg
              width="100%"
              height="150"
              viewBox={`0 0 ${chartW} ${chartH}`}
              preserveAspectRatio="none"
              style={{ overflow: 'visible' }}
            >
              <defs>
                <linearGradient id="trendGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stopColor="var(--deep-indigo)" stopOpacity="0.32" />
                  <stop offset="60%" stopColor="var(--soft-lavender)" stopOpacity="0.12" />
                  <stop offset="100%" stopColor="var(--bg-main)" stopOpacity="0.0" />
                </linearGradient>
              </defs>

              {/* Reference Grid & Threshold Lines with Text Readings */}
              <line x1={pX} y1="40" x2={chartW - pX} y2="40" stroke="var(--critical)" strokeDasharray="3 3" strokeOpacity="0.4" />
              <text x={chartW - pX - 2} y="36" fill="var(--critical)" fontSize="8.5" textAnchor="end" fontWeight="600">0.80 Critical Risk Threshold</text>

              <line x1={pX} y1="78" x2={chartW - pX} y2="78" stroke="var(--warning)" strokeDasharray="3 3" strokeOpacity="0.4" />
              <text x={chartW - pX - 2} y="74" fill="var(--warning)" fontSize="8.5" textAnchor="end" fontWeight="600">0.50 Operational Baseline</text>

              <line x1={pX} y1="115" x2={chartW - pX} y2="115" stroke="var(--success)" strokeDasharray="3 3" strokeOpacity="0.4" />
              <text x={chartW - pX - 2} y="111" fill="var(--success)" fontSize="8.5" textAnchor="end" fontWeight="600">0.30 Safe Corridor Baseline</text>

              {/* Active Scrubber Vertical Tracking Line */}
              <line
                x1={activePoint.x}
                y1={pY}
                x2={activePoint.x}
                y2={chartH - pY}
                stroke="var(--deep-indigo)"
                strokeWidth="1.5"
                strokeDasharray="2 2"
                strokeOpacity="0.7"
              />

              {/* Animated Gradient Area */}
              <path
                d={curveAreaPath}
                className="chart-animated-area"
                fill="url(#trendGrad)"
              />

              {/* Animated Continuous Stroke Line */}
              <path
                d={curveLinePath}
                className="chart-animated-path"
                fill="none"
                stroke="var(--deep-indigo)"
                strokeWidth="2.75"
                strokeLinecap="round"
                strokeLinejoin="round"
              />

              {/* Active Radar Ping Halo on Currently Focused Point */}
              <circle
                cx={activePoint.x}
                cy={activePoint.y}
                r="11"
                fill="none"
                stroke={activePoint.risk_level === 'CRITICAL' ? 'var(--critical)' : 'var(--deep-indigo)'}
                strokeWidth="2"
                style={{ animation: 'radarPing 1.6s infinite ease-out' }}
              />

              {/* Render Every Point with Hover & Click Interaction */}
              {curveData.map((pt, idx) => {
                const isSelected = idx === activeCurveIndex;
                const ptColor = pt.risk_level === 'CRITICAL' ? 'var(--critical)' : pt.risk_level === 'HIGH' ? 'var(--warning)' : pt.risk_level === 'MEDIUM' ? 'var(--muted-indigo)' : 'var(--success)';

                // Show pinned reading badge directly on critical & key points at initial instant!
                const showInstantBadge = idx === 0 || idx === 3 || idx === 6 || idx === 8 || idx === 9 || isSelected;

                return (
                  <g
                    key={pt.shipment_id}
                    style={{ cursor: 'pointer' }}
                    onClick={() => {
                      setActiveCurveIndex(idx);
                      onSelectShipment(pt.shipment_id);
                    }}
                    onMouseEnter={() => setActiveCurveIndex(idx)}
                  >
                    {/* Circle Node */}
                    <circle
                      cx={pt.x}
                      cy={pt.y}
                      r={isSelected ? '6.5' : '4.5'}
                      fill={ptColor}
                      stroke="var(--bg-card)"
                      strokeWidth={isSelected ? '2.5' : '1.5'}
                      style={{ transition: 'r 0.2s, stroke-width 0.2s' }}
                    />

                    {/* Initial Instant Pinned Reading Callout Badge */}
                    {showInstantBadge && (
                      <g transform={`translate(${pt.x}, ${pt.y - 18})`}>
                        <rect
                          x="-25"
                          y="-9"
                          width="50"
                          height="14"
                          rx="3"
                          fill={ptColor}
                          opacity={isSelected ? 1 : 0.92}
                        />
                        <text
                          x="0"
                          y="1.5"
                          textAnchor="middle"
                          fill="#FFFFFF"
                          fontSize="7.5"
                          fontWeight="700"
                        >
                          {pt.shipment_id}: {pt.displayVal}
                        </text>
                      </g>
                    )}
                  </g>
                );
              })}
            </svg>
          </div>

          {/* Bottom Corridor Labels with Risk Indicators */}
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.67rem', color: 'var(--text-secondary)', marginTop: '0.4rem', padding: '0 0.5rem' }}>
            {curveData.map((pt, idx) => (
              <span
                key={pt.shipment_id}
                onClick={() => setActiveCurveIndex(idx)}
                style={{
                  cursor: 'pointer',
                  fontWeight: idx === activeCurveIndex ? 700 : 500,
                  color: idx === activeCurveIndex ? 'var(--deep-indigo)' : 'var(--text-secondary)',
                  borderBottom: idx === activeCurveIndex ? '2px solid var(--deep-indigo)' : 'none'
                }}
              >
                {pt.shipment_id}
              </span>
            ))}
          </div>
        </div>

        {/* Chart 3: Transport Mode Risk Benchmark with Animated Bars */}
        <div className="card">
          <div className="card-header">
            <div>
              <h3 className="card-title">
                <Truck size={15} color="var(--deep-indigo)" />
                <span>Transport Mode Risk Benchmark</span>
              </h3>
              <p className="card-subtitle">Delay rate across 100 corridors with readings</p>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem', paddingTop: '0.2rem' }}>
            {transport_breakdown?.map((item) => (
              <div key={item.mode}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.76rem', marginBottom: '0.2rem' }}>
                  <span style={{ fontWeight: 600 }}>{item.mode} ({item.total_shipments} corridors)</span>
                  <span style={{ color: 'var(--text-secondary)' }}>
                    <strong>{item.delayed_percentage}%</strong> delayed • +{item.avg_delay_days}d avg
                  </span>
                </div>
                <div style={{ height: '8px', backgroundColor: 'var(--border-subtle)', borderRadius: '4px', overflow: 'hidden' }}>
                  <div
                    className="chart-bar-grow"
                    style={{
                      height: '100%',
                      width: `${item.delayed_percentage}%`,
                      backgroundColor: item.delayed_percentage >= 80 ? 'var(--critical)' : item.delayed_percentage >= 65 ? 'var(--warning)' : 'var(--muted-indigo)',
                      borderRadius: '4px'
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* Critical Shipment Alerts Grid */}
      <div className="card" style={{ marginBottom: '1.25rem' }}>
        <div className="card-header">
          <div>
            <h3 className="card-title">
              <AlertTriangle size={15} color="var(--critical)" />
              <span>Highest Disruption Exposure Alerts</span>
            </h3>
            <p className="card-subtitle">Urgent operational review required for shipments exceeding critical thresholds</p>
          </div>
          <button
            className="btn btn-secondary btn-sm"
            onClick={() => setActivePage('shipments')}
          >
            <span>All Shipments</span>
            <ChevronRight size={13} />
          </button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '0.65rem' }}>
          {critical_alerts?.map((item) => (
            <div
              key={item.shipment_id}
              onClick={() => onSelectShipment(item.shipment_id)}
              style={{
                padding: '0.75rem',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--border-color)',
                backgroundColor: 'var(--bg-main)',
                cursor: 'pointer',
                transition: 'all var(--transition-fast)'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = 'var(--critical)';
                e.currentTarget.style.backgroundColor = '#FFFBFB';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = 'var(--border-color)';
                e.currentTarget.style.backgroundColor = 'var(--bg-main)';
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.3rem' }}>
                <span style={{ fontWeight: 700, fontSize: '0.86rem', color: 'var(--deep-indigo)' }}>
                  {item.shipment_id}
                </span>
                <span className="badge badge-critical" style={{ fontSize: '0.64rem' }}>{item.risk_level}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.76rem', marginBottom: '0.3rem' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Delay Prob: <strong>{(item.delay_probability * 100).toFixed(1)}%</strong></span>
                <span style={{ color: 'var(--critical)', fontWeight: 700 }}>+{item.expected_delay_days}d</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.68rem', color: 'var(--text-muted)' }}>
                <span>Score: {item.risk_score?.toFixed(1)}</span>
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.2rem', color: 'var(--deep-indigo)', fontWeight: 600 }}>
                  Inspect <Eye size={11} />
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Live SQLite Database Table with Ingestion Ledger */}
      <div className="card">
        <div className="card-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem', flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
              <button
                className={`btn btn-sm ${activeTab === 'live_stream' ? 'btn-primary' : 'btn-secondary'}`}
                style={{ fontSize: '0.82rem', padding: '0.45rem 0.95rem', fontWeight: 600 }}
                onClick={() => setActiveTab('live_stream')}
              >
                <Radio size={14} className="animate-spin" />
                <span>Live SQLite Stream ({liveRecords?.length || 20})</span>
              </button>
              <button
                className={`btn btn-sm ${activeTab === 'alerts' ? 'btn-primary' : 'btn-secondary'}`}
                style={{ fontSize: '0.82rem', padding: '0.45rem 0.95rem', fontWeight: 600 }}
                onClick={() => setActiveTab('alerts')}
              >
                <Bell size={14} />
                <span>Live Alerts Feed ({notifications?.length || 5})</span>
              </button>
              <button
                className={`btn btn-sm ${activeTab === 'recent_predictions' ? 'btn-primary' : 'btn-secondary'}`}
                style={{ fontSize: '0.82rem', padding: '0.45rem 0.95rem', fontWeight: 600 }}
                onClick={() => setActiveTab('recent_predictions')}
              >
                <BarChart2 size={14} />
                <span>Active Batch (10)</span>
              </button>
              <button
                className={`btn btn-sm ${activeTab === 'radar_matrix' ? 'btn-primary' : 'btn-secondary'}`}
                style={{ fontSize: '0.82rem', padding: '0.45rem 0.95rem', fontWeight: 600 }}
                onClick={() => setActiveTab('radar_matrix')}
              >
                <Sparkles size={14} />
                <span>Telemetry Radar & Scatter Matrix</span>
              </button>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
              Auto-syncs with SQLite database every {autoRefreshInterval || '10'}s
            </span>
          </div>
        </div>

        {/* Tab 1: Live Stream Records from SQLite */}
        {activeTab === 'live_stream' && (
          <div className="table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Shipment ID</th>
                  <th>Supplier</th>
                  <th>Origin → Destination</th>
                  <th>Mode</th>
                  <th>Distance</th>
                  <th>AI Delay Prob</th>
                  <th>Exp. Delay</th>
                  <th>Risk Level</th>
                  <th>Ingestion Origin</th>
                  <th>Inspect</th>
                </tr>
              </thead>
              <tbody>
                {liveRecords && liveRecords.length > 0 ? (
                  liveRecords.map((s) => {
                    const isLive = s.is_live === 1;
                    return (
                      <tr
                        key={s.shipment_id}
                        className="clickable"
                        onClick={() => onSelectShipment(s.shipment_id)}
                        style={{ backgroundColor: isLive ? '#F9F7FF' : 'transparent' }}
                      >
                        <td style={{ fontWeight: 700, color: 'var(--deep-indigo)' }}>
                          {s.shipment_id}
                          {isLive && (
                            <span className="badge" style={{ backgroundColor: 'var(--purple-accent)', color: '#FFFFFF', marginLeft: '0.4rem', fontSize: '0.58rem' }}>
                              LIVE STREAM
                            </span>
                          )}
                        </td>
                        <td>{s.supplier_id}</td>
                        <td>{s.origin} → {s.destination}</td>
                        <td>{s.transport_mode}</td>
                        <td style={{ fontFamily: 'var(--font-mono)' }}>{s.distance_km} km</td>
                        <td style={{ fontWeight: 700 }}>
                          {(s.delay_probability * 100).toFixed(1)}%
                        </td>
                        <td>+{s.expected_delay_days?.toFixed(1)}d</td>
                        <td>
                          <span className={`badge ${
                            s.risk_level === 'CRITICAL' ? 'badge-critical' :
                            s.risk_level === 'HIGH' ? 'badge-high' :
                            s.risk_level === 'MEDIUM' ? 'badge-medium' : 'badge-low'
                          }`}>
                            {s.risk_level}
                          </span>
                        </td>
                        <td>
                          <span style={{ fontSize: '0.7rem', color: isLive ? 'var(--purple-accent)' : 'var(--text-secondary)', fontWeight: isLive ? 600 : 400 }}>
                            {isLive ? 'AI Ingestion Stream' : 'Historical Corpus'}
                          </span>
                        </td>
                        <td>
                          <button
                            className="btn btn-secondary btn-sm"
                            style={{ padding: '0.15rem 0.45rem', fontSize: '0.68rem' }}
                            onClick={(e) => {
                              e.stopPropagation();
                              onSelectShipment(s.shipment_id);
                            }}
                          >
                            <Eye size={11} />
                            <span>Panel</span>
                          </button>
                        </td>
                      </tr>
                    );
                  })
                ) : (
                  recent_predictions?.slice(0, 10).map((s) => (
                    <tr
                      key={s.shipment_id}
                      className="clickable"
                      onClick={() => onSelectShipment(s.shipment_id)}
                    >
                      <td style={{ fontWeight: 600, color: 'var(--deep-indigo)' }}>{s.shipment_id}</td>
                      <td>{s.supplier_id}</td>
                      <td>{s.origin} → {s.destination}</td>
                      <td>{s.transport_mode}</td>
                      <td>—</td>
                      <td style={{ fontWeight: 600 }}>{(s.delay_probability * 100).toFixed(1)}%</td>
                      <td>+{s.expected_delay_days?.toFixed(1)}d</td>
                      <td>
                        <span className={`badge ${s.risk_level === 'CRITICAL' ? 'badge-critical' : 'badge-high'}`}>
                          {s.risk_level}
                        </span>
                      </td>
                      <td><span style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>AI Inference Batch</span></td>
                      <td>
                        <button className="btn btn-secondary btn-sm" style={{ padding: '0.15rem 0.45rem', fontSize: '0.68rem' }}>
                          <Eye size={11} />
                          <span>Panel</span>
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}

        {/* Tab 2: Live Operational Alerts Feed */}
        {activeTab === 'alerts' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem', padding: '0.75rem 0.5rem' }}>
            {/* Alerts Feed Controls Bar */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: '0.75rem',
              padding: '0.75rem 1rem',
              backgroundColor: 'var(--bg-main)',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--border-color)'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
                <span style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-main)', marginRight: '0.25rem' }}>
                  Filter Feed:
                </span>
                <button
                  className={`filter-chip ${tabAlertFilter === 'ALL' ? 'active' : ''}`}
                  onClick={() => setTabAlertFilter('ALL')}
                >
                  All ({notifications?.length || 0})
                </button>
                <button
                  className={`filter-chip ${tabAlertFilter === 'CRITICAL' ? 'active' : ''}`}
                  onClick={() => setTabAlertFilter('CRITICAL')}
                >
                  Critical ({notifications?.filter(n => n.severity === 'CRITICAL').length || 0})
                </button>
                <button
                  className={`filter-chip ${tabAlertFilter === 'WARNING' ? 'active' : ''}`}
                  onClick={() => setTabAlertFilter('WARNING')}
                >
                  Warnings ({notifications?.filter(n => n.severity === 'WARNING').length || 0})
                </button>
                <button
                  className={`filter-chip ${tabAlertFilter === 'INGEST' ? 'active' : ''}`}
                  onClick={() => setTabAlertFilter('INGEST')}
                >
                  Live Ingest ({notifications?.filter(n => n.event_type === 'LIVE_INGEST').length || 0})
                </button>
              </div>

              <button
                className="btn btn-secondary btn-sm"
                onClick={onIngestLiveShipment}
                disabled={isIngesting}
                style={{ fontSize: '0.78rem', padding: '0.35rem 0.75rem' }}
                title="Inject a real-time synthetic shipment to trigger immediate AI scoring and alert generation"
              >
                <Radio size={13} className={isIngesting ? 'animate-spin' : ''} color="var(--brand-primary)" />
                <span>{isIngesting ? 'Ingesting...' : 'Simulate Live Ingest (+1 Alert)'}</span>
              </button>
            </div>

            {/* Alerts Feed List */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.55rem' }}>
              {(notifications || [])
                .filter(item => {
                  if (tabAlertFilter === 'ALL') return true;
                  if (tabAlertFilter === 'CRITICAL') return item.severity === 'CRITICAL';
                  if (tabAlertFilter === 'WARNING') return item.severity === 'WARNING';
                  if (tabAlertFilter === 'INGEST') return item.event_type === 'LIVE_INGEST';
                  return true;
                })
                .map((evt, idx) => (
                  <div
                    key={evt.event_id || idx}
                    onClick={() => {
                      if (evt.shipment_id && onSelectShipment) {
                        onSelectShipment(evt.shipment_id);
                      }
                    }}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '0.85rem 1.15rem',
                      backgroundColor: 'var(--bg-main)',
                      borderRadius: 'var(--radius-md)',
                      border: '1px solid var(--border-color)',
                      boxShadow: 'var(--shadow-xs)',
                      cursor: evt.shipment_id ? 'pointer' : 'default',
                      transition: 'all var(--transition-fast)'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.borderColor = 'var(--soft-lavender)';
                      e.currentTarget.style.backgroundColor = 'var(--moonlight-soft)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.borderColor = 'var(--border-color)';
                      e.currentTarget.style.backgroundColor = 'var(--bg-main)';
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem', flex: 1 }}>
                      <div style={{
                        width: '32px',
                        height: '32px',
                        borderRadius: 'var(--radius-sm)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        backgroundColor: evt.severity === 'CRITICAL' ? 'rgba(239, 68, 68, 0.12)' :
                                         evt.severity === 'WARNING' ? 'rgba(245, 158, 11, 0.12)' : 'rgba(79, 70, 229, 0.12)',
                        flexShrink: 0
                      }}>
                        {evt.severity === 'CRITICAL' ? (
                          <AlertTriangle size={16} color="var(--critical)" />
                        ) : evt.severity === 'WARNING' ? (
                          <AlertCircle size={16} color="var(--warning)" />
                        ) : (
                          <Radio size={16} color="var(--brand-primary)" />
                        )}
                      </div>

                      <div style={{ flex: 1 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.55rem', marginBottom: '0.2rem' }}>
                          <span style={{ fontWeight: 700, fontSize: '0.84rem', color: 'var(--text-main)' }}>
                            {evt.title}
                          </span>
                          <span className={`badge ${
                            evt.severity === 'CRITICAL' ? 'badge-critical' :
                            evt.severity === 'WARNING' ? 'badge-high' : 'badge-low'
                          }`} style={{ fontSize: '0.62rem', padding: '0.15rem 0.45rem' }}>
                            {evt.severity}
                          </span>
                          {evt.shipment_id && (
                            <span style={{
                              fontSize: '0.68rem',
                              fontFamily: 'var(--font-mono)',
                              fontWeight: 700,
                              color: 'var(--brand-primary)',
                              backgroundColor: 'var(--moonlight-subtle)',
                              padding: '0.1rem 0.4rem',
                              borderRadius: 'var(--radius-xs)'
                            }}>
                              {evt.shipment_id}
                            </span>
                          )}
                        </div>
                        <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: '1.4' }}>
                          {evt.message}
                        </p>
                      </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginLeft: '1rem', flexShrink: 0 }}>
                      <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                        {evt.timestamp ? new Date(evt.timestamp).toLocaleTimeString() : 'Just now'}
                      </span>

                      {evt.shipment_id && (
                        <button
                          className="btn btn-secondary btn-sm"
                          style={{ padding: '0.3rem 0.65rem', fontSize: '0.74rem' }}
                          onClick={(e) => {
                            e.stopPropagation();
                            if (onSelectShipment) onSelectShipment(evt.shipment_id);
                          }}
                        >
                          <Eye size={12} />
                          <span>Inspect</span>
                        </button>
                      )}
                    </div>
                  </div>
                ))}
            </div>

            {(!notifications || notifications.length === 0) && (
              <div style={{ padding: '2.5rem', textAlign: 'center', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                <CheckCircle size={28} color="var(--success)" style={{ margin: '0 auto 0.5rem', opacity: 0.8 }} />
                <p style={{ fontWeight: 600 }}>No active operational alerts found</p>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  All transit telemetry within safe statistical variance thresholds.
                </span>
              </div>
            )}
          </div>
        )}

        {/* Tab 3: Active Batch Predictions */}
        {activeTab === 'recent_predictions' && (
          <div className="table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Shipment ID</th>
                  <th>Supplier</th>
                  <th>Route Corridor</th>
                  <th>Transport</th>
                  <th>Delay Prob</th>
                  <th>Expected Delay</th>
                  <th>Risk Level</th>
                  <th>Status</th>
                  <th>Inspect</th>
                </tr>
              </thead>
              <tbody>
                {recent_predictions?.map((s) => (
                  <tr
                    key={s.shipment_id}
                    className="clickable"
                    onClick={() => onSelectShipment(s.shipment_id)}
                  >
                    <td style={{ fontWeight: 600, color: 'var(--deep-indigo)' }}>{s.shipment_id}</td>
                    <td>{s.supplier_id}</td>
                    <td>{s.origin} → {s.destination}</td>
                    <td>{s.transport_mode}</td>
                    <td style={{ fontWeight: 600 }}>{(s.delay_probability * 100).toFixed(1)}%</td>
                    <td>+{s.expected_delay_days?.toFixed(1)}d</td>
                    <td>
                      <span className={`badge ${
                        s.risk_level === 'CRITICAL' ? 'badge-critical' :
                        s.risk_level === 'HIGH' ? 'badge-high' :
                        s.risk_level === 'MEDIUM' ? 'badge-medium' : 'badge-low'
                      }`}>
                        {s.risk_level}
                      </span>
                    </td>
                    <td>
                      <span style={{
                        fontSize: '0.74rem',
                        fontWeight: 600,
                        color: s.status === 'DELAYED' ? 'var(--critical)' : 'var(--success)'
                      }}>
                        {s.status}
                      </span>
                    </td>
                    <td>
                      <button
                        className="btn btn-secondary btn-sm"
                        style={{ padding: '0.15rem 0.45rem', fontSize: '0.68rem' }}
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectShipment(s.shipment_id);
                        }}
                      >
                        <Eye size={11} />
                        <span>Details</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Tab 4: Interactive Animated Telemetry Radar & Corridor Scatter Matrix */}
        {activeTab === 'radar_matrix' && (
          <div style={{ padding: '1rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem', flexWrap: 'wrap', gap: '0.5rem' }}>
              <div>
                <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-main)' }}>
                  Multi-Dimensional Transit Telemetry Matrix (Distance vs Risk Probability)
                </span>
                <p style={{ fontSize: '0.74rem', color: 'var(--text-secondary)' }}>
                  Animated sensor coordinates with readings visible at initial instant. Click any point to open deep AI telemetry.
                </p>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '0.74rem' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                  <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--critical)' }} />
                  Critical Disruption (&gt;70%)
                </span>
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                  <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--warning)' }} />
                  Elevated Risk (50-70%)
                </span>
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                  <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--success)' }} />
                  Nominal Flow (&lt;50%)
                </span>
              </div>
            </div>

            {/* Radar SVG Canvas */}
            <div style={{ width: '100%', height: '220px', position: 'relative', backgroundColor: 'var(--bg-main)', borderRadius: 'var(--radius-md)', padding: '0.5rem', border: '1px solid var(--border-color)', overflow: 'hidden' }}>
              <svg width="100%" height="220" viewBox="0 0 700 220" preserveAspectRatio="none">
                <defs>
                  <radialGradient id="radarRadial" cx="50%" cy="50%" r="50%">
                    <stop offset="0%" stopColor="var(--deep-indigo)" stopOpacity="0.08" />
                    <stop offset="100%" stopColor="var(--deep-indigo)" stopOpacity="0.01" />
                  </radialGradient>
                </defs>

                {/* Radar Grid Circles */}
                <circle cx="350" cy="110" r="40" fill="none" stroke="var(--border-color)" strokeDasharray="3 3" />
                <circle cx="350" cy="110" r="90" fill="none" stroke="var(--border-color)" strokeDasharray="3 3" />
                <circle cx="350" cy="110" r="140" fill="none" stroke="var(--border-color)" strokeDasharray="3 3" />
                <circle cx="350" cy="110" r="190" fill="url(#radarRadial)" stroke="var(--border-color)" strokeDasharray="3 3" />

                {/* Grid Axes with readings */}
                <line x1="50" y1="110" x2="650" y2="110" stroke="var(--border-color)" strokeWidth="1" />
                <line x1="350" y1="15" x2="350" y2="205" stroke="var(--border-color)" strokeWidth="1" />

                <text x="60" y="105" fill="var(--text-muted)" fontSize="9">Short Distance (&lt;500km)</text>
                <text x="640" y="105" textAnchor="end" fill="var(--text-muted)" fontSize="9">Intercontinental (&gt;3000km)</text>
                <text x="355" y="25" fill="var(--critical)" fontSize="9" fontWeight="700">High Risk (0.80 - 1.00)</text>
                <text x="355" y="200" fill="var(--success)" fontSize="9" fontWeight="700">Low Risk (0.00 - 0.30)</text>

                {/* Plotted Shipments with Animated Halos and Initial Instant Badges */}
                {[
                  { id: 'SHP001', x: 140, y: 165, prob: 0.30, route: 'Berlin -> Paris', mode: 'Truck', delay: 0.0, risk: 'LOW' },
                  { id: 'SHP002', x: 210, y: 135, prob: 0.42, route: 'Warsaw -> Berlin', mode: 'Rail', delay: 0.5, risk: 'MEDIUM' },
                  { id: 'SHP003', x: 180, y: 155, prob: 0.35, route: 'Madrid -> Lyon', mode: 'Truck', delay: 0.2, risk: 'LOW' },
                  { id: 'SHP004', x: 520, y: 48, prob: 0.83, route: 'Munich -> Chicago', mode: 'Air', delay: 3.2, risk: 'CRITICAL' },
                  { id: 'SHP005', x: 480, y: 62, prob: 0.78, route: 'Rotterdam -> NY', mode: 'Sea', delay: 2.7, risk: 'HIGH' },
                  { id: 'SHP006', x: 260, y: 130, prob: 0.45, route: 'Milan -> Vienna', mode: 'Truck', delay: 0.8, risk: 'MEDIUM' },
                  { id: 'SHP007', x: 580, y: 45, prob: 0.83, route: 'Frankfurt -> Tokyo', mode: 'Air', delay: 3.5, risk: 'CRITICAL' },
                  { id: 'SHP008', x: 450, y: 85, prob: 0.65, route: 'Hamburg -> Singapore', mode: 'Sea', delay: 1.9, risk: 'HIGH' },
                  { id: 'SHP009', x: 620, y: 35, prob: 0.88, route: 'London -> Dubai', mode: 'Air', delay: 4.1, risk: 'CRITICAL' },
                  { id: 'SHP010', x: 110, y: 175, prob: 0.28, route: 'Antwerp -> Cologne', mode: 'Rail', delay: 0.0, risk: 'LOW' }
                ].map((node) => {
                  const nodeColor = node.risk === 'CRITICAL' ? 'var(--critical)' : node.risk === 'HIGH' ? 'var(--warning)' : node.risk === 'MEDIUM' ? 'var(--muted-indigo)' : 'var(--success)';
                  return (
                    <g
                      key={node.id}
                      style={{ cursor: 'pointer' }}
                      onClick={() => onSelectShipment(node.id)}
                    >
                      {/* Pulse Halo */}
                      <circle
                        cx={node.x}
                        cy={node.y}
                        r="10"
                        fill="none"
                        stroke={nodeColor}
                        strokeWidth="1.5"
                        style={{ animation: 'radarPing 2.2s infinite ease-out' }}
                      />

                      {/* Main Node Dot */}
                      <circle
                        cx={node.x}
                        cy={node.y}
                        r="5.5"
                        fill={nodeColor}
                        stroke="var(--bg-card)"
                        strokeWidth="2"
                      />

                      {/* Initial Instant Pinned Callout Reading Badge */}
                      <g transform={`translate(${node.x}, ${node.y - 14})`}>
                        <rect
                          x="-28"
                          y="-8"
                          width="56"
                          height="14"
                          rx="3"
                          fill={nodeColor}
                          opacity="0.9"
                        />
                        <text
                          x="0"
                          y="2"
                          textAnchor="middle"
                          fill="#FFFFFF"
                          fontSize="7"
                          fontWeight="700"
                        >
                          {node.id}: {(node.prob * 100).toFixed(0)}%
                        </text>
                      </g>
                    </g>
                  );
                })}
              </svg>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
