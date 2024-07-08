import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import Header from './Header';
import './CameraStream.css';
import io from 'socket.io-client';

const CameraStream = () => {
    const [error, setError] = useState('');
    const [username, setUsername] = useState('');
    const [role, setRole] = useState('');
    const [image, setImage] = useState(null); // State to hold the camera frame image
    const navigate = useNavigate();
    const socket = io('http://localhost:5000'); // Establish Socket.IO connection

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

        // Start receiving camera frames
        socket.on('camera_frame', (data) => {
            const arrayBufferView = new Uint8Array(data.data);
            const blob = new Blob([arrayBufferView], { type: 'image/jpeg' });
            const imageUrl = URL.createObjectURL(blob);
            setImage(imageUrl);
        });

        // Emit request to start camera feed
        socket.emit('start_camera_feed', { cameraLocation: 'YourCameraLocation' }); // Replace 'YourCameraLocation' with your actual camera location

        return () => {
            // Clean up socket listeners
            socket.off('camera_frame');
        };

    }, [navigate, socket]);

    return (
        <div>
            <Header username={username} role={role} />
            <div className="camera-feed-container">
                {image ? <img src={image} alt="Camera Feed" /> : <p>Loading camera feed...</p>}
            </div>
            {error && <p className="error">{error}</p>}
        </div>
    );
};

export default CameraStream;
