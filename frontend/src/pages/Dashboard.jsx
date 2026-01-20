import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import "../styles/dashboard.css";

const Dashboard = () => {
  const navigate = useNavigate();

  const [userId, setUserId] = useState("");
  const [risk, setRisk] = useState(null);

  // 🔐 HARD SECURITY CHECK (VERY IMPORTANT)
  useEffect(() => {
    const isAuth = localStorage.getItem("isAdminLoggedIn");

    if (isAuth !== "true") {
      navigate("/login", { replace: true });
    }
  }, [navigate]);

  const predict = () => {
    if (!userId) return alert("Enter User ID");

    setRisk({
      score: 82,
      level: "Level 3",
      action: "Debit Freeze & Cyber Cell Escalation",
    });
  };

  return (
    <>
      <Navbar isAdmin={true} />

      <div style={styles.container}>
        <div style={styles.card}>
          <h2>Risk Prediction</h2>

          <input
            style={styles.input}
            placeholder="Enter User ID"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
          />

          <button style={styles.button} onClick={predict}>
            Predict Risk
          </button>

          {risk && (
            <div style={styles.result}>
              <p><b>Risk Score:</b> {risk.score}/100</p>
              <p><b>Risk Level:</b> {risk.level}</p>
              <p><b>Recommended Action:</b></p>
              <p style={{ color: "#d32f2f", fontWeight: "bold" }}>
                {risk.action}
              </p>
            </div>
          )}
        </div>
      </div>
    </>
  );
};

const styles = {
  container: {
    backgroundColor: "#f4f6f9",
    minHeight: "100vh",
    padding: "40px",
  },
  card: {
    maxWidth: "500px",
    margin: "auto",
    backgroundColor: "white",
    padding: "30px",
    borderRadius: "12px",
    boxShadow: "0 6px 18px rgba(0,0,0,0.15)",
  },
  input: {
    width: "100%",
    padding: "12px",
    margin: "15px 0",
    borderRadius: "6px",
    border: "1px solid #ccc",
  },
  button: {
    width: "100%",
    padding: "12px",
    backgroundColor: "#0b3c5d",
    color: "white",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
  },
  result: {
    marginTop: "20px",
    padding: "15px",
    backgroundColor: "#fafafa",
    borderRadius: "8px",
  },
};

export default Dashboard;
