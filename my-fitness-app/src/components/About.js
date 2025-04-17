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
                    FitTrack is an AI and ML-powered web app that helps users maintain perfect posture during exercises using just their phone camera. It provides instant voice feedback, counts reps, and tracks your progress – just like a personal trainer!
                </p>
            </div>

            <div className="info-box">
                <h2>🌟 Key Features</h2>
                <ul>
                    <li>📹 Real-time camera-based posture tracking</li>
                    <li>🔊 Voice feedback to correct posture instantly</li>
                    <li>📈 Repetition counter and time tracker</li>
                    <li>🤖 AI-based pose estimation using MediaPipe & OpenCV</li>
                    <li>📊 Goal progress and history tracking</li>
                    <li>🗂️ Lightweight and sensor-free usage</li>
                </ul>
            </div>

            <div className="info-box">
                <h2>🛠️ Tech Stack</h2>
                <ul>
                    <li>⚛️ React (Frontend)</li>
                    <li>🐍 Flask (Backend)</li>
                    <li>🎯 MediaPipe + OpenCV (AI Pose Estimation)</li>
                    <li>🗄️ SQLite (Database)</li>
                    <li>🎨 Custom CSS </li>
                </ul>
            </div>

            <div className="info-box">
                <h2>🎯 Our Vision</h2>
                <p>
                    Our goal is to make fitness simple, smart, and accessible for everyone — no wearables or gym required. FitTrack gives users real-time feedback to improve form, and stay consistent.
                </p>
            </div>

            <div className="info-box">
                <h2>👩‍💻 Developers</h2>
                <p>
                    This project is developed by a passionate team of Computer Science students:
                </p>
                <ul>
                    <li><strong>Aishwarya S</strong></li>
                    <li><strong>Nayana Shamji</strong></li>
                    <li><strong>Sreehari Saji</strong></li>
                    <li><strong>Vaishnavi Rajesh</strong></li>
                </ul>
                <p>
                    We built FitTrack to combine our interests in AI, fitness, and impactful tech solutions.
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
