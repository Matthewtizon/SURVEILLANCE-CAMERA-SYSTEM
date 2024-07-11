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

        const socket = socketIOClient('http://localhost:5000');

        socket.on('connect', () => {
            console.log('Connected to SocketIO');
        });

        socket.on('disconnect', () => {
            console.log('Disconnected from SocketIO');
        });

        socket.on('camera_frame', ({ frame }) => {
            console.log('Received camera frame');
            setFrames(prevFrames => [...prevFrames, frame]);
        });

        return () => {
            socket.disconnect();
        };

    }, []);

    return (
        <div>
            <Header username={username} role={role} />
            <div className="camera-feed-container">
                {frames.length > 0 && frames.map((frame, index) => (
                    <img key={index} src={`data:image/jpeg;base64,${frame}`} alt={`Frame ${index}`} />
                ))}
            </div>
            {error && <div className="error-message">{error}</div>}
        </div>
    );
};

export default CameraStream;
