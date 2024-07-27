// src/components/UserManagement.js
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Container, Button, Table, TableBody, TableCell, TableHead, TableRow, Typography, Box } from '@mui/material';
import Header from './Header';
import Sidebar from './SideBar';
import Register from './Register';
import './UserManagement.css';

const UserManagement = () => {
    const [loading, setLoading] = useState(true);
    const [users, setUsers] = useState([]);
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
        };

        fetchUserData();
    }, [navigate]);

    const deleteUser = async (userId) => {
        const token = localStorage.getItem('token');

        try {
            const response = await axios.delete(`http://localhost:5000/users/${userId}`, {
                headers: { Authorization: `Bearer ${token}` }
            });

            if (response.status === 200) {
                setUsers(users.filter(user => user.user_id !== userId));
            }
        } catch (error) {
            console.error('Error deleting user:', error);
        }
    };

    const openRegisterWindow = () => {
        window.open('/register', '_blank', 'width=600,height=400'); // Adjust size as needed
    };

    const toggleSidebar = () => {
        setSidebarOpen(!sidebarOpen);
    };

    if (loading) {
        return <div>Loading...</div>;
    }

    return (
        <Box display="flex" flexDirection="column" flexGrow={1}>
            <Sidebar isOpen={sidebarOpen} toggleSidebar={toggleSidebar} role={role} />
            <Box className={`main-content ${sidebarOpen ? 'expanded' : 'collapsed'}`} flexGrow={1}>
                <Header dashboardType="Administrator" username={username} role={role} />
                <Container>
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
                                            onClick={() => deleteUser(user.user_id)}
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
                        onClick={openRegisterWindow} 
                        className="register-button"
                    >
                        Register New User
                    </Button>
                </Container>
            </Box>
        </Box>
    );
};

export default UserManagement;
