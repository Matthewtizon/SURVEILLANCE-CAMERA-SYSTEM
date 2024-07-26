// src/components/CameraStream.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import Header from './Header';
import Sidebar from './SideBar'; // Import Sidebar
import './Header.css';

const CameraStream = () => {
    const [cameras, setCameras] = useState([]);
    const [error, setError] = useState(null);
    const [username, setUsername] = useState('');
    const [role, setRole] = useState('');
    const [dashboardType, setDashboardType] = useState('');
    const [sidebarOpen, setSidebarOpen] = useState(true); // State for sidebar visibility
    const navigate = useNavigate();

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
                setDashboardType(role === 'Administrator' ? 'Admin' : 'Security');
            } catch (error) {
                console.error('Failed to fetch cameras or user info:', error);
                setError('Failed to fetch cameras or user info. Please try again.');
            }
        };

        fetchCameras();
    }, []);

    const handleBackToDashboard = () => {
        if (dashboardType === 'Admin') {
            navigate('/admin-dashboard');
        } else if (dashboardType === 'Security') {
            navigate('/security-dashboard');
        }
    };

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
                <button onClick={handleBackToDashboard} className="back-button">
                    Back to Dashboard
                </button>
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
