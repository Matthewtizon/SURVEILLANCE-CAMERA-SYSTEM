import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Box, CircularProgress, Container, Typography, IconButton } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import Header from './Header';
import Sidebar from './SideBar';
import './Dashboard.css'; // Use a separate CSS file for custom styles.

const SecurityDashboard = () => {
    const [loading, setLoading] = useState(true);
    const [username, setUsername] = useState('');
    const [role, setRole] = useState('');
    const [sidebarOpen, setSidebarOpen] = useState(true);
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
                const user = response.data.logged_in_as;
                setUsername(user.username);
                setRole(user.role);
                setLoading(false);
            } catch (error) {
                console.error('Error fetching user data:', error);
                localStorage.removeItem('token');
                navigate('/login');
            }
        };

        fetchUserData();
    }, [navigate]);

    const toggleSidebar = () => {
        setSidebarOpen(!sidebarOpen);
    };

    if (loading) {
        return (
            <Box className="loading-container" display="flex" justifyContent="center" alignItems="center" height="100vh">
                <CircularProgress />
            </Box>
        );
    }

    return (
        <Box display="flex" minHeight="100vh" flexDirection={{ xs: 'column', md: 'row' }}>
            {/* Sidebar - Hidden for smaller screens */}
            {sidebarOpen && (
                <Box display={{ xs: 'none', md: 'block' }}>
                    <Sidebar isOpen={sidebarOpen} toggleSidebar={toggleSidebar} role={role} />
                </Box>
            )}
            {/* Main Content */}
            <Box flexGrow={1} className={`main-content ${sidebarOpen ? 'expanded' : 'collapsed'}`}>
                {/* Header with Mobile Menu Button */}
                <Box display={{ xs: 'flex', md: 'none' }} p={2} alignItems="center" justifyContent="space-between">
                    <IconButton onClick={toggleSidebar}>
                        <MenuIcon />
                    </IconButton>
                    <Typography variant="h6" noWrap>
                        Security Staff Dashboard
                    </Typography>
                </Box>
                {/* Header */}
                <Header dashboardType="Security Staff" username={username} role={role} />

                {/* Content */}
                <Container sx={{ mt: 4 }}>
                    <Typography variant="h4" gutterBottom>
                        Welcome, {username}!
                    </Typography>
                    <Typography variant="subtitle1" gutterBottom color="textSecondary">
                        Role: {role}
                    </Typography>
                </Container>
            </Box>
        </Box>
    );
};

export default SecurityDashboard;
