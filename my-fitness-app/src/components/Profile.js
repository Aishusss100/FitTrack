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
    const [isEditing, setIsEditing] = useState(false);
    const [editedData, setEditedData] = useState({
        name: '',
        date_of_birth: '',
        email: ''
    });
    const [updateMessage, setUpdateMessage] = useState('');
    const [caloriesData, setCaloriesData] = useState({
        weekly: { calories_burned: 0, total_reps: 0, total_duration: 0 },
        monthly: { calories_burned: 0, total_reps: 0, total_duration: 0 }
    });
    const [caloriesLoading, setCaloriesLoading] = useState(true);

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
                setEditedData({
                    name: profileResponse.data.name || '',
                    date_of_birth: profileResponse.data.date_of_birth || '',
                    email: profileResponse.data.email || ''
                });

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

                // Fetch calories data
                await fetchCaloriesData();
            } catch (error) {
                console.error('Error fetching profile data:', error);
                setError(error.response?.data?.message || 'Failed to load profile data');
                setLoading(false);
            }
        };

        fetchProfileData();
    }, []);

    // Function to fetch calories data
    const fetchCaloriesData = async () => {
        try {
            setCaloriesLoading(true);
            
            // Fetch weekly calories
            const weeklyResponse = await axios.get('http://localhost:5000/api/get_total_calories', {
                params: { view_type: 'weekly' },
                withCredentials: true
            });
            
            // Fetch monthly calories
            const monthlyResponse = await axios.get('http://localhost:5000/api/get_total_calories', {
                params: { view_type: 'monthly' },
                withCredentials: true
            });
            
            setCaloriesData({
                weekly: weeklyResponse.data,
                monthly: monthlyResponse.data
            });
            
            setCaloriesLoading(false);
        } catch (error) {
            console.error('Error fetching calories data:', error);
            setCaloriesLoading(false);
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setEditedData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleEdit = () => {
        setIsEditing(true);
    };

    const handleCancel = () => {
        setIsEditing(false);
        setEditedData({
            name: profileData.name || '',
            date_of_birth: profileData.date_of_birth || '',
            email: profileData.email || ''
        });
        setUpdateMessage('');
    };

    const handleSave = async () => {
        try {
            const response = await axios.post('http://localhost:5000/api/update_profile', editedData, {
                withCredentials: true
            });
            
            if (response.data.success) {
                setProfileData(prev => ({
                    ...prev,
                    name: editedData.name,
                    date_of_birth: editedData.date_of_birth,
                    email: editedData.email
                }));
                setIsEditing(false);
                setUpdateMessage('Profile updated successfully!');
                
                // Clear the message after 3 seconds
                setTimeout(() => {
                    setUpdateMessage('');
                }, 3000);
            }
        } catch (error) {
            console.error('Error updating profile:', error);
            setUpdateMessage('Failed to update profile. Please try again.');
        }
    };

    // Format duration to display in minutes and seconds
    const formatDuration = (durationInSeconds) => {
        const minutes = Math.floor(durationInSeconds / 60);
        const seconds = durationInSeconds % 60;
        return `${minutes > 0 ? `${minutes}m ` : ''}${seconds}s`;
    };

    if (loading) {
        return (
            <div className="profile-container">
                <h1 className="profile-title">My Profile</h1>
                <div className="loading">Loading profile data...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="profile-container">
                <h1 className="profile-title">My Profile</h1>
                <div className="error-message">{error}</div>
            </div>
        );
    }

    return (
        <div className="profile-container">
            <h1 className="profile-title">My Profile</h1>
            
            <div className="personal-details">
                <div className="details-header">
                    <h2>Personal Information</h2>
                    {!isEditing ? (
                        <button className="edit-button" onClick={handleEdit}>Edit</button>
                    ) : (
                        <div className="edit-actions">
                            <button className="save-button" onClick={handleSave}>Save</button>
                            <button className="cancel-button" onClick={handleCancel}>Cancel</button>
                        </div>
                    )}
                </div>
                
                {updateMessage && <div className="update-message">{updateMessage}</div>}
                
                <div className="profile-field">
                    <span className="field-label">Username:</span>
                    <span className="field-value">{profileData.username}</span>
                </div>
                
                <div className="profile-field">
                    <span className="field-label">Name:</span>
                    {isEditing ? (
                        <input 
                            type="text" 
                            name="name" 
                            value={editedData.name} 
                            onChange={handleInputChange} 
                            className="edit-input"
                        />
                    ) : (
                        <span className="field-value">{profileData.name || 'Not provided'}</span>
                    )}
                </div>
                
                <div className="profile-field">
                    <span className="field-label">Date of Birth:</span>
                    {isEditing ? (
                        <input 
                            type="date" 
                            name="date_of_birth" 
                            value={editedData.date_of_birth} 
                            onChange={handleInputChange} 
                            className="edit-input"
                        />
                    ) : (
                        <span className="field-value">{profileData.date_of_birth || 'Not provided'}</span>
                    )}
                </div>
                
                <div className="profile-field">
                    <span className="field-label">Email:</span>
                    {isEditing ? (
                        <input 
                            type="email" 
                            name="email" 
                            value={editedData.email} 
                            onChange={handleInputChange} 
                            className="edit-input"
                        />
                    ) : (
                        <span className="field-value">{profileData.email || 'Not provided'}</span>
                    )}
                </div>

                {/* Calories Summary Section */}
                <div className="calories-summary">
                    <h3>Fitness Progress Summary</h3>
                    {caloriesLoading ? (
                        <div className="loading">Loading calories data...</div>
                    ) : (
                        <div className="calories-cards">
                            <div className="calories-card">
                                <h4>Last 7 Days</h4>
                                <div className="calories-detail">
                                    <span>Calories Burned:</span>
                                    <span>{caloriesData.weekly.calories_burned.toFixed(2)} cal</span>
                                </div>
                                <div className="calories-detail">
                                    <span>Total Reps:</span>
                                    <span>{caloriesData.weekly.total_reps}</span>
                                </div>
                                <div className="calories-detail">
                                    <span>Total Duration:</span>
                                    <span>{formatDuration(caloriesData.weekly.total_duration)}</span>
                                </div>
                            </div>
                            <div className="calories-card">
                                <h4>Last 30 Days</h4>
                                <div className="calories-detail">
                                    <span>Calories Burned:</span>
                                    <span>{caloriesData.monthly.calories_burned.toFixed(2)} cal</span>
                                </div>
                                <div className="calories-detail">
                                    <span>Total Reps:</span>
                                    <span>{caloriesData.monthly.total_reps}</span>
                                </div>
                                <div className="calories-detail">
                                    <span>Total Duration:</span>
                                    <span>{formatDuration(caloriesData.monthly.total_duration)}</span>
                                </div>
                            </div>
                        </div>
                    )}
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
                                <span>{formatDuration(perf.bestDuration)}</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default Profile;