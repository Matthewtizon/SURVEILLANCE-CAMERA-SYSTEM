import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Box, CircularProgress, Container, Typography, Button } from '@mui/material';
import Header from './Header';
import Sidebar from './SideBar';  // Ensure Sidebar handles icons-only in mobile
import './Loading.css';
import './Dashboard.css'; // Custom styles

const AdminDashboard = () => {
    const [loading, setLoading] = useState(true);
    const [username, setUsername] = useState('');
    const [role, setRole] = useState('');
    const [sidebarOpen, setSidebarOpen] = useState(true);  // Sidebar state
    const [streaming, setStreaming] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchUserData = async () => {
            const token = localStorage.getItem('token');
            if (!token) {
                navigate('/login');
                return;
            }

            try {
                const response = await axios.get('http://10.242.104.90:5000/api/protected', {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setUsername(response.data.logged_in_as.username);
                setRole(response.data.logged_in_as.role);
                setLoading(false);
            } catch (error) {
                console.error('Error fetching user data:', error);
                localStorage.removeItem('token');
                navigate('/login');
            }
        };

        fetchUserData();
    }, [navigate]);

    // Toggle sidebar open/close
    const toggleSidebar = () => {
        setSidebarOpen(!sidebarOpen);
    };

    // Start video streaming
    const startStreaming = () => {
        setStreaming(true);
    };

    // Responsive handling for mobile layout
    useEffect(() => {
        const handleResize = () => {
            if (window.innerWidth < 600) {
                setSidebarOpen(false); // Auto-collapse sidebar on small screens
            } else {
                setSidebarOpen(true);  // Expand sidebar on larger screens
            }
        };

        window.addEventListener('resize', handleResize);
        handleResize(); // Initial check

        return () => window.removeEventListener('resize', handleResize);
    }, []);

    if (loading) {
        return (
            <Box className="loading-container">
                <CircularProgress />
            </Box>
        );
    }

    return (
        <Box display="flex">
            <Sidebar isOpen={sidebarOpen} toggleSidebar={toggleSidebar} role={role} />
            <Box className={`main-content ${sidebarOpen ? 'expanded' : 'collapsed'}`} flexGrow={1}>
                <Header dashboardType="Administrator" username={username} role={role} />
                <Container>
                    <Typography variant="h4" gutterBottom>
                        Welcome to the Admin Dashboard {username}
                    </Typography>

                    {/* Button to start video streaming */}
                    <Button variant="contained" color="primary" onClick={startStreaming}>
                        Start Streaming
                    </Button>

                    {/* If streaming is true, show the video stream */}
                    {streaming && (
                        <Box mt={2}>
                            <img
                                src="http://10.242.104.90:5000/api/video_feed"  // Correct URL for the Flask video feed
                                alt="Camera Feed"
                                style={{ width: '100%', maxHeight: '600px' }}
                            />
                        </Box>
                    )}
                </Container>
            </Box>
        </Box>
    );
};

export default AdminDashboard;
