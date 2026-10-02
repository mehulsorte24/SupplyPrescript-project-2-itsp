import React, { useState, useRef, useEffect } from 'react';
import {
  Bell,
  Menu,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Maximize2,
  Minimize2,
  Clock,
  AlertTriangle,
  Radio,
  ExternalLink,
  X,
  Sun,
  Moon,
  Layers,
  CheckCheck,
  Eye,
  ArrowRight,
  Filter
} from 'lucide-react';
import TechStackModal from './TechStackModal';

const PAGE_TITLES = {
  overview: 'Overview Dashboard',
  shipments: 'Shipment Intelligence',
  risks: 'Risk Analysis Workspace',
  recommendations: 'AI Prescriptive Recommendations',
  decisions: 'Decision Center & Manager Workspace',
  feedback: 'Model Feedback & Monitoring',
  pipeline: 'AI Pipeline & Architecture',
  about: 'About Project & System Design',
};

export default function Header({
  activePage,
  mobileOpen,
  setMobileOpen,
  apiOnline,
  refreshData,
  isRefreshing,
  autoRefreshInterval,
  setAutoRefreshInterval,
  countdown,
  widescreen169,
  setWidescreen169,
  notifications = [],
  setNotifications,
  onNavigateToPage,
  onSelectShipment,
  theme,
  toggleTheme
}) {
  const [showNotifications, setShowNotifications] = useState(false);
  const [showTechModal, setShowTechModal] = useState(false);
  const [alertFilter, setAlertFilter] = useState('ALL'); // 'ALL' | 'CRITICAL' | 'WARNING' | 'INGEST'

  const notificationsRef = useRef(null);
  const pageTitle = PAGE_TITLES[activePage] || 'Dashboard';

  const unreadCount = notifications?.filter(n => !n.is_read)?.length ?? notifications?.length ?? 15;

  // Click outside to close notifications dropdown
  useEffect(() => {
    function handleClickOutside(event) {
      if (notificationsRef.current && !notificationsRef.current.contains(event.target)) {
        setShowNotifications(false);
      }
    }
    if (showNotifications) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showNotifications]);

  const handleMarkAllRead = () => {
    if (setNotifications) {
      setNotifications(prev => prev.map(n => ({ ...n, is_read: 1 })));
    }
  };

  const handleAlertClick = (evt) => {
    // Mark as read in local state
    if (setNotifications) {
      setNotifications(prev => prev.map(n => n.event_id === evt.event_id ? { ...n, is_read: 1 } : n));
    }
    setShowNotifications(false);

    if (evt.shipment_id && onSelectShipment) {
      onSelectShipment(evt.shipment_id);
    } else if (evt.event_type === 'CRITICAL_ALERT') {
      onNavigateToPage('risks');
    } else if (evt.event_type === 'DRIFT_WARNING') {
      onNavigateToPage('feedback');
    } else if (evt.event_type === 'RECOMMENDATION_READY') {
      onNavigateToPage('recommendations');
    } else {
      onNavigateToPage('shipments');
    }
  };

  // Filter notifications
  const filteredNotifications = (notifications || []).filter(item => {
    if (alertFilter === 'ALL') return true;
    if (alertFilter === 'CRITICAL') return item.severity === 'CRITICAL';
    if (alertFilter === 'WARNING') return item.severity === 'WARNING';
    if (alertFilter === 'INGEST') return item.event_type === 'LIVE_INGEST';
    return true;
  });

  return (
    <header className="top-header">
      {/* Left Section: Live System Status */}
      <div className="header-left">
        <button
          className="sidebar-toggle-btn mobile-menu-btn"
          onClick={() => setMobileOpen(!mobileOpen)}
          aria-label="Open mobile menu"
        >
          <Menu size={18} />
        </button>

        <div
          className={`api-badge ${apiOnline ? 'online' : 'standalone'}`}
          title={apiOnline ? "Connected to Python REST API & SQLite (port 8000)" : "Running in standalone engine mode"}
        >
          <Radio size={12} className={apiOnline ? 'status-dot' : ''} />
          <span>{apiOnline ? 'Live SQLite' : 'Standalone'}</span>
        </div>
      </div>

      {/* Right Section: Organized Action Clusters */}
      <div className="header-right">
        {/* Cluster 1: Telemetry Sync Controls */}
        <div className="header-group sync-group">
          <div className="refresh-control" title="Live Auto-Refresh Interval">
            <Clock size={13} color="var(--muted-indigo)" />
            <span className="sync-label">Sync:</span>
            <select
              className="refresh-select"
              value={autoRefreshInterval}
              onChange={(e) => setAutoRefreshInterval(Number(e.target.value))}
              aria-label="Sync interval"
            >
              <option value={0}>Off</option>
              <option value={5}>5s</option>
              <option value={10}>10s</option>
              <option value={15}>15s</option>
            </select>
            {autoRefreshInterval > 0 && (
              <span className="countdown-chip">
                {countdown}s
              </span>
            )}
          </div>

          <button
            className="btn btn-secondary btn-sm sync-btn"
            onClick={refreshData}
            disabled={isRefreshing}
            title="Manual refresh from AI engine"
          >
            <RefreshCw size={13} className={isRefreshing ? 'animate-spin' : ''} />
            <span>{isRefreshing ? 'Syncing...' : 'Sync'}</span>
          </button>
        </div>

        <div className="header-divider" />

        {/* Cluster 2: Enterprise Frameworks & Libraries Button */}
        <button
          className="header-pill-btn tech-stack-btn"
          onClick={() => setShowTechModal(true)}
          title="Enterprise Frameworks, Libraries & System Architecture"
        >
          <Layers size={14} color="var(--brand-primary)" />
          <span>Frameworks</span>
        </button>

        <div className="header-divider" />

        {/* Cluster 3: View & Theme Mode Toggles */}
        <div className="header-group view-group">
          <button
            className={`header-icon-btn aspect-ratio-btn ${widescreen169 ? 'active' : ''}`}
            onClick={() => setWidescreen169(!widescreen169)}
            title={widescreen169 ? "Switch to fluid wide layout" : "Lock into 16:9 widescreen presentation display"}
          >
            {widescreen169 ? <Minimize2 size={13} /> : <Maximize2 size={13} />}
            <span>16:9</span>
          </button>

          <button
            className="header-icon-btn theme-toggle-btn"
            onClick={toggleTheme}
            title={theme === 'dark' ? "Switch to Light Mode" : "Switch to Obsidian Moonlight Dark Theme"}
            aria-label="Toggle Dark Mode"
          >
            {theme === 'dark' ? (
              <Sun size={14} color="#FBBF24" />
            ) : (
              <Moon size={14} color="var(--brand-primary)" />
            )}
            <span>{theme === 'dark' ? 'Dark' : 'Light'}</span>
          </button>
        </div>

        <div className="header-divider" />

        {/* Cluster 4: Live Alerts Feed (15) Button with Interactive Dropdown */}
        <div className="notifications-wrapper" ref={notificationsRef}>
          <button
            className={`header-icon-btn notifications-trigger-btn ${showNotifications ? 'active' : ''}`}
            onClick={() => setShowNotifications(!showNotifications)}
            title={`Live Alerts Feed (${unreadCount} unread)`}
            aria-label="Alerts"
          >
            <Bell size={15} />
            {unreadCount > 0 && (
              <span className="notification-counter-badge">
                {unreadCount > 99 ? '99+' : unreadCount}
              </span>
            )}
          </button>

          {/* Notifications Dropdown Drawer */}
          {showNotifications && (
            <div className="notifications-menu" onClick={(e) => e.stopPropagation()}>
              <div className="notifications-header">
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
                  <Bell size={15} color="var(--brand-primary)" />
                  <div>
                    <span style={{ fontWeight: 700, fontSize: '0.84rem', color: 'var(--text-main)', display: 'block' }}>
                      Live Alerts Feed ({notifications?.length || 0})
                    </span>
                    <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>
                      Real-time telemetry and decision signals
                    </span>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                  {unreadCount > 0 && (
                    <button
                      className="btn btn-secondary btn-sm"
                      onClick={handleMarkAllRead}
                      style={{ fontSize: '0.68rem', padding: '0.2rem 0.45rem', gap: '0.25rem' }}
                      title="Mark all notifications as read"
                    >
                      <CheckCheck size={12} />
                      <span>Read All</span>
                    </button>
                  )}
                  <button
                    onClick={() => setShowNotifications(false)}
                    style={{ color: 'var(--text-muted)', padding: '3px', borderRadius: '4px' }}
                    aria-label="Close alerts"
                  >
                    <X size={15} />
                  </button>
                </div>
              </div>

              {/* Alert Filter Chips */}
              <div className="notifications-filters">
                <button
                  className={`filter-chip ${alertFilter === 'ALL' ? 'active' : ''}`}
                  onClick={() => setAlertFilter('ALL')}
                >
                  All ({notifications?.length || 0})
                </button>
                <button
                  className={`filter-chip ${alertFilter === 'CRITICAL' ? 'active' : ''}`}
                  onClick={() => setAlertFilter('CRITICAL')}
                >
                  Critical ({notifications?.filter(n => n.severity === 'CRITICAL').length || 0})
                </button>
                <button
                  className={`filter-chip ${alertFilter === 'INGEST' ? 'active' : ''}`}
                  onClick={() => setAlertFilter('INGEST')}
                >
                  Live Ingest ({notifications?.filter(n => n.event_type === 'LIVE_INGEST').length || 0})
                </button>
              </div>

              {/* Alerts List */}
              <div className="notifications-list">
                {filteredNotifications.length > 0 ? (
                  filteredNotifications.map((evt, idx) => (
                    <div
                      key={evt.event_id || idx}
                      className={`notification-item ${evt.is_read ? 'read' : 'unread'}`}
                      onClick={() => handleAlertClick(evt)}
                    >
                      <div className="notification-icon-col">
                        {evt.severity === 'CRITICAL' ? (
                          <div className="alert-avatar critical">
                            <AlertTriangle size={14} color="#EF4444" />
                          </div>
                        ) : evt.severity === 'WARNING' ? (
                          <div className="alert-avatar warning">
                            <AlertCircle size={14} color="#F59E0B" />
                          </div>
                        ) : (
                          <div className="alert-avatar info">
                            <Radio size={14} color="var(--brand-primary)" />
                          </div>
                        )}
                      </div>

                      <div className="notification-content-col">
                        <div className="notification-row-top">
                          <span className="notification-title">
                            {evt.title || evt.event_type}
                          </span>
                          <span className={`badge ${
                            evt.severity === 'CRITICAL' ? 'badge-critical' :
                            evt.severity === 'WARNING' ? 'badge-high' : 'badge-low'
                          }`} style={{ fontSize: '0.58rem', padding: '0.1rem 0.35rem' }}>
                            {evt.severity}
                          </span>
                        </div>

                        <p className="notification-msg">
                          {evt.message}
                        </p>

                        <div className="notification-row-bottom">
                          <span className="notification-time">
                            {evt.timestamp ? new Date(evt.timestamp).toLocaleTimeString() : 'Just now'}
                          </span>
                          {evt.shipment_id && (
                            <span className="inspect-link">
                              <Eye size={11} />
                              <span>Inspect {evt.shipment_id}</span>
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div style={{ padding: '2.5rem 1rem', textAlign: 'center', color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
                    <CheckCircle2 size={24} color="var(--success)" style={{ margin: '0 auto 0.5rem', opacity: 0.8 }} />
                    <p style={{ fontWeight: 600 }}>All operational alerts nominal</p>
                    <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>No pending events for current filter</span>
                  </div>
                )}
              </div>

              {/* Drawer Footer */}
              <div className="notifications-footer">
                <button
                  className="view-all-alerts-btn"
                  onClick={() => {
                    setShowNotifications(false);
                    onNavigateToPage('overview');
                  }}
                >
                  <span>Open Live Alerts Feed in Dashboard</span>
                  <ArrowRight size={13} />
                </button>
              </div>
            </div>
          )}
        </div>

        <div className="header-divider" />

        {/* Cluster 5: User Profile Badge */}
        <div className="user-profile-btn" title="Logged in as Supply Chain Operations Lead">
          <div className="user-avatar">MS</div>
          <div className="user-meta">
            <span className="user-name">Mehul Sorte</span>
            <span className="user-role">Operations Lead</span>
          </div>
        </div>
      </div>

      {/* Enterprise Tech Stack Modal */}
      <TechStackModal
        isOpen={showTechModal}
        onClose={() => setShowTechModal(false)}
        onNavigateToPage={onNavigateToPage}
      />
    </header>
  );
}
