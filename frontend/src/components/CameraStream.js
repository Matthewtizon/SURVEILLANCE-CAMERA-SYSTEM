import React, { useEffect, useState } from 'react';
import axios from 'axios';
import io from 'socket.io-client';
import { Box, Container, Typography, Button } from '@mui/material';
import Header from './Header';
import Sidebar from './SideBar';

const CameraStream = () => {
    const [error, setError] = useState(null);
    const [username, setUsername] = useState('');
    const [role, setRole] = useState('');
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const [isCameraOpen, setIsCameraOpen] = useState({});
    const [smsEnabled, setSmsEnabled] = useState(false);
    const socket = io('http://10.242.104.90:5000', {
        transports: ['websocket'],
    });

    useEffect(() => {
        const fetchUserData = async () => {
            try {
                const token = localStorage.getItem('token');
                const userResponse = await axios.get('http://10.242.104.90:5000/protected', {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });
                const { role, username } = userResponse.data.logged_in_as;
                setUsername(username);
                setRole(role);
            } catch (error) {
                console.error('Failed to fetch user info:', error);
                setError('Failed to fetch user info. Please try again.');
            }
        };

        fetchUserData();

        // Listen for video frames from the server
        socket.on('video_frame', (data) => {
            const { camera_ip, frame } = data;
            const base64Frame = `data:image/jpeg;base64,${btoa(
                String.fromCharCode(...new Uint8Array(frame))
            )}`;
            const imgElement = document.getElementById(`camera-${camera_ip}`);
            if (imgElement) {
                imgElement.src = base64Frame;
            }
        });

        return () => {
            socket.disconnect();
        };
    }, []);

    const toggleSidebar = () => {
        setSidebarOpen(!sidebarOpen);
    };

    const openCamera = async (cameraIp) => {
        try {
            const token = localStorage.getItem('token');
            const response = await axios.get(`http://10.242.104.90:5000/open_camera/${cameraIp}`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });
            setIsCameraOpen((prev) => ({ ...prev, [cameraIp]: true }));
            console.log(response.data.message);
        } catch (error) {
            console.error('Failed to open camera:', error);
        }
    };

    const closeCamera = async (cameraIp) => {
        try {
            const token = localStorage.getItem('token');
            const response = await axios.get(`http://10.242.104.90:5000/close_camera/${cameraIp}`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });
            setIsCameraOpen((prev) => ({ ...prev, [cameraIp]: false }));
            console.log(response.data.message);
        } catch (error) {
            console.error('Failed to close camera:', error);
        }
    };

    const toggleSmsNotifications = async () => {
        try {
            const response = await axios.post(
                'http://localhost:5000/toggle_sms_notifications',
                { enabled: !smsEnabled },
                { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
            );
            setSmsEnabled(response.data.sms_notifications_enabled);
        } catch (error) {
            console.error("Error toggling SMS notifications", error);
        }
    };

    return (
        <Box display="flex">
            <Sidebar isOpen={sidebarOpen} toggleSidebar={toggleSidebar} role={role} />
            <Box className={`main-content ${sidebarOpen ? 'expanded' : 'collapsed'}`} flexGrow={1}>
                <Header dashboardType="Camera" username={username} role={role} />
                <Container>
                    {error && <Typography color="error">{error}</Typography>}
                    <Box sx={{ mt: 4 }}>
                        <Typography variant="h6">Welcome to the Camera Dashboard</Typography>
                        <Typography variant="body1">Use the sidebar to navigate.</Typography>
                        <Box>
                            <Button onClick={toggleSmsNotifications}>
                                {smsEnabled ? 'Disable SMS Notifications' : 'Enable SMS Notifications'}                                
                            </Button>
                        </Box>

                        {/* Replace with your camera IPs */}
                        {[0, 1, 2].map((cameraIp) => (
                            <Box key={cameraIp} sx={{ mb: 2 }}>
                                <Typography variant="subtitle1">Camera {cameraIp}</Typography>
                                <Button variant="contained" onClick={() => openCamera(cameraIp)} disabled={isCameraOpen[cameraIp]}>
                                    Open Camera
                                </Button>
                                <Button variant="contained" onClick={() => closeCamera(cameraIp)} disabled={!isCameraOpen[cameraIp]} sx={{ ml: 1 }}>
                                    Close Camera
                                </Button>
                                <img id={`camera-${cameraIp}`} alt={`Camera ${cameraIp}`} style={{ width: '320px', height: '240px', display: isCameraOpen[cameraIp] ? 'block' : 'none' }} />
                            </Box>
                        ))}
                    </Box>
                </Container>
            </Box>
        </Box>
        
    );
};

export default CameraStream;
