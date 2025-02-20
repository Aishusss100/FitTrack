import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import './Exercise.css';

const Exercise = () => {
    const { exercise } = useParams();
    const [targetReps, setTargetReps] = useState(0);
    const [tracking, setTracking] = useState(false);
    const [backgroundColor, setBackgroundColor] = useState('#fff');

    const handleSetTarget = async () => {
        try {
            const response = await axios.post('http://localhost:5000/api/set_target', { target_reps: targetReps });
            console.log(response.data);
            setBackgroundColor('#ffcccc');  // Change background color when target is set
        } catch (error) {
            console.error(error);
        }
    };

    const handleStart = async () => {
        try {
            const response = await axios.post('http://localhost:5000/api/start');
            console.log(response.data);
            setTracking(true);  // Ensure tracking is set to true after the start API call
        } catch (error) {
            console.error(error);
        }
    };

    const handleStop = async () => {
        try {
            const response = await axios.post('http://localhost:5000/api/stop');
            console.log(response.data);
            setTracking(false);  // Ensure tracking is set to false after the stop API call
            window.location.reload();  // Refresh the page after stopping the exercise
        } catch (error) {
            console.error(error);
        }
    };

    return (
        <div className="exercise-container" style={{ backgroundColor: backgroundColor }}>
            <h1>{exercise} Exercise</h1>
            <div className="instructions">
                <h2>Instructions</h2>
                <p>1. Ensure you have enough space around you to perform the exercise safely.</p>
                <p>2. Stand about 1 feet away from the camera for better visibility.</p>
                <p>3. Ensure there is sufficient lighting in the room.</p>
                <p>4. Wear comfortable clothing that allows you to move freely.</p>
            </div>
            <div className="target-input">
                <label>Set Target Reps:</label>
                <input 
                    type="number" 
                    value={targetReps} 
                    onChange={(e) => setTargetReps(e.target.value)} 
                />
                <button onClick={handleSetTarget}>Set Target</button>
            </div>
            <div className="buttons">
                <button onClick={handleStart}>Start</button>
                <button onClick={handleStop}>Stop</button>
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
