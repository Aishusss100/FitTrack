import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './NewSignup.css';

const NewSignup = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [name, setName] = useState('');
    const [dateOfBirth, setDateOfBirth] = useState('');
    const [email, setEmail] = useState('');
    const [message, setMessage] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        console.log("Form submitted with values:", { username, password, confirmPassword, name, dateOfBirth, email });
        if (password !== confirmPassword) {
            setMessage('Passwords do not match.');
            return;
        }

    let response = null;
    let errorMessage = 'Login failed. Please check your credentials.';

    try {
        response = await axios.post('http://localhost:5000/api/signup', {
            username,
            password,
            name,
            dateOfBirth,
            email,
        }, {
            withCredentials: true
        });
    } catch (localError) {
        console.error('Signup error (localhost):', localError);

        // Try network IP if localhost fails
        try {
            response = await axios.post('http://192.168.220.149:5000/api/login', {
                username,
                password,
                name,
                dateOfBirth,
                email,
            }, {
                withCredentials: true
            });
        } catch (networkError) {
            console.error('Signup error (network):', networkError);
            errorMessage = networkError.response?.data?.message || errorMessage;
        }
    }
        
    if (response) {
        console.log('Signup response:', response.data);
        setMessage(response.data.message || 'Signup successful');

        if (response.data.message === 'Signup successful' || response.status === 200) {
            navigate('/login');
        }
    } else {
        setMessage(errorMessage);
    }};


    return (
        <div className="signup-container">
            <div className="signup-box">
                <h2>Sign Up</h2>
                <form onSubmit={handleSubmit}>
                    <input
                        type="text"
                        placeholder="Name"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        required
                    />
                    <input
                        type="date"
                        placeholder="Date of Birth"
                        value={dateOfBirth}
                        onChange={(e) => setDateOfBirth(e.target.value)}
                        required
                    />
                    <input
                        type="email"
                        placeholder="Email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                    />
                    <input
                        type="text"
                        placeholder="Username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                    />
                    <input
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                    <input
                        type="password"
                        placeholder="Confirm Password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        required
                    />
                    <button type="submit">Sign Up</button>
                </form>
                <p className="message">{message}</p>
                <p className="login-link">
                    Already have an account? <span onClick={() => navigate('/login')}>Login</span>
                </p>
            </div>
        </div>
    );
};

export default NewSignup;
