import React, { useState, useEffect } from "react";
import {
  BrowserRouter as Router,
  Route,
  Routes,
  useLocation,
  Navigate,
} from "react-router-dom";
import Login from "./components/Login";
import NewSignup from "./components/NewSignup";
import Home from "./components/Home";
import Exercise from "./components/Exercise";
import TitleBars from "./components/TitleBars";
import SplashScreen from "./components/SplashScreen";
import Profile from "./components/Profile";
import Sidebar from "./components/TempSidebar"; // Import Sidebar
import ProgressPage from "./components/ProgressPage"; // Import ProgressPage
import GoalTrackerPage from "./components/GoalTrackerPage"; // Import GoalTrackerPage
import "./App.css";

function App() {
  const location = useLocation();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [showSplash, setShowSplash] = useState(true); // State to show/hide splash screen

  // Determine when to show the TitleBar (not on Splash, Login, Signup)
  const showTitleBar = !["/splash", "/login", "/signup"].includes(
    location.pathname
  );

  // Sidebar toggle functionality
  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  // Splash screen logic: Auto-hide after 3 seconds
  useEffect(() => {
    const timer = setTimeout(() => setShowSplash(false), 3000); // Show splash for 3 seconds
    return () => clearTimeout(timer); // Cleanup the timer
  }, []);

  if (showSplash && location.pathname === "/splash") {
    return <SplashScreen />;
  }

  return (
    <div className="App">
      {/* TitleBar with Sidebar Button */}
      {showTitleBar && <TitleBars toggleSidebar={toggleSidebar} />}

      {/* Sidebar Component */}
      {isSidebarOpen && <Sidebar onClose={toggleSidebar} />}

      <Routes>
        <Route path="/splash" element={<SplashScreen />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<NewSignup />} />
        <Route path="/home" element={<Home />} />
        <Route path="/exercise/:exercise" element={<Exercise />} />
        <Route path="/progress" element={<ProgressPage />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/goals" element={<GoalTrackerPage />} /> {/* New Goal Tracker Route */}
        <Route path="/" element={<Navigate to="/splash" />} /> {/* Redirect "/" to Splash */}
      </Routes>
    </div>
  );
}

function WrappedApp() {
  return (
    <Router>
      <App />
    </Router>
  );
}

export default WrappedApp;
