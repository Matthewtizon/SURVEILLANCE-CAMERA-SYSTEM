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
    const [datasetLoading, setDatasetLoading] = useState(false);
    const [datasets, setDatasets] = useState([]); // State to hold datasets

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
                fetchDataset(); // Fetch datasets
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

    const fetchDataset = async () => {
        const token = localStorage.getItem('token');
        if (!token) {
            navigate('/login');
            return;
        }

        try {
            const response = await axios.get('http://10.242.104.90:5000/api/dataset', {
                headers: { Authorization: `Bearer ${token}` }
            });
            if (response.status === 200) {
                setDatasets(response.data.data);
            }
        } catch (error) {
            console.error('Error fetching dataset:', error);
        }
    };

    const handleCreateDataset = async () => {
        if (!personName) {
            setMessage("Please enter a person's name.");
            return;
        }

        const token = localStorage.getItem('token');

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
                headers: { Authorization: `Bearer ${token}` }
            });

            if (response.status === 200) {
                setMessage(response.data.message);
                fetchDataset(); // Refresh dataset list
            }
        } catch (error) {
            setMessage('Error: ' + error.message);
        } finally {
            setDatasetLoading(false);
        }
    };

    const handleDeleteDataset = async (personName) => {
        const token = localStorage.getItem('token');
        if (!token) {
            navigate('/login');
            return;
        }

        try {
            const response = await axios.delete('http://10.242.104.90:5000/api/dataset', {
                headers: { Authorization: `Bearer ${token}` },
                data: { person_name: personName }
            });

            if (response.status === 200) {
                setDatasets(datasets.filter(dataset => dataset.name !== personName));
                alert(response.data.message);
            }
        } catch (error) {
            console.error('Error deleting dataset:', error);
            alert('Error deleting dataset.');
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

                    {/* Dataset List */}
                    <Box mt={4}>
                        <Typography variant="h5" gutterBottom>
                            Existing Datasets
                        </Typography>
                        <ul>
                            {datasets.map(dataset => (
                                <li key={dataset.name} style={{ display: 'flex', alignItems: 'center', marginBottom: '10px' }}>
                                    <Typography style={{ flex: 1 }}>{dataset.name}</Typography>
                                    <Button
                                        variant="outlined"
                                        color="secondary"
                                        onClick={() => handleDeleteDataset(dataset.name)}
                                    >
                                        Delete
                                    </Button>
                                </li>
                            ))}
                        </ul>
                    </Box>
                </Container>
            </Box>
        </Box>
    );
};

export default AddPerson;
