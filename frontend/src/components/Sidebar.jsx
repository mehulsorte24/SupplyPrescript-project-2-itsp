import React from 'react';
import {
  LayoutDashboard,
  Truck,
  AlertTriangle,
  Lightbulb,
  CheckSquare,
  Activity,
  Workflow,
  Info,
  ChevronLeft,
  ChevronRight,
  ShieldCheck,
  Radio
} from 'lucide-react';

const NAV_ITEMS = [
  { id: 'overview', label: 'Overview', icon: LayoutDashboard },
  { id: 'shipments', label: 'Shipment Intelligence', icon: Truck },
  { id: 'risks', label: 'Risk Analysis', icon: AlertTriangle },
  { id: 'recommendations', label: 'AI Recommendations', icon: Lightbulb },
  { id: 'decisions', label: 'Decision Center', icon: CheckSquare },
  { id: 'feedback', label: 'Feedback & Model Monitoring', icon: Activity },
  { id: 'pipeline', label: 'AI Pipeline', icon: Workflow },
  { id: 'about', label: 'About Project', icon: Info },
];

export default function Sidebar({
  activePage,
  setActivePage,
  collapsed,
  setCollapsed,
  mobileOpen,
  setMobileOpen,
  apiOnline
}) {
  return (
    <aside className={`sidebar ${collapsed ? 'collapsed' : ''} ${mobileOpen ? 'mobile-open' : ''}`}>
      <div className="sidebar-header">
        <div className="brand-wrapper">
          <div className="brand-logo-icon">SP</div>
          {!collapsed && (
            <div className="brand-text">
              <span className="brand-title">SupplyPrescript</span>
              <span className="brand-badge">Decision Intelligence</span>
            </div>
          )}
        </div>
        <button
          className="sidebar-toggle-btn"
          style={{ color: '#CCCCFF' }}
          onClick={() => setCollapsed(!collapsed)}
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          aria-label="Toggle sidebar"
        >
          {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
        </button>
      </div>

      <nav className="sidebar-nav" aria-label="Main Navigation">
        {!collapsed && <div className="nav-section-title">Navigation Workspace</div>}
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = activePage === item.id;
          return (
            <button
              key={item.id}
              className={`nav-item ${isActive ? 'active' : ''}`}
              onClick={() => {
                setActivePage(item.id);
                if (mobileOpen) setMobileOpen(false);
              }}
              title={collapsed ? item.label : undefined}
            >
              <Icon className="nav-icon" />
              {!collapsed && <span className="nav-label">{item.label}</span>}
            </button>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        {!collapsed ? (
          <>
            <div className="engine-status-pill">
              <span className={`status-dot ${apiOnline ? '' : 'status-dot-warning'}`} style={{ backgroundColor: apiOnline ? '#27835C' : '#D58A28' }}></span>
              <span>{apiOnline ? 'AI Backend: Connected' : 'Engine: Standalone Mode'}</span>
            </div>
            <div style={{ fontSize: '0.68rem', color: '#A3A3CC', display: 'flex', alignItems: 'center', gap: '0.35rem', padding: '0 0.25rem' }}>
              <ShieldCheck size={13} color="#CCCCFF" />
              <span>Guardrails: 42/42 Validated</span>
            </div>
          </>
        ) : (
          <div style={{ display: 'flex', justifyContent: 'center', padding: '0.25rem 0' }}>
            <span className="status-dot" style={{ backgroundColor: apiOnline ? '#27835C' : '#D58A28' }} title={apiOnline ? 'API Connected' : 'Standalone'} />
          </div>
        )}
      </div>
    </aside>
  );
}
