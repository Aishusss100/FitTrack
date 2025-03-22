import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import axios from "axios";
import "./TitleBars.css";

// Home Title Bar with Streak Display
function TitleBarHome({ toggleSidebar }) {
  const navigate = useNavigate();
  const [streak, setStreak] = useState(0); // State to store streak count

  useEffect(() => {
    // Fetch streak count from the backend
    const fetchStreak = async () => {
      try {
        const response = await axios.get("http://localhost:5000/api/get_streak", {
          withCredentials: true, // Include session credentials
        });
        setStreak(response.data.streak); // Update streak count
      } catch (error) {
        console.error("Error fetching streak:", error);
      }
    };

    fetchStreak();
  }, []);

  const handleLogout = () => navigate("/login");
  const goToProfile = () => navigate("/profile");

  return (
    <header className="TitleBar">
      <button className="sidebar-button" onClick={toggleSidebar}>☰</button>
      <h1>FitTrack</h1>
      <div className="button-group">
        <button className="profile-button" onClick={goToProfile}>
          <i className="fas fa-user"></i> Profile
        </button>
        {streak > 0 && (
          <div className="streak-display">
            <span className="streak-icon">🔥</span>
            <span className="streak-count">{streak}</span>
          </div>
        )}
        <button className="logout-button" onClick={handleLogout}>Logout</button>
      </div>
    </header>
  );
}


// Exercise Title Bar
function TitleBarExercise({ toggleSidebar }) {
  const navigate = useNavigate();

  const handleLogout = () => navigate("/login");
  const goToHome = () => navigate("/home");

  return (
    <header className="TitleBar">
      <button className="sidebar-button" onClick={toggleSidebar}>☰</button>
      <h1>FitTrack</h1>
      <div className="button-group">
        <button className="home-button" onClick={goToHome}>Home</button>
        <button className="logout-button" onClick={handleLogout}>Logout</button>
      </div>
    </header>
  );
}

// Profile Title Bar
function TitleBarProfile({ toggleSidebar }) {
  const navigate = useNavigate();

  const handleLogout = () => navigate("/login");
  const goToHome = () => navigate("/home");

  return (
    <header className="TitleBar">
      <button className="sidebar-button" onClick={toggleSidebar}>☰</button>
      <h1>Profile</h1>
      <div className="button-group">
        <button className="home-button" onClick={goToHome}>Home</button>
        <button className="logout-button" onClick={handleLogout}>Logout</button>
      </div>
    </header>
  );
}

// Progress Title Bar
function TitleBarProgress({ toggleSidebar }) {
  const navigate = useNavigate();

  const handleLogout = () => navigate("/login");
  const goToHome = () => navigate("/home");

  return (
    <header className="TitleBar">
      <button className="sidebar-button" onClick={toggleSidebar}>☰</button>
      <h1>Progress</h1>
      <div className="button-group">
        <button className="home-button" onClick={goToHome}>Home</button>
        <button className="logout-button" onClick={handleLogout}>Logout</button>
      </div>
    </header>
  );
}

// Login Title Bar
function TitleBarLogin() {
  return (
    <header className="TitleBar">
      <h1>FitTrack</h1>
    </header>
  );
}

// Main TitleBars Component (Router-based)
function TitleBars({ toggleSidebar }) {
  const location = useLocation();
  const pathname = location.pathname;

  switch (true) {
    case pathname === "/home":
      return <TitleBarHome toggleSidebar={toggleSidebar} />;
    case pathname.startsWith("/exercise"):
      return <TitleBarExercise toggleSidebar={toggleSidebar} />;
    case pathname === "/profile":
      return <TitleBarProfile toggleSidebar={toggleSidebar} />;
    case pathname === "/progress":
      return <TitleBarProgress toggleSidebar={toggleSidebar} />;
    case pathname === "/login":
      return <TitleBarLogin />;
    default:
      return null;
  }
}

export default TitleBars;
