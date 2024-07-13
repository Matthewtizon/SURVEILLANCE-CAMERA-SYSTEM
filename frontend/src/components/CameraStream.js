import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import socketIOClient from 'socket.io-client';
import Header from './Header';
import './CameraStream.css';

const CameraStream = () => {
    const [error, setError] = useState('');
    const [username, setUsername] = useState('');
    const [role, setRole] = useState('');
    const videoRef = useRef(null);
    const navigate = useNavigate();

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) {
            setError('Token not found. Please log in again.');
            return;
        }

        const fetchUserData = async () => {
            try {
                const response = await axios.get('http://localhost:5000/protected', {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setUsername(response.data.logged_in_as.username);
                setRole(response.data.logged_in_as.role);
            } catch (err) {
                setError('Failed to fetch user data. Please log in again.');
                localStorage.removeItem('token');
                navigate('/login');
            }
        };

        fetchUserData();

        const socket = socketIOClient('http://localhost:5000');

        socket.on('connect', () => {
            console.log('Connected to SocketIO');
        });

        socket.on('disconnect', () => {
            console.log('Disconnected from SocketIO');
        });

        // Clean up socket connection
        return () => {
            socket.disconnect();
        };

    }, []);

    const startVideoStream = async (cameraId) => {
        try {
            const response = await axios.get(`http://localhost:5000/stream_video/${cameraId}`, {
                responseType: 'blob'  // Ensure response is treated as a blob
            });

            // Create a URL for the blob object to use in <video> tag
            const videoURL = URL.createObjectURL(response.data);
            if (videoRef.current) {
                videoRef.current.src = videoURL;
                videoRef.current.play();
            }
        } catch (err) {
            console.error('Failed to start video stream:', err);
        }
    };

    return (
        <div>
            <Header username={username} role={role} />
            <div className="camera-feed-container">
                <video ref={videoRef} width="640" height="480" controls autoPlay></video>
            </div>
            {error && <div className="error-message">{error}</div>}
        </div>
    );
};

export default CameraStream;
