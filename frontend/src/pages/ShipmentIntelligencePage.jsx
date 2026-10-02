import React, { useState, useMemo } from 'react';
import {
  Search,
  Filter,
  ArrowUpDown,
  Eye,
  Download,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  MapPin,
  Truck
} from 'lucide-react';

export default function ShipmentIntelligencePage({
  shipments,
  isLoading,
  onSelectShipment
}) {
  const [searchTerm, setSearchTerm] = useState('');
  const [riskFilter, setRiskFilter] = useState('ALL');
  const [modeFilter, setModeFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [supplierFilter, setSupplierFilter] = useState('ALL');
  const [sortField, setSortField] = useState('shipment_id');
  const [sortAsc, setSortAsc] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 15;

  // Extract unique suppliers for filter dropdown
  const suppliers = useMemo(() => {
    if (!shipments) return [];
    const set = new Set();
    shipments.forEach(s => {
      if (s.supplier_id) set.add(s.supplier_id);
    });
    return Array.from(set).sort();
  }, [shipments]);

  // Filtering
  const filteredShipments = useMemo(() => {
    if (!shipments) return [];
    return shipments.filter(s => {
      // Search term
      if (searchTerm) {
        const term = searchTerm.toLowerCase();
        const matches =
          (s.shipment_id && s.shipment_id.toLowerCase().includes(term)) ||
          (s.supplier_id && s.supplier_id.toLowerCase().includes(term)) ||
          (s.origin && s.origin.toLowerCase().includes(term)) ||
          (s.destination && s.destination.toLowerCase().includes(term)) ||
          (s.transport_mode && s.transport_mode.toLowerCase().includes(term));
        if (!matches) return false;
      }

      // Risk filter
      if (riskFilter !== 'ALL') {
        if (String(s.risk_level).toUpperCase() !== riskFilter) return false;
      }

      // Mode filter
      if (modeFilter !== 'ALL') {
        if (String(s.transport_mode).toUpperCase() !== modeFilter) return false;
      }

      // Status filter
      if (statusFilter !== 'ALL') {
        if (String(s.prediction_status).toUpperCase() !== statusFilter) return false;
      }

      // Supplier filter
      if (supplierFilter !== 'ALL') {
        if (String(s.supplier_id).toUpperCase() !== supplierFilter) return false;
      }

      return true;
    });
  }, [shipments, searchTerm, riskFilter, modeFilter, statusFilter, supplierFilter]);

  // Sorting
  const sortedShipments = useMemo(() => {
    return [...filteredShipments].sort((a, b) => {
      let valA = a[sortField];
      let valB = b[sortField];

      if (typeof valA === 'string') valA = valA.toLowerCase();
      if (typeof valB === 'string') valB = valB.toLowerCase();

      if (valA < valB) return sortAsc ? -1 : 1;
      if (valA > valB) return sortAsc ? 1 : -1;
      return 0;
    });
  }, [filteredShipments, sortField, sortAsc]);

  // Pagination
  const totalPages = Math.ceil(sortedShipments.length / pageSize) || 1;
  const paginatedShipments = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return sortedShipments.slice(start, start + pageSize);
  }, [sortedShipments, currentPage]);

  const handleSort = (field) => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(true);
    }
  };

  const resetFilters = () => {
    setSearchTerm('');
    setRiskFilter('ALL');
    setModeFilter('ALL');
    setStatusFilter('ALL');
    setSupplierFilter('ALL');
    setCurrentPage(1);
  };

  return (
    <div className="page-container">
      {/* Page Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Shipment Intelligence</h1>
          <p className="page-subtitle">
            Search, filter, and inspect AI-predicted delay probabilities and operational features for all 100 enterprise shipments.
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            Showing <strong>{filteredShipments.length}</strong> of {shipments?.length || 100} shipments
          </span>
        </div>
      </div>

      {/* Filter and Search Bar Card */}
      <div className="card" style={{ marginBottom: '1.25rem', padding: '1rem 1.25rem' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '0.75rem', alignItems: 'end' }}>
          {/* Search Input */}
          <div style={{ gridColumn: 'span 2' }}>
            <label className="form-label">Search Corridor, ID or Supplier</label>
            <div style={{ position: 'relative' }}>
              <input
                type="text"
                className="form-input"
                placeholder="Search SHP0000001, Bangalore, SUP002..."
                value={searchTerm}
                onChange={(e) => {
                  setSearchTerm(e.target.value);
                  setCurrentPage(1);
                }}
                style={{ paddingLeft: '2.2rem' }}
              />
              <Search
                size={16}
                color="var(--text-muted)"
                style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)' }}
              />
            </div>
          </div>

          {/* Risk Level Filter */}
          <div>
            <label className="form-label">Risk Level</label>
            <select
              className="form-select"
              value={riskFilter}
              onChange={(e) => {
                setRiskFilter(e.target.value);
                setCurrentPage(1);
              }}
            >
              <option value="ALL">All Risk Levels</option>
              <option value="CRITICAL">Critical Risk</option>
              <option value="HIGH">High Risk</option>
              <option value="MEDIUM">Medium Risk</option>
              <option value="LOW">Low Risk</option>
            </select>
          </div>

          {/* Transport Mode Filter */}
          <div>
            <label className="form-label">Transport Mode</label>
            <select
              className="form-select"
              value={modeFilter}
              onChange={(e) => {
                setModeFilter(e.target.value);
                setCurrentPage(1);
              }}
            >
              <option value="ALL">All Modes</option>
              <option value="ROAD">Road</option>
              <option value="RAIL">Rail</option>
              <option value="SEA">Sea</option>
              <option value="AIR">Air</option>
            </select>
          </div>

          {/* Prediction Status Filter */}
          <div>
            <label className="form-label">Prediction Status</label>
            <select
              className="form-select"
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setCurrentPage(1);
              }}
            >
              <option value="ALL">All Predictions</option>
              <option value="DELAYED">Delayed</option>
              <option value="ON_TIME">On-Time</option>
            </select>
          </div>

          {/* Supplier Filter */}
          <div>
            <label className="form-label">Supplier</label>
            <select
              className="form-select"
              value={supplierFilter}
              onChange={(e) => {
                setSupplierFilter(e.target.value);
                setCurrentPage(1);
              }}
            >
              <option value="ALL">All Suppliers</option>
              {suppliers.map(sup => (
                <option key={sup} value={sup}>{sup}</option>
              ))}
            </select>
          </div>

          {/* Reset Filters button */}
          <div>
            <button
              className="btn btn-secondary"
              style={{ width: '100%', height: '38px' }}
              onClick={resetFilters}
            >
              Reset Filters
            </button>
          </div>
        </div>
      </div>

      {/* Shipments Data Table Card */}
      <div className="card">
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th onClick={() => handleSort('shipment_id')} style={{ cursor: 'pointer' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                    <span>Shipment ID</span>
                    <ArrowUpDown size={12} />
                  </div>
                </th>
                <th onClick={() => handleSort('supplier_id')} style={{ cursor: 'pointer' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                    <span>Supplier</span>
                    <ArrowUpDown size={12} />
                  </div>
                </th>
                <th onClick={() => handleSort('origin')} style={{ cursor: 'pointer' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                    <span>Origin → Destination</span>
                    <ArrowUpDown size={12} />
                  </div>
                </th>
                <th onClick={() => handleSort('transport_mode')} style={{ cursor: 'pointer' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                    <span>Mode</span>
                    <ArrowUpDown size={12} />
                  </div>
                </th>
                <th onClick={() => handleSort('distance_km')} style={{ cursor: 'pointer' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                    <span>Distance</span>
                    <ArrowUpDown size={12} />
                  </div>
                </th>
                <th onClick={() => handleSort('delay_probability')} style={{ cursor: 'pointer' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                    <span>Delay Prob</span>
                    <ArrowUpDown size={12} />
                  </div>
                </th>
                <th onClick={() => handleSort('expected_delay_days')} style={{ cursor: 'pointer' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                    <span>Exp. Delay</span>
                    <ArrowUpDown size={12} />
                  </div>
                </th>
                <th onClick={() => handleSort('risk_level')} style={{ cursor: 'pointer' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                    <span>Risk Level</span>
                    <ArrowUpDown size={12} />
                  </div>
                </th>
                <th onClick={() => handleSort('prediction_status')} style={{ cursor: 'pointer' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                    <span>Prediction</span>
                    <ArrowUpDown size={12} />
                  </div>
                </th>
                <th style={{ textAlign: 'center' }}>Inspect</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan={10} style={{ textAlign: 'center', padding: '2.5rem' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem' }}>
                      <RefreshCw size={22} className="animate-spin" color="var(--deep-indigo)" />
                      <span style={{ fontSize: '0.84rem', color: 'var(--text-secondary)' }}>Loading shipments data...</span>
                    </div>
                  </td>
                </tr>
              ) : paginatedShipments.length === 0 ? (
                <tr>
                  <td colSpan={10} style={{ textAlign: 'center', padding: '3rem' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.65rem' }}>
                      <AlertTriangle size={32} color="var(--text-muted)" />
                      <span style={{ fontWeight: 600, fontSize: '0.95rem' }}>No shipments match your search or filter criteria.</span>
                      <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Try broadening your risk level, mode, or supplier filters.</p>
                      <button className="btn btn-secondary btn-sm" onClick={resetFilters}>Reset All Filters</button>
                    </div>
                  </td>
                </tr>
              ) : (
                paginatedShipments.map((s) => {
                  const prob = typeof s.delay_probability === 'number'
                    ? (s.delay_probability * 100).toFixed(1)
                    : '25.0';
                  const expDays = typeof s.expected_delay_days === 'number'
                    ? s.expected_delay_days.toFixed(1)
                    : (s.actual_delay_days || 0.5);

                  return (
                    <tr
                      key={s.shipment_id}
                      className="clickable"
                      onClick={() => onSelectShipment(s.shipment_id)}
                    >
                      <td style={{ fontWeight: 600, color: 'var(--deep-indigo)' }}>
                        {s.shipment_id}
                      </td>
                      <td>
                        <span style={{ fontWeight: 500 }}>{s.supplier_id}</span>
                      </td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                          <span>{s.origin}</span>
                          <span style={{ color: 'var(--text-muted)' }}>→</span>
                          <span>{s.destination}</span>
                        </div>
                      </td>
                      <td>
                        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem' }}>
                          <Truck size={13} color="var(--muted-indigo)" />
                          {s.transport_mode}
                        </span>
                      </td>
                      <td style={{ fontFamily: 'var(--font-mono)' }}>
                        {s.distance_km ? `${s.distance_km} km` : '—'}
                      </td>
                      <td style={{ fontWeight: 600 }}>
                        {prob}%
                      </td>
                      <td>
                        <span style={{ color: expDays >= 3 ? 'var(--critical)' : 'var(--text-main)', fontWeight: expDays >= 3 ? 600 : 400 }}>
                          +{expDays}d
                        </span>
                      </td>
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
                          fontSize: '0.78rem',
                          fontWeight: 600,
                          color: s.prediction_status === 'DELAYED' ? 'var(--critical)' : 'var(--success)'
                        }}>
                          {s.prediction_status}
                        </span>
                      </td>
                      <td style={{ textAlign: 'center' }}>
                        <button
                          className="btn btn-secondary btn-sm"
                          style={{ padding: '0.2rem 0.55rem', fontSize: '0.72rem' }}
                          onClick={(e) => {
                            e.stopPropagation();
                            onSelectShipment(s.shipment_id);
                          }}
                        >
                          <Eye size={12} />
                          <span>Panel</span>
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Controls */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '1.25rem', paddingTop: '0.75rem', borderTop: '1px solid var(--border-subtle)' }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            Page <strong>{currentPage}</strong> of <strong>{totalPages}</strong> ({filteredShipments.length} total shipments)
          </div>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              className="btn btn-secondary btn-sm"
              disabled={currentPage <= 1}
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
            >
              Previous
            </button>
            <button
              className="btn btn-secondary btn-sm"
              disabled={currentPage >= totalPages}
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
