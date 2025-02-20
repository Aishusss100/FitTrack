// components/SplashScreen.js
import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './SplashScreen.css';
import backgroundImage from '../assets/dumbbell.png';

function SplashScreen() {
    const navigate = useNavigate();

    useEffect(() => {
        setTimeout(() => {
            navigate('/login');
        }, 3000); // Adjust the duration as needed
    }, [navigate]);

    return (
        <div className="SplashScreen" style={{ backgroundImage: `url(${backgroundImage})` }}>
            <div className="SplashShape">
                <h1>FitTrack</h1> {/* Replace 'FitTrack' with your chosen app name */}
            </div>
        </div>
    );
}

export default SplashScreen;
