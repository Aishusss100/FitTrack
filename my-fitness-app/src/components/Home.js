// components/Home.js
import React from 'react';
import { Link } from 'react-router-dom';
import './Home.css';

const Home = () => {
    const exercises = [
        { name: 'Bicep Curl (Left)', route: '/exercise/bicep_curl_left', icon: '💪' },
        { name: 'Bicep Curl (Right)', route: '/exercise/bicep_curl_right', icon: '💪' },
        { name: 'Overhead Press (Left)', route: '/exercise/overhead_press_left', icon: '🏋️‍♂️' },
        { name: 'Overhead Press (Right)', route: '/exercise/overhead_press_right', icon: '🏋️‍♂️' },
        { name: 'Lateral Raise (Left)', route: '/exercise/lateral_raise_left', icon: '↔️' },
        { name: 'Lateral Raise (Right)', route: '/exercise/lateral_raise_right', icon: '↔️' },
        { name: 'Front Raise (Left)', route: '/exercise/front_raise_left', icon: '⬆️' },
        { name: 'Front Raise (Right)', route: '/exercise/front_raise_right', icon: '⬆️' },
        { name: 'Single Arm Dumbbell (Left)', route: '/exercise/single_arm_dumbbell_left', icon: '🎯' },
        { name: 'Single Arm Dumbbell (Right)', route: '/exercise/single_arm_dumbbell_right', icon: '🎯' }
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
        </div>
    );
};

export default Home;
