// src/components/Register.js
import React, { useState } from 'react';
import axios from 'axios';
import { Box, Button, Container, TextField, Typography } from '@mui/material';

const Register = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [message, setMessage] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const token = localStorage.getItem('token'); // Assume token is stored in localStorage
            const response = await axios.post('http://localhost:5000/register', {
                username,
                password,
                role: 'Security Staff', // Directly set the role to 'Security Staff'
            }, {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });
            setMessage(response.data.message);
            window.location.reload(); // Reload the page after successful registration
        } catch (error) {
            console.error('Error registering user', error);
            setMessage('Error registering user');
        }
    };

    return (
        <Container maxWidth="xs">
            <Box mt={8} display="flex" flexDirection="column" alignItems="center">
                <Typography variant="h4" gutterBottom>
                    Register
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
                        Register
                    </Button>
                    {message && <Typography color={message.includes('failed') ? 'error' : 'primary'}>{message}</Typography>}
                </Box>
            </Box>
        </Container>
    );
};

export default Register;
