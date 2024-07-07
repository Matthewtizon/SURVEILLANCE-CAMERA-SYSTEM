// src/components/CameraStream.js
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
    const [cameraFeeds, setCameraFeeds] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        const token = localStorage.getItem('token');

        if (!token) {
            setError('Token not found. Please log in again.');
            return;
        }

        // Fetch user data
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

        // Fetch camera feeds
        const fetchCameraFeeds = async () => {
            try {
                const response = await axios.get('http://localhost:5000/cameras', {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setCameraFeeds(response.data);
            } catch (err) {
                setError('Failed to fetch camera feeds.');
            }
        };

        fetchCameraFeeds();
    }, [navigate]);

    const handleCameraClick = async (cameraLocation) => {
        const token = localStorage.getItem('token');
        if (!token) {
            setError('Token not found. Please log in again.');
            return;
        }

        try {
            const response = await axios.get(`http://localhost:5000/camera_feed/${encodeURIComponent(cameraLocation)}`, {
                headers: { Authorization: `Bearer ${token}` },
                params: { token }
            });

            if (response.data.message === 'Streaming started') {
                const socket = io('http://localhost:5000');
                socket.on('camera_frame', (data) => {
                    if (data.image) {
                        const imgSrc = `data:image/jpeg;base64,${data.data}`;
                        const imgElement = document.getElementById(`camera-${cameraLocation}`);
                        if (imgElement) {
                            imgElement.src = imgSrc;
                        }
                    }
                });
            }
        } catch (err) {
            setError('Failed to start camera feed.');
        }
    };

    return (
        <div>
            <Header username={username} role={role} />
            <div className="camera-feed-container">
                {cameraFeeds.map((feed) => (
                    <div key={feed.camera_id} className="camera-feed">
                        <h3>{feed.location}</h3>
                        <video id={`camera-${feed.location}`} autoPlay></video>
                        <button onClick={() => handleCameraClick(feed.location)}>View Feed</button>
                    </div>
                ))}
            </div>
            {error && <p className="error">{error}</p>}
        </div>
    );
};

export default CameraStream;
