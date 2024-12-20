// src/components/Login.js
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Box, Button, Container, TextField, Typography, Grid, Paper } from '@mui/material';

const Login = ({ setRole }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post('http://10.242.104.90:5000/api/login', {
                username,
                password,
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
        <Container maxWidth="md">
            <Paper elevation={3} sx={{ mt: 8, p: 4 }}>
                <Grid container spacing={4} alignItems="center">
                    {/* Left Side - Title and Description */}
                    <Grid item xs={12} md={6}>
                        <Box display="flex" flexDirection="column" alignItems="center">
                            <Typography variant="h3" gutterBottom sx={{ fontWeight: 'bold', textAlign: 'center' }}>
                                Face Recognition
                            </Typography>
                            <Typography variant="h5" color="textSecondary" gutterBottom sx={{ textAlign: 'center' }}>
                                Intruder Detection System
                            </Typography>
                            <Typography variant="body1" color="textSecondary" sx={{ textAlign: 'center', mt: 2 }}>
                                Secure access and monitor intrusions efficiently with our advanced face recognition system.
                            </Typography>
                        </Box>
                    </Grid>
                    {/* Right Side - Login Form */}
                    <Grid item xs={12} md={6}>
                        <Box display="flex" flexDirection="column" alignItems="center">
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
                    </Grid>
                </Grid>
            </Paper>
        </Container>
    );
};

export default Login;
