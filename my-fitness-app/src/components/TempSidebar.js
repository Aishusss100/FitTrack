import React, { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import "./Sidebar.css";

const Sidebar = ({ onClose }) => {
  const [username, setUsername] = useState(""); 
  const [error, setError] = useState(null); 

  useEffect(() => {
    const fetchUsername = async () => {
      try {
        const response = await fetch("http://localhost:5000/api/get_username", {
          method: "GET",
          credentials: "include",
        });

        if (!response.ok) {
          throw new Error("Failed to fetch username");
        }

        const data = await response.json();
        setUsername(data.username);
      } catch (err) {
        console.error(err);
        setError("User not logged in");
      }
    };

    fetchUsername();
  }, []);

  return (
    <div className="sidebar">
      {/* Sidebar Header */}
      <div className="sidebar-header">
        <h2 className="username">{error || username}</h2>
        <button className="sidebar-button back-button" onClick={onClose}>
          ←
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
          className={({ isActive }) => (isActive ? "sidebar-link active" : "sidebar-link")}
          onClick={onClose}
        >
          Goal Tracker
        </NavLink>
        <NavLink
          to="/about"
          className={({ isActive }) => (isActive ? "sidebar-link active" : "sidebar-link")}
          onClick={onClose}
        >
          About
        </NavLink>
      </nav>
    </div>
  );
};

export default Sidebar;
