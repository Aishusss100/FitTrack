import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import './TitleBars.css';

function TitleBarHome() {
    const navigate = useNavigate();

    const handleLogout = () => {
        navigate('/login');
    };

    const goToProfile = () => {
        navigate('/profile'); // Navigate to the Profile page
    };

    return (
        <header className="TitleBar">
            <h1>FitTrack</h1>
            <div className="button-group">
                <button className="profile-button" onClick={goToProfile}>Profile</button>
                <button className="logout-button" onClick={handleLogout}>Logout</button>
            </div>
        </header>
    );
}

function TitleBarExercise() {
    const navigate = useNavigate();

    const handleLogout = () => {
        navigate('/login');
    };

    const goToHome = () => {
        navigate('/home'); // Navigate to the Home page
    };

    return (
        <header className="TitleBar">
            <h1>FitTrack</h1>
            <div className="button-group">
                <button className="home-button" onClick={goToHome}>Home</button>
                <button className="logout-button" onClick={handleLogout}>Logout</button>
            </div>
        </header>
    );
}

function TitleBarProfile() {
    const navigate = useNavigate();

    const handleLogout = () => {
        navigate('/login');
    };

    const goToHome = () => {
        navigate('/home'); // Navigate back to Home page
    };

    return (
        <header className="TitleBar">
            <h1>Profile</h1>
            <div className="button-group">
                <button className="home-button" onClick={goToHome}>Home</button>
                <button className="logout-button" onClick={handleLogout}>Logout</button>
            </div>
        </header>
    );
}

function TitleBarLogin() {
    return <header className="TitleBar"><h1>FitTrack</h1></header>;
}

function TitleBars() {
    const location = useLocation();
    const pathname = location.pathname;

    if (pathname === '/home') {
        return <TitleBarHome />;
    } else if (pathname.startsWith('/exercise')) {
        return <TitleBarExercise />;
    } else if (pathname === '/profile') {
        return <TitleBarProfile />;
    } else if (pathname === '/login') {
        return <TitleBarLogin />;
    } else {
        return null; // No title bar for signup and any other routes
    }
}

export default TitleBars;
