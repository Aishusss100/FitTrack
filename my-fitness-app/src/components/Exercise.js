import React, { useState } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import "./Exercise.css";

const Exercise = () => {
    const { exercise } = useParams();
    const DEFAULT_BACKGROUND_COLOR = "#fff";
    const TRACKING_BACKGROUND_COLOR = "#f5e1a4";
    const TARGET_SET_COLOR = "#d1f4e8";

    const [targetReps, setTargetReps] = useState(0);
    const [tracking, setTracking] = useState(false);
    const [backgroundColor, setBackgroundColor] = useState(DEFAULT_BACKGROUND_COLOR);
    const [errorMessage, setErrorMessage] = useState("");
    const [elapsedTime, setElapsedTime] = useState(0);
    const [timerId, setTimerId] = useState(null);

    const formatExerciseTitle = (exercise) => {
        return exercise.replace(/_/g, " ").replace(/(^\w|\s\w)/g, (m) => m.toUpperCase());
    };

    const handleSetTarget = async () => {
        if (targetReps <= 0) {
            setErrorMessage("Please enter a valid number of target repetitions.");
            return;
        }
        try {
            await axios.post(
                "http://localhost:5000/api/set_target",
                {
                    target_reps: targetReps,
                    exercise,
                },
                { withCredentials: true }
            );
            setBackgroundColor(TARGET_SET_COLOR);
            setErrorMessage("");
        } catch (error) {
            console.error(error);
            setErrorMessage("Failed to set target repetitions. Please try again.");
        }
    };

    const handleStart = async () => {
        try {
            await axios.post(
                "http://localhost:5000/api/start",
                { exercise },
                { withCredentials: true }
            );
            setTracking(true);
            setElapsedTime(0);
            setBackgroundColor(TRACKING_BACKGROUND_COLOR);

            const intervalId = setInterval(() => {
                setElapsedTime((prevTime) => prevTime + 1);
            }, 1000);

            setTimerId(intervalId);
        } catch (error) {
            console.error(error);
            setErrorMessage("Failed to start exercise tracking. Please try again.");
        }
    };

    const handleStop = async () => {
        if (!window.confirm("Are you sure you want to stop this exercise?")) return;

        try {
            await axios.post(
                "http://localhost:5000/api/stop",
                {
                    exercise_name: exercise,
                    duration: elapsedTime,
                    reps: targetReps || 0,
                },
                { withCredentials: true }
            );
            setTracking(false);
            clearInterval(timerId);
            setTimerId(null);
            setBackgroundColor(DEFAULT_BACKGROUND_COLOR);
            setElapsedTime(0);
            window.location.reload();
        } catch (error) {
            console.error(error);
            setErrorMessage("Failed to stop exercise tracking. Please try again.");
        }
    };

    const formatTime = (timeInSeconds) => {
        const minutes = Math.floor(timeInSeconds / 60);
        const seconds = timeInSeconds % 60;
        return `${minutes}:${seconds < 10 ? "0" : ""}${seconds}`;
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
                <button onClick={handleSetTarget}>Set Target</button>
            </div>

            {errorMessage && <div className="error-message">{errorMessage}</div>}

            <div className="buttons">
                <button onClick={handleStart} disabled={tracking}>
                    Start
                </button>
                <button onClick={handleStop} disabled={!tracking}>
                    Stop
                </button>
            </div>

            <div className="stopwatch">
                <h2>Time: {formatTime(elapsedTime)}</h2>
            </div>

            {tracking && (
                <div className="video-and-angle">
                    <div className="video-feed">
                        <h2>Video Feed</h2>
                        <img
                            src={`http://localhost:5000/api/video_feed?exercise=${exercise}`}
                            alt="Video Feed"
                        />
                    </div>
                </div>
            )}
        </div>
    );
};

export default Exercise;
