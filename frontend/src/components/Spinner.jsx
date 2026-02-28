import React from "react";
import "../styles/spinner.css";

const Spinner = ({ message = "Loading..." }) => {
  return (
    <div className="spinner-overlay">
      <div className="spinner-container">
        <div className="spinner"></div>
        <p className="spinner-text">{message}</p>
      </div>
    </div>
  );
};

export default Spinner;
