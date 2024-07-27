// src/components/UserManagement.js
import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Container, Button, Table, TableBody, TableCell, TableHead, TableRow, Typography, Box, Modal, CircularProgress, Snackbar, Slide } from '@mui/material';
import Header from './Header';
import Sidebar from './SideBar';
import Register from './Register';
import './UserManagement.css'; // Import the CSS file
import './Loading.css';

const UserManagement = () => {
    const [loading, setLoading] = useState(true);
    const [users, setUsers] = useState([]);
    const [showRegisterForm, setShowRegisterForm] = useState(false);
    const [username, setUsername] = useState('');
    const [role, setRole] = useState('');
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const [snackbarOpen, setSnackbarOpen] = useState(false);
    const [userToDelete, setUserToDelete] = useState(null);
    const navigate = useNavigate();

    const fetchUserData = useCallback(async () => {
        const token = localStorage.getItem('token');
        if (!token) {
            navigate('/login');
            return;
        }

        try {
            const response = await axios.get('http://localhost:5000/protected', {
                headers: { Authorization: `Bearer ${token}` }
            });
            setUsername(response.data.logged_in_as.username);
            setRole(response.data.logged_in_as.role);

            const userResponse = await axios.get('http://localhost:5000/users', {
                headers: { Authorization: `Bearer ${token}` }
            });
            setUsers(userResponse.data);
            setLoading(false);
        } catch (error) {
            console.error('Error fetching user data:', error);
            localStorage.removeItem('token');
            navigate('/login');
        }
    }, [navigate]);

    useEffect(() => {
        fetchUserData();
    }, [fetchUserData]);

    const deleteUser = async () => {
        if (!userToDelete) return;
        
        const token = localStorage.getItem('token');

        try {
            const response = await axios.delete(`http://localhost:5000/users/${userToDelete}`, {
                headers: { Authorization: `Bearer ${token}` }
            });

            if (response.status === 200) {
                setUsers(users.filter(user => user.user_id !== userToDelete));
                setSnackbarOpen(false); // Close snackbar if deletion is successful
                setUserToDelete(null); // Clear user to delete
            }
        } catch (error) {
            console.error('Error deleting user:', error);
            setSnackbarOpen(false); // Close snackbar on error as well
            setUserToDelete(null); // Clear user to delete
        }
    };

    const handleDeleteClick = (userId) => {
        if (role === 'Security Staff') {
            setUserToDelete(userId);
            setSnackbarOpen(true);
            // Automatically close the snackbar after 2 seconds
            setTimeout(() => {
                setSnackbarOpen(false);
                setUserToDelete(null);
            }, 2000);
        } else {
            deleteUser(userId);
        }
    };

    const toggleRegisterForm = () => {
        setShowRegisterForm(!showRegisterForm);
    };

    const toggleSidebar = () => {
        setSidebarOpen(!sidebarOpen);
    };

    const handleSnackbarClose = () => {
        setSnackbarOpen(false);
    };

    return (
        <Box display="flex">
            <Sidebar isOpen={sidebarOpen} toggleSidebar={toggleSidebar} role={role} />
            <Box className={`main-content ${sidebarOpen ? 'expanded' : 'collapsed'}`} flexGrow={1}>
                <Header dashboardType="User Management" username={username} role={role} />
                <Container>
                    {loading ? (
                        <Box className="loading-container">
                            <CircularProgress />
                        </Box>
                    ) : (
                        <>
                            <Typography variant="h4">User List</Typography>
                            <Table>
                                <TableHead>
                                    <TableRow>
                                        <TableCell>ID</TableCell>
                                        <TableCell>Username</TableCell>
                                        <TableCell>Role</TableCell>
                                        <TableCell>Actions</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {users.map(user => (
                                        <TableRow key={user.user_id}>
                                            <TableCell>{user.user_id}</TableCell>
                                            <TableCell>{user.username}</TableCell>
                                            <TableCell>{user.role}</TableCell>
                                            <TableCell>
                                                <Button
                                                    variant="contained"
                                                    color="secondary"
                                                    onClick={() => handleDeleteClick(user.user_id)}
                                                >
                                                    Delete
                                                </Button>
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                            <Button
                                variant="contained"
                                color="primary"
                                onClick={toggleRegisterForm}
                                className="toggle-button"
                                style={{ position: 'absolute', bottom: 20, right: 20 }}
                            >
                                {showRegisterForm ? 'Hide Register Form' : 'Show Register Form'}
                            </Button>
                            <Modal
                                open={showRegisterForm}
                                onClose={toggleRegisterForm}
                                aria-labelledby="register-modal-title"
                                aria-describedby="register-modal-description"
                            >
                                <Box className="modal-box">
                                    <Register refreshUserData={fetchUserData} />
                                </Box>
                            </Modal>

                            <Snackbar
                                open={snackbarOpen}
                                autoHideDuration={2000}
                                onClose={handleSnackbarClose}
                                message="Security Staff cannot delete users. This action will be aborted."
                                TransitionComponent={SlideTransition}
                                sx={{ top: 50 }} // Position the Snackbar 20px from the top
                            />
                        </>
                    )}
                </Container>
            </Box>
        </Box>
    );
};

// Transition component for Snackbar
const SlideTransition = (props) => {
    return <Slide {...props} direction="down" />;
};

export default UserManagement;
