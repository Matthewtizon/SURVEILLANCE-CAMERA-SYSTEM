import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Box, CircularProgress, Container, Typography, TextField, Button } from '@mui/material';
import Header from './Header';
import Sidebar from './SideBar';
import './Loading.css';

const AddPerson = () => {
    const [loading, setLoading] = useState(true);
    const [username, setUsername] = useState('');
    const [role, setRole] = useState('');
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const navigate = useNavigate();
    const [personName, setPersonName] = useState('');
    const [message, setMessage] = useState('');
    const [datasetLoading, setDatasetLoading] = useState(false);  // New state for dataset loading

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

    const toggleSidebar = () => {
        setSidebarOpen(!sidebarOpen);
    };

    const handleCreateDataset = async () => {
        if (!personName) {
            setMessage("Please enter a person's name.");
            return;
        }
    
        const token = localStorage.getItem('token');  // Get token from localStorage
    
        if (!token) {
            setMessage('You are not authorized. Please login.');
            return;
        }
    
        setDatasetLoading(true);
        setMessage('');
    
        try {
            const response = await axios.post('http://10.242.104.90:5000/create-dataset', {
                person_name: personName
            }, {
                headers: { Authorization: `Bearer ${token}` }  // Add token to headers
            });
    
            if (response.status === 200) {
                setMessage(response.data.message);
            }
        } catch (error) {
            setMessage('Error: ' + error.message);
        } finally {
            setDatasetLoading(false);
        }
    };
    
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
                <Header dashboardType="Face Management" username={username} role={role} />
                <Container>
                    <Typography variant="h4" gutterBottom>
                        Welcome to the Face Management Dashboard {username}
                    </Typography>

                    {/* Add Person Form */}
                    <Box>
                        <Typography variant="h5" gutterBottom>
                            Add Person Directory
                        </Typography>
                        <TextField
                            label="Enter Person's Name"
                            variant="outlined"
                            fullWidth
                            value={personName}
                            onChange={(e) => setPersonName(e.target.value)}
                            margin="normal"
                        />
                        <Button
                            variant="contained"
                            color="primary"
                            onClick={handleCreateDataset}
                            disabled={datasetLoading}
                        >
                            {datasetLoading ? 'Creating Dataset...' : 'Create Dataset'}
                        </Button>

                        {message && <Typography variant="body2" color="error">{message}</Typography>}
                    </Box>
                </Container>
            </Box>
        </Box>
    );
};

export default AddPerson;
