import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Box, CircularProgress, Container, Typography, Switch, FormControlLabel, Button, Grid } from '@mui/material';
import Header from './Header';
import Sidebar from './SideBar';
import './Loading.css';

const CameraStream = () => {
    const [cameraStatus, setCameraStatus] = useState([]);
    const [selectedCamera, setSelectedCamera] = useState(0);
    const [displayAllCameras, setDisplayAllCameras] = useState(false);
    const [error, setError] = useState(null);
    const [username, setUsername] = useState('');
    const [role, setRole] = useState('');
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const [image, setImage] = useState(null);
    const [uploadError, setUploadError] = useState(null);
    const [images, setImages] = useState([]);  // Initialize images as an empty array

    useEffect(() => {
        const fetchCameraStatus = async () => {
            try {
                const token = localStorage.getItem('token');
                
                const [cameraResponse, userResponse] = await Promise.all([
                    axios.get('http://localhost:5000/cameras', {
                        headers: {
                            Authorization: `Bearer ${token}`,
                        },
                    }),
                    axios.get('http://localhost:5000/protected', {
                        headers: {
                            Authorization: `Bearer ${token}`,
                        },
                    }),
                ]);

                setCameraStatus(cameraResponse.data.cameras);
                const { role, username } = userResponse.data.logged_in_as;
                setUsername(username);
                setRole(role);

                setSelectedCamera(cameraResponse.data.cameras[0]?.camera_id || 0);

                // Fetch images after setting the user info
                fetchImages();
            } catch (error) {
                console.error('Failed to fetch camera status or user info:', error);
                setError('Failed to fetch camera status or user info. Please try again.');
            }
        };

        fetchCameraStatus();
    }, []);

    const fetchImages = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await axios.get('http://localhost:5000/images', {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });
            setImages(response.data || []);  // Ensure response.data is an array
        } catch (error) {
            console.error('Failed to fetch images:', error);
            setError('Failed to fetch images. Please try again.');
        }
    };

    const toggleSidebar = () => {
        setSidebarOpen(!sidebarOpen);
    };

    const handleImageChange = (event) => {
        setImage(event.target.files[0]);
    };

    const handleImageUpload = async () => {
        if (!image) {
            setUploadError('Please select an image to upload.');
            return;
        }

        try {
            const formData = new FormData();
            formData.append('image', image);

            const token = localStorage.getItem('token');
            const response = await axios.post('http://localhost:5000/upload_image', formData, {
                headers: {
                    Authorization: `Bearer ${token}`,
                    'Content-Type': 'multipart/form-data',
                },
            });

            if (response.status === 200) {
                setUploadError(null);
                alert('Image uploaded successfully!');
                setImage(null);
                fetchImages(); // Fetch the images again after uploading
            } else {
                setUploadError('Failed to upload the image.');
            }
        } catch (error) {
            console.error('Error uploading image:', error);
            setUploadError('Error uploading image. Please try again.');
        }
    };

    const renderCameraFeed = (cameraId) => (
        <Box key={cameraId} sx={{ position: 'relative', my: 2, textAlign: 'center' }}>
            <Typography
                variant="caption"
                sx={{
                    position: 'absolute',
                    top: '8px',
                    right: '8px',
                    color: 'white',
                    padding: '2px',
                    fontSize: '0.75rem',
                    fontWeight: 'bold',
                }}
            >
                Camera {cameraId}
            </Typography>
            <img
                src={`http://localhost:5000/video_feed/${cameraId}?token=${localStorage.getItem('token')}`}
                alt={`Camera ${cameraId}`}
                style={{ maxWidth: '100%', maxHeight: '400px', objectFit: 'cover' }}
                onError={(e) => {
                    const { nativeEvent } = e;
                    setError('Failed to load camera feed.');
                    console.error('Error loading camera feed:', nativeEvent);
                }}
            />
        </Box>
    );

    return (
        <Box display="flex">
            <Sidebar isOpen={sidebarOpen} toggleSidebar={toggleSidebar} role={role} />
            <Box className={`main-content ${sidebarOpen ? 'expanded' : 'collapsed'}`} flexGrow={1}>
                <Header dashboardType="Camera Management" username={username} role={role} />
                <Container>
                    {error && <Typography color="error">{error}</Typography>}
                    {cameraStatus.length > 0 ? (
                        <Box>
                            <Box sx={{ mt: 4, textAlign: 'center' }}>
                                <FormControlLabel
                                    control={
                                        <Switch
                                            checked={displayAllCameras}
                                            onChange={() => setDisplayAllCameras(!displayAllCameras)}
                                            name="displayAllCameras"
                                            color="primary"
                                        />
                                    }
                                    label="Display All Cameras"
                                />
                            </Box>
                            {displayAllCameras ? (
                                cameraStatus.map(camera => renderCameraFeed(camera.camera_id))
                            ) : (
                                renderCameraFeed(selectedCamera)
                            )}
                        </Box>
                    ) : (
                        <Box className="loading-container">
                            <CircularProgress />
                        </Box>
                    )}
                    <Box sx={{ mt: 4, textAlign: 'center' }}>
                        <Typography variant="h6">Upload an Image</Typography>
                        <input
                            accept="image/*"
                            id="contained-button-file"
                            type="file"
                            style={{ display: 'none' }}
                            onChange={handleImageChange}
                        />
                        <label htmlFor="contained-button-file">
                            <Button variant="contained" component="span">
                                Choose Image
                            </Button>
                        </label>
                        <Button
                            variant="contained"
                            color="primary"
                            sx={{ ml: 2 }}
                            onClick={handleImageUpload}
                        >
                            Upload
                        </Button>
                        {uploadError && <Typography color="error">{uploadError}</Typography>}
                    </Box>
                    <Box sx={{ mt: 4 }}>
                        <Typography variant="h6">Uploaded Images</Typography>
                        <Grid container spacing={2}>
                            {images.length > 0 ? (
                                images.map((img, index) => (
                                    <Grid item xs={12} sm={6} md={4} key={index}>
                                        <img
                                            src={`http://localhost:5000/images/${img}`}
                                            alt={`Uploaded ${img}`}
                                            style={{ width: '100%', height: 'auto', borderRadius: '4px' }}
                                        />
                                    </Grid>
                                ))
                            ) : (
                                <Typography>No images found.</Typography>
                            )}
                        </Grid>
                    </Box>
                </Container>
            </Box>
        </Box>
    );
};

export default CameraStream;
