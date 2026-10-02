/**
 * SupplyPrescript Centralized API Client
 * Enterprise-grade client with error resilience, live database streaming, and telemetry support.
 */

const API_BASE = import.meta.env.VITE_API_URL || '/api';

/**
 * Standard fetch helper with timeout and JSON error handling
 */
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const defaultHeaders = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
  };

  const config = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...(options.headers || {}),
    },
  };

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 8000);
    const response = await fetch(url, { ...config, signal: controller.signal });
    clearTimeout(timeoutId);

    if (!response.ok) {
      let errDetail = 'Request failed';
      try {
        const errJson = await response.json();
        errDetail = errJson.error || errJson.message || response.statusText;
      } catch {
        errDetail = response.statusText;
      }
      const error = new Error(`API Error [${response.status}]: ${errDetail}`);
      error.status = response.status;
      throw error;
    }

    return await response.json();
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new Error('API Request timed out after 8s');
    }
    throw error;
  }
}

export const api = {
  checkHealth: () => apiRequest('/health'),
  getDashboard: () => apiRequest('/dashboard'),
  getShipments: (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.risk) params.set('risk', filters.risk);
    if (filters.mode) params.set('mode', filters.mode);
    if (filters.status) params.set('status', filters.status);
    if (filters.supplier) params.set('supplier', filters.supplier);
    if (filters.search) params.set('search', filters.search);
    const qs = params.toString();
    return apiRequest(`/shipments${qs ? `?${qs}` : ''}`);
  },
  getShipmentDetails: (id) => apiRequest(`/shipments/${id}`),
  getPredictions: () => apiRequest('/predictions'),
  getRisks: () => apiRequest('/risks'),
  getRecommendations: () => apiRequest('/recommendations'),
  getDecisions: () => apiRequest('/decisions'),
  createDecision: (payload) => apiRequest('/decisions', {
    method: 'POST',
    body: JSON.stringify(payload),
  }),
  getFeedback: () => apiRequest('/feedback'),
  getPipeline: () => apiRequest('/pipeline'),

  // Real SQLite Database & Live Telemetry Ingest
  getDatabaseStats: () => apiRequest('/database/stats'),
  getDatabaseRecords: (limit = 25) => apiRequest(`/database/records?limit=${limit}`),
  ingestLiveShipment: () => apiRequest('/database/ingest', {
    method: 'POST',
    body: JSON.stringify({}),
  }),
  switchScenario: (scenario) => apiRequest('/database/scenario', {
    method: 'POST',
    body: JSON.stringify({ scenario }),
  }),
  getNotifications: () => apiRequest('/notifications'),
};
