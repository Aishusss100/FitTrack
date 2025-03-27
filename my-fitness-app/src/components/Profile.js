import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Profile.css';

const Profile = () => {
    const [profileData, setProfileData] = useState({
        username: '',
        name: '',
        date_of_birth: '',
        email: ''
    });
    const [exercisePerformance, setExercisePerformance] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    // List of all exercises to track
    const exercises = [
        'bicep_curl_left', 'bicep_curl_right',
        'overhead_press_left', 'overhead_press_right',
        'lateral_raise_left', 'lateral_raise_right',
        'front_raise_left', 'front_raise_right',
        'single_arm_dumbbell_left', 'single_arm_dumbbell_right'
    ];

    useEffect(() => {
        const fetchProfileData = async () => {
            try {
                setLoading(true);
                // Fetch profile data
                const profileResponse = await axios.get('http://localhost:5000/api/profile', {
                    withCredentials: true
                });
                setProfileData(profileResponse.data);

                // Fetch highest performance for each exercise
                const performancePromises = exercises.map(async (exercise) => {
                    try {
                        const performanceResponse = await axios.get('http://localhost:5000/api/get_progress', {
                            params: { 
                                exercise_name: exercise, 
                                view_type: 'monthly' 
                            },
                            withCredentials: true
                        });

                        // Find the day with highest reps
                        const performanceData = performanceResponse.data;
                        const bestPerformanceDay = performanceData.reduce((max, day) => 
                            (day.reps > max.reps) ? day : max, 
                            { date: 'No data', reps: 0, duration: 0 }
                        );

                        return {
                            exercise: exercise,
                            bestDate: bestPerformanceDay.date,
                            bestReps: bestPerformanceDay.reps,
                            bestDuration: bestPerformanceDay.duration
                        };
                    } catch (err) {
                        console.error(`Error fetching performance for ${exercise}:`, err);
                        return {
                            exercise: exercise,
                            bestDate: 'No data',
                            bestReps: 0,
                            bestDuration: 0
                        };
                    }
                });

                // Wait for all performance data to be fetched
                const performanceResults = await Promise.all(performancePromises);
                setExercisePerformance(performanceResults);
                setLoading(false);
            } catch (error) {
                console.error('Error fetching profile data:', error);
                setError(error.response?.data?.message || 'Failed to load profile data');
                setLoading(false);
            }
        };

        fetchProfileData();
    }, []);

    if (loading) {
        return (
            <div className="profile-container">
                <h1>My Profile</h1>
                <div className="loading">Loading profile data...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="profile-container">
                <h1>My Profile</h1>
                <div className="error-message">{error}</div>
            </div>
        );
    }

    return (
        <div className="profile-container">
            <h1 className="profile-title">My Profile</h1>
            
            <div className="personal-details">
                <h2>Personal Information</h2>
                <div className="profile-field">
                    <span className="field-label">Username:</span>
                    <span className="field-value">{profileData.username}</span>
                </div>
                
                <div className="profile-field">
                    <span className="field-label">Name:</span>
                    <span className="field-value">{profileData.name || 'Not provided'}</span>
                </div>
                
                <div className="profile-field">
                    <span className="field-label">Date of Birth:</span>
                    <span className="field-value">{profileData.date_of_birth || 'Not provided'}</span>
                </div>
                
                <div className="profile-field">
                    <span className="field-label">Email:</span>
                    <span className="field-value">{profileData.email || 'Not provided'}</span>
                </div>
            </div>

            <div className="exercise-performance-container">
                <h2>Best Performance by Exercise</h2>
                <div className="exercise-performance-grid">
                    {exercisePerformance.map((perf) => (
                        <div key={perf.exercise} className="exercise-performance-card">
                            <h3>{perf.exercise.replace(/_/g, ' ')}</h3>
                            <div className="performance-detail">
                                <span>Best Date:</span>
                                <span>{perf.bestDate}</span>
                            </div>
                            <div className="performance-detail">
                                <span>Best Reps:</span>
                                <span>{perf.bestReps}</span>
                            </div>
                            <div className="performance-detail">
                                <span>Best Duration:</span>
                                <span>{perf.bestDuration} sec</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default Profile;