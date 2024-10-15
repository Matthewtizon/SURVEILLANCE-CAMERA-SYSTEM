// src/components/RecordedVideo.js
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Box, CircularProgress, Container, Typography, Grid, Card, CardContent, CardMedia, TextField, Button } from '@mui/material';
import Header from './Header';
import Sidebar from './SideBar';
import './Loading.css';

const RecordedVideo = () => {
    const [loading, setLoading] = useState(true);
    const [username, setUsername] = useState('');
    const [role, setRole] = useState('');
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const [videos, setVideos] = useState([]);
    const [startDate, setStartDate] = useState('');
    const [endDate, setEndDate] = useState('');
    const [loadingVideos, setLoadingVideos] = useState(false); // Separate state for loading videos
    const navigate = useNavigate();

    // Fetch user data on component mount
    useEffect(() => {
        const fetchUserData = async () => {
            const token = localStorage.getItem('token');
            if (!token) {
                navigate('/login');
                return;
            }

            try {
                const response = await axios.get('http://10.242.104.90:5000/protected', {
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

    // Function to fetch videos based on the selected date range
    const fetchVideos = async () => {
        setLoadingVideos(true);
        const token = localStorage.getItem('token');

        try {
            const response = await axios.get(`http://10.242.104.90:5000/get_recorded_videos?start_date=${startDate}&end_date=${endDate}`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setVideos(response.data);
            setLoadingVideos(false);
        } catch (error) {
            console.error('Error fetching videos:', error);
            setLoadingVideos(false);
        }
    };

    const toggleSidebar = () => {
        setSidebarOpen(!sidebarOpen);
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
                <Header dashboardType="Recorded Videos" username={username} role={role} />
                <Container>
                    <Typography variant="h4" gutterBottom>
                        Recorded Videos
                    </Typography>
                    
                    {/* Date range selection */}
                    <Box mb={3} display="flex" alignItems="center" gap={2}>
                        <TextField
                            label="Start Date"
                            type="date"
                            value={startDate}
                            onChange={(e) => setStartDate(e.target.value)}
                            InputLabelProps={{
                                shrink: true,
                            }}
                        />
                        <TextField
                            label="End Date"
                            type="date"
                            value={endDate}
                            onChange={(e) => setEndDate(e.target.value)}
                            InputLabelProps={{
                                shrink: true,
                            }}
                        />
                        <Button variant="contained" onClick={fetchVideos}>
                            Fetch Videos
                        </Button>
                    </Box>

                    {/* Show loading spinner while fetching videos */}
                    {loadingVideos ? (
                        <Box textAlign="center">
                            <CircularProgress />
                            <Typography>Loading videos...</Typography>
                        </Box>
                    ) : (
                        <Grid container spacing={3}>
                            {videos.length === 0 ? (
                                <Typography>No videos found for the selected date range.</Typography>
                            ) : (
                                videos.map((video, index) => (
                                    <Grid item xs={12} sm={6} md={4} key={index}>
                                        <Card>
                                            <CardMedia
                                                component="video"
                                                controls
                                                src={video.url}
                                                title={new Date(video.date).toLocaleString()}
                                            />
                                            <CardContent>
                                                <Typography variant="body1">
                                                    {new Date(video.date).toLocaleString()}
                                                </Typography>
                                            </CardContent>
                                        </Card>
                                    </Grid>
                                ))
                            )}
                        </Grid>
                    )}
                </Container>
            </Box>
        </Box>
    );
};

export default RecordedVideo;
