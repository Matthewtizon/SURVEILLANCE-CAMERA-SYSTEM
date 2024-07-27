// src/components/CameraStream.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Box, CircularProgress, Container, Typography } from '@mui/material';
import Header from './Header';
import Sidebar from './SideBar';
import './Loading.css';

const CameraStream = () => {
    const [cameras, setCameras] = useState([]);
    const [error, setError] = useState(null);
    const [username, setUsername] = useState('');
    const [role, setRole] = useState('');
    const [sidebarOpen, setSidebarOpen] = useState(true);

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
        <Box key={camera.camera_id} my={2}>
            <Typography variant="h6">Camera {camera.camera_id}</Typography>
            <img src={`http://localhost:5000/video_feed/${camera.camera_id}`} alt={`Camera ${camera.camera_id}`} />
        </Box>
    );

    return (
        <Box display="flex">
            <Sidebar isOpen={sidebarOpen} toggleSidebar={toggleSidebar} role={role} />
            <Box className={`main-content ${sidebarOpen ? 'expanded' : 'collapsed'}`} flexGrow={1}>
                <Header dashboardType="Camera Management" username={username} role={role} />
                <Container>
                    {error && <Typography color="error">{error}</Typography>}
                    {cameras.length > 0 ? (
                        cameras.map(camera => renderCameraFeed(camera))
                    ) : (
                        <Box className="loading-container">
                            <CircularProgress />
                        </Box>
                    )}
                </Container>
            </Box>
        </Box>
    );
};

export default CameraStream;
