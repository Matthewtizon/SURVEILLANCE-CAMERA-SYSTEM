// src/components/CameraStream.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Box, CircularProgress, Container, Typography } from '@mui/material';
import Header from './Header';
import Sidebar from './SideBar';
import './Loading.css';

const CameraStream = () => {
    const [cameraStatus, setCameraStatus] = useState([]);
    const [error, setError] = useState(null);
    const [username, setUsername] = useState('');
    const [role, setRole] = useState('');
    const [sidebarOpen, setSidebarOpen] = useState(true);

    useEffect(() => {
        const fetchCameraStatus = async () => {
            try {
                const token = localStorage.getItem('token');
                
                const [cameraResponse, userResponse] = await Promise.all([
                    axios.get('http://localhost:5000/camera_status', {
                        headers: {
                            Authorization: `Bearer ${token}`,
                        },
                    }),
                    axios.get('http://localhost:5000/protected', {
                        headers: {
                            Authorization: `Bearer ${token}`,
                        },
                    }),
                ]);

                setCameraStatus(cameraResponse.data);
                const { role, username } = userResponse.data.logged_in_as;
                setUsername(username);
                setRole(role);
            } catch (error) {
                console.error('Failed to fetch camera status or user info:', error);
                setError('Failed to fetch camera status or user info. Please try again.');
            }
        };

        fetchCameraStatus();
    }, []);

    const toggleSidebar = () => {
        setSidebarOpen(!sidebarOpen);
    };

    const renderCameraFeed = (camera) => (
        <Box key={camera.port} sx={{ my: 2, textAlign: 'center' }}>
            <Typography variant="h6">Camera {camera.port}</Typography>
            {camera.occupied ? (
                <img
                    src={`http://localhost:5000/video_feed/${camera.port}`}
                    alt={`Camera ${camera.port}`}
                    style={{ maxWidth: '100%', maxHeight: '400px' }}
                />
            ) : (
                <Box
                    sx={{
                        width: '100%',
                        height: '400px',
                        backgroundColor: 'black',
                        color: 'white',
                        display: 'flex',
                        justifyContent: 'center',
                        alignItems: 'center',
                    }}
                >
                    Not Available
                </Box>
            )}
        </Box>
    );

    return (
        <Box display="flex">
            <Sidebar isOpen={sidebarOpen} toggleSidebar={toggleSidebar} role={role} />
            <Box className={`main-content ${sidebarOpen ? 'expanded' : 'collapsed'}`} flexGrow={1}>
                <Header dashboardType="Camera Management" username={username} role={role} />
                <Container>
                    {error && <Typography color="error">{error}</Typography>}
                    {cameraStatus.length > 0 ? (
                        cameraStatus.map(camera => renderCameraFeed(camera))
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
