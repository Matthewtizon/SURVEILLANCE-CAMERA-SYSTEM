// src/components/Header.js
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppBar, Box, Button, Toolbar, Typography } from '@mui/material';
import ProfileManagement from './ProfileManagement';
import AuditTrail from './AuditTrail'; // Import the AuditTrail component

const Header = ({ dashboardType, username, role }) => {
    const navigate = useNavigate();
    const [auditModalOpen, setAuditModalOpen] = useState(false);

    const handleLogout = () => {
        localStorage.removeItem('token');
        navigate('/login');
    };

    const toggleAuditModal = () => {
        setAuditModalOpen(!auditModalOpen);
    };

    return (
        <AppBar position="static">
            <Toolbar>
                <Typography variant="h6" sx={{ flexGrow: 1 }}>
                    {dashboardType} Dashboard
                </Typography>
                <Box display="flex" alignItems="center">
                    <Button color="inherit" onClick={toggleAuditModal}>
                        Audit Trail
                    </Button>
                    <ProfileManagement username={username} role={role} />
                    <Button color="inherit" onClick={handleLogout}>
                        Logout
                    </Button>
                </Box>
            </Toolbar>
            {/* Audit Trail Modal */}
            {auditModalOpen && <AuditTrail onClose={toggleAuditModal} />}
        </AppBar>
    );
};

export default Header;
