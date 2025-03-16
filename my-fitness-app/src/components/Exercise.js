import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import './Exercise.css';

const Exercise = () => {
    const { exercise } = useParams();
    const DEFAULT_BACKGROUND_COLOR = '#fff'; // Default background color
    const TARGET_SET_COLOR = '#d1f4e8'; // Background color when target is set

    const [targetReps, setTargetReps] = useState(0);
    const [tracking, setTracking] = useState(false);
    const [backgroundColor, setBackgroundColor] = useState(DEFAULT_BACKGROUND_COLOR);
    const [errorMessage, setErrorMessage] = useState('');

    // Format exercise title for better readability
    const formatExerciseTitle = (exercise) => {
        return exercise.replace(/_/g, ' ').replace(/(^\w|\s\w)/g, m => m.toUpperCase());
    };

    const handleSetTarget = async () => {
        if (targetReps <= 0) {
            setErrorMessage('Please enter a valid number of target repetitions.');
            return;
        }
        try {
            const response = await axios.post('http://localhost:5000/api/set_target', {
                target_reps: targetReps,
                exercise: exercise // Include exercise in the payload
            });
            console.log(response.data);
            setBackgroundColor(TARGET_SET_COLOR); // Change background color when target is set
            setErrorMessage(''); // Clear any previous error
        } catch (error) {
            console.error(error);
            setErrorMessage('Failed to set target repetitions. Please try again.');
        }
    };

    const handleStart = async () => {
        try {
            const response = await axios.post('http://localhost:5000/api/start', { exercise });
            console.log(response.data);
            setTracking(true); // Ensure tracking is set to true after the start API call
        } catch (error) {
            console.error(error);
            setErrorMessage('Failed to start exercise tracking. Please try again.');
        }
    };

    const handleStop = async () => {
        if (!window.confirm('Are you sure you want to stop this exercise?')) return; // Confirm before stopping

        try {
            const response = await axios.post('http://localhost:5000/api/stop');
            console.log(response.data);
            setTracking(false); // Ensure tracking is set to false
            setBackgroundColor(DEFAULT_BACKGROUND_COLOR); // Reset background color
            window.location.reload(); // Refresh the page after stopping the exercise
        } catch (error) {
            console.error(error);
            setErrorMessage('Failed to stop exercise tracking. Please try again.');
        }
    };

    return (
        <div className="exercise-container" style={{ backgroundColor: backgroundColor }}>
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

            {/* Display error messages */}
            {errorMessage && <div className="error-message">{errorMessage}</div>}

            <div className="buttons">
                <button onClick={handleStart}>Start</button>
                <button onClick={handleStop}>Stop</button>
            </div>

            {tracking && (
                <div className="video-feed">
                    <h2>Video Feed</h2>
                    <img
                        src={`http://localhost:5000/api/video_feed?exercise=${exercise}`}
                        alt="Video Feed"
                    />
                </div>
            )}
        </div>
    );
};

export default Exercise;
