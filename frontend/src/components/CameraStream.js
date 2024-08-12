import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Box, CircularProgress, Container, Typography, Switch, FormControlLabel } from '@mui/material';
import Header from './Header';
import Sidebar from './SideBar';
import './Loading.css';

const CameraStream = () => {
    const [cameraStatus, setCameraStatus] = useState([]);
    const [selectedCamera, setSelectedCamera] = useState(0);
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
                    axios.get('http://localhost:5000/cameras', {
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

                setCameraStatus(cameraResponse.data.cameras);
                const { role, username } = userResponse.data.logged_in_as;
                setUsername(username);
                setRole(role);

                // Set the single camera as selected initially
                setSelectedCamera(0);
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

    const renderCameraFeed = () => (
        <Box key={selectedCamera} sx={{ position: 'relative', my: 2, textAlign: 'center' }}>
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
                Camera {selectedCamera}
            </Typography>
            <img
                src={`http://localhost:5000/video_feed/${selectedCamera}`}
                alt={`Camera ${selectedCamera}`}
                style={{ maxWidth: '100%', maxHeight: '400px', objectFit: 'cover' }}
                onError={() => setError('Failed to load camera feed.')}
            />
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
                            {renderCameraFeed()}
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
