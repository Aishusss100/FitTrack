import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import "./Exercise.css";

// Import exercise GIFs
import bicepCurlRightGif from "../assets/One-Arm-Biceps-Curl-right.gif";
import bicepCurlLeftGif from "../assets/One-Arm-Biceps-Curl-left.gif";
import lateralRaiseRightGif from "../assets/lateral raise right.gif";
import lateralRaiseLeftGif from "../assets/lateral raise left.gif";
import frontRaiseRightGif from "../assets/how-to-do-dumbbell-front-raise.gif";
import overheadPressRightGif from "../assets/overhead press right.gif"; 
import singleArmDumbbellGif from "../assets/single arm dumbell.gif"
const Exercise = () => {
    const { exercise } = useParams();
    const COLORS = {
        DEFAULT: "default",
        TARGET_SET: "target-set",
        TRACKING: "tracking"
    };

    const [targetReps, setTargetReps] = useState("");
    const [tracking, setTracking] = useState(false);
    const [containerState, setContainerState] = useState(COLORS.DEFAULT);
    const [errorMessage, setErrorMessage] = useState("");
    const [elapsedTime, setElapsedTime] = useState(0);
    const [timerId, setTimerId] = useState(null);

    // Function to get the appropriate GIF based on exercise type
    const getExerciseGif = () => {
        switch (exercise) {
            case "bicep_curl_right":
                return bicepCurlRightGif;
            case "bicep_curl_left":
                return bicepCurlLeftGif;
            case "lateral_raise_right":
                return lateralRaiseRightGif;
            case "lateral_raise_left":
                return lateralRaiseLeftGif;
            case "front_raise_right":
                return frontRaiseRightGif;
            case "front_raise_left":
                return frontRaiseRightGif; // Use right GIF and mirror it
            case "overhead_press_right":
                return overheadPressRightGif;
            case "overhead_press_left":
                return overheadPressRightGif; // Use right GIF and mirror it
            case "single_arm_dumbbell_right":
                return singleArmDumbbellGif; // Mirror for right
            case "single_arm_dumbbell_left":
                return singleArmDumbbellGif; // Original for left
                
            default:
                return null;
        }
    };

    const formatExerciseTitle = (exercise) => {
        return exercise.replace(/_/g, " ").replace(/(^\w|\s\w)/g, (m) => m.toUpperCase());
    };

    const handleSetTarget = async () => {
        const reps = parseInt(targetReps);
        if (reps <= 0 && targetReps !== "") {
            setErrorMessage("Please enter a valid number of target repetitions.");
            return;
        }
        
        try {
            await axios.post(
                "http://localhost:5000/api/set_target",
                {
                    target_reps: reps || 0,
                    exercise,
                },
                { withCredentials: true }
            );
            setContainerState(COLORS.TARGET_SET);
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
            setContainerState(COLORS.TRACKING);

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
                    reps: parseInt(targetReps) || 0,
                },
                { withCredentials: true }
            );
            setTracking(false);
            clearInterval(timerId);
            setTimerId(null);
            setContainerState(COLORS.DEFAULT);
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

    // Determine if we should show the exercise GIF
    const exerciseGif = getExerciseGif();

    return (
        <div className={`exercise-container ${containerState}`}>
            <div className="exercise-grid">
                <div className="exercise-left-column">
                    <h1>{formatExerciseTitle(exercise)} Exercise</h1>
                    <div className="instructions">
                        <h2>Instructions</h2>
                        <p>1. Ensure you have enough space around you to perform the exercise safely.</p>
                        <p>2. Stand about 1 meter away from the camera for better visibility.</p>
                        <p>3. Ensure there is sufficient lighting in the room.</p>
                        <p>4. Wear comfortable clothing that allows you to move freely.</p>
                    </div>
                    
                    {/* Display the exercise GIF if available */}
                    {exerciseGif && (
                        <div className="exercise-demo">
                            <h2>Exercise Demonstration</h2>
                            <img 
                                src={exerciseGif} 
                                alt={`${formatExerciseTitle(exercise)} demonstration`} 
                                className={`exercise-gif 
                                    ${["lateral_raise_left", "lateral_raise_right", "front_raise_left", "front_raise_right", "overhead_press_left", "overhead_press_right","single_arm_dumbbell_left","single_arm_dumbbell_right"].includes(exercise) ? "lateral-raise" : ""} 
                                    ${["front_raise_left", "overhead_press_left","single_arm_dumbbell_right"].includes(exercise) ? "mirrored" : ""}`
                                }
                            />
                        </div>
                    )}
                </div>

                <div className="exercise-right-column">
                    <div className="target-input">
                        <label>Target Reps (Optional):</label>
                        <input
                            type="text"
                            value={targetReps}
                            onChange={(e) => {
                                const value = e.target.value;
                                setTargetReps(value === '' ? '' : parseInt(value) || '');
                            }}
                            placeholder="Enter reps (optional)"
                        />
                        <button onClick={handleSetTarget}>Set Target</button>
                    </div>

                    {errorMessage && <div className="error-message">{errorMessage}</div>}

                    <div className="buttons">
                        <button onClick={handleStart} disabled={tracking}>Start</button>
                        <button onClick={handleStop} disabled={!tracking}>Stop</button>
                    </div>

                    <div className="stopwatch">
                        <h2>Time: {formatTime(elapsedTime)}</h2>
                    </div>

                    {tracking && (
                        <div className="video-and-angle">
                            <div className="video-feed">
                                <h2>Video Feed</h2>
                                <img src={`http://localhost:5000/api/video_feed?exercise=${exercise}`} alt="Video Feed" />
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Exercise;
