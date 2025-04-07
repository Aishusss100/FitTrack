import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './Login.css';

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [message, setMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        setMessage('');
        setIsLoading(true);
        

        let response = null;
        let errorMessage = 'Login failed. Please check your credentials.';

        try {
            response = await axios.post('http://localhost:5000/api/login', {
                username: username,
                password: password
            }, {
                withCredentials: true
            });
        } catch (localError) {
            console.error('Login error (localhost):', localError);
    
            // Try network IP if localhost fails
            try {
                response = await axios.post('http://192.168.126.149:5000/api/login', {
                    username: username,
                    password: password
                }, {
                    withCredentials: true
                });
            } catch (networkError) {
                console.error('Login error (network):', networkError);
                errorMessage = networkError.response?.data?.message || errorMessage;
            }
        }
            
        if (response) {
            console.log('Login response:', response.data);
            setMessage(response.data.message || 'Login successful');
            setIsLoading(false);

            if (response.data.message === 'Login successful' || response.status === 200) {
                navigate('/home');
            }
        } else {
            setMessage(errorMessage);
            setIsLoading(false);
        }
    };

    return (
        <div className="login-container">
            <h1>FitTrack</h1>
            {message && <div className={message.includes('failed') ? "error-message" : "success-message"}>{message}</div>}
            <form onSubmit={handleLogin}>
                <div className="form-group">
                    <label htmlFor="username">Username</label>
                    <input
                        type="text"
                        id="username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                    />
                </div>
                <div className="form-group_password-group">
                    <label htmlFor="password">Password</label>
                    <div className="password-wrapper">
                        <input
                            type={showPassword ? 'text' : 'password'}
                            id="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                        <button 
                            type="button" 
                            className="toggle-password" 
                            onClick={() => setShowPassword(!showPassword)}
                        >
                            {showPassword ? '🙈  ' : '👁️'}
                        </button>
                    </div>
                </div>
                <button type="submit" className="toggle-submit"  disabled={isLoading}>
                    {isLoading ? 'Logging in...' : 'Login'}
                </button>
            </form>
            <p>
                Don't have an account? <span 
                    className="signup-link" 
                    onClick={() => navigate('/signup')}
                >
                    Sign Up
                </span>
            </p>
        </div>
    );
};

export default Login;
