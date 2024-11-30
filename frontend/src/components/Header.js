import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppBar, Box, Button, Toolbar, Typography } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';  // Import menu icon for mobile
import ProfileManagement from './ProfileManagement';
import AuditTrail from './AuditTrail'; // Import the AuditTrail component
import './Header.css'; // Add a CSS file for additional custom styles.

const Header = ({ username, role }) => {
    const navigate = useNavigate();
    const [auditModalOpen, setAuditModalOpen] = useState(false);
    const [sidebarOpen, setSidebarOpen] = useState(false);  // For mobile sidebar toggle

    const handleLogout = () => {
        localStorage.removeItem('token');
        navigate('/login');
    };

    const toggleAuditModal = () => {
        setAuditModalOpen(!auditModalOpen);
    };

    const toggleSidebar = () => {
        setSidebarOpen(!sidebarOpen);
    };

    return (
        <AppBar position="static">
            <Toolbar sx={{ width: '100%', padding: 0 }}>
                <Box 
                    display="flex" 
                    alignItems="center" 
                    sx={{ width: '100%' }}
                >
                    {/* Box for buttons aligned to the right */}
                    <Box display="flex" alignItems="center" gap={2}> {/* Add gap between buttons */}
                        {/* Audit Trail Button */}
                        <Button color="inherit" onClick={toggleAuditModal}>
                            Audit Trail
                        </Button>
                        
                        {/* Profile Management Button */}
                        <ProfileManagement username={username} role={role} />
                        
                        {/* Logout Button */}
                        <Button color="inherit" onClick={handleLogout}>
                            Logout
                        </Button>
                    </Box>
                </Box>
            </Toolbar>

            {/* Audit Trail Modal */}
            {auditModalOpen && <AuditTrail onClose={toggleAuditModal} />}
        </AppBar>
    );
};

export default Header;
