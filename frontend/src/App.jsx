import React, { useState, useEffect, useCallback, useRef } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import ShipmentDrawer from './components/ShipmentDrawer';
import OverviewPage from './pages/OverviewPage';
import ShipmentIntelligencePage from './pages/ShipmentIntelligencePage';
import RiskAnalysisPage from './pages/RiskAnalysisPage';
import RecommendationsPage from './pages/RecommendationsPage';
import DecisionCenterPage from './pages/DecisionCenterPage';
import FeedbackMonitoringPage from './pages/FeedbackMonitoringPage';
import AIPipelinePage from './pages/AIPipelinePage';
import AboutProjectPage from './pages/AboutProjectPage';
import { api } from './services/api';
import { CheckCircle2, AlertCircle, AlertTriangle, X, Radio } from 'lucide-react';

export default function App() {
  const [activePage, setActivePage] = useState('overview');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [apiOnline, setApiOnline] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [widescreen169, setWidescreen169] = useState(false);

  // Theme state ('light' | 'dark')
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('supplyprescript_theme') || 'light';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('supplyprescript_theme', theme);
  }, [theme]);

  // Auto-refresh states (Off=0, 5s, 10s, 15s)
  const [autoRefreshInterval, setAutoRefreshInterval] = useState(10);
  const [countdown, setCountdown] = useState(10);

  // Data states
  const [dashboardData, setDashboardData] = useState(null);
  const [shipmentsData, setShipmentsData] = useState([]);
  const [riskData, setRiskData] = useState(null);
  const [recommendationData, setRecommendationData] = useState(null);
  const [decisionsData, setDecisionsData] = useState(null);
  const [feedbackData, setFeedbackData] = useState(null);
  const [pipelineData, setPipelineData] = useState(null);
  const [dbStats, setDbStats] = useState(null);
  const [liveRecords, setLiveRecords] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [autoStreamEnabled, setAutoStreamEnabled] = useState(false);

  // UI state for modals/drawers
  const [selectedShipment, setSelectedShipment] = useState(null);
  const [selectedIntelligence, setSelectedIntelligence] = useState(null);
  const [preselectedAction, setPreselectedAction] = useState(null);
  const [preselectedShipmentForDecision, setPreselectedShipmentForDecision] = useState(null);
  const [isSubmittingDecision, setIsSubmittingDecision] = useState(false);
  const [isIngesting, setIsIngesting] = useState(false);

  // Toast notifications with debounce & deduplication
  const [toasts, setToasts] = useState([]);
  const recentToastsRef = useRef(new Map());

  const addToast = useCallback((message, type = 'info') => {
    const now = Date.now();
    const lastTime = recentToastsRef.current.get(message);
    // Ignore duplicate identical notification if triggered within 1500ms
    if (lastTime && now - lastTime < 1500) {
      return;
    }
    recentToastsRef.current.set(message, now);

    const id = `${now}-${Math.random()}`;
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 4500);
  }, []);

  const removeToast = (id) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

  // Main data loader
  const loadAllData = useCallback(async (isSilent = false) => {
    if (!isSilent) setIsRefreshing(true);
    try {
      // 1. Health check
      try {
        await api.checkHealth();
        setApiOnline(true);
      } catch (err) {
        setApiOnline(false);
      }

      // 2. Load dashboard
      const dash = await api.getDashboard();
      setDashboardData(dash);

      // 3. Load shipments
      const ships = await api.getShipments();
      setShipmentsData(ships.shipments || []);

      // 4. Load risks
      const r = await api.getRisks();
      setRiskData(r);

      // 5. Load recommendations
      const recs = await api.getRecommendations();
      setRecommendationData(recs);

      // 6. Load decisions
      const decs = await api.getDecisions();
      setDecisionsData(decs);

      // 7. Load feedback
      const fb = await api.getFeedback();
      setFeedbackData(fb);

      // 8. Load pipeline
      const pipe = await api.getPipeline();
      setPipelineData(pipe);

      // 9. Load SQLite stats & live records & notifications
      try {
        const stats = await api.getDatabaseStats();
        setDbStats(stats);
        const live = await api.getDatabaseRecords(20);
        setLiveRecords(live.records || []);
        const notifs = await api.getNotifications();
        setNotifications(notifs.notifications || []);
      } catch (e) {
        console.warn("Could not load db stats:", e);
      }

    } catch (err) {
      console.warn("API Error encountered:", err);
      if (!isSilent) {
        addToast(`Data sync notice: ${err.message || 'Connecting to data layer'}`, 'error');
      }
    } finally {
      if (!isSilent) setIsRefreshing(false);
    }
  }, [addToast]);

  // Initial load guarded against StrictMode double-execution
  const hasLoadedInitialRef = useRef(false);
  useEffect(() => {
    if (hasLoadedInitialRef.current) return;
    hasLoadedInitialRef.current = true;
    loadAllData();
  }, [loadAllData]);

  // Auto-refresh countdown interval with continuous streaming capability
  useEffect(() => {
    if (autoRefreshInterval <= 0) {
      setCountdown(0);
      return;
    }

    setCountdown(autoRefreshInterval);

    const timer = setInterval(async () => {
      setCountdown(prev => {
        if (prev <= 1) {
          // If continuous streaming is enabled, fluctuate live sensor telemetry or generate live shipment
          if (autoStreamEnabled) {
            // Alternate or perform live sensor telemetry updates & synthetic ingest
            api.switchScenario('fluctuate_live').catch(() => {});
            if (Math.random() > 0.4) {
              api.ingestLiveShipment().catch(() => {});
            }
          }
          loadAllData(true); // Silent background auto-refresh
          return autoRefreshInterval;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [autoRefreshInterval, autoStreamEnabled, loadAllData]);

  // Handle clicking a shipment for drawer view
  const handleOpenShipmentDrawer = async (shipmentId) => {
    try {
      const found = shipmentsData.find(s => s.shipment_id === shipmentId);
      if (found) {
        setSelectedShipment(found);
      }
      const details = await api.getShipmentDetails(shipmentId);
      if (details.shipment) setSelectedShipment(details.shipment);
      if (details.intelligence) setSelectedIntelligence(details.intelligence);
    } catch (e) {
      console.warn("Could not fetch shipment details:", e);
    }
  };

  // Handle selecting an action from Recommendations to review in Decision Center
  const handleSelectActionForDecision = (rec) => {
    setPreselectedAction(rec);
    setActivePage('decisions');
    addToast(`Transferred recommendation '${rec.action_name}' to Decision Center workspace.`, 'info');
  };

  // Handle selecting a shipment from drawer to review in Decision Center
  const handleSelectShipmentForDecision = (shipment) => {
    setPreselectedShipmentForDecision(shipment);
    setSelectedShipment(null);
    setActivePage('decisions');
    addToast(`Selected ${shipment.shipment_id} for manager decision review.`, 'info');
  };

  // Handle submitting decision in Decision Center
  const handleSubmitDecision = async (decisionPayload) => {
    setIsSubmittingDecision(true);
    try {
      const resp = await api.createDecision(decisionPayload);
      addToast(resp.message || "Manager decision successfully recorded into AI intelligence ledger.", 'success');

      const updatedDecs = await api.getDecisions();
      setDecisionsData(updatedDecs);
      const updatedDash = await api.getDashboard();
      setDashboardData(updatedDash);

      setPreselectedAction(null);
    } catch (err) {
      addToast(`Error saving decision: ${err.message}`, 'error');
    } finally {
      setIsSubmittingDecision(false);
    }
  };

  // Handle live ingestion trigger (simulating live telemetry into SQLite)
  const handleIngestLiveShipment = async () => {
    setIsIngesting(true);
    try {
      const resp = await api.ingestLiveShipment();
      const s = resp.shipment;
      addToast(`Live Ingest: ${s.shipment_id} (${s.origin} -> ${s.destination}) scored as ${s.risk_level} Risk & saved to SQLite!`, s.risk_level === 'CRITICAL' ? 'warning' : 'success');

      // Immediate reload of data
      await loadAllData(true);
    } catch (err) {
      addToast(`Live ingest failed: ${err.message}`, 'error');
    } finally {
      setIsIngesting(false);
    }
  };

  // Handle switching dynamic scenario datasets
  const handleSwitchScenario = async (scenarioKey) => {
    setIsRefreshing(true);
    try {
      const resp = await api.switchScenario(scenarioKey);
      addToast(resp.message || `Switched dataset scenario to '${scenarioKey}'`, 'info');
      await loadAllData(true);
    } catch (err) {
      addToast(`Failed to switch dataset: ${err.message}`, 'error');
    } finally {
      setIsRefreshing(false);
    }
  };

  // Toggle Dark/Light Theme (invokes addToast directly, outside of state updater)
  const toggleTheme = () => {
    const nextTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(nextTheme);
    addToast(nextTheme === 'dark' ? 'Obsidian Moonlight Dark Theme enabled' : 'Light Moonlight Theme enabled', 'info');
  };

  return (
    <div className={`app-container ${widescreen169 ? 'widescreen-mode' : ''}`} data-theme={theme}>
      {/* Sidebar Navigation */}
      <Sidebar
        activePage={activePage}
        setActivePage={setActivePage}
        collapsed={sidebarCollapsed}
        setCollapsed={setSidebarCollapsed}
        mobileOpen={mobileMenuOpen}
        setMobileOpen={setMobileMenuOpen}
        apiOnline={apiOnline}
      />

      {/* Main App Content Viewport */}
      <div className="main-wrapper">
        <Header
          activePage={activePage}
          mobileOpen={mobileMenuOpen}
          setMobileOpen={setMobileMenuOpen}
          apiOnline={apiOnline}
          refreshData={() => loadAllData(false)}
          isRefreshing={isRefreshing}
          autoRefreshInterval={autoRefreshInterval}
          setAutoRefreshInterval={setAutoRefreshInterval}
          countdown={countdown}
          widescreen169={widescreen169}
          setWidescreen169={setWidescreen169}
          notifications={notifications}
          setNotifications={setNotifications}
          onNavigateToPage={setActivePage}
          onSelectShipment={handleOpenShipmentDrawer}
          theme={theme}
          toggleTheme={toggleTheme}
        />

        <main style={{ flex: 1, paddingBottom: '2.5rem' }}>
          {activePage === 'overview' && (
            <OverviewPage
              dashboardData={dashboardData}
              dbStats={dbStats}
              liveRecords={liveRecords}
              notifications={notifications}
              isLoading={!dashboardData && isRefreshing}
              onSelectShipment={handleOpenShipmentDrawer}
              setActivePage={setActivePage}
              onIngestLiveShipment={handleIngestLiveShipment}
              isIngesting={isIngesting}
              autoRefreshInterval={autoRefreshInterval}
              setAutoRefreshInterval={setAutoRefreshInterval}
              countdown={countdown}
              autoStreamEnabled={autoStreamEnabled}
              setAutoStreamEnabled={setAutoStreamEnabled}
              onSwitchScenario={handleSwitchScenario}
            />
          )}

          {activePage === 'shipments' && (
            <ShipmentIntelligencePage
              shipments={shipmentsData}
              isLoading={shipmentsData.length === 0 && isRefreshing}
              onSelectShipment={handleOpenShipmentDrawer}
            />
          )}

          {activePage === 'risks' && (
            <RiskAnalysisPage
              riskData={riskData}
              isLoading={!riskData && isRefreshing}
              onSelectShipment={handleOpenShipmentDrawer}
            />
          )}

          {activePage === 'recommendations' && (
            <RecommendationsPage
              recommendationData={recommendationData}
              isLoading={!recommendationData && isRefreshing}
              onSelectActionForDecision={handleSelectActionForDecision}
            />
          )}

          {activePage === 'decisions' && (
            <DecisionCenterPage
              decisionsData={decisionsData}
              preselectedAction={preselectedAction}
              preselectedShipment={preselectedShipmentForDecision}
              onSubmitDecision={handleSubmitDecision}
              isSubmitting={isSubmittingDecision}
              apiOnline={apiOnline}
            />
          )}

          {activePage === 'feedback' && (
            <FeedbackMonitoringPage
              feedbackData={feedbackData}
              isLoading={!feedbackData && isRefreshing}
            />
          )}

          {activePage === 'pipeline' && (
            <AIPipelinePage
              pipelineData={pipelineData}
              isLoading={!pipelineData && isRefreshing}
            />
          )}

          {activePage === 'about' && (
            <AboutProjectPage />
          )}
        </main>
      </div>

      {/* Side Drawer for Shipment Feature and Intelligence Inspection */}
      {selectedShipment && (
        <ShipmentDrawer
          shipment={selectedShipment}
          intelligence={selectedIntelligence}
          onClose={() => {
            setSelectedShipment(null);
            setSelectedIntelligence(null);
          }}
          onSelectForDecision={handleSelectShipmentForDecision}
        />
      )}

      {/* Toast Notification Container */}
      <div className="toast-container">
        {toasts.map((toast) => (
          <div key={toast.id} className={`toast ${toast.type}`}>
            {toast.type === 'success' ? (
              <CheckCircle2 size={15} color="var(--success)" />
            ) : toast.type === 'warning' ? (
              <AlertTriangle size={15} color="var(--warning)" />
            ) : toast.type === 'error' ? (
              <AlertCircle size={15} color="var(--critical)" />
            ) : (
              <Radio size={14} color="var(--moonlight-lavender)" />
            )}
            <span style={{ flex: 1 }}>{toast.message}</span>
            <button
              onClick={() => removeToast(toast.id)}
              style={{ color: 'rgba(255, 255, 255, 0.7)', padding: '2px' }}
              aria-label="Close notification"
            >
              <X size={13} />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
