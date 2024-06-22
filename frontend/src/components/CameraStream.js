// src/components/CameraStream.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './CameraStream.css';

const CameraStream = () => {
    const [streams, setStreams] = useState([]);
    const [error, setError] = useState('');

    useEffect(() => {
        const token = localStorage.getItem('token');
        const fetchCameras = async () => {
            try {
                const response = await axios.get('http://localhost:5000/cameras', {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                    },
                });
                setStreams(response.data);
            } catch (error) {
                console.error('Error fetching camera list:', error);
                setError('Failed to fetch camera list. Please try again.');
            }
        };

        fetchCameras();
    }, []);

    return (
        <div className="camera-stream-container">
            {error && <p className="error">{error}</p>}
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
