import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import socketIOClient from 'socket.io-client';
import Header from './Header';
import './CameraStream.css';

const CameraStream = () => {
    const [error, setError] = useState('');
    const [username, setUsername] = useState('');
    const [role, setRole] = useState('');
    const [frames, setFrames] = useState([]);
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

        const socket = socketIOClient('http://localhost:5000', {
            query: { token }
        });

        socket.on('connect', () => {
            console.log('Connected to socket server');
        });

        socket.on('camera_frame', (data) => {
            console.log(`Received frame for ${data.cameraLocation}`);  // Debug statement
            const imgSrc = `data:image/jpeg;base64,${data.data}`;
            setFrames((prevFrames) => [...prevFrames, imgSrc]);
        });

        socket.on('disconnect', () => {
            console.log('Disconnected from socket server');
        });

        return () => {
            socket.disconnect();
        };
    }, [navigate]);

    return (
        <div>
            <Header username={username} role={role} />
            <div className="camera-feed-container">
                {frames.map((src, index) => (
                    <img key={index} src={src} alt={`Frame ${index}`} className="camera-feed-frame" />
                ))}
            </div>
            {error && <p className="error">{error}</p>}
        </div>
    );
};

export default CameraStream;
