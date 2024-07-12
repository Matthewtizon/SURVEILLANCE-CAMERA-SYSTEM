import React, { useEffect, useRef } from 'react';
import io from 'socket.io-client';

const CameraStream = () => {
    const videoRef = useRef(null);

    useEffect(() => {
        const socket = io('http://localhost:5000'); // Replace with your server URL

        socket.on('camera_frame', (frame) => {
            console.log('Received frame:', frame); // Log the received frame for debugging
            if (videoRef.current) {
                videoRef.current.src = `data:image/jpeg;base64,${frame}`;
            }
        });

        socket.on('connect_error', (error) => {
            console.error('Connection error:', error); // Log connection errors
        });

        return () => {
            socket.disconnect();
            console.log('Socket disconnected'); // Log disconnection
        };
    }, []);

    return (
        <div>
            <h2>Camera 1 Stream</h2>
            <video ref={videoRef} autoPlay controls width="640" height="480" />
        </div>
    );
};

export default CameraStream;
