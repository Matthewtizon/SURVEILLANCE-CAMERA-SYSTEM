// src/components/CameraStream.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Header from './Header';
import Sidebar from './SideBar'; // Import Sidebar
import './Header.css';

const CameraStream = () => {
    const [cameras, setCameras] = useState([]);
    const [error, setError] = useState(null);
    const [username, setUsername] = useState('');
    const [role, setRole] = useState('');
    const [sidebarOpen, setSidebarOpen] = useState(true); // State for sidebar visibility

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
                
                const userResponse = await axios.get('http://localhost:5000/protected', {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });
                const { role, username } = userResponse.data.logged_in_as;
                setUsername(username);
                setRole(role);
            } catch (error) {
                console.error('Failed to fetch cameras or user info:', error);
                setError('Failed to fetch cameras or user info. Please try again.');
            }
        };

        fetchCameras();
    }, []);

    const toggleSidebar = () => {
        setSidebarOpen(!sidebarOpen);
    };

    const renderCameraFeed = (camera) => (
        <div key={camera.camera_id}>
            <h2>Camera {camera.camera_id}</h2>
            <img src={`http://localhost:5000/video_feed/${camera.camera_id}`} alt={`Camera ${camera.camera_id}`} />
        </div>
    );

    console.log('Cameras:', cameras);
    console.log('Error:', error);

    return (
        <div>
            <Sidebar isOpen={sidebarOpen} toggleSidebar={toggleSidebar} role={role} /> {/* Add Sidebar */}
            <div className={`main-content ${sidebarOpen ? 'expanded' : 'collapsed'}`}>
                <Header dashboardType="Camera Management" username={username} role={role} />
                {error && <p>{error}</p>}
                {cameras.length > 0 ? (
                    cameras.map(camera => renderCameraFeed(camera))
                ) : (
                    <p>Loading cameras...</p>
                )}
            </div>
        </div>
    );
};

export default CameraStream;