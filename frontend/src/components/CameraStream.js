import React, { useState, useEffect } from 'react';

const CameraStream = ({ cameraId }) => {
    const [streamUrl, setStreamUrl] = useState('');

    useEffect(() => {
        const fetchStreamUrl = () => {
            const token = localStorage.getItem('token');
            if (token) {
                setStreamUrl(`http://localhost:5000/camera_feed/${cameraId}?token=${token}`);
            } else {
                console.error('No token found');
            }
        };

        fetchStreamUrl();
    }, [cameraId]);

    return (
        <div>
            <h2>Live Camera Stream</h2>
            {streamUrl && (
                <img
                    src={streamUrl}
                    alt="Live camera stream"
                    style={{ width: '400px', height: '300px' }}
                />
            )}
        </div>
    );
};

export default CameraStream;
