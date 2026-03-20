import React from "react";
import Navbar from "../components/Navbar";
import "../styles/advisor.css";

const Advisor = () => {
  const advisoryTopics = [
    {
      id: 1,
      icon: "🔒",
      title: "Why Does a Bank Freeze an Account?",
      color: "blue",
      items: [
        "Suspicious or unusual transactions",
        "Cyber fraud complaints",
        "KYC not updated",
        "High-risk transaction behavior",
      ],
    },
    {
      id: 2,
      icon: "💳",
      title: "What To Do If Your Debit Card Is Frozen?",
      color: "purple",
      items: [
        "Do not panic – this is a safety measure",
        "Visit your bank branch",
        "Complete KYC re-verification",
        "Cooperate with bank officials",
      ],
    },
    {
      id: 3,
      icon: "🛡️",
      title: "Fraud Prevention Tips",
      color: "green",
      items: [
        "Never share OTP or PIN",
        "Verify UPI collect requests",
        "Avoid unknown links and calls",
        "Report suspicious activity immediately",
      ],
    },
  ];

  return (
    <>
      <Navbar isAdmin={false} />

      <div className="advisor-container">
        <div className="advisor-header">
          <div className="header-content">
            <h1>Customer Advisor</h1>
            <p className="header-subtitle">Awareness & Guidance for Safe Banking</p>
            <div className="header-divider"></div>
          </div>
        </div>

        <div className="advisor-content">
          {advisoryTopics.map((topic) => (
            <div key={topic.id} className={`advisor-card advisor-card-${topic.color}`}>
              <div className="card-header">
                <span className="card-icon">{topic.icon}</span>
                <h2>{topic.title}</h2>
              </div>
              <ul className="card-list">
                {topic.items.map((item, index) => (
                  <li key={index} className="list-item">
                    <span className="list-bullet">✓</span>
                    <span className="list-text">{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}

          <div className="advisor-card advisor-card-highlight">
            <div className="card-header">
              <span className="card-icon">🚨</span>
              <h2>Cyber Cell Awareness</h2>
            </div>
            <div className="highlight-content">
              <p className="highlight-message">
                <span className="safe-badge">SAFE</span>
                Contacting the cyber cell is safe. You will not be humiliated or treated as a criminal.
              </p>
              <p className="highlight-message">
                <span className="support-badge">SUPPORT</span>
                Even if fraudulent transactions occurred unknowingly, cyber cell teams focus on resolution, not punishment.
              </p>
              <div className="trust-indicators">
                <div className="trust-item">
                  <span className="trust-icon">✓</span>
                  <span>Confidential & Professional</span>
                </div>
                <div className="trust-item">
                  <span className="trust-icon">✓</span>
                  <span>Legal Protection</span>
                </div>
                <div className="trust-item">
                  <span className="trust-icon">✓</span>
                  <span>Quick Resolution</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="quick-help">
          <h3>❓ Quick Help</h3>
          <div className="help-grid">
            <div className="help-item">
              <p className="help-title">Emergency?</p>
              <p className="help-text">Contact your bank immediately</p>
            </div>
            <div className="help-item">
              <p className="help-title">Not Sure?</p>
              <p className="help-text">Verify through official channels</p>
            </div>
            <div className="help-item">
              <p className="help-title">Suspicious Activity?</p>
              <p className="help-text">Report to cyber cell ASAP</p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Advisor;
