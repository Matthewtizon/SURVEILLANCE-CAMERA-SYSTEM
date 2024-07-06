// src/components/CameraStream.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import Header from './Header';
import './CameraStream.css';

const CameraStream = () => {
    const [error, setError] = useState('');
    const [username, setUsername] = useState('');
    const [role, setRole] = useState('');
    const [cameraFeeds, setCameraFeeds] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        const token = localStorage.getItem('token');
    
        // Fetch user data
        const fetchUserData = async () => {
            try {
                const response = await axios.get('http://localhost:5000/protected', {
                    headers: { Authorization: `Bearer ${token}` }
                });
                const user = response.data.logged_in_as;
                setUsername(user.username);
                setRole(user.role);
            } catch (error) {
                console.error('Error fetching user data:', error);
                setError('Failed to fetch user data. Please try again.');
    
                // Example token refresh logic
                const refreshToken = await axios.post('http://localhost:5000/refresh_token', {
                    refresh_token: localStorage.getItem('refresh_token')
                });
    
                if (refreshToken.data && refreshToken.data.access_token) {
                    localStorage.setItem('token', refreshToken.data.access_token);
                    // Retry fetching user data or camera streams
                    fetchUserData();
                    fetchCameraStreams();
                } else {
                    console.error('Failed to refresh token:', refreshToken.data);
                }
            }
        };
    
        // Fetch camera streams
        const fetchCameraStreams = async () => {
            try {
                const response = await axios.get('http://localhost:5000/cameras', {
                    headers: { Authorization: `Bearer ${token}` }
                });
                const cameras = response.data;
                const streams = cameras.map(camera => `http://localhost:5000/camera_feed/${camera.location}?token=${token}`);
                setCameraFeeds(streams);
            } catch (error) {
                console.error('Error fetching camera streams:', error);
                setError('Failed to fetch camera streams. Please try again.');
            }
        };
    
        fetchUserData();
        fetchCameraStreams();
    }, []);

    const handleBackClick = () => {
        if (role === 'Administrator') {
            navigate('/admin-dashboard');
        } else if (role === 'Security Staff') {
            navigate('/security-dashboard');
        }
    };

    return (
        <div className="camera-stream-container">
            <Header dashboardType="Camera Stream" username={username} />
            {error && <p className="error">{error}</p>}
            <button onClick={handleBackClick} className="back-button">Back to Dashboard</button>
            <div className="camera-feeds">
                {cameraFeeds.map((feedUrl, index) => (
                    <img key={index} src={feedUrl} alt={`Camera Feed ${index}`} />
                ))}
            </div>
        </div>
    );
};

export default CameraStream;
