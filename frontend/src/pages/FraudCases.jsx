import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import Spinner from "../components/Spinner";
import api from "../api/client";
import "../styles/fraud_cases.css";

const FraudCases = () => {
  const navigate = useNavigate();

  // State Management
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Resolve Modal State
  const [showResolveModal, setShowResolveModal] = useState(false);
  const [selectedCase, setSelectedCase] = useState(null);
  const [resolutionReason, setResolutionReason] = useState("");
  const [resolving, setResolving] = useState(false);

  // Investigation State
  const [investigating, setInvestigating] = useState(false);

  // Case History Modal State
  const [showHistoryModal, setShowHistoryModal] = useState(false);
  const [historyData, setHistoryData] = useState(null);
  const [historyLoading, setHistoryLoading] = useState(false);

  // UI State
  const [filterStatus, setFilterStatus] = useState("all"); // "all", "open", "investigating"
  const [sortBy, setSortBy] = useState("created_at"); // "created_at", "risk_level", "user_id"

  // 🔐 HARD SECURITY CHECK
  useEffect(() => {
    const isAuth = localStorage.getItem("isAdminLoggedIn");
    if (isAuth !== "true") {
      navigate("/login", { replace: true });
    }
  }, [navigate]);

  // ============ FETCH OPEN CASES ============
  useEffect(() => {
    fetchOpenCases();
  }, []);

  const fetchOpenCases = async () => {
    setLoading(true);
    setError("");
    try {
      const response = await api.get("/admin/cases/list/open");
      setCases(response.data.cases || []);
    } catch (err) {
      console.error("Error fetching cases:", err);
      const errorMsg = err.response?.data?.detail || "Failed to fetch cases";
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  // ============ START INVESTIGATION ============
  const handleStartInvestigation = async (fraudCase) => {
    const adminId = localStorage.getItem("adminId");
    if (!adminId) {
      alert("Admin ID not found. Please login again.");
      return;
    }

    // Confirmation
    if (!window.confirm(`Start investigation for case #${fraudCase.id} (${fraudCase.user_id})?`)) {
      return;
    }

    setInvestigating(true);
    try {
      const payload = {
        case_id: fraudCase.id,
        admin_id: adminId,
      };

      const response = await api.put(`/admin/cases/${fraudCase.id}/investigate`, payload);

      if (response.status === 200) {
        alert(`✓ Investigation started for case #${fraudCase.id}`);
        fetchOpenCases(); // Refresh the list
      }
    } catch (err) {
      console.error("Error starting investigation:", err);
      const errorMsg = err.response?.data?.detail || "Failed to start investigation";
      alert(`Error: ${errorMsg}`);
    } finally {
      setInvestigating(false);
    }
  };

  // ============ RESOLVE CASE ============
  const handleResolveClick = (fraudCase) => {
    setSelectedCase(fraudCase);
    setResolutionReason("");
    setShowResolveModal(true);
  };

  const submitResolveCase = async () => {
    if (!selectedCase || !resolutionReason.trim()) {
      alert("Please enter a resolution reason");
      return;
    }

    const adminId = localStorage.getItem("adminId");
    if (!adminId) {
      alert("Admin ID not found. Please login again.");
      return;
    }

    setResolving(true);
    try {
      const payload = {
        case_id: selectedCase.id,
        resolution_reason: resolutionReason,
        admin_id: adminId,
      };

      const response = await api.put(`/admin/cases/${selectedCase.id}/resolve`, payload);

      if (response.status === 200) {
        const timestamp = new Date().toLocaleDateString("en-IN") + " " + new Date().toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" });
        alert(`✓ Case #${selectedCase.id} resolved successfully!\n\nResolved By: ${adminId}\nTime: ${timestamp}`);
        setShowResolveModal(false);
        setSelectedCase(null);
        setResolutionReason("");
        fetchOpenCases(); // Refresh the list
      }
    } catch (err) {
      console.error("Error resolving case:", err);
      const errorMsg = err.response?.data?.detail || "Failed to resolve case";
      alert(`Error: ${errorMsg}`);
    } finally {
      setResolving(false);
    }
  };

  // ============ VIEW CASE HISTORY ============
  const handleViewHistory = async (userId) => {
    setHistoryLoading(true);
    try {
      const response = await api.get(`/admin/cases/history/${userId}`);
      setHistoryData(response.data);
      setShowHistoryModal(true);
    } catch (err) {
      console.error("Error fetching history:", err);
      alert("Failed to fetch case history");
    } finally {
      setHistoryLoading(false);
    }
  };

  // ============ GET CASE COUNTS BY STATUS ============
  const getCaseCountsByStatus = () => {
    const counts = {
      all: cases.length,
      open: cases.filter((c) => c.status === "OPEN").length,
      investigating: cases.filter((c) => c.status === "UNDER_INVESTIGATION").length,
      resolved: cases.filter((c) => c.status === "RESOLVED").length,
    };
    return counts;
  };

  const caseCounts = getCaseCountsByStatus();

  const parseApiDate = (dateStr) => {
    if (!dateStr || typeof dateStr !== "string") return null;

    // Backend sends UTC timestamps without timezone suffix (e.g. 2026-04-22T04:36:00).
    // Append Z so browser parses it as UTC and converts correctly to local time.
    const hasTimezone = /([zZ]|[+\-]\d{2}:\d{2})$/.test(dateStr);
    const normalized = hasTimezone ? dateStr : `${dateStr}Z`;
    const parsedDate = new Date(normalized);

    return Number.isNaN(parsedDate.getTime()) ? null : parsedDate;
  };

  // ============ FILTERING & SORTING ============
  const getFilteredAndSortedCases = () => {
    let filtered = [...cases];

    // ALWAYS exclude RESOLVED cases from this view (they belong in Resolved Cases section)
    filtered = filtered.filter((c) => c.status !== "RESOLVED");

    // Filter by status
    if (filterStatus === "open") {
      filtered = filtered.filter((c) => c.status === "OPEN");
    } else if (filterStatus === "investigating") {
      filtered = filtered.filter((c) => c.status === "UNDER_INVESTIGATION");
    }
    // If filterStatus === "all", show all non-resolved cases (already filtered above)

    // Sort
    filtered.sort((a, b) => {
      if (sortBy === "created_at") {
        const firstDate = parseApiDate(a.created_at);
        const secondDate = parseApiDate(b.created_at);
        return (secondDate?.getTime() || 0) - (firstDate?.getTime() || 0);
      } else if (sortBy === "risk_level") {
        return b.risk_level - a.risk_level;
      } else if (sortBy === "user_id") {
        return a.user_id.localeCompare(b.user_id);
      }
      return 0;
    });

    return filtered;
  };

  const getRiskLevelColor = (level) => {
    const colors = {
      1: { backgroundColor: "#fff3e0", color: "#e65100" },
      2: { backgroundColor: "#ffe0b2", color: "#e65100" },
      3: { backgroundColor: "#ffccbc", color: "#d84315" },
    };
    return colors[level] || {};
  };

  const getStatusColor = (status) => {
    const colors = {
      OPEN: { backgroundColor: "#ffebee", color: "#c62828" },
      UNDER_INVESTIGATION: { backgroundColor: "#e3f2fd", color: "#1565c0" },
      RESOLVED: { backgroundColor: "#e8f5e9", color: "#2e7d32" },
    };
    return colors[status] || {};
  };

  const formatDateTime = (dateStr) => {
    if (!dateStr) return "N/A";
    const date = parseApiDate(dateStr);
    if (!date) return "N/A";
    return date.toLocaleDateString("en-IN") + " " + date.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" });
  };

  const filteredCases = getFilteredAndSortedCases();

  return (
    <>
      <Navbar isAdmin={true} />
      {loading && <Spinner message="Loading fraud cases..." />}

      <div style={styles.container} className="fraud-cases-page">
        <div style={styles.backgroundLayer} className="fraud-cases-background-layer" />
        <div style={styles.containerOverlay} />

        <div style={styles.content}>
          <div style={styles.header}>
            <h1>🚨 Active Fraud Cases</h1>
            <p>View and manage OPEN and UNDER_INVESTIGATION fraud cases (Resolved cases are archived)</p>
          </div>

          {/* Filters & Controls */}
          <div style={styles.controlsSection}>
            <div style={styles.filterGroup}>
              <label style={styles.label}>Filter by Status:</label>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                style={styles.select}
              >
                <option value="all">All Active Cases</option>
                <option value="open">🔴 Open Only</option>
                <option value="investigating">🟡 Under Investigation Only</option>
              </select>
            </div>

          <div style={styles.filterGroup}>
            <label style={styles.label}>Sort by:</label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              style={styles.select}
            >
              <option value="created_at">Created Date (Newest)</option>
              <option value="risk_level">Risk Level (High to Low)</option>
              <option value="user_id">User ID (A to Z)</option>
            </select>
          </div>

            <button style={styles.refreshBtn} onClick={fetchOpenCases}>
              🔄 Refresh
            </button>
          </div>

          {/* Error Message */}
          {error && (
            <div
              style={{ ...styles.card, backgroundColor: "#ffebee", borderLeft: "4px solid #d32f2f", marginBottom: "20px" }}
            >
              <p style={{ color: "#d32f2f" }}>
                <b>Error:</b> {error}
              </p>
            </div>
          )}

          {/* Cases Table */}
          {filteredCases.length > 0 ? (
            <div style={styles.card}>
            <div
              style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}
              className="fraud-cases-summary-row"
            >
              <h2 style={{ marginTop: 0, marginBottom: 0 }}>Active Fraud Cases</h2>
              <div style={{ fontSize: "14px", color: "#666" }} className="fraud-cases-summary-stats">
                <span style={{ marginRight: "20px" }} className="fraud-cases-stat-item">
                  <b>🔴 Open:</b> <span style={{ color: "#c62828", fontWeight: "bold" }}>{caseCounts.open}</span>
                </span>
                <span style={{ marginRight: "20px" }} className="fraud-cases-stat-item">
                  <b>🟡 Investigating:</b> <span style={{ color: "#1565c0", fontWeight: "bold" }}>{caseCounts.investigating}</span>
                </span>
                <span className="fraud-cases-stat-item fraud-cases-total-item">
                  <b>Total Active:</b> <span style={{ color: "#d32f2f", fontWeight: "bold" }}>{caseCounts.open + caseCounts.investigating}</span>
                </span>
              </div>
            </div>

            <div style={styles.tableWrapper}>
              <table style={styles.table}>
                <thead>
                  <tr style={styles.tableHeader}>
                    <th style={styles.th}>Case ID</th>
                    <th style={styles.th}>User ID</th>
                    <th style={styles.th}>Risk Level</th>
                    <th style={styles.th}>Action Required</th>
                    <th style={styles.th}>Status</th>
                    <th style={styles.th}>Created By</th>
                    <th style={styles.th}>Created Date</th>
                    <th style={styles.th}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredCases.map((fraudCase) => (
                    <tr key={fraudCase.id} style={styles.tableRow}>
                      <td style={styles.td}>
                        <span style={{ fontWeight: "bold", color: "#0b3c5d" }}>#{fraudCase.id}</span>
                      </td>
                      <td style={styles.td}>
                        <span
                          style={{
                            cursor: "pointer",
                            color: "#1976d2",
                            textDecoration: "underline",
                          }}
                          onClick={() => handleViewHistory(fraudCase.user_id)}
                          title="Click to view case history"
                        >
                          {fraudCase.user_id}
                        </span>
                      </td>
                      <td style={styles.td}>
                        <span
                          style={{
                            ...getRiskLevelColor(fraudCase.risk_level),
                            padding: "4px 8px",
                            borderRadius: "4px",
                            fontWeight: "bold",
                          }}
                        >
                          Level {fraudCase.risk_level}
                        </span>
                      </td>
                      <td style={{ ...styles.td, fontSize: "12px" }}>
                        {fraudCase.recommended_action}
                      </td>
                      <td style={styles.td}>
                        <span
                          style={{
                            ...getStatusColor(fraudCase.status),
                            padding: "4px 12px",
                            borderRadius: "4px",
                            fontWeight: "bold",
                          }}
                        >
                          {fraudCase.status === "OPEN" && "🔴 OPEN"}
                          {fraudCase.status === "UNDER_INVESTIGATION" && "🟡 INVESTIGATING"}
                          {fraudCase.status === "RESOLVED" && "🟢 RESOLVED"}
                        </span>
                      </td>
                      <td style={styles.td}>
                        <span style={{ fontSize: "12px", color: "#666" }}>
                          {fraudCase.created_by_admin_id}
                        </span>
                      </td>
                      <td style={styles.td}>
                        <span style={{ fontSize: "12px", color: "#666" }}>
                          {formatDateTime(fraudCase.created_at)}
                        </span>
                      </td>
                      <td style={styles.td}>
                        {fraudCase.status === "OPEN" && (
                          <button
                            style={styles.investigateBtn}
                            onClick={() => handleStartInvestigation(fraudCase)}
                            disabled={investigating}
                          >
                            🔍 Investigate
                          </button>
                        )}
                        {fraudCase.status === "UNDER_INVESTIGATION" && (
                          <button
                            style={styles.resolveBtn}
                            onClick={() => handleResolveClick(fraudCase)}
                          >
                            ✓ Resolve
                          </button>
                        )}
                        {fraudCase.status === "RESOLVED" && (
                          <span style={{ color: "#999", fontSize: "12px" }}>—</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            </div>
          ) : (
            <div style={styles.card}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
              <h2 style={{ marginTop: 0, marginBottom: 0 }}>Active Fraud Cases</h2>
              <div style={{ fontSize: "14px", color: "#666" }}>
                <span style={{ marginRight: "20px" }}>
                  <b>🔴 Open:</b> <span style={{ color: "#c62828", fontWeight: "bold" }}>{caseCounts.open}</span>
                </span>
                <span style={{ marginRight: "20px" }}>
                  <b>🟡 Investigating:</b> <span style={{ color: "#1565c0", fontWeight: "bold" }}>{caseCounts.investigating}</span>
                </span>
                <span>
                  <b>Total Active:</b> <span style={{ color: "#d32f2f", fontWeight: "bold" }}>{caseCounts.open + caseCounts.investigating}</span>
                </span>
              </div>
            </div>
            <div style={styles.emptyState}>
              <p style={{ fontSize: "48px", marginBottom: "10px" }}>✓</p>
              <h2>All Active Cases Resolved!</h2>
              <p>No more fraud cases to investigate. All cases in the selected filter have been resolved.</p>
            </div>
            </div>
          )}
        </div>
      </div>

      {/* ============ RESOLVE MODAL ============ */}
      {showResolveModal && selectedCase && (
        <div style={styles.modalOverlay} onClick={() => !resolving && setShowResolveModal(false)}>
          <div style={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <div style={styles.modalHeader}>
              <h3>✓ Resolve Case #{selectedCase.id}</h3>
              <button
                style={styles.closeBtn}
                onClick={() => !resolving && setShowResolveModal(false)}
                disabled={resolving}
              >
                ✕
              </button>
            </div>

            <div style={{ padding: "20px" }}>
              <p style={{ fontSize: "14px", color: "#666", marginBottom: "15px" }}>
                <b>User ID:</b> {selectedCase.user_id} | <b>Risk Level:</b> Level {selectedCase.risk_level}
              </p>

              {/* Admin Info Box */}
              <div style={{ 
                backgroundColor: "#e3f2fd", 
                padding: "12px 15px", 
                borderRadius: "6px", 
                borderLeft: "4px solid #1565c0",
                marginBottom: "20px",
                fontSize: "13px"
              }}>
                <b>Resolving Admin:</b> {localStorage.getItem("adminId")}
                <p style={{ margin: "5px 0 0 0", color: "#666", fontSize: "12px" }}>
                  This case will be marked as resolved by this admin ID
                </p>
              </div>

              <label style={styles.label}>Resolution Reason:</label>
              <textarea
                value={resolutionReason}
                onChange={(e) => setResolutionReason(e.target.value)}
                placeholder="e.g., False Positive - Account Verified, Fraud Confirmed - Action Taken, Customer Dispute Resolved, etc."
                style={styles.textarea}
                disabled={resolving}
              />

              <p style={{ fontSize: "12px", color: "#999", marginBottom: "20px" }}>
                * Provide a clear reason for resolution so admins can understand the outcome later.
              </p>

              <div style={{ display: "flex", gap: "10px", justifyContent: "flex-end" }}>
                <button
                  style={styles.secondaryBtn}
                  onClick={() => !resolving && setShowResolveModal(false)}
                  disabled={resolving}
                >
                  ✕ Cancel
                </button>
                <button
                  style={{
                    ...styles.button,
                    backgroundColor: "#2e7d32",
                    opacity: resolving || !resolutionReason.trim() ? 0.6 : 1,
                  }}
                  onClick={submitResolveCase}
                  disabled={resolving || !resolutionReason.trim()}
                >
                  {resolving ? "Resolving..." : "✓ Resolve Case"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ============ CASE HISTORY MODAL ============ */}
      {showHistoryModal && historyData && (
        <div style={styles.modalOverlay} onClick={() => !historyLoading && setShowHistoryModal(false)}>
          <div style={{ ...styles.modalContent, maxHeight: "80vh", overflow: "auto" }} onClick={(e) => e.stopPropagation()}>
            <div style={styles.modalHeader}>
              <h3>📋 Case History - {historyData.user_id}</h3>
              <button
                style={styles.closeBtn}
                onClick={() => !historyLoading && setShowHistoryModal(false)}
                disabled={historyLoading}
              >
                ✕
              </button>
            </div>

            <div style={{ padding: "20px" }}>
              {historyLoading ? (
                <p>Loading case history...</p>
              ) : (
                <>
                  {/* Open Cases Section */}
                  {historyData.open_cases && historyData.open_cases.length > 0 && (
                    <div style={{ marginBottom: "30px" }}>
                      <h4 style={{ color: "#d32f2f", borderBottom: "2px solid #d32f2f", paddingBottom: "10px" }}>
                        🔴 Open Cases: {historyData.open_cases.length}
                      </h4>
                      {historyData.open_cases.map((caseItem) => (
                        <div key={caseItem.id} style={{ ...styles.historyCard, marginBottom: "10px" }}>
                          <p>
                            <b>Case ID:</b> #{caseItem.id} | <b>Risk Level:</b> Level {caseItem.risk_level}
                          </p>
                          <p>
                            <b>Action:</b> {caseItem.recommended_action}
                          </p>
                          <p style={{ fontSize: "12px", color: "#666" }}>
                            Created: {formatDateTime(caseItem.created_at)} by {caseItem.created_by_admin_id}
                          </p>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Resolved Cases Section */}
                  {historyData.resolved_cases && historyData.resolved_cases.length > 0 && (
                    <div>
                      <h4 style={{ color: "#2e7d32", borderBottom: "2px solid #2e7d32", paddingBottom: "10px" }}>
                        🟢 Resolved Cases: {historyData.resolved_cases.length}
                      </h4>
                      {historyData.resolved_cases.map((caseItem) => (
                        <div key={caseItem.id} style={{ ...styles.historyCard, marginBottom: "10px", backgroundColor: "#f1f8f6" }}>
                          <p>
                            <b>Case ID:</b> #{caseItem.id} | <b>Risk Level:</b> Level {caseItem.risk_level}
                          </p>
                          <p>
                            <b>Reason:</b> {caseItem.resolution_reason}
                          </p>
                          <p style={{ fontSize: "12px", color: "#666" }}>
                            Created: {formatDateTime(caseItem.created_at)} by {caseItem.created_by_admin_id} | Resolved by:{" "}
                            {caseItem.resolved_by_admin_id} on {formatDateTime(caseItem.resolved_at)}
                          </p>
                        </div>
                      ))}
                    </div>
                  )}

                  {historyData.total_cases === 0 && (
                    <p style={{ textAlign: "center", color: "#999" }}>No cases found for this user</p>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
};

const styles = {
  container: {
    backgroundColor: "transparent",
    minHeight: "100vh",
    padding: "40px 20px",
    maxWidth: "1400px",
    margin: "0 auto",
    position: "relative",
    overflow: "hidden",
  },
  backgroundLayer: {
    position: "fixed",
    inset: 0,
    background:
      "radial-gradient(circle at 20% 15%, rgba(22, 150, 255, 0.35) 0%, transparent 45%)," +
      "radial-gradient(circle at 80% 70%, rgba(15, 52, 96, 0.55) 0%, transparent 50%)," +
      "linear-gradient(135deg, #0a1f44 0%, #0f3460 45%, #1696ff 100%)",
    backgroundSize: "200% 200%",
    backgroundPosition: "20% 20%",
    zIndex: 0,
    pointerEvents: "none",
    willChange: "background-position",
  },
  containerOverlay: {
    position: "fixed",
    inset: 0,
    background:
      "linear-gradient(180deg, rgba(10, 31, 68, 0.65) 0%, rgba(10, 31, 68, 0.25) 50%, rgba(10, 31, 68, 0.65) 100%)",
    zIndex: 1,
    pointerEvents: "none",
  },
  content: {
    position: "relative",
    zIndex: 2,
  },
  header: {
    marginBottom: "30px",
    textAlign: "center",
    color: "white",
  },
  controlsSection: {
    display: "flex",
    gap: "20px",
    marginBottom: "30px",
    flexWrap: "wrap",
    alignItems: "flex-end",
  },
  filterGroup: {
    display: "flex",
    flexDirection: "column",
    gap: "8px",
  },
  label: {
    fontSize: "14px",
    fontWeight: "bold",
    color: "white",
  },
  select: {
    padding: "10px 12px",
    border: "1px solid #ddd",
    borderRadius: "6px",
    fontSize: "14px",
    cursor: "pointer",
    minWidth: "200px",
  },
  refreshBtn: {
    padding: "10px 20px",
    backgroundColor: "#0b3c5d",
    color: "white",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
    fontSize: "14px",
    fontWeight: "bold",
    transition: "background-color 0.3s",
  },
  card: {
    backgroundColor: "white",
    padding: "30px",
    borderRadius: "8px",
    boxShadow: "0 2px 8px rgba(0, 0, 0, 0.1)",
    marginBottom: "20px",
  },
  tableWrapper: {
    overflowX: "auto",
  },
  table: {
    width: "100%",
    borderCollapse: "collapse",
    marginTop: "20px",
  },
  tableHeader: {
    backgroundColor: "#0b3c5d",
    color: "white",
  },
  th: {
    padding: "12px 15px",
    textAlign: "left",
    fontWeight: "bold",
    fontSize: "14px",
  },
  tableRow: {
    borderBottom: "1px solid #eee",
    transition: "background-color 0.2s",
  },
  td: {
    padding: "12px 15px",
    fontSize: "14px",
  },
  investigateBtn: {
    padding: "8px 16px",
    backgroundColor: "#1565c0",
    color: "white",
    border: "none",
    borderRadius: "4px",
    cursor: "pointer",
    fontSize: "13px",
    fontWeight: "bold",
    transition: "background-color 0.3s",
  },
  resolveBtn: {
    padding: "8px 16px",
    backgroundColor: "#2e7d32",
    color: "white",
    border: "none",
    borderRadius: "4px",
    cursor: "pointer",
    fontSize: "13px",
    fontWeight: "bold",
    transition: "background-color 0.3s",
  },
  emptyState: {
    backgroundColor: "white",
    padding: "60px 40px",
    borderRadius: "8px",
    textAlign: "center",
    boxShadow: "0 2px 8px rgba(0, 0, 0, 0.1)",
  },
  modalOverlay: {
    position: "fixed",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: "rgba(0, 0, 0, 0.5)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 1000,
  },
  modalContent: {
    backgroundColor: "white",
    borderRadius: "8px",
    boxShadow: "0 4px 16px rgba(0, 0, 0, 0.3)",
    maxWidth: "500px",
    width: "90%",
  },
  modalHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "20px",
    borderBottom: "1px solid #eee",
  },
  closeBtn: {
    background: "none",
    border: "none",
    fontSize: "20px",
    cursor: "pointer",
    color: "#999",
    padding: 0,
    width: "30px",
    height: "30px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
  textarea: {
    width: "100%",
    padding: "12px",
    border: "1px solid #ddd",
    borderRadius: "6px",
    fontSize: "14px",
    fontFamily: "Arial, sans-serif",
    minHeight: "100px",
    resize: "vertical",
    marginBottom: "10px",
  },
  button: {
    padding: "12px 24px",
    backgroundColor: "#0b3c5d",
    color: "white",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
    fontSize: "14px",
    fontWeight: "bold",
    transition: "background-color 0.3s",
  },
  secondaryBtn: {
    padding: "12px 24px",
    backgroundColor: "#e0e0e0",
    color: "#333",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
    fontSize: "14px",
    fontWeight: "bold",
    transition: "background-color 0.3s",
  },
  historyCard: {
    backgroundColor: "#f9f9f9",
    padding: "12px 15px",
    borderRadius: "6px",
    borderLeft: "4px solid #0b3c5d",
  },
};

export default FraudCases;
