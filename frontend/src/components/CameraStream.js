import React, { useEffect, useState, useRef } from 'react';
import axios from 'axios';
import io from 'socket.io-client';
import { Box, Container, Typography, Button, Grid, TextField } from '@mui/material';
import Header from './Header';
import Sidebar from './SideBar';

const CameraStream = () => {
    const [error, setError] = useState(null);
    const [username, setUsername] = useState('');
    const [role, setRole] = useState('');
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const [isCameraOpen, setIsCameraOpen] = useState({});
    const [cameras, setCameras] = useState([]);
    const [newCameraName, setNewCameraName] = useState('');
    const [newCameraRTSP, setNewCameraRTSP] = useState('');
    const [editCameraName, setEditCameraName] = useState('');
    const [editCameraRTSP, setEditCameraRTSP] = useState('');
    const [editingCameraId, setEditingCameraId] = useState(null);
    const cameraRefs = useRef({});  // Use useRef to keep track of image elements

    const socket = io('http://10.242.104.90:5000', {
        transports: ['websocket'],
    });

    useEffect(() => {
        const fetchUserData = async () => {
            try {
                const token = localStorage.getItem('token');
                const userResponse = await axios.get('http://10.242.104.90:5000/api/protected', {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });
                const { role, username } = userResponse.data.logged_in_as;
                setUsername(username);
                setRole(role);
            } catch (error) {
                console.error('Failed to fetch user info:', error);
                setError('Failed to fetch user info. Please try again.');
            }
        };

        const fetchCameras = async () => {
            try {
                const token = localStorage.getItem('token');
                const camerasResponse = await axios.get('http://10.242.104.90:5000/api/cameras', {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });
                setCameras(camerasResponse.data);
            } catch (error) {
                console.error('Failed to fetch cameras:', error);
                setError('Failed to fetch cameras. Please try again.');
            }
        };

        const fetchCameraStatus = async () => {
            try {
                const token = localStorage.getItem('token');
                const statusResponse = await axios.get('http://10.242.104.90:5000/api/camera_status', {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });
                setIsCameraOpen(statusResponse.data);
            } catch (error) {
                console.error('Failed to fetch camera status:', error);
                setError('Failed to fetch camera status. Please try again.');
            }
        };

        fetchUserData();
        fetchCameras();
        fetchCameraStatus();


        // Listen for video frames from the server
        socket.on('video_frame', (data) => {
            const { camera_ip, frame } = data;
            const base64Frame = `data:image/jpeg;base64,${btoa(
                String.fromCharCode(...new Uint8Array(frame))
            )}`;
            const imgElement = document.getElementById(`camera-${camera_ip}`);
            if (imgElement) {
                imgElement.src = base64Frame;
            }
        });

        // Listen for video frames from the server
        socket.on('video_frame', (data) => {
            const { camera_id, frame } = data;
            const base64Frame = `data:image/jpeg;base64,${btoa(
                String.fromCharCode(...new Uint8Array(frame))
            )}`;

            if (cameraRefs.current[camera_id]) {
                cameraRefs.current[camera_id].src = base64Frame;  // Directly update image element
            }
        });

        // Listen for camera status changes
        socket.on('camera_status_changed', (data) => {
            const { camera_ip, status } = data;
            setIsCameraOpen((prev) => ({
                ...prev,
                [camera_ip]: status,
            }));
        });

        return () => {
            socket.disconnect();
        };
    }, []);

    const toggleSidebar = () => {
        setSidebarOpen(!sidebarOpen);
    };

    const openCamera = async (cameraIp) => {
        try {
            const token = localStorage.getItem('token');
            const response = await axios.get(`http://10.242.104.90:5000/api/open_camera/${cameraIp}`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });
            setIsCameraOpen((prev) => ({ ...prev, [cameraIp]: true }));
            console.log(response.data.message);
        } catch (error) {
            console.error('Failed to open camera:', error);
        }
    };

    const closeCamera = async (cameraIp) => {
        try {
            const token = localStorage.getItem('token');
            const response = await axios.get(`http://10.242.104.90:5000/api/close_camera/${cameraIp}`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });
            setIsCameraOpen((prev) => ({ ...prev, [cameraIp]: false }));
            console.log(response.data.message);
        } catch (error) {
            console.error('Failed to close camera:', error);
        }
    };

    // Function to add a new camera
    const addCamera = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await axios.post('http://10.242.104.90:5000/api/cameras', {
                name: newCameraName,
                rtsp_url: newCameraRTSP,
            }, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });
            setCameras([...cameras, response.data.camera]);
            setNewCameraName('');
            setNewCameraRTSP('');
        } catch (error) {
            console.error('Failed to add camera:', error);
            setError('Failed to add camera. Please check the details and try again.');
        }
    };

    // Function to update an existing camera
    const updateCamera = async (cameraId) => {
        try {
            const token = localStorage.getItem('token');
            const response = await axios.put(`http://10.242.104.90:5000/api/cameras/${cameraId}`, {
                name: editCameraName,
                // rtsp_url: editCameraRTSP,
            }, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });
            const updatedCamera = response.data.camera;
            setCameras((prevCameras) =>
                prevCameras.map((camera) =>
                    camera.id === updatedCamera.id ? updatedCamera : camera
                )
            );
            setEditingCameraId(null);
            setEditCameraName('');
            //setEditCameraRTSP('');
        } catch (error) {
            console.error('Failed to update camera:', error);
            setError('Failed to update camera. Please try again.');
        }
    };

    // Function to delete a camera
    const deleteCamera = async (cameraId, rtspUrl) => {
        try {
            const token = localStorage.getItem('token');
            await axios.delete(`http://10.242.104.90:5000/api/cameras/${cameraId}`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
                data: { rtsp_url: rtspUrl },  // Send rtsp_url in the request body
            });
            setCameras((prevCameras) => prevCameras.filter((camera) => camera.id !== cameraId));
        } catch (error) {
            console.error('Failed to delete camera:', error);
            setError('Failed to delete camera. Please try again.');
        }
    };

    // Responsive handling for mobile layout
    useEffect(() => {
        const handleResize = () => {
            if (window.innerWidth < 600) {
                setSidebarOpen(false); // Auto-collapse sidebar on small screens
            } else {
                setSidebarOpen(true);  // Expand sidebar on larger screens
            }
        };

        window.addEventListener('resize', handleResize);
        handleResize(); // Initial check

        return () => window.removeEventListener('resize', handleResize);
    }, []);

    return (
        <Box display="flex">
            <Sidebar isOpen={sidebarOpen} toggleSidebar={toggleSidebar} role={role} />
            <Box className={`main-content ${sidebarOpen ? 'expanded' : 'collapsed'}`} flexGrow={1}>
                <Header dashboardType="Camera" username={username} role={role} />
                <Container>
                    {error && <Typography color="error">{error}</Typography>}
                    <Box sx={{ mt: 4 }}>
                        <Typography variant="h6">Camera Management</Typography>


                        {[0].map((cameraIp) => (
                            <Box key={cameraIp} sx={{ mb: 2 }}>
                                <Typography variant="subtitle1">Camera {cameraIp}</Typography>
                                <Button variant="contained" onClick={() => openCamera(cameraIp)} disabled={isCameraOpen[cameraIp]}>
                                    Open Camera
                                </Button>
                                <Button variant="contained" onClick={() => closeCamera(cameraIp)} disabled={!isCameraOpen[cameraIp]} sx={{ ml: 1 }}>
                                    Close Camera
                                </Button>
                                <img id={`camera-${cameraIp}`} alt={`Camera ${cameraIp}`} style={{ width: '320px', height: '240px', display: isCameraOpen[cameraIp] ? 'block' : 'none' }} />
                            </Box>
                        ))}

                        {/* Add Camera Form */}
                        <Box sx={{ mb: 4 }}>
                            <Typography variant="subtitle1">Add New Camera</Typography>
                            <Grid container spacing={2} alignItems="center">
                                <Grid item xs={12} sm={4}>
                                    <TextField
                                        label="Camera Name"
                                        value={newCameraName}
                                        onChange={(e) => setNewCameraName(e.target.value)}
                                        fullWidth
                                    />
                                </Grid>
                                <Grid item xs={12} sm={6}>
                                    <TextField
                                        label="RTSP URL"
                                        value={newCameraRTSP}
                                        onChange={(e) => setNewCameraRTSP(e.target.value)}
                                        fullWidth
                                    />
                                </Grid>
                                <Grid item xs={12} sm={2}>
                                    <Button variant="contained" color="primary" onClick={addCamera} fullWidth>
                                        Add Camera
                                    </Button>
                                </Grid>
                            </Grid>
                        </Box>

                        {/* List of Cameras */}
                        <Grid container spacing={4}>
                            {cameras.map((camera) => (
                                <Grid item xs={12} sm={6} md={4} key={camera.id}>
                                    <Box sx={{ border: '1px solid #ccc', borderRadius: '8px', p: 2 }}>
                                        <Typography variant="h6">{camera.name}</Typography>
                                        
                                        {/* Video Stream */}
                                        <Box sx={{ mt: 2 }}>
                                            <img
                                                ref={(el) => (cameraRefs.current[camera.id] = el)}
                                                alt={`Camera ${camera.id}`}
                                                style={{ width: '100%', height: 'auto' }}
                                            />
                                            <p>{camera.name}</p>
                                        </Box>

                                        {editingCameraId === camera.id ? (
                                            <Box>
                                                <TextField
                                                    label="Edit Camera Name"
                                                    value={editCameraName}
                                                    onChange={(e) => setEditCameraName(e.target.value)}
                                                    fullWidth
                                                />
                                                <Button variant="contained" color="primary" onClick={() => updateCamera(camera.id)} fullWidth>
                                                    Save Changes
                                                </Button>
                                            </Box>
                                        ) : (
                                            <Box sx={{ mt: 2 }}>
                                                <Button
                                                    variant="contained"
                                                    color="primary"
                                                    onClick={() => {
                                                        setEditingCameraId(camera.id);
                                                        setEditCameraName(camera.name);
                                                        setEditCameraRTSP(camera.rtsp_url);
                                                    }}
                                                    fullWidth
                                                >
                                                    Edit
                                                </Button>
                                            </Box>
                                        )}
                                        <Button variant="contained" color="error" onClick={() => deleteCamera(camera.id, camera.rtsp_url)} fullWidth sx={{ mt: 1 }}>
                                            Delete
                                        </Button>
                                    </Box>
                                </Grid>
                            ))}
                        </Grid>
                    </Box>
                </Container>
            </Box>
        </Box>
    );
};

export default CameraStream;
