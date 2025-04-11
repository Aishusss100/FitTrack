import React, { useLayoutEffect } from "react";
import "./About.css";

const About = () => {
    useLayoutEffect(() => {
        window.scrollTo({ top: 0, behavior: "smooth" });
    }, []);

    return (
        <div className="about-page">
            <div className="hero-box">
                <h1>Welcome to <span>FitTrack</span></h1>
                <p>Your AI-powered fitness trainer in real time!</p>
            </div>

            <div className="info-box">
                <h2>🚀 What is FitTrack?</h2>
                <p>
                    FitTrack is an AI and ML-powered web app that helps users maintain perfect posture during exercises using camera-based pose detection. It gives instant voice feedback and counts reps with high accuracy.
                </p>
            </div>

            <div className="info-box">
                <h2>🌟 Features</h2>
                <ul>
                    <li>📹 Real-time camera-based posture tracking</li>
                    <li>🔊 Instant voice posture feedback</li>
                    <li>📈 Rep counter + time tracker</li>
                    <li>🤖 MediaPipe & OpenCV-based pose estimation</li>
                    <li>🎯 Goal tracking & progress dashboard</li>
                </ul>
            </div>

            <div className="info-box">
                <h2>🛠️ Tech Stack</h2>
                <ul>
                    <li>⚛️ React</li>
                    <li>🐍 Flask</li>
                    <li>🎯 MediaPipe + OpenCV</li>
                    <li>🗄️ SQLite</li>
                    <li>🎨 Custom CSS (Maroon-themed)</li>
                </ul>
            </div>

            <div className="info-box">
                <h2>👩‍💻 Developer</h2>
                <p>
                    I'm <strong>Aishwarya</strong>, a CSE student passionate about fitness and AI. FitTrack is my project to make posture correction easier and more accessible with just a camera and smart tracking.
                </p>
            </div>

            <div className="info-box contact-box">
                <h2>📬 Contact</h2>
                <p>Email: <a href="mailto:your.email@example.com">your.email@example.com</a></p>
                <p>LinkedIn: <a href="https://www.linkedin.com/" target="_blank" rel="noreferrer">Visit Profile</a></p>
            </div>

            <footer className="footer">
                <p>&copy; 2025 FitTrack. All rights reserved.</p>
            </footer>
        </div>
    );
};

export default About;
