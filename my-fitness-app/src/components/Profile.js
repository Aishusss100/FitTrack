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
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchProfileData = async () => {
            try {
                setLoading(true);
                const response = await axios.get('http://localhost:5000/api/profile', {
                    withCredentials: true // Important for cookies/session
                });
                
                console.log('Profile data response:', response.data);
                setProfileData(response.data);
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
            
            <div className="profile-image-container">
                <img src="/profile.png" alt="Profile" className="profile-image" />
            </div>
            
            <div className="profile-card">
                <div className="profile-field">
                    <h3 className="field-label">Username:</h3>
                    <p className="field-value">{profileData.username}</p>
                </div>
                
                <div className="profile-field">
                    <h3 className="field-label">Name:</h3>
                    <p className="field-value">{profileData.name || 'Not provided'}</p>
                </div>
                
                <div className="profile-field">
                    <h3 className="field-label">Date of Birth:</h3>
                    <p className="field-value">{profileData.date_of_birth || 'Not provided'}</p>
                </div>
                
                <div className="profile-field">
                    <h3 className="field-label">Email:</h3>
                    <p className="field-value">{profileData.email || 'Not provided'}</p>
                </div>
            </div>
        </div>
    );
};

export default Profile;