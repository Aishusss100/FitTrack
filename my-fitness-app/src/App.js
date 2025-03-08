import React from 'react';
import { BrowserRouter as Router, Route, Routes, useLocation } from 'react-router-dom';
import Login from './components/Login';
import NewSignup from './components/NewSignup'; // Import the Signup component
import Home from './components/Home';
import Exercise from './components/Exercise';
import TitleBars from './components/TitleBars'; // Import the combined TitleBars component
import SplashScreen from './components/SplashScreen'; // Import the SplashScreen component
import Profile from './components/Profile'; // Import the new Profile component
import TidioChat from './components/TidioChat'; // Import TidioChat component
import './App.css';

function App() {
    // Access the current location
    const location = useLocation();

    // Check if the current route is '/home' or '/exercise' (ensures chatbox is not on other pages)
    const showTidioChat = location.pathname === '/home' || location.pathname.startsWith('/exercise');

    return (
        <div className="App">
            {/* Conditionally render the TidioChat for Home and Exercise pages */}
            {showTidioChat && <TidioChat />}
            <Routes>
                <Route path="/splash" element={<SplashScreen />} />
                <Route path="/login" element={<><TitleBars /><Login /></>} />
                <Route path="/signup" element={<NewSignup />} /> {/* No title bar for Signup */}
                <Route path="/home" element={<><TitleBars /><Home /></>} />
                <Route path="/exercise/:exercise" element={<><TitleBars /><Exercise /></>} />
                <Route path="/profile" element={<><TitleBars /><Profile /></>} /> {/* Added Profile route */}
                <Route path="/" element={<SplashScreen />} />
            </Routes>
        </div>
    );
}

// Wrap the App with Router for proper routing context
function WrappedApp() {
    return (
        <Router>
            <App />
        </Router>
    );
}

export default WrappedApp;
