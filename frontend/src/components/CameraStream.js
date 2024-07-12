// src/components/CameraStream.js
import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import Header from './Header';
import './CameraStream.css';
import { io } from 'socket.io-client';

const ENDPOINT = 'http://localhost:5000';  // Adjust the endpoint as per your setup

const CameraStream = () => {
    const [error, setError] = useState('');
    const [username, setUsername] = useState('');
    const [role, setRole] = useState('');
    const navigate = useNavigate();
    const videoRef = useRef();

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
            } catch (error) {
                console.error('Error fetching data:', error);
                setError('Failed to fetch data. Please try again.');
            }
        };

        fetchUserData();

        const socket = io(ENDPOINT);
        
        socket.on('connect', () => {
            console.log('Connected to server');
        });

        socket.on('disconnect', () => {
            console.log('Disconnected from server');
        });

        socket.on('camera_frame', (data) => {
            const frame = new Blob([data.data], { type: 'image/jpeg' });
            const imgUrl = URL.createObjectURL(frame);
            videoRef.current.src = imgUrl;
        });

        return () => socket.disconnect();
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
            <div>
                <video ref={videoRef} autoPlay />
            </div>
        </div>
    );
};

export default CameraStream;
