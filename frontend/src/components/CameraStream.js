// src/components/CameraStream.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import Header from './Header';
import './CameraStream.css';

const CameraStream = () => {
    const [streams, setStreams] = useState([]);
    const [error, setError] = useState('');
    const [username, setUsername] = useState('');
    const [role, setRole] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        const token = localStorage.getItem('token');
        const fetchUserData = async () => {
            try {
                const response = await axios.get('http://localhost:5000/protected', {
                    headers: { Authorization: `Bearer ${token}` }
                });
                const user = response.data.logged_in_as;
                setUsername(user.username);
                setRole(user.role);

                const streamsResponse = await axios.get('http://localhost:5000/cameras', {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setStreams(streamsResponse.data);
            } catch (error) {
                console.error('Error fetching data:', error);
                setError('Failed to fetch data. Please try again.');
            }
        };

        fetchUserData();
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
            {streams.map((stream, index) => (
                <div key={index} className="camera-stream">
                    <h3>{stream.location}</h3>
                    <img
                        src={`http://localhost:5000/camera_feed/${stream.camera_id}?token=${localStorage.getItem('token')}`}
                        alt={`Camera ${stream.camera_id}`}
                    />
                </div>
            ))}
        </div>
    );
};

export default CameraStream;
