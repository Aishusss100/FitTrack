// components/Home.js
import React from 'react';
import { Link } from 'react-router-dom';
import './Home.css';
import TidioChat from './TidioChat'; // Import TidioChat

const Home = () => {
    return (
        <div className="home-container">
            <TidioChat /> {/* Include TidioChat component */}
            <div className="exercise-selection">
                <h2>Select Exercise</h2>
                <Link to="/exercise/bicep_curl">
                    <button>Bicep Curl</button>
                </Link>
                <Link to="/exercise/single_arm_dumbbell">
                    <button>Single Arm Dumbbell</button>
                </Link>
            </div>
        </div>
    );
};

export default Home;
