import React, { useState } from 'react';
import {
  CheckSquare,
  Send,
  History,
  ShieldCheck,
  AlertCircle,
  CheckCircle2,
  User,
  Clock,
  FileText,
  AlertTriangle,
  Lightbulb,
  ExternalLink
} from 'lucide-react';

const CANDIDATE_ACTIONS = [
  'Expedite transportation',
  'Prioritize critical shipments',
  'Increase inventory buffer',
  'Evaluate alternate supplier',
  'Increase monitoring frequency',
  'Custom Manager Directive'
];

export default function DecisionCenterPage({
  decisionsData,
  preselectedAction,
  preselectedShipment,
  onSubmitDecision,
  isSubmitting,
  apiOnline
}) {
  const currentDecision = decisionsData?.current_decision || {};
  const decisionOutcomes = decisionsData?.decision_outcomes || {};
  const historyList = decisionsData?.history || [];

  const [selectedAction, setSelectedAction] = useState(
    preselectedAction?.action_name || currentDecision?.manager_decision?.selected_action || CANDIDATE_ACTIONS[0]
  );
  const [rationale, setRationale] = useState(
    preselectedAction ? `Implementing ${preselectedAction.action_name} to mitigate ${preselectedAction.rationale || 'disruption risk'}` : ''
  );
  const [targetScope, setTargetScope] = useState(preselectedShipment?.shipment_id || 'BATCH_ALL');
  const [managerName, setManagerName] = useState('Mehul Sorte (Supply Chain Lead)');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!rationale.trim()) {
      alert('Please enter a manager decision rationale before submitting.');
      return;
    }

    onSubmitDecision({
      selected_action: selectedAction,
      rationale: rationale,
      shipment_id: targetScope === 'BATCH_ALL' ? null : targetScope,
      manager_name: managerName,
      recommended_action: preselectedAction?.action_name || 'Expedite transportation',
      recommended_rank: preselectedAction?.rank || 1,
      relevance_score: preselectedAction?.relevance_score || 75,
      risk_level: 'CRITICAL',
      delay_probability: 71.85,
      expected_delay_days: 3.423
    });
  };

  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Manager Decision Center</h1>
          <p className="page-subtitle">
            Formal human-in-the-loop review, decision commitment, and audit ledger capturing operational interventions.
          </p>
        </div>
      </div>

      {/* Human-in-the-Loop Governance Notice */}
      <div style={{
        backgroundColor: 'var(--bg-card)',
        border: '1px solid var(--border-color)',
        borderRadius: 'var(--radius-lg)',
        padding: '1.25rem',
        marginBottom: '1.75rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '1rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
          <div style={{
            width: '38px',
            height: '38px',
            borderRadius: 'var(--radius-md)',
            backgroundColor: 'var(--moonlight-soft)',
            color: 'var(--deep-indigo)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0
          }}>
            <ShieldCheck size={20} />
          </div>
          <div>
            <span style={{ fontWeight: 700, fontSize: '0.92rem', color: 'var(--deep-indigo)' }}>
              Closed-Loop Operational Integrity Guardrail
            </span>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.15rem' }}>
              AI models produce risk assessments and prescriptive candidates. Official decisions must be reviewed, signed off, and authorized by an operations manager.
            </p>
          </div>
        </div>
        <span className="badge" style={{ backgroundColor: 'var(--moonlight-subtle)', color: 'var(--deep-indigo)', padding: '0.4rem 0.75rem' }}>
          ISO-Compliant Audit Ledger
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>

        {/* Left Column: Manager Decision Capture Form */}
        <div className="card">
          <div className="card-header">
            <div>
              <h3 className="card-title">
                <CheckSquare size={17} color="var(--deep-indigo)" />
                <span>Capture Manager Decision</span>
              </h3>
              <p className="card-subtitle">Authorize response strategy for active disruption</p>
            </div>
            {preselectedAction && (
              <span className="badge" style={{ backgroundColor: 'var(--moonlight-soft)', color: 'var(--deep-indigo)' }}>
                Imported from AI Recs
              </span>
            )}
          </div>

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.15rem' }}>
            {/* Target Scope */}
            <div>
              <label className="form-label">Target Evaluation Scope</label>
              <select
                className="form-select"
                value={targetScope}
                onChange={(e) => setTargetScope(e.target.value)}
              >
                <option value="BATCH_ALL">Active Batch (All 10 High-Exposure Shipments)</option>
                <option value="SHP0000009">SHP0000009 — Nagpur to Pune (Critical, 6.96d delay)</option>
                <option value="SHP0000004">SHP0000004 — Hyderabad to Pune (Critical, 6.97d delay)</option>
                <option value="SHP0000008">SHP0000008 — Hyderabad to Jaipur (Critical, 6.02d delay)</option>
                <option value="SHP0000007">SHP0000007 — Nagpur to Jaipur (Critical, 5.97d delay)</option>
                <option value="SHP0000005">SHP0000005 — Delhi to Ahmedabad (Critical, 2.72d delay)</option>
              </select>
            </div>

            {/* Selected Action */}
            <div>
              <label className="form-label">Manager Selected Action</label>
              <select
                className="form-select"
                value={selectedAction}
                onChange={(e) => setSelectedAction(e.target.value)}
              >
                {CANDIDATE_ACTIONS.map(action => (
                  <option key={action} value={action}>{action}</option>
                ))}
              </select>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginTop: '0.35rem', fontSize: '0.74rem', color: 'var(--text-secondary)' }}>
                <Lightbulb size={12} color="var(--deep-indigo)" />
                <span>AI Recommendation: <strong>Expedite transportation</strong> (Rank #1)</span>
              </div>
            </div>

            {/* Manager Rationale */}
            <div>
              <label className="form-label">
                Decision Rationale & Operational Justification
              </label>
              <textarea
                className="form-textarea"
                rows={4}
                placeholder="State the operational justification for selecting this action (e.g., Expedite transportation because the shipment has critical risk and the expected delay is significant)..."
                value={rationale}
                onChange={(e) => setRationale(e.target.value)}
                required
              />
              <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', display: 'block', marginTop: '0.25rem' }}>
                Required for decision audit trail and continuous outcome feedback learning.
              </span>
            </div>

            {/* Sign-off Manager */}
            <div>
              <label className="form-label">Authorizing Manager</label>
              <input
                type="text"
                className="form-input"
                value={managerName}
                onChange={(e) => setManagerName(e.target.value)}
              />
            </div>

            {/* Submit Button */}
            <div style={{ paddingTop: '0.5rem' }}>
              <button
                type="submit"
                className="btn btn-primary"
                style={{ width: '100%', height: '42px' }}
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <span>Recording Decision into AI Ledger...</span>
                ) : (
                  <>
                    <Send size={15} />
                    <span>Submit and Commit Manager Decision</span>
                  </>
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Right Column: Active Captured Decision & Outcome Tracking */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>

          {/* Current Captured Decision Card */}
          <div className="card" style={{ borderLeft: '4px solid var(--deep-indigo)' }}>
            <div className="card-header">
              <div>
                <h3 className="card-title">
                  <FileText size={17} color="var(--deep-indigo)" />
                  <span>Latest Committed Decision</span>
                </h3>
                <p className="card-subtitle">Active entry in AI Decision Ledger</p>
              </div>
              <span className="badge" style={{ backgroundColor: 'var(--success-bg)', color: 'var(--success)' }}>
                {currentDecision.decision_status || 'CAPTURED'}
              </span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.82rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.45rem 0', borderBottom: '1px solid var(--border-subtle)' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Decision ID:</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: 'var(--deep-indigo)' }}>
                  {currentDecision.decision_id || 'DEC-20260926180203-841489'}
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.45rem 0', borderBottom: '1px solid var(--border-subtle)' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Committed Action:</span>
                <span style={{ fontWeight: 700 }}>
                  {currentDecision.manager_decision?.selected_action || 'Expedite transportation'}
                </span>
              </div>
              <div style={{ padding: '0.45rem 0', borderBottom: '1px solid var(--border-subtle)' }}>
                <span style={{ color: 'var(--text-secondary)', display: 'block', marginBottom: '0.2rem' }}>Manager Rationale:</span>
                <p style={{ fontStyle: 'italic', color: 'var(--text-main)', lineHeight: '1.4' }}>
                  "{currentDecision.manager_decision?.rationale || 'Expedite transportation because the shipment has critical risk and the expected delay is significant.'}"
                </p>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.45rem 0' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Timestamp:</span>
                <span>{currentDecision.decision_timestamp ? new Date(currentDecision.decision_timestamp).toLocaleString() : 'Sep 26, 2026, 11:32 PM'}</span>
              </div>
            </div>
          </div>

          {/* Decision Outcome Tracking Status Card */}
          <div className="card">
            <div className="card-header">
              <div>
                <h3 className="card-title">
                  <Clock size={17} color="var(--muted-indigo)" />
                  <span>Outcome Tracking & Learning Status</span>
                </h3>
                <p className="card-subtitle">Tracking actual arrival against predicted delay</p>
              </div>
              <span className="badge" style={{ backgroundColor: 'var(--moonlight-soft)', color: 'var(--deep-indigo)' }}>
                REFERENCE: SHP0000001
              </span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.82rem' }}>
              <div style={{ padding: '0.75rem', backgroundColor: 'var(--bg-main)', borderRadius: 'var(--radius-md)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
                  <span>Prediction vs Actual:</span>
                  <span style={{ fontWeight: 600, color: 'var(--critical)' }}>
                    {decisionOutcomes?.outcome_assessment?.assessment || 'PREDICTION_CLASSIFICATION_MISMATCH'}
                  </span>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', fontSize: '0.78rem' }}>
                  <div>
                    <span style={{ color: 'var(--text-secondary)', display: 'block' }}>Predicted:</span>
                    <strong>{decisionOutcomes?.prediction_vs_actual?.predicted_status || 'ON_TIME'} ({decisionOutcomes?.prediction_vs_actual?.predicted_delay_days || 0.58}d)</strong>
                  </div>
                  <div>
                    <span style={{ color: 'var(--text-secondary)', display: 'block' }}>Actual Arrival:</span>
                    <strong>{decisionOutcomes?.prediction_vs_actual?.actual_status || 'DELAYED'} ({decisionOutcomes?.prediction_vs_actual?.actual_delay_days || 2.0}d)</strong>
                  </div>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.45rem 0', borderBottom: '1px solid var(--border-subtle)' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Absolute Delay Error:</span>
                <span style={{ fontWeight: 700 }}>{decisionOutcomes?.prediction_vs_actual?.absolute_delay_error_days || 1.42} days</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.45rem 0', borderBottom: '1px solid var(--border-subtle)' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Feedback Signal Available:</span>
                <span className="badge" style={{ backgroundColor: 'var(--success-bg)', color: 'var(--success)' }}>
                  YES (NEGATIVE_OUTCOME_SIGNAL)
                </span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.45rem 0' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Recommendation Weights:</span>
                <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>Protected (Locked by Guardrail)</span>
              </div>
            </div>
          </div>

        </div>
      </div>

      {/* Decision Audit History Table */}
      <div className="card">
        <div className="card-header">
          <div>
            <h3 className="card-title">
              <History size={17} color="var(--deep-indigo)" />
              <span>Manager Decision Audit Log ({historyList.length})</span>
            </h3>
            <p className="card-subtitle">Permanent historical record of decisions captured in system</p>
          </div>
        </div>

        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Decision ID</th>
                <th>Selected Action</th>
                <th>Manager Rationale</th>
                <th>Authorizer</th>
                <th>Scope</th>
                <th>Outcome Status</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {historyList.map((dec) => (
                <tr key={dec.decision_id}>
                  <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: 'var(--deep-indigo)' }}>
                    {dec.decision_id}
                  </td>
                  <td>
                    <span style={{ fontWeight: 600 }}>
                      {dec.manager_decision?.selected_action}
                    </span>
                  </td>
                  <td style={{ maxWidth: '300px' }}>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                      {dec.manager_decision?.rationale}
                    </span>
                  </td>
                  <td>
                    <span style={{ fontSize: '0.8rem' }}>{dec.manager_decision?.manager_name || 'Mehul Sorte'}</span>
                  </td>
                  <td>
                    <span className="badge" style={{ backgroundColor: 'var(--bg-main)', color: 'var(--text-secondary)' }}>
                      {dec.manager_decision?.shipment_id || 'BATCH_ALL'}
                    </span>
                  </td>
                  <td>
                    <span className="badge" style={{ backgroundColor: 'var(--moonlight-soft)', color: 'var(--deep-indigo)' }}>
                      {dec.outcome_tracking?.outcome_available ? 'EVALUATED' : 'CAPTURED'}
                    </span>
                  </td>
                  <td>
                    <span style={{ fontSize: '0.76rem', color: 'var(--text-muted)' }}>
                      {dec.decision_timestamp ? new Date(dec.decision_timestamp).toLocaleDateString() : 'Sep 26, 2026'}
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
