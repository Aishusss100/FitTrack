import React, { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import "./Sidebar.css";

const Sidebar = ({ onClose }) => {
  const [username, setUsername] = useState(""); // State to hold the username
  const [error, setError] = useState(null); // State to handle any errors

  // Fetch username from the backend
  useEffect(() => {
    const fetchUsername = async () => {
      try {
        const response = await fetch("http://localhost:5000/api/get_username", {
          method: "GET",
          credentials: "include", // Include cookies for session
        });

        if (!response.ok) {
          throw new Error("Failed to fetch username");
        }

        const data = await response.json();
        setUsername(data.username); // Update username state
      } catch (err) {
        console.error(err);
        setError("User not logged in"); // Set error message if any
      }
    };

    fetchUsername();
  }, []); // Run only on component mount

  return (
    <div className="sidebar">
      {/* Sidebar Header */}
      <div className="sidebar-header">
        <h2 className="username">{error || username}</h2> {/* Display username or error */}
        <button className="sidebar-button back-button" onClick={onClose}>
          ← {/* Back arrow */}
        </button>
      </div>
      {/* Sidebar Navigation */}
      <nav className="sidebar-nav">
        <NavLink
          to="/home"
          className={({ isActive }) => (isActive ? "sidebar-link active" : "sidebar-link")}
          onClick={onClose}
        >
          Home
        </NavLink>
        <NavLink
          to="/profile"
          className={({ isActive }) => (isActive ? "sidebar-link active" : "sidebar-link")}
          onClick={onClose}
        >
          Profile
        </NavLink>
        <NavLink
          to="/progress"
          className={({ isActive }) => (isActive ? "sidebar-link active" : "sidebar-link")}
          onClick={onClose}
        >
          Progress
        </NavLink>
        <NavLink
          to="/goals"
          className={({ isActive }) => (isActive ? "sidebar-link active" : "sidebar-link")} // New Goal Tracker link
          onClick={onClose}
        >
          Goal Tracker
        </NavLink>
        <NavLink
          to="/feedback"
          className={({ isActive }) => (isActive ? "sidebar-link active" : "sidebar-link")}
          onClick={onClose}
        >
          Feedback
        </NavLink>
      </nav>
    </div>
  );
};

export default Sidebar;
