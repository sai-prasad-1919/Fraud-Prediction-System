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
        <h1 className="home-title">Fraud Prediction System</h1>
        <p className="home-subtitle">
          Secure banking with intelligent transaction  risk level analysis
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

      
      <div className="home-features">
        <h2>Why Choose Our System?</h2>
        <div className="features-grid">
          <div className="feature-card">
            <h3>Real-Time Fraud Detection</h3>
            <p>
              Transactions are analyzed instantly using machine learning models
              to detect suspicious activity before damage happens.
            </p>
          </div>

          <div className="feature-card">
            <h3>Risk Level Classification</h3>
            <p>
              Each user is assigned a Low, Medium, or High risk score
              based on recent transaction behavior.
            </p>
          </div>

          <div className="feature-card">
            <h3>Bank-Grade Security</h3>
            <p>
              All data is processed securely following banking-level
              security standards and best practices.
            </p>
          </div>
        </div>
      </div>
      <div className="home-how">

        <div className="home-users">
        <h2>Who Can Use This System?</h2>
        <div className="user-box">
          <ul>
            <p>
            <strong>Bank Administrators</strong> can monitor high-risk accounts,
            review suspicious transactions, and take preventive actions.
          </p>

          <p>
            <strong>Customer Advisors</strong> can guide customers with safety
            recommendations and fraud awareness tips.
          </p>

          <p>
            <strong>Customers</strong> can understand their transaction risk levels
            and stay protected from digital fraud.
          </p>
          </ul>
          
        </div>
      </div>


      <h2>How It Works</h2>
      <ol>
        <li>User transactions are collected from the system</li>
        <li>Machine learning model analyzes transaction patterns</li>
        <li>Risk score is generated for each user</li>
        <li>Admin reviews high-risk accounts and take the required action</li>
        
  </ol>
</div>

    </>
  );
};

export default Home;