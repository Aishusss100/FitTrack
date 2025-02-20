import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Login from './components/Login';
import NewSignup from './components/NewSignup'; // Import the new Signup component
import Home from './components/Home';
import Exercise from './components/Exercise';
import TitleBars from './components/TitleBars'; // Import the combined TitleBars component
import SplashScreen from './components/SplashScreen'; // Import the SplashScreen component
import './App.css';

function App() {
    return (
        <Router>
            <div className="App">
                <Routes>
                    <Route path="/splash" element={<SplashScreen />} />
                    <Route path="/login" element={<><TitleBars /><Login /></>} />
                    <Route path="/signup" element={<NewSignup />} /> {/* No title bar for Signup */}
                    <Route path="/home" element={<><TitleBars /><Home /></>} />
                    <Route path="/exercise/:exercise" element={<><TitleBars /><Exercise /></>} />
                    <Route path="/" element={<SplashScreen />} />
                </Routes>
            </div>
        </Router>
    );
}

export default App;
