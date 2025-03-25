import React, { useState } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import "./Exercise.css";

const Exercise = () => {
    const { exercise } = useParams();
    const DEFAULT_BACKGROUND_COLOR = "#fff";
    const TARGET_SET_COLOR = "#d1f4e8";

    const [targetReps, setTargetReps] = useState(0);
    const [tracking, setTracking] = useState(false);
    const [backgroundColor, setBackgroundColor] = useState(DEFAULT_BACKGROUND_COLOR);
    const [errorMessage, setErrorMessage] = useState("");
    const [loading, setLoading] = useState(false);

    const API_LOCAL = "http://localhost:5000/api/";
    const API_NETWORK = "http://192.168.126.149:5000/api/";

    const formatExerciseTitle = (exercise) => 
        exercise.replace(/_/g, " ").replace(/(^\w|\s\w)/g, (m) => m.toUpperCase());

    const sendRequest = async (endpoint, payload) => {
        setLoading(true);
        try {
            let response = await axios.post(`${API_LOCAL}${endpoint}`, payload);
            return response.data;
        } catch (error) {
            console.error("Local API failed, trying Network API...");
            try {
                let response = await axios.post(`${API_NETWORK}${endpoint}`, payload);
                return response.data;
            } catch (error) {
                console.error("Network API failed.");
                setErrorMessage("Failed to connect to server. Please try again.");
                return null;
            }
        } finally {
            setLoading(false);
        }
    };

    const handleSetTarget = async () => {
        if (targetReps <= 0) {
            setErrorMessage("Please enter a valid number of target repetitions.");
            return;
        }

        const success = await sendRequest("set_target", { target_reps: targetReps, exercise });
        if (success) {
            setBackgroundColor(TARGET_SET_COLOR);
            setErrorMessage("");
        }
    };

    const handleStart = async () => {
        const success = await sendRequest("start", { exercise });
        if (success) setTracking(true);
    };

    const handleStop = async () => {
        if (!window.confirm("Are you sure you want to stop this exercise?")) return;

        const success = await sendRequest("stop", { exercise });
        if (success) {
            setTracking(false);
            setBackgroundColor(DEFAULT_BACKGROUND_COLOR);
            window.location.reload();
        }
    };

    return (
        <div className="exercise-container" style={{ backgroundColor }}>
            <h1>{formatExerciseTitle(exercise)} Exercise</h1>

            <div className="instructions">
                <h2>Instructions</h2>
                <p>1. Ensure you have enough space around you to perform the exercise safely.</p>
                <p>2. Stand about 1 meter away from the camera for better visibility.</p>
                <p>3. Ensure there is sufficient lighting in the room.</p>
                <p>4. Wear comfortable clothing that allows you to move freely.</p>
            </div>

            <div className="target-input">
                <label>Set Target Reps:</label>
                <input
                    type="number"
                    value={targetReps}
                    onChange={(e) => setTargetReps(parseInt(e.target.value) || 0)}
                />
                <button onClick={handleSetTarget} disabled={loading}>
                    {loading ? "Setting..." : "Set Target"}
                </button>
            </div>

            {errorMessage && <div className="error-message">{errorMessage}</div>}

            <div className="buttons">
                <button onClick={handleStart} disabled={tracking || loading}>
                    {tracking ? "Tracking..." : "Start"}
                </button>
                <button onClick={handleStop} disabled={!tracking || loading}>
                    Stop
                </button>
            </div>

            {tracking && (
                <div className="video-feed">
                    <h2>Video Feed</h2>
                    <img src={`http://localhost:5000/api/video_feed?exercise=${exercise}`} alt="Video Feed" />
                </div>
            )}
        </div>
    );
};

export default Exercise;
