// src/components/CameraStream.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Box, CircularProgress, Container, Typography, Button, ButtonGroup, Switch, FormControlLabel } from '@mui/material';
import Header from './Header';
import Sidebar from './SideBar';
import './Loading.css';

const CameraStream = () => {
    const [cameraStatus, setCameraStatus] = useState([]);
    const [selectedCamera, setSelectedCamera] = useState(null);
    const [displayAllCameras, setDisplayAllCameras] = useState(false);
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

                // Set the first camera as the selected camera initially
                if (cameraResponse.data.length > 0) {
                    setSelectedCamera(cameraResponse.data[0].port);
                }
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

    const handleCameraSelect = (port) => {
        setSelectedCamera(port);
    };

    const renderCameraFeed = (camera) => (
        <Box key={camera.port} sx={{ position: 'relative', my: 2, textAlign: 'center' }}>
            <Typography
                variant="caption"
                sx={{
                    position: 'absolute',
                    top: '8px',
                    right: '8px',
                    color: 'white',
                    padding: '2px',
                    fontSize: '0.75rem',
                    fontWeight: 'bold',
                }}
            >
                Camera {camera.port}
            </Typography>
            {camera.occupied ? (
                <img
                    src={`http://localhost:5000/video_feed/${camera.port}`}
                    alt={`Camera ${camera.port}`}
                    style={{ maxWidth: '100%', maxHeight: '400px', objectFit: 'cover' }}
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

    const renderAllCameras = () => (
        <Box sx={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
            gap: '16px',
            alignItems: 'start',
        }}>
            {cameraStatus.map(camera => renderCameraFeed(camera))}
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
                        <Box>
                            <Box sx={{ mt: 4, textAlign: 'center' }}>
                                <FormControlLabel
                                    control={
                                        <Switch
                                            checked={displayAllCameras}
                                            onChange={() => setDisplayAllCameras(!displayAllCameras)}
                                            name="displayAllCameras"
                                            color="primary"
                                        />
                                    }
                                    label="Display All Cameras"
                                />
                            </Box>
                            {displayAllCameras ? (
                                renderAllCameras()
                            ) : (
                                renderCameraFeed(cameraStatus.find(cam => cam.port === selectedCamera))
                            )}
                            {!displayAllCameras && (
                                <Box sx={{ mt: 4, textAlign: 'center' }}>
                                    <ButtonGroup variant="contained" aria-label="camera selection">
                                        {cameraStatus.map(camera => (
                                            <Button
                                                key={camera.port}
                                                onClick={() => handleCameraSelect(camera.port)}
                                                disabled={!camera.occupied}
                                                sx={{
                                                    borderColor: selectedCamera === camera.port ? 'blue' : 'transparent',
                                                    color: selectedCamera === camera.port ? 'blue' : 'inherit',
                                                    borderWidth: '2px',
                                                    borderStyle: 'solid',
                                                    '&:hover': {
                                                        borderColor: selectedCamera === camera.port ? 'darkblue' : 'inherit',
                                                    },
                                                }}
                                            >
                                                Camera {camera.port}
                                            </Button>
                                        ))}
                                    </ButtonGroup>
                                </Box>
                            )}
                        </Box>
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
