import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import "../styles/login.css";

const Login = () => {
  const navigate = useNavigate();
  const [adminId, setAdminId] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = (e) => {
    e.preventDefault();

    if (!adminId || !password) {
      setError("Both Admin ID and Password are required.");
      return;
    }

    // Demo credentials
    if (adminId === "admin" && password === "Password@123") {
      localStorage.setItem("isAdminLoggedIn", "true");
      setError("");
      navigate("/dashboard", { replace: true });
    } else {
      setError("Invalid credentials. Access denied.");
    }
  };

  return (
    <>
      <Navbar isAdmin={false} />

      <div className="login-wrapper">
        <form className="login-card" onSubmit={handleLogin}>
          <h2 className="login-title">Bank Admin Login</h2>
          <p className="login-subtitle">Authorized personnel only</p>

          {error && <div className="login-error">{error}</div>}

          <input
            className="login-input"
            type="text"
            placeholder="Admin ID"
            value={adminId}
            onChange={(e) => setAdminId(e.target.value)}
          />

          <input
            className="login-input"
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <button className="login-btn" type="submit">
            Login
          </button>

          <p style={{ textAlign: "center", fontSize: "12px", marginTop: "10px", color: "#666" }}>
            Demo: <b>admin / Password@123</b>
          </p>
        </form>
      </div>
    </>
  );
};

export default Login;
