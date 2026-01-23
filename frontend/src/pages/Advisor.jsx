import React from "react";
import Navbar from "../components/Navbar";
import "../styles/advisor.css";

const Advisor = () => {
  return (
    <>
      <Navbar isAdmin={false} />

      <div className="advisor-header">
        <h1>Customer Advisory</h1>
        <p>Safety Guidelines & Account Risk Information</p>
      </div>

      <div className="advisor-section">
        <h2>Why Can an Account Be Restricted?</h2>
        <ul>
          <li>Unusual or suspicious transaction activity</li>
          <li>Cyber fraud complaints or investigations</li>
          <li>KYC or re-verification pending</li>
          <li>Links to high-risk applications or sources</li>
        </ul>
      </div>

      <div className="advisor-section">
        <h2>Risk Classification</h2>
        <ul>
          <li>
            <b>High Risk:</b> Serious suspicious or fraudulent activity detected.
            Account may be fully frozen and verification is mandatory.
          </li>
          <li>
            <b>Medium Risk:</b> Unusual transactions observed. Debit transactions
            may be temporarily restricted until KYC is completed.
          </li>
          <li>
            <b>Low Risk:</b> Minor irregular patterns detected. Transactions
            continue under monitoring.
          </li>
        </ul>
      </div>

      <div className="advisor-section">
        <h2>KYC & Mobile Number Verification</h2>
        <p>
          KYC re-verification may be required by your <b>bank</b> or your{" "}
          <b>mobile service provider</b>. Understand that UPI issues are not
          always related only to bank KYC.
        </p>
        <p>
          If your bank KYC is updated and problems still continue, please visit
          your mobile network service center to complete SIM KYC verification.
        </p>
      </div>

      <div className="advisor-section advisor-highlight">
        <h2>What If Your Account Is Frozen?</h2>
        <ul>
          <li>Do not panic — this is a safety procedure</li>
          <li>Contact your bank branch for the exact reason</li>
          <li>If cyber cell is involved, call <b>1930</b> (India Cyber Crime Helpline)</li>
          <li>Follow the instructions provided for resolution</li>
        </ul>
        <p>
          Cyber crime teams focus on <b>problem resolution and protection</b>, not
          punishment, when customers are victims.
        </p>
      </div>

      <div className="advisor-section">
        <h2>Fraud Prevention Tips</h2>
        <ul>
          <li>Never share OTP, PIN, or card details</li>
          <li>Verify UPI collect requests before approving</li>
          <li>Avoid unknown links, apps, and calls</li>
          <li>Report suspicious activity immediately</li>
        </ul>
      </div>
    </>
  );
};

export default Advisor;
