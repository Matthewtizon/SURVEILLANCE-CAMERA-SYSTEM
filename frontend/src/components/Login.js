import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Box, Button, Container, TextField, Typography } from '@mui/material';
import { requestFCMToken } from '../firebase'; // Import the function to get FCM token

const Login = ({ setRole }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();
    const [deviceToken, setDeviceToken] = useState(null);

    useEffect(() => {
        // Request FCM token on component mount
        const getToken = async () => {
            const token = await requestFCMToken();
            setDeviceToken(token); // Store the FCM token in the state
        };

        getToken();
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post('http://10.242.104.90:5000/login', {
                username,
                password,
                device_token: deviceToken, // Include the FCM token
            }, {
                headers: {
                    'Content-Type': 'application/json'
                },
                withCredentials: true
            });
            
            const { access_token, user_info } = response.data;

            if (!user_info || !user_info.role) {
                setError('Role not found in response data');
                return;
            }

            localStorage.setItem('token', access_token);
            setRole(user_info.role);

            if (user_info.role === 'Administrator') {
                navigate('/admin-dashboard');
            } else if (user_info.role === 'Security Staff') {
                navigate('/security-dashboard');
            } else if (user_info.role === 'Assistant Administrator') {
                navigate('/admin-dashboard'); // Adjust the route based on your needs
            } else {
                setError('Unknown role');
            }
        } catch (err) {
            console.error('Login Error:', err);
            setError('Invalid credentials');
        }
    };

    return (
        <Container maxWidth="xs">
            <Box mt={8} display="flex" flexDirection="column" alignItems="center">
                <Typography variant="h4" gutterBottom>
                    Login
                </Typography>
                <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
                    <TextField
                        margin="normal"
                        required
                        fullWidth
                        id="username"
                        label="Username"
                        name="username"
                        autoComplete="username"
                        autoFocus
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                    />
                    <TextField
                        margin="normal"
                        required
                        fullWidth
                        name="password"
                        label="Password"
                        type="password"
                        id="password"
                        autoComplete="current-password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />
                    <Button
                        type="submit"
                        fullWidth
                        variant="contained"
                        sx={{ mt: 3, mb: 2 }}
                    >
                        Login
                    </Button>
                    {error && <Typography color="error">{error}</Typography>}
                </Box>
            </Box>
        </Container>
    );
};

export default Login;
