import React, { useState,  useRef } from "react";
import { Link } from "react-router-dom";
import "./Home.css"; // Ensure CSS includes the animation styles
import axios from "axios";

const Home = () => {
    const [caloriesBurned, setCaloriesBurned] = useState(null); // Current calories
    const [totalReps, setTotalReps] = useState(null); // Total reps
    const [totalDuration, setTotalDuration] = useState(null); // Total duration
    const [showModal, setShowModal] = useState(false); // Modal visibility
    const [isLoading, setIsLoading] = useState(false); // Loading state
    const [isShaking, setIsShaking] = useState(false); // Shake state for button
    const previousCalories = useRef(0); // Track the previous calories value

    // Fetch progress from the backend
    const fetchProgress = async () => {
        try {
            setIsLoading(true); // Show loading spinner
            console.log("Fetching progress data...");

            const response = await axios.get("http://localhost:5000/api/get_total_calories", {
                params: { view_type: "daily" },
                withCredentials: true,
            });

            console.log("API Response:", response.data);

            if (response.data) {
                const newCalories = response.data.calories_burned.toFixed(2);
                setCaloriesBurned(newCalories);
                setTotalReps(response.data.total_reps || 0);
                setTotalDuration(response.data.total_duration || 0);

                // Check for improvement
                if (newCalories > previousCalories.current) {
                    setIsShaking(true); // Enable shake animation
                    setTimeout(() => setIsShaking(false), 1000); // Stop shaking after 1 second
                }

                // Update previous calories
                previousCalories.current = newCalories;
            } else {
                console.error("Progress data missing in response:", response.data);
                setCaloriesBurned(0);
                setTotalReps(0);
                setTotalDuration(0);
            }
        } catch (error) {
            console.error("Error fetching progress:", error);
            setCaloriesBurned(0);
            setTotalReps(0);
            setTotalDuration(0);
        } finally {
            setIsLoading(false); // Hide loading spinner
        }
    };

    // Open the modal and fetch progress
    const openModal = () => {
        fetchProgress(); // Refresh data before showing the modal
        setShowModal(true);
    };

    // Close the modal
    const closeModal = () => setShowModal(false);

    const exercises = [
        { name: "Bicep Curl (Left)", route: "/exercise/bicep_curl_left", icon: "💪" },
        { name: "Bicep Curl (Right)", route: "/exercise/bicep_curl_right", icon: "💪" },
        { name: "Overhead Press (Left)", route: "/exercise/overhead_press_left", icon: "🏋️‍♂️" },
        { name: "Overhead Press (Right)", route: "/exercise/overhead_press_right", icon: "🏋️‍♂️" },
        { name: "Lateral Raise (Left)", route: "/exercise/lateral_raise_left", icon: "↔️" },
        { name: "Lateral Raise (Right)", route: "/exercise/lateral_raise_right", icon: "↔️" },
        { name: "Front Raise (Left)", route: "/exercise/front_raise_left", icon: "⬆️" },
        { name: "Front Raise (Right)", route: "/exercise/front_raise_right", icon: "⬆️" },
        { name: "Single Arm Dumbbell (Left)", route: "/exercise/single_arm_dumbbell_left", icon: "🎯" },
        { name: "Single Arm Dumbbell (Right)", route: "/exercise/single_arm_dumbbell_right", icon: "🎯" },
    ];

    return (
        <div className="home-container">
            <h2>Select Your Exercise</h2>
            <div className="exercise-selection">
                {exercises.map((exercise, index) => (
                    <Link to={exercise.route} key={index} className="exercise-tile">
                        <div className="icon">{exercise.icon}</div>
                        <div className="label">{exercise.name}</div>
                    </Link>
                ))}
            </div>

            {/* Floating Button */}
            <button
                className={`floating-round-button ${isShaking ? "shake" : ""}`}
                onClick={openModal}
            >
                🔥
            </button>

            {/* Modal for displaying progress */}
            {showModal && (
                <div className="modal-overlay" onClick={closeModal}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <h3>Daily Progress</h3>
                        {isLoading ? (
                            <p>Loading...</p>
                        ) : (
                            <div>
                                <p><strong>Calories Burned:</strong> {caloriesBurned} calories</p>
                                <p><strong>Total Reps:</strong> {totalReps}</p>
                                <p><strong>Total Duration:</strong> {Math.floor(totalDuration / 60)} minutes {totalDuration % 60} seconds</p>
                            </div>
                        )}
                        <button className="close-modal-button" onClick={closeModal}>
                            Close
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Home;
