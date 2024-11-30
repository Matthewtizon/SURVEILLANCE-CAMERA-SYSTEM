// src/components/UserManagement.js
import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
    Container,
    Button,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Typography,
    Box,
    Modal,
    CircularProgress,
    Snackbar,
    Slide,
    Dialog,
    DialogActions,
    TextField,
    DialogContent,
    DialogContentText,
    DialogTitle
} from '@mui/material';
import Header from './Header';
import Sidebar from './SideBar';
import Register from './Register';
import './UserManagement.css'; // Import the CSS file
import './Snackbar.css';

const UserManagement = () => {
    const [loading, setLoading] = useState(true);
    const [users, setUsers] = useState([]);
    const [showRegisterForm, setShowRegisterForm] = useState(false);
    const [username, setUsername] = useState('');
    const [role, setRole] = useState('');
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const [snackbarOpen, setSnackbarOpen] = useState(false);
    const [snackbarMessage, setSnackbarMessage] = useState('');
    const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
    const [userToDelete, setUserToDelete] = useState(null);
    const navigate = useNavigate();
    const [editDialogOpen, setEditDialogOpen] = useState(false);
    const [userToEdit, setUserToEdit] = useState(null); 

    const fetchUserData = useCallback(async () => {
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

            const userResponse = await axios.get('http://10.242.104.90:5000/api/users', {
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
        const token = localStorage.getItem('token');

        try {
            const response = await axios.delete(`http://10.242.104.90:5000/api/users/${userToDelete.user_id}`, {
                headers: { Authorization: `Bearer ${token}` }
            });

            if (response.status === 200) {
                setUsers(users.filter(user => user.user_id !== userToDelete.user_id));
                setSnackbarMessage('User deleted successfully unsubscribed to notifications!.');
                setSnackbarOpen(true);
                setDeleteDialogOpen(false);
                setUserToDelete(null);
            }
        } catch (error) {
            console.error('Error deleting user:', error);
        }
    };

    const handleDeleteClick = (user) => {
        if (role === 'Security Staff') {
            setSnackbarMessage('Security Staff cannot delete users. This action will be aborted.');
            setSnackbarOpen(true);
            setTimeout(() => {
                setSnackbarOpen(false);
            }, 2000);
        } else if (username === user.username) {
            setSnackbarMessage('You cannot delete your own account.');
            setSnackbarOpen(true);
            setTimeout(() => {
                setSnackbarOpen(false);
            }, 2000);
        } else if (role === 'Assistant Administrator' && user.role === 'Administrator') {
            setSnackbarMessage('Based on your role, you can only delete Security Staff accounts.');
            setSnackbarOpen(true);
            setTimeout(() => {
                setSnackbarOpen(false);
            }, 2000);
        } else {
            setUserToDelete(user);
            setDeleteDialogOpen(true);
        }
    };

    const handleSaveEdit = async () => {
        const token = localStorage.getItem('token');
        try {
            const response = await axios.put(
                `http://10.242.104.90:5000/api/users/${userToEdit.user_id}`,
                userToEdit,
                {
                    headers: { Authorization: `Bearer ${token}` }
                }
            );
    
            if (response.status === 200) {
                setUsers((prevUsers) =>
                    prevUsers.map((user) =>
                        user.user_id === userToEdit.user_id ? userToEdit : user
                    )
                );
                setSnackbarMessage('User updated successfully update subscription to notifications!.');
                setSnackbarOpen(true);
                setEditDialogOpen(false);
            }
        } catch (error) {
            console.error('Error updating user:', error);
        }
    };

    const toggleRegisterForm = () => {
        if (role === 'Administrator' || role === 'Assistant Administrator') {
            setShowRegisterForm(!showRegisterForm);
        } else {
            setSnackbarMessage('Only administrators and assistant administrators can access the register form.');
            setSnackbarOpen(true);
        }
    };

    const handleEditClick = (user) => {
        setUserToEdit(user);
        setEditDialogOpen(true);
    };

    const toggleSidebar = () => {
        setSidebarOpen(!sidebarOpen);
    };

    const handleSnackbarClose = () => {
        setSnackbarOpen(false);
    };

    const showSnackbarMessage = (message) => {
        setSnackbarMessage(message);
        setSnackbarOpen(true);
    };

    const handleRegisterSuccess = () => {
        setShowRegisterForm(false); // Close the register modal
        fetchUserData(); // Refresh the user data
    };

    const handleDeleteDialogClose = () => {
        setDeleteDialogOpen(false);
        setUserToDelete(null);
    };

    useEffect(() => {
        const handleResize = () => {
            if (window.innerWidth < 600) {
                setSidebarOpen(false);
            } else {
                setSidebarOpen(true);
            }
        };

        window.addEventListener('resize', handleResize);
        handleResize();

        return () => window.removeEventListener('resize', handleResize);
    }, []);

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
                            <TableContainer style={{ overflowX: 'auto' }}>
                                <Table>
                                    <TableHead>
                                        <TableRow>
                                            <TableCell>ID</TableCell>
                                            <TableCell>Username</TableCell>
                                            <TableCell>Full Name</TableCell>
                                            <TableCell>Email</TableCell>
                                            <TableCell>Phone Number</TableCell>
                                            <TableCell>Role</TableCell>
                                            <TableCell>Actions</TableCell>
                                        </TableRow>
                                    </TableHead>
                                    <TableBody>
                                        {users.map((user) => (
                                            <TableRow key={user.user_id}>
                                                <TableCell>{user.user_id}</TableCell>
                                                <TableCell>{user.username}</TableCell>
                                                <TableCell>{user.full_name}</TableCell>
                                                <TableCell>{user.email}</TableCell>
                                                <TableCell>{user.phone_number}</TableCell>
                                                <TableCell>{user.role}</TableCell>
                                                <TableCell>
                                                    <Box display="flex" flexDirection="column">
                                                        <Button
                                                            variant="contained"
                                                            color="primary"
                                                            onClick={() => handleEditClick(user)}
                                                            style={{ marginBottom: '8px' }}
                                                        >
                                                            Edit
                                                        </Button>
                                                        <Button
                                                            variant="contained"
                                                            color="secondary"
                                                            onClick={() => handleDeleteClick(user)}
                                                        >
                                                            Delete
                                                        </Button>
                                                    </Box>
                                                </TableCell>
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>
                            </TableContainer>

                            <Box style={{ marginTop: '20px' }}>
                                <Button
                                    variant="contained"
                                    color="primary"
                                    onClick={toggleRegisterForm}
                                    className="toggle-button"
                                >
                                    {showRegisterForm ? 'Hide Register Form' : 'Show Register Form'}
                                </Button>

                                <Modal
                                    open={showRegisterForm}
                                    onClose={toggleRegisterForm}
                                    aria-labelledby="register-modal-title"
                                    aria-describedby="register-modal-description"
                                >
                                    <Box className="modal-content">
                                        <Register 
                                            refreshUserData={fetchUserData} 
                                            showSnackbarMessage={showSnackbarMessage} 
                                            onSuccess={handleRegisterSuccess} 
                                        />
                                    </Box>
                                </Modal>
                            </Box>
                        </>
                    )}
                </Container>

                <Snackbar
                    open={snackbarOpen}
                    onClose={handleSnackbarClose}
                    message={snackbarMessage}
                    TransitionComponent={Slide}
                    autoHideDuration={3000}
                />

                {/* Delete Dialog */}
                <Dialog open={deleteDialogOpen} onClose={handleDeleteDialogClose}>
                    <DialogTitle>Confirm Deletion</DialogTitle>
                    <DialogContent>
                        <DialogContentText>
                            Are you sure you want to delete the user {userToDelete?.username}?
                        </DialogContentText>
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={handleDeleteDialogClose} color="primary">
                            Cancel
                        </Button>
                        <Button onClick={deleteUser} color="secondary">
                            Delete
                        </Button>
                    </DialogActions>
                </Dialog>

                {/* Edit Dialog */}
                <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)}>
                    <DialogTitle>Edit User</DialogTitle>
                    <DialogContent>
                        <DialogContentText>
                            Edit the details of the user.
                        </DialogContentText>
                        <TextField
                            label="Username"
                            value={userToEdit?.username || ''}
                            onChange={(e) =>
                                setUserToEdit({ ...userToEdit, username: e.target.value })
                            }
                            fullWidth
                            margin="normal"
                        />
                        <TextField
                            label="Full Name"
                            value={userToEdit?.full_name || ''}
                            onChange={(e) =>
                                setUserToEdit({ ...userToEdit, full_name: e.target.value })
                            }
                            fullWidth
                            margin="normal"
                        />
                        <TextField
                            label="Email"
                            value={userToEdit?.email || ''}
                            onChange={(e) =>
                                setUserToEdit({ ...userToEdit, email: e.target.value })
                            }
                            fullWidth
                            margin="normal"
                        />
                        <TextField
                            label="Phone Number"
                            value={userToEdit?.phone_number || ''}
                            onChange={(e) =>
                                setUserToEdit({ ...userToEdit, phone_number: e.target.value })
                            }
                            fullWidth
                            margin="normal"
                        />
                        <TextField
                            label="Role"
                            value={userToEdit?.role || ''}
                            onChange={(e) =>
                                setUserToEdit({ ...userToEdit, role: e.target.value })
                            }
                            fullWidth
                            margin="normal"
                        />
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={() => setEditDialogOpen(false)} color="primary">
                            Cancel
                        </Button>
                        <Button onClick={handleSaveEdit} color="secondary">
                            Save
                        </Button>
                    </DialogActions>
                </Dialog>
            </Box>
        </Box>
    );
};

export default UserManagement;
