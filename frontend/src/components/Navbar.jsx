import React from "react";
import { useNavigate } from "react-router-dom";
import "../styles/navbar.css";

const Navbar = ({ isAdmin }) => {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("isAdminLoggedIn");
    navigate("/login", { replace: true });
  };

  return (
  <div className="navbar">
    <div className="navbar-logo">🏦 Fraud Prediction System</div>

    <div className="navbar-actions">
      <button className="nav-btn" onClick={() => navigate("/")}>Home</button>
      <button className="nav-btn" onClick={() => navigate("/advisor")}>
        Customer Advisor
      </button>

      {isAdmin && (
        <button className="logout-btn" onClick={handleLogout}>
          Logout
        </button>
      )}
    </div>
  </div>
);
};

export default Navbar;