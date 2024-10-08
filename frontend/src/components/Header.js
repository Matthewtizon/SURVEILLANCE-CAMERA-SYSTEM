// src/components/Header.js
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { AppBar, Box, Button, Toolbar, Typography } from '@mui/material';
import ProfileManagement from './ProfileManagement'; // Import ProfileManagement

const Header = ({ dashboardType, username, role }) => {
    const navigate = useNavigate();

    const handleLogout = () => {
        localStorage.removeItem('token');
        navigate('/login');
    };

    return (
        <AppBar position="static">
            <Toolbar>
                <Typography variant="h6" sx={{ flexGrow: 1 }}>
                    {dashboardType} Dashboard
                </Typography>
                <Box display="flex" alignItems="center">
                    <ProfileManagement username={username} role={role} />
                    <Button color="inherit" onClick={handleLogout}>
                        Logout
                    </Button>
                </Box>
            </Toolbar>
        </AppBar>
    );
};

export default Header;
