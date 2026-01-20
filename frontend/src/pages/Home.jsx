import React from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import "../styles/home.css";

const Home = () => {
  const navigate = useNavigate();

  return (
    <>
      <Navbar isAdmin={false} />

      <div className="home-hero">
        <h1 className="home-title">AI-Driven Fraud Prediction System</h1>
        <p className="home-subtitle">
          Secure banking with intelligent transaction risk analysis
        </p>

        <div className="home-actions">
          <button className="btn-primary" onClick={() => navigate("/login")}>
            Admin Login
          </button>
          <button className="btn-secondary" onClick={() => navigate("/advisor")}>
            Customer Advisor
          </button>
        </div>
      </div>
    </>
  );
};

export default Home;