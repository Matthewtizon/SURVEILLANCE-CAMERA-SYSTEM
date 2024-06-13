// src/components/CameraFeeds.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './CameraFeeds.css';

const CameraFeeds = () => {
    const [cameras, setCameras] = useState([]);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchCameras = async () => {
            try {
                const token = localStorage.getItem('token');
                const response = await axios.get('http://localhost:5000/cameras', {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setCameras(response.data);
            } catch (err) {
                setError('Network Error: Unable to fetch camera feeds');
                console.error('Error fetching cameras', err);
            }
        };

        fetchCameras();
    }, []);

    if (error) {
        return <div>{error}</div>;
    }

    return (
        <div className="camera-feeds-container">
            <h2>Camera Feeds</h2>
            <div className="camera-feeds">
                {cameras.map(camera => (
                    <div key={camera.id} className="camera-feed">
                        <h3>{camera.name}</h3>
                        <img src={camera.url} alt={`Camera ${camera.id}`} />
                    </div>
                ))}
            </div>
        </div>
    );
};

export default CameraFeeds;
