// CameraStream.js

import React, { useEffect, useState } from 'react';
import axios from 'axios';

const CameraStream = () => {
    const [cameras, setCameras] = useState([]);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchCameras = async () => {
            try {
                const token = localStorage.getItem('token');
                const response = await axios.get('http://localhost:5000/cameras', {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });
                setCameras(response.data.cameras);
            } catch (error) {
                setError('Failed to fetch cameras. Please try again.');
            }
        };

        fetchCameras();
    }, []);

    const renderCameraFeed = (cameraId) => {
        return (
            <div key={cameraId}>
                <h2>Camera {cameraId}</h2>
                <img src={`http://localhost:5000/video_feed/${cameraId}`} alt={`Camera ${cameraId}`} />
            </div>
        );
    };

    return (
        <div>
            {error && <p>{error}</p>}
            {cameras.length > 0 ? (
                cameras.map(camera => renderCameraFeed(camera.camera_id))
            ) : (
                <p>Loading cameras...</p>
            )}
        </div>
    );
};

export default CameraStream;
