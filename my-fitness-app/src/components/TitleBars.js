import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import axios from "axios";
import "./TitleBars.css";

// Tooltip Wrapper Component
const Tooltip = ({ children, text }) => {
  return (
    <div className="tooltip">
      {children}
      <span className="tooltiptext">{text}</span>
    </div>
  );
};

// Home Title Bar with Streak Display
function TitleBarHome({ toggleSidebar }) {
  const navigate = useNavigate();
  const [streak, setStreak] = useState(0); // State to store streak count
  const [pendingGoalsCount, setPendingGoalsCount] = useState(0); // State to store pending goals count

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

    // Fetch pending goals count from the backend
    const fetchPendingGoalsCount = async () => {
      try {
        const response = await axios.get("http://localhost:5000/api/get_pending_goals_count", {
          withCredentials: true, // Include session credentials
        });
        setPendingGoalsCount(response.data.pending_goals_count); // Update pending goals count
      } catch (error) {
        console.error("Error fetching pending goals count:", error);
      }
    };

    fetchStreak();
    fetchPendingGoalsCount();
  }, []);

  const handleLogout = () => navigate("/login");
  const goToProfile = () => navigate("/profile");
  const goToGoals = () => navigate("/goals");

  return (
    <header className="TitleBar">
      <button className="sidebar-button" onClick={toggleSidebar}>☰</button>
      <h1>FitTrack</h1>
      <div className="button-group">
        {streak > 0 && (
          <Tooltip text="Consecutive Days Active">
            <div className="streak-display">
              <span className="streak-icon">🔥</span>
              <span className="streak-count">{streak}</span>
            </div>
          </Tooltip>
        )}
        {pendingGoalsCount > 0 && (
          <Tooltip text="Uncompleted Goals">
            <div className="pending-goals-display" onClick={goToGoals}>
              <span className="pending-goals-icon">🎯</span>
              <span className="pending-goals-count">{pendingGoalsCount}</span>
            </div>
          </Tooltip>
        )}
        <button className="profile-button" onClick={goToProfile}>
          <i className="fas fa-user"></i> Profile
        </button>
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

// Goals Title Bar (NEW)
function TitleBarGoals({ toggleSidebar }) {
  const navigate = useNavigate();

  const handleLogout = () => navigate("/login");
  const goToHome = () => navigate("/home");

  return (
    <header className="TitleBar">
      <button className="sidebar-button" onClick={toggleSidebar}>☰</button>
      <h1>Goal Tracker</h1>
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
// Add this new About Title Bar
function TitleBarAbout({ toggleSidebar }) {
  const navigate = useNavigate();

  const handleLogout = () => navigate("/login");
  const goToHome = () => navigate("/home");

  return (
    <header className="TitleBar">
      <button className="sidebar-button" onClick={toggleSidebar}>☰</button>
      <h1>About</h1>
      <div className="button-group">
        <button className="home-button" onClick={goToHome}>Home</button>
        <button className="logout-button" onClick={handleLogout}>Logout</button>
      </div>
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
    case pathname === "/goals":
      return <TitleBarGoals toggleSidebar={toggleSidebar} />;
    case pathname === "/about":
      return <TitleBarAbout toggleSidebar={toggleSidebar} />;
    case pathname === "/login":
      return <TitleBarLogin />;
    default:
      return null;
  }
  
}

export default TitleBars;