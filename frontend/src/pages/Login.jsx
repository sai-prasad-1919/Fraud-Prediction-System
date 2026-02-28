import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import { adminLogin } from "../api/adminAuth";
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

    adminLogin(adminId, password)
      .then((res) => {
        localStorage.setItem("admin_token", res.data.access_token);
        localStorage.setItem("isAdminLoggedIn", "true");
        localStorage.setItem("adminId", adminId); // Store adminId for case creation
        navigate("/dashboard");
      })
      .catch(() => {
        setError("Invalid credentials");
      });
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
        </form>
      </div>
    </>
  );
};

export default Login;
