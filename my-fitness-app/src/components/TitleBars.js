// components/TitleBars.js
import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import './TitleBars.css';

function TitleBarHome() {
    const navigate = useNavigate();
    const handleLogout = () => {
        navigate('/login');
    };

    return (
        <header className="TitleBar">
            <h1>FitTrack</h1>
            <button className="logout-button" onClick={handleLogout}>Logout</button>
        </header>
    );
}

function TitleBarExercise() {
    const navigate = useNavigate();
    const handleLogout = () => {
        navigate('/login');
    };

    return (
        <header className="TitleBar">
            <h1>FitTrack</h1>
            <button className="logout-button" onClick={handleLogout}>Logout</button>
        </header>
    );
}

function TitleBarLogin() {
    return <header className="TitleBar"> <h1>FitTrack</h1> </header>;
}

function TitleBars() {
    const location = useLocation();
    const pathname = location.pathname;

    if (pathname === '/home') {
        return <TitleBarHome />;
    } else if (pathname.startsWith('/exercise')) {
        return <TitleBarExercise />;
    } else if (pathname === '/login') {
        return <TitleBarLogin />;
    } else {
        return null; // No title bar for signup and any other routes
    }
}

export default TitleBars;
