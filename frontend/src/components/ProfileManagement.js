// src/components/ProfileManagement.js
import React, { useState, useEffect } from 'react';
import { Menu, MenuItem, Typography, Box, Button, TextField, Dialog, DialogActions, DialogContent, DialogTitle, Snackbar, Slide } from '@mui/material';
import axios from 'axios';
import './Snackbar.css';

const ProfileManagement = ({ username, role }) => {
    const [anchorEl, setAnchorEl] = useState(null);
    const [profile, setProfile] = useState({});
    const [loading, setLoading] = useState(true);
    const [changePasswordOpen, setChangePasswordOpen] = useState(false);
    const [oldPassword, setOldPassword] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [passwordError, setPasswordError] = useState('');
    const [snackbarOpen, setSnackbarOpen] = useState(false);
    const [snackbarMessage, setSnackbarMessage] = useState('');

    const handleClick = (event) => {
        setAnchorEl(event.currentTarget);
    };

    const handleClose = () => {
        setAnchorEl(null);
    };

    const handlePasswordDialogOpen = () => {
        setChangePasswordOpen(true);
        handleClose();
    };

    const handlePasswordDialogClose = () => {
        setChangePasswordOpen(false);
        setOldPassword('');
        setNewPassword('');
        setConfirmPassword('');
        setPasswordError('');
    };

    const handleSnackbarClose = () => {
        setSnackbarOpen(false);
    };

    useEffect(() => {
        const fetchProfileData = async () => {
            const token = localStorage.getItem('token');
            try {
                const response = await axios.get('http://10.242.104.90:5000/api/profile', {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setProfile(response.data);
            } catch (error) {
                console.error('Error fetching profile data:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchProfileData();
    }, []);

    const handleChangePassword = async () => {
        if (newPassword !== confirmPassword) {
            setPasswordError('New passwords do not match');
            setSnackbarMessage('New passwords do not match');
            setSnackbarOpen(true);
            return;
        }

        const token = localStorage.getItem('token');
        try {
            const response = await axios.post('http://10.242.104.90:5000/api/change-password', {
                old_password: oldPassword,
                new_password: newPassword
            }, {
                headers: { Authorization: `Bearer ${token}` }
            });

            if (response.data.success) {
                setSnackbarMessage('Password changed successfully');
                handlePasswordDialogClose();
            } else {
                setPasswordError(response.data.message || 'Password change failed');
                setSnackbarMessage(response.data.message || 'Password change failed');
            }
            setSnackbarOpen(true);
        } catch (error) {
            console.error('Error changing password:', error);
            setPasswordError('An error occurred while changing password');
            setSnackbarMessage('An error occurred while changing password');
            setSnackbarOpen(true);
        }
    };

    return (
        <>
            <Typography variant="body1" color="inherit" onClick={handleClick} sx={{ cursor: 'pointer' }}>
                {username}
            </Typography>
            <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleClose}
            >
                {loading ? (
                    <MenuItem disabled>
                        <Typography>Loading...</Typography>
                    </MenuItem>
                ) : (
                    <>
                        <MenuItem>
                            <Box>
                                <Typography variant="h6">{profile.full_name}</Typography>
                                <Typography variant="body2">Username: {profile.username}</Typography>
                                <Typography variant="body2">Email: {profile.email}</Typography>
                                <Typography variant="body2">Phone: {profile.phone_number}</Typography>
                                <Typography variant="body2">Role: {role}</Typography>
                            </Box>
                        </MenuItem>
                        <MenuItem onClick={handlePasswordDialogOpen}>
                            <Typography variant="body2">Change Password</Typography>
                        </MenuItem>
                    </>
                )}
            </Menu>

            <Dialog open={changePasswordOpen} onClose={handlePasswordDialogClose}>
                <DialogTitle>Change Password</DialogTitle>
                <DialogContent>
                    <TextField
                        margin="dense"
                        label="Old Password"
                        type="password"
                        fullWidth
                        value={oldPassword}
                        onChange={(e) => setOldPassword(e.target.value)}
                    />
                    <TextField
                        margin="dense"
                        label="New Password"
                        type="password"
                        fullWidth
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                    />
                    <TextField
                        margin="dense"
                        label="Confirm New Password"
                        type="password"
                        fullWidth
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                    />
                    {passwordError && <Typography color="error">{passwordError}</Typography>}
                </DialogContent>
                <DialogActions>
                    <Button onClick={handlePasswordDialogClose} color="primary">
                        Cancel
                    </Button>
                    <Button onClick={handleChangePassword} color="primary">
                        Change Password
                    </Button>
                </DialogActions>
            </Dialog>

            <Snackbar
                open={snackbarOpen}
                autoHideDuration={2000}
                onClose={handleSnackbarClose}
                message={snackbarMessage}
                TransitionComponent={SlideTransition}
                classes={{ root: 'snackbar-top-center' }}
            />
        </>
    );
};

// Transition component for Snackbar
const SlideTransition = (props) => {
    return <Slide {...props} direction="down" />;
};

export default ProfileManagement;
