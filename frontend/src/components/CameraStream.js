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
                console.error('Failed to fetch cameras:', error);
                setError('Failed to fetch cameras. Please try again.');
            }
        };

        fetchCameras();
    }, []);

    const renderCameraFeed = (camera) => {
        return (
            <div key={camera.camera_id}>
                <h2>Camera {camera.camera_id}</h2>
                <img src={`http://localhost:5000/video_feed/${camera.camera_id}`} alt={`Camera ${camera.camera_id}`} />
            </div>
        );
    };

    console.log('Cameras:', cameras);
    console.log('Error:', error);

    return (
        <div>
            {error && <p>{error}</p>}
            {cameras.length > 0 ? (
                cameras.map(camera => renderCameraFeed(camera))
            ) : (
                <p>Loading cameras...</p>
            )}
        </div>
    );
};

export default CameraStream;
