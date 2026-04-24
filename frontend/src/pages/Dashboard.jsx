import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import Spinner from "../components/Spinner";
import api from "../api/client";
import "../styles/dashboard.css";
import bgImage from "../image.png";

const Dashboard = () => {
  const navigate = useNavigate();

  // Individual Search
  const [userId, setUserId] = useState("");
  const [risk, setRisk] = useState(null);

  // Range Search
  const [startUserId, setStartUserId] = useState("");
  const [endUserId, setEndUserId] = useState("");
  const [rangeResults, setRangeResults] = useState([]);
  const [filteredResults, setFilteredResults] = useState([]);

  // UI State
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState("individual"); // "individual" or "range"
  const [sortBy, setSortBy] = useState("risk_level"); // "risk_level", "user_id"

  // Transaction Modal
  const [showModal, setShowModal] = useState(false);
  const [modalTransactions, setModalTransactions] = useState([]);
  const [modalTitle, setModalTitle] = useState("");

  // 🚨 Action Modal for Fraud Case
  const [showActionModal, setShowActionModal] = useState(false);
  const [actionCaseData, setActionCaseData] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);

  // Active case cache to prevent duplicate case creation for same user
  const [activeCasesByUser, setActiveCasesByUser] = useState({});

  // 🔐 HARD SECURITY CHECK
  useEffect(() => {
    const isAuth = localStorage.getItem("isAdminLoggedIn");
    if (isAuth !== "true") {
      navigate("/login", { replace: true });
    }
  }, [navigate]);

  const buildActiveCasesByUser = (cases = []) => {
    const activeMap = {};

    cases.forEach((caseItem) => {
      const userKey = caseItem?.user_id;
      if (!userKey) return;

      // Keep the latest case if duplicates already exist.
      const existingCase = activeMap[userKey];
      if (!existingCase || (caseItem.id || 0) > (existingCase.id || 0)) {
        activeMap[userKey] = caseItem;
      }
    });

    return activeMap;
  };

  const fetchActiveCases = async () => {
    try {
      const response = await api.get("/admin/cases/list/open");
      const openCases = response.data?.cases || [];
      setActiveCasesByUser(buildActiveCasesByUser(openCases));
    } catch (err) {
      console.error("Error fetching active cases:", err);
    }
  };

  useEffect(() => {
    fetchActiveCases();
  }, []);

  const getActiveCaseForUser = (caseUserId) => {
    if (!caseUserId) return null;
    return activeCasesByUser[caseUserId] || null;
  };

  // ============ INDIVIDUAL USER PREDICTION ============
  const predict = async () => {
    if (!userId) return alert("Enter User ID number");

    let userIdNum = userId.toString().trim();
    if (userIdNum.startsWith("USER") || userIdNum.startsWith("user")) {
      userIdNum = userIdNum.slice(4);
    }

    if (isNaN(userIdNum) || userIdNum === "") {
      setError("Invalid User ID. Enter a number like 1, 2141, etc.");
      return;
    }

    const userIdFormatted = `USER${userIdNum.padStart(4, "0")}`;
    setLoading(true);
    setError("");
    setRisk(null);

    try {
      console.log("Individual prediction for:", userIdFormatted);
      const response = await api.post("/admin/predict", {
        start_user_id: userIdFormatted,
        end_user_id: userIdFormatted,
      });

      const predictions = response.data;

      if (Object.keys(predictions).length === 0) {
        setRisk({
          score: 0,
          level: "No Risk",
          action: "All transactions are fine for this user",
          txnCount: 0,
          isGenuine: true,
          userId: userIdFormatted,
        });
        setLoading(false);
        return;
      }

      let riskLevel = null;
      let riskData = null;

      if (predictions.level_3 && predictions.level_3.length > 0) {
        riskLevel = 3;
        riskData = predictions.level_3[0];
      } else if (predictions.level_2 && predictions.level_2.length > 0) {
        riskLevel = 2;
        riskData = predictions.level_2[0];
      } else if (predictions.level_1 && predictions.level_1.length > 0) {
        riskLevel = 1;
        riskData = predictions.level_1[0];
      }

      if (!riskData) {
        setError("Unable to compute risk score");
        setLoading(false);
        return;
      }

      const riskActions = {
        1: "KYC Review Required",
        2: "Debit Freeze & Cyber Cell Escalation",
        3: "Full Account Freeze & Immediate Investigation",
      };

      setRisk({
        score: riskData.risk_pct,
        level: `Level ${riskLevel}`,
        action: riskActions[riskLevel],
        txnCount: riskData.window_txn_count,
        transactions: riskData.sample_transactions || [],
        riskLevelNum: riskLevel,
        userId: riskData.user_id || userIdFormatted,
      });
    } catch (err) {
      console.error("Prediction error:", err);
      let errorMsg = err.response?.data?.detail || "Error fetching prediction";
      if (typeof errorMsg !== "string") {
        errorMsg = JSON.stringify(errorMsg);
      }
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  // ============ RANGE USER PREDICTION ============
  const predictRange = async () => {
    if (!startUserId || !endUserId) return alert("Enter both start and end User IDs");

    let startNum = parseInt(startUserId.toString().trim());
    let endNum = parseInt(endUserId.toString().trim());

    if (isNaN(startNum) || isNaN(endNum)) {
      setError("Both IDs must be valid numbers");
      return;
    }

    if (startNum > endNum) {
      setError("Start ID cannot be greater than End ID");
      return;
    }

    if (endNum - startNum > 5000) {
      setError("Range too large. Maximum 5000 users at a time");
      return;
    }

    setLoading(true);
    setError("");
    setRangeResults([]);
    setFilteredResults([]);

    try {
      const startFormatted = `USER${startNum.toString().padStart(4, "0")}`;
      const endFormatted = `USER${endNum.toString().padStart(4, "0")}`;

      console.log(`Range prediction: ${startFormatted} to ${endFormatted}`);
      const response = await api.post("/admin/predict", {
        start_user_id: startFormatted,
        end_user_id: endFormatted,
      });

      const predictions = response.data;
      
      // Flatten all risky users into one array
      const allRiskyUsers = [];
      const riskLevelMap = { level_1: 1, level_2: 2, level_3: 3 };

      for (const [levelKey, users] of Object.entries(predictions)) {
        if (users && Array.isArray(users)) {
          const level = riskLevelMap[levelKey] || 0;
          allRiskyUsers.push(
            ...users.map((user) => ({
              ...user,
              risk_level: level,
              risk_level_name: {
                1: "Level 1 - KYC Review",
                2: "Level 2 - Debit Freeze",
                3: "Level 3 - Full Freeze",
              }[level],
            }))
          );
        }
      }

      setRangeResults(allRiskyUsers);
      setFilteredResults(allRiskyUsers);

      if (allRiskyUsers.length === 0) {
        setError(`No fraud risk found for users ${startNum} to ${endNum}`);
      }
    } catch (err) {
      console.error("Range prediction error:", err);
      let errorMsg = err.response?.data?.detail || "Error fetching predictions";
      if (typeof errorMsg !== "string") {
        errorMsg = JSON.stringify(errorMsg);
      }
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  // ============ FILTERING & SORTING ============
  useEffect(() => {
    let results = [...rangeResults];

    // Sort
    results.sort((a, b) => {
      if (sortBy === "risk_level") {
        return b.risk_level - a.risk_level; // Highest level first
      } else if (sortBy === "user_id") {
        return a.user_id.localeCompare(b.user_id); // Alphabetical
      }
      return 0;
    });

    setFilteredResults(results);
  }, [sortBy, rangeResults]);

  // ============ MODAL HANDLERS ============
  const handleViewTransactions = (transactions, title) => {
    setModalTransactions(transactions || []);
    setModalTitle(title);
    setShowModal(true);
  };

  // ============ TAKE ACTION FOR FRAUD CASE ============
  const handleTakeAction = (caseData) => {
    setActionCaseData(caseData);
    setShowActionModal(true);
  };

  const createCaseFromAction = async () => {
    if (!actionCaseData) return;

    const adminId = localStorage.getItem("adminId");
    if (!adminId) {
      alert("Admin ID not found. Please login again.");
      return;
    }

    const existingActiveCase = getActiveCaseForUser(actionCaseData.user_id);
    if (existingActiveCase) {
      alert(
        `Active case #${existingActiveCase.id} (${existingActiveCase.status}) already exists for ${actionCaseData.user_id}. Resolve it before creating a new case.`
      );
      setShowActionModal(false);
      setActionCaseData(null);
      return;
    }

    setActionLoading(true);
    try {
      const payload = {
        user_id: actionCaseData.user_id,
        risk_level: actionCaseData.risk_level,
        admin_id: adminId,
      };

      console.log("Creating fraud case:", payload);
      const response = await api.post("/admin/cases/create", payload);

      if (response.status === 200) {
        alert(`✓ Fraud case #${response.data.case_id} created successfully for ${actionCaseData.user_id}`);
        setShowActionModal(false);
        setActionCaseData(null);
        // Clear the prediction
        setRisk(null);
        setUserId("");
        fetchActiveCases();
      }
    } catch (err) {
      console.error("Error creating case:", err);
      const errorMsg = err.response?.data?.detail || "Failed to create case";
      alert(`Error: ${errorMsg}`);

      if (typeof errorMsg === "string" && errorMsg.toLowerCase().includes("already exists")) {
        fetchActiveCases();
        setShowActionModal(false);
        setActionCaseData(null);
      }
    } finally {
      setActionLoading(false);
    }
  };

  const activeCaseForIndividualUser = risk?.userId ? getActiveCaseForUser(risk.userId) : null;

  return (
    <>
      <Navbar isAdmin={true} />
      {loading && <Spinner message="Fetching fraud predictions..." />}

      <div style={styles.container} className="dashboard-page">
        <div style={styles.backgroundLayer} />
        <div style={styles.containerOverlay} />
        {/* TABS */}
        <div style={styles.tabContainer} className="dashboard-tabs-container">
          <button
            className="dashboard-tab-btn"
            style={{
              ...styles.tab,
              backgroundColor: activeTab === "individual" ? "#0b3c5d" : "#e0e0e0",
              color: activeTab === "individual" ? "white" : "black",
            }}
            onClick={() => {
              setActiveTab("individual");
              setError("");
              setRisk(null);
            }}
          >
            <span className="tab-icon">🔍</span> Individual Search
          </button>
          <button
            className="dashboard-tab-btn"
            style={{
              ...styles.tab,
              backgroundColor: activeTab === "range" ? "#0b3c5d" : "#e0e0e0",
              color: activeTab === "range" ? "white" : "black",
            }}
            onClick={() => {
              setActiveTab("range");
              setError("");
              setRangeResults([]);
              setFilteredResults([]);
            }}
          >
            <span className="tab-icon">📊</span> Range Search (Bulk Check)
          </button>
        </div>

        {/* ============ INDIVIDUAL SEARCH ============ */}
        {activeTab === "individual" && (
          <div style={styles.card} className="dashboard-card-animated">
            <h2>Individual User Risk Check</h2>

            <input
              className="dashboard-input-animated"
              style={styles.input}
              type="number"
              placeholder="Enter User ID (e.g., 1, 100, 2141)"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
            />

            <button
              className="dashboard-btn-primary"
              style={{
                ...styles.button,
                width: "260px",
                maxWidth: "100%",
                display: "block",
                margin: "10px auto 0",
                opacity: loading ? 0.6 : 1,
              }}
              onClick={predict}
              disabled={loading}
            >
              {loading ? "🔄 Checking..." : "✓ Check Risk"}
            </button>

            {error && (
              <div style={{ ...styles.result, backgroundColor: "#ffebee" }} className="dashboard-result-error">
                <p style={{ color: "#d32f2f" }}>
                  <b>⚠️ Error:</b> {String(error)}
                </p>
              </div>
            )}

            {risk && (
              <div style={{ ...styles.result, backgroundColor: risk.isGenuine ? "#e8f5e9" : "#fafafa" }} className="dashboard-result-card">
                {risk.isGenuine ? (
                  <>
                    <p style={{ color: "#2e7d32", fontSize: "18px", fontWeight: "bold" }}>✓ All Transactions Are Genuine</p>
                    <p style={{ color: "#2e7d32" }}>No fraud risk detected for this user. All transactions appear safe.</p>
                  </>
                ) : (
                  <>
                    <p>
                      <b>Risk Level:</b> {risk.level}
                    </p>
                    <p>
                      <b>Transactions Analyzed:</b> {risk.txnCount}
                    </p>
                    <p>
                      <b>Recommended Action:</b>
                    </p>
                    <p style={{ color: "#d32f2f", fontWeight: "bold" }}>{risk.action}</p>
                    
                    <div style={styles.buttonRow}>
                      <button
                        style={styles.secondaryBtn}
                        onClick={() => handleViewTransactions(risk.transactions, `Transactions for USER${userId.padStart(4, "0")}`)}
                      >
                        📋 View Transactions
                      </button>
                      {activeCaseForIndividualUser ? (
                        <button
                          style={styles.disabledActionBtn}
                          disabled={true}
                          title={`Active case #${activeCaseForIndividualUser.id} (${activeCaseForIndividualUser.status}) already exists`}
                        >
                          ⛔ Active Case
                        </button>
                      ) : (
                        <button
                          style={styles.actionBtn}
                          onClick={() =>
                            handleTakeAction({
                              user_id: `USER${userId.padStart(4, "0")}`,
                              risk_level: risk.riskLevelNum,
                            })
                          }
                        >
                          ⚡ Take Action
                        </button>
                      )}
                    </div>
                    {activeCaseForIndividualUser && (
                      <p style={styles.activeCaseNote}>
                        Case #{activeCaseForIndividualUser.id} is already {activeCaseForIndividualUser.status}. Resolve that case before creating a new one.
                      </p>
                    )}
                  </>
                )}
              </div>
            )}
          </div>
        )}

        {/* ============ RANGE SEARCH ============ */}
        {activeTab === "range" && (
          <div style={styles.card} className="dashboard-card-animated dashboard-range-search">
            <h2>Bulk Risk Check (User Range)</h2>

            <div style={styles.inputRow}>
              <div className="form-group-animated">
                <label style={styles.label}>From User ID</label>
                <input
                  className="dashboard-input-animated"
                  style={styles.input}
                  type="number"
                  placeholder="e.g., 1"
                  value={startUserId}
                  onChange={(e) => setStartUserId(e.target.value)}
                />
              </div>
              <div className="form-group-animated">
                <label style={styles.label}>To User ID</label>
                <input
                  className="dashboard-input-animated"
                  style={styles.input}
                  type="number"
                  placeholder="e.g., 100"
                  value={endUserId}
                  onChange={(e) => setEndUserId(e.target.value)}
                />
              </div>
            </div>

            <button
              className="dashboard-btn-primary"
              style={{
                ...styles.button,
                width: "260px",
                maxWidth: "100%",
                display: "block",
                margin: "10px auto 0",
                opacity: loading ? 0.6 : 1,
              }}
              onClick={predictRange}
              disabled={loading}
            >
              {loading ? "🔄 Scanning..." : "🔎 Scan for Fraud"}
            </button>

            {error && (
              <div style={{ ...styles.result, backgroundColor: "#ffebee" }} className="dashboard-result-error">
                <p style={{ color: "#d32f2f" }}>
                  <b>✓ No Risky Accounts Found:</b> {String(error)}
                </p>
              </div>
            )}

            {/* Results Table */}
            {filteredResults.length > 0 && (
              <div style={styles.resultsSection} className="dashboard-results-animated">
                <div style={styles.resultHeader} className="dashboard-results-header">
                  <h3>Risky Accounts Found: {filteredResults.length}</h3>
                  <div style={styles.sortContainer} className="dashboard-sort-container">
                    <label style={styles.sortLabel} className="dashboard-sort-label">Sort by:</label>
                    <select
                      className="dashboard-sort-select"
                      value={sortBy}
                      onChange={(e) => setSortBy(e.target.value)}
                      style={styles.sortSelect}
                    >
                      <option value="risk_level">Risk User</option>
                      <option value="user_id">User ID</option>
                    </select>
                  </div>
                </div>

                <div style={styles.tableWrapper} className="dashboard-table-wrapper">
                <table style={styles.table}>
                  <thead>
                    <tr style={styles.tableHeader}>
                      <th style={styles.th}>User ID</th>
                      <th style={styles.th}>Risk Level</th>
                      <th style={styles.th}>Txns Analyzed</th>
                      <th style={styles.th}>Recommended Action</th>
                      <th style={styles.th}>View Txns</th>
                      <th style={styles.th}>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredResults.map((user, idx) => {
                      const activeCaseForUser = getActiveCaseForUser(user.user_id);

                      return (
                      <tr key={idx} style={{...styles.tableRow, animationDelay: `${idx * 0.05}s`}} className="table-row-animated">
                        <td style={styles.td}>{user.user_id}</td>
                        <td style={styles.td}>
                          <span style={getRiskLevelColor(user.risk_level)} className="risk-badge">{user.risk_level_name}</span>
                        </td>
                        <td style={styles.td}>
                          <span className="txn-count-badge">{user.window_txn_count}</span>
                        
                        </td>
                        <td style={{ ...styles.td, fontSize: "12px" }}>
                          {user.risk_level === 1 && "KYC Review Required"}
                          {user.risk_level === 2 && "Debit Freeze & Cyber Cell"}
                          {user.risk_level === 3 && "Full Account Freeze"}
                        </td>
                        <td style={styles.td}>
                          <button
                            className="dashboard-icon-btn"
                            style={styles.smallBtn}
                            onClick={() => handleViewTransactions(user.sample_transactions, `Transactions for ${user.user_id}`)}
                          >
                            📋
                          </button>
                        </td>
                        <td style={styles.td}>
                          <button
                            className="dashboard-action-btn-small"
                            style={activeCaseForUser ? styles.disabledActionBtn : styles.actionBtn}
                            onClick={() =>
                              !activeCaseForUser &&
                              handleTakeAction({
                                user_id: user.user_id,
                                risk_level: user.risk_level,
                              })
                            }
                            disabled={Boolean(activeCaseForUser)}
                            title={
                              activeCaseForUser
                                ? `Active case #${activeCaseForUser.id} (${activeCaseForUser.status}) already exists`
                                : "Create fraud case"
                            }
                          >
                            {activeCaseForUser ? "⛔" : "⚡"}
                          </button>
                        </td>
                      </tr>
                      );
                    })}
                  </tbody>
                </table>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* ============ TRANSACTION MODAL ============ */}
      {showModal && (
        <div style={styles.modalOverlay} className="dashboard-modal-overlay" onClick={() => setShowModal(false)}>
          <div style={styles.modalContent} className="dashboard-modal-content" onClick={(e) => e.stopPropagation()}>
            <div style={styles.modalHeader}>
              <h3>📋 {modalTitle}</h3>
              <button
                className="modal-close-btn"
                style={styles.closeBtn}
                onClick={() => setShowModal(false)}
              >
                ✕
              </button>
            </div>

            {modalTransactions && modalTransactions.length > 0 ? (
              <div style={styles.transactionsList}>
                {modalTransactions.map((txn, idx) => {
                  const txnDate = txn.transaction_datetime ? new Date(txn.transaction_datetime) : null;
                  const txnTime = txnDate ? txnDate.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" }) : "N/A";
                  const txnTimeHour = txnDate ? txnDate.getHours() : null;
                  const isSuspiciousTime = txnTimeHour !== null && (txnTimeHour < 6 || txnTimeHour > 22);

                  return (
                    <div key={idx} style={{...styles.transactionCard, animationDelay: `${idx * 0.08}s`}} className="transaction-card-animated">
                      <div style={styles.txnRow}>
                        <span style={styles.txnLabel}>Transaction ID:</span>
                        <span style={{ fontWeight: "bold", color: "#0b3c5d" }}>{txn.transaction_id || txn.id || "N/A"}</span>
                      </div>

                      <div style={styles.txnRow}>
                        <span style={styles.txnLabel}>Date & Time:</span>
                        <span>
                          {txnDate ? txnDate.toLocaleDateString("en-IN") : "N/A"} {txnTime}
                          {isSuspiciousTime && <span style={{ color: "#d32f2f", fontWeight: "bold", marginLeft: "8px" }}>⚠️ Suspicious Time</span>}
                        </span>
                      </div>

                      <div style={styles.txnRow}>
                        <span style={styles.txnLabel}>Amount:</span>
                        <span style={{ fontWeight: "bold", color: "#d32f2f" }}>₹ {txn.amount?.toFixed(2) || "N/A"}</span>
                      </div>

                      <div style={styles.txnRow}>
                        <span style={styles.txnLabel}>Type:</span>
                        <span style={{ 
                          fontWeight: "bold", 
                          color: "#0b3c5d",
                          backgroundColor: "#e3f2fd",
                          padding: "4px 8px",
                          borderRadius: "4px"
                        }}>
                          {txn.payment_type || "N/A"}
                        </span>
                        {txn.transaction_type && (
                          <span style={{ 
                            fontWeight: "bold", 
                            marginLeft: "8px",
                            color: txn.transaction_type === "CREDIT" ? "#2e7d32" : "#d32f2f",
                            backgroundColor: txn.transaction_type === "CREDIT" ? "#e8f5e9" : "#ffebee",
                            padding: "4px 8px",
                            borderRadius: "4px"
                          }}>
                            ({txn.transaction_type})
                          </span>
                        )}
                      </div>

                      <div style={styles.txnRow}>
                        <span style={styles.txnLabel}>From:</span>
                        <span style={{ color: "#0b3c5d", fontWeight: "500" }}>
                          {txn.user_bank || "User Bank"} • {txn.location_city || "City"}, {txn.location_state || "State"}
                        </span>
                      </div>

                      <div style={styles.txnRow}>
                        <span style={styles.txnLabel}>To:</span>
                        <span style={{ color: "#0b3c5d", fontWeight: "500" }}>
                          {txn.counterparty_bank || "Recipient Bank"} • 
                          <span style={{ fontFamily: "monospace", color: "#666", marginLeft: "4px" }}>
                            {txn.counterparty_account || "Account"}
                          </span>
                        </span>
                      </div>

                      <div style={styles.txnRow}>
                        <span style={styles.txnLabel}>Beneficiary:</span>
                        <span style={{
                          fontWeight: "bold",
                          color: txn.is_beneficiary ? "#2e7d32" : "#ff9800",
                          backgroundColor: txn.is_beneficiary ? "#e8f5e9" : "#fff3e0",
                          padding: "4px 8px",
                          borderRadius: "4px"
                        }}>
                          {txn.is_beneficiary ? "✓ Known Beneficiary" : "⚠️ Non-Beneficiary"}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p style={{ textAlign: "center", color: "#999", padding: "20px" }}>No transactions available</p>
            )}
          </div>
        </div>
      )}

      {/* ============ ACTION MODAL (Take Action) ============ */}
      {showActionModal && actionCaseData && (
        <div style={styles.modalOverlay} onClick={() => !actionLoading && setShowActionModal(false)}>
          <div style={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <div style={styles.modalHeader}>
              <h3>🚨 Create Fraud Case</h3>
              <button
                style={styles.closeBtn}
                onClick={() => !actionLoading && setShowActionModal(false)}
                disabled={actionLoading}
              >
                ✕
              </button>
            </div>

            <div style={{ padding: "20px" }}>
              <p style={{ fontSize: "18px", fontWeight: "bold", marginBottom: "15px" }}>
                Confirm Case Details
              </p>

              <div style={{ backgroundColor: "#f5f5f5", padding: "15px", borderRadius: "8px", marginBottom: "20px" }}>
                <p>
                  <b>User ID:</b> {actionCaseData.user_id}
                </p>
                <p>
                  <b>Risk Level:</b> Level {actionCaseData.risk_level}
                </p>
                <p>
                  <b>Action Required:</b>
                  {actionCaseData.risk_level === 1 && " KYC Review Required"}
                  {actionCaseData.risk_level === 2 && " Debit Freeze & Cyber Cell Escalation"}
                  {actionCaseData.risk_level === 3 && " Full Account Freeze & Immediate Investigation"}
                </p>
              </div>

              <p style={{ color: "#666", fontSize: "14px", marginBottom: "20px" }}>
                📝 This case will be added to the Fraud Cases list where you can mark it as "Under Investigation" and then
                "Resolved" with a reason.
              </p>

              <div style={{ display: "flex", gap: "10px", justifyContent: "flex-end" }}>
                <button
                  style={{
                    ...styles.secondaryBtn,
                    opacity: actionLoading ? 0.6 : 1,
                  }}
                  onClick={() => !actionLoading && setShowActionModal(false)}
                  disabled={actionLoading}
                >
                  ✕ Cancel
                </button>
                <button
                  style={{
                    ...styles.button,
                    backgroundColor: "#d32f2f",
                    opacity: actionLoading ? 0.6 : 1,
                  }}
                  onClick={createCaseFromAction}
                  disabled={actionLoading}
                >
                  {actionLoading ? "Creating..." : "✓ Create Case"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

// Helper function for risk level color
const getRiskLevelColor = (level) => {
  const colors = {
    1: { backgroundColor: "#fff3e0", color: "#e65100", padding: "4px 8px", borderRadius: "4px" },
    2: { backgroundColor: "#ffe0b2", color: "#e65100", padding: "4px 8px", borderRadius: "4px" },
    3: { backgroundColor: "#ffccbc", color: "#d84315", padding: "4px 8px", borderRadius: "4px", fontWeight: "bold" },
  };
  return colors[level] || {};
};

const styles = {
  container: {
    minHeight: "100vh",
    padding: "0 20px",
    position: "relative",
    overflow: "hidden",
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "center",
    zIndex: 0,
  },
  backgroundLayer: {
    position: "absolute",
    inset: 0,
    backgroundImage: `url(${bgImage})`,
    backgroundSize: "cover",
    backgroundPosition: "center",
    backgroundAttachment: "scroll",
    zIndex: 0,
    pointerEvents: "none",
    animation: "dashboardBgTransform 12s ease-in-out infinite",
    willChange: "transform",
  },
  containerOverlay: {
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background:
      "radial-gradient(circle at 15% 20%, rgba(22, 150, 255, 0.20) 0%, transparent 45%)," +
      "radial-gradient(circle at 85% 75%, rgba(15, 52, 96, 0.25) 0%, transparent 50%)," +
      "linear-gradient(135deg, rgba(10, 31, 68, 0.78) 0%, rgba(15, 52, 96, 0.55) 45%, rgba(22, 150, 255, 0.22) 100%)",
    pointerEvents: "none",
    zIndex: 0,
    animation: "bgFloat 15s ease-in-out infinite",
  },
  tabContainer: {
    display: "flex",
    gap: "10px",
    maxWidth: "1000px",
    margin: "60px auto 30px",
    justifyContent: "center",
    position: "relative",
    zIndex: 2,
  },
  tab: {
    flex: 1,
    padding: "12px 20px",
    border: "2px solid rgba(22, 150, 255, 0.3)",
    borderRadius: "8px",
    cursor: "pointer",
    fontSize: "16px",
    fontWeight: "bold",
    transition: "all 0.3s ease",
    background: "rgba(255, 255, 255, 0.9)",
    color: "#0a1e2e",
    boxShadow: "0 4px 15px rgba(0,0,0,0.2)",
    animation: "slideUp 0.6s ease-out",
  },
  card: {
    maxWidth: "1100px",
    width: "100%",
    margin: "0 auto",
    backgroundColor: "rgba(255, 255, 255, 0.97)",
    padding: "clamp(20px, 4vw, 60px)",
    borderRadius: "16px",
    boxShadow: "0 20px 60px rgba(0,0,0,0.3), 0 0 40px rgba(22, 150, 255, 0.15)",
    border: "2px solid rgba(22, 150, 255, 0.3)",
    backdropFilter: "blur(10px)",
    position: "relative",
    zIndex: 2,
    animation: "slideUp 0.6s ease-out, cardGlow 4s ease-in-out infinite",
    overflow: "hidden",
  },
  inputRow: {
    display: "flex",
    flexWrap: "wrap",
    gap: "20px",
    marginBottom: "20px",
  },
  label: {
    display: "block",
    marginBottom: "8px",
    fontWeight: "bold",
    color: "#0a1e2e",
    fontSize: "14px",
  },
  input: {
    width: "100%",
    padding: "13px 15px",
    marginBottom: "15px",
    borderRadius: "8px",
    border: "2px solid #e0e0e0",
    background: "rgba(245, 245, 245, 0.7)",
    fontSize: "14px",
    transition: "all 0.3s ease",
    boxSizing: "border-box",
    animation: "slideUp 0.7s ease-out",
  },
  button: {
    width: "100%",
    padding: "13px",
    background: "linear-gradient(135deg, #1696ff 0%, #0f3460 100%)",
    color: "white",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
    fontWeight: "600",
    fontSize: "15px",
    boxShadow: "0 4px 15px rgba(22, 150, 255, 0.3)",
    transition: "all 0.3s ease",
    marginTop: "10px",
    position: "relative",
    overflow: "hidden",
    animation: "slideUp 0.8s ease-out, buttonShimmer 3s ease-in-out infinite",
  },
  result: {
    marginTop: "20px",
    padding: "18px 20px",
    background: "linear-gradient(135deg, rgba(255, 107, 107, 0.08) 0%, rgba(255, 107, 107, 0.03) 100%)",
    borderRadius: "8px",
    borderLeft: "5px solid #ff6b6b",
    border: "1px solid rgba(255, 107, 107, 0.2)",
    boxShadow: "0 4px 15px rgba(0,0,0,0.1)",
    fontWeight: "500",
    color: "#333",
    animation: "fadeIn 0.4s ease-in, resultPulse 2s ease-in-out infinite",
  },
  resultsSection: {
    marginTop: "30px",
    animation: "fadeIn 0.6s ease-in",
  },
  resultHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "20px",
    paddingBottom: "10px",
    borderBottom: "2px solid rgba(22, 150, 255, 0.3)",
  },
  sortContainer: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
  },
  sortLabel: {
    fontSize: "16px",
    fontWeight: "500",
    color: "#0a1e2e",
  },
  sortSelect: {
    padding: "10px 40px 10px 14px",
    border: "2px solid rgba(22, 150, 255, 0.32)",
    borderRadius: "10px",
    cursor: "pointer",
    background: "rgba(255, 255, 255, 0.96)",
    color: "#0a1e2e",
    fontWeight: "700",
    minWidth: "180px",
    height: "52px",
    outline: "none",
    transition: "border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease",
  },
  tableWrapper: {
    width: "100%",
    overflowX: "auto",
    WebkitOverflowScrolling: "touch",
  },
  table: {
    width: "100%",
    minWidth: "760px",
    borderCollapse: "collapse",
    backgroundColor: "rgba(255, 255, 255, 0.95)",
    boxShadow: "0 8px 25px rgba(0,0,0,0.2)",
    borderRadius: "8px",
    overflow: "hidden",
    animation: "slideUp 0.7s ease-out",
  },
  tableHeader: {
    background: "linear-gradient(135deg, #1696ff 0%, #0f3460 100%)",
    color: "white",
  },
  th: {
    padding: "12px",
    textAlign: "left",
    fontWeight: "bold",
  },
  tableRow: {
    borderBottom: "1px solid #e0e0e0",
    transition: "all 0.3s ease",
  },
  td: {
    padding: "12px",
    textAlign: "left",
    color: "#0a1e2e",
  },
  actionBtn: {
    padding: "6px 12px",
    background: "linear-gradient(135deg, #1696ff 0%, #0f3460 100%)",
    color: "white",
    border: "none",
    borderRadius: "4px",
    cursor: "pointer",
    fontSize: "12px",
    fontWeight: "bold",
    transition: "all 0.3s ease",
    boxShadow: "0 2px 8px rgba(22, 150, 255, 0.3)",
    position: "relative",
    overflow: "hidden",
  },
  disabledActionBtn: {
    padding: "6px 12px",
    background: "#9e9e9e",
    color: "white",
    border: "none",
    borderRadius: "4px",
    cursor: "not-allowed",
    fontSize: "12px",
    fontWeight: "bold",
    boxShadow: "none",
  },
  buttonRow: {
    display: "flex",
    gap: "10px",
    marginTop: "20px",
  },
  activeCaseNote: {
    marginTop: "12px",
    color: "#d32f2f",
    fontSize: "13px",
    fontWeight: "600",
  },
  secondaryBtn: {
    flex: 1,
    padding: "10px 15px",
    background: "rgba(255, 255, 255, 0.9)",
    color: "#0a1e2e",
    border: "2px solid rgba(22, 150, 255, 0.3)",
    borderRadius: "6px",
    cursor: "pointer",
    fontSize: "14px",
    fontWeight: "bold",
    transition: "all 0.3s ease",
  },
  smallBtn: {
    padding: "4px 8px",
    background: "linear-gradient(135deg, #1696ff 0%, #0f3460 100%)",
    color: "white",
    border: "none",
    borderRadius: "4px",
    cursor: "pointer",
    fontSize: "11px",
    fontWeight: "bold",
    transition: "all 0.3s ease",
    boxShadow: "0 2px 6px rgba(22, 150, 255, 0.3)",
    animation: "buttonShimmer 3s ease-in-out infinite",
  },
  modalOverlay: {
    position: "fixed",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: "rgba(0,0,0,0.7)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 1000,
    animation: "fadeIn 0.3s ease-in",
  },
  modalContent: {
    backgroundColor: "rgba(255, 255, 255, 0.98)",
    borderRadius: "16px",
    padding: "30px",
    maxWidth: "600px",
    maxHeight: "80vh",
    overflowY: "auto",
    boxShadow: "0 20px 60px rgba(0,0,0,0.4)",
    border: "2px solid rgba(22, 150, 255, 0.3)",
    backdropFilter: "blur(10px)",
    animation: "slideUp 0.4s ease-out",
  },
  modalHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "20px",
    borderBottom: "2px solid rgba(22, 150, 255, 0.3)",
    paddingBottom: "15px",
  },
  closeBtn: {
    backgroundColor: "transparent",
    border: "none",
    fontSize: "24px",
    cursor: "pointer",
    color: "#999",
    transition: "all 0.3s ease",
  },
  transactionsList: {
    display: "flex",
    flexDirection: "column",
    gap: "15px",
  },
  transactionCard: {
    backgroundColor: "rgba(245, 245, 245, 0.8)",
    padding: "15px",
    borderRadius: "8px",
    border: "1px solid rgba(22, 150, 255, 0.2)",
    boxShadow: "0 2px 8px rgba(22, 150, 255, 0.1)",
    animation: "fadeIn 0.4s ease-in",
    transition: "all 0.3s ease",
  },
  txnRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "8px",
    fontSize: "14px",
  },
  txnLabel: {
    fontWeight: "bold",
    color: "#1696ff",
    minWidth: "120px",
  },
};

export default Dashboard;
