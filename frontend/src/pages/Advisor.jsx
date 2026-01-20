import React from "react";
import Navbar from "../components/Navbar";
import "../styles/advisor.css";

const Advisor = () => {
  return (
    <>
      <Navbar isAdmin={false} />

      <div className="advisor-header">
        <h1>Customer Advisor</h1>
        <p>Awareness & Guidance for Safe Banking</p>
      </div>

      <div className="advisor-section">
        <h2>Why Does a Bank Freeze an Account?</h2>
        <ul>
          <li>Suspicious or unusual transactions</li>
          <li>Cyber fraud complaints</li>
          <li>KYC not updated</li>
          <li>High-risk transaction behavior</li>
        </ul>
      </div>

      <div className="advisor-section">
        <h2>What To Do If Your Debit Card Is Frozen?</h2>
        <ul>
          <li>Do not panic – this is a safety measure</li>
          <li>Visit your bank branch</li>
          <li>Complete KYC re-verification</li>
          <li>Cooperate with bank officials</li>
        </ul>
      </div>

      <div className="advisor-section advisor-highlight">
        <h2>Cyber Cell Awareness</h2>
        <p>
          Contacting the cyber cell is <b>safe</b>.  
          You will <b>not be humiliated</b> or treated as a criminal.
        </p>
        <p>
          Even if fraudulent transactions occurred unknowingly,  
          cyber cell teams focus on <b>resolution, not punishment</b>.
        </p>
      </div>

      <div className="advisor-section">
        <h2>Fraud Prevention Tips</h2>
        <ul>
          <li>Never share OTP or PIN</li>
          <li>Verify UPI collect requests</li>
          <li>Avoid unknown links and calls</li>
          <li>Report suspicious activity immediately</li>
        </ul>
      </div>
    </>
  );
};

export default Advisor;
