// src/components/Register.js
import React, { useState } from 'react';
import axios from 'axios';
import { Box, Button, Container, TextField, Typography, MenuItem, Select, InputLabel, FormControl } from '@mui/material';

const Register = ({ refreshUserData, showSnackbarMessage, onSuccess }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [role, setRole] = useState('Security Staff');
    const [message, setMessage] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const token = localStorage.getItem('token'); // Assume token is stored in localStorage
            const response = await axios.post('http://localhost:5000/register', {
                username,
                password,
                role,
            }, {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });
            setMessage(response.data.message);
            showSnackbarMessage(response.data.message); // Show success message
            refreshUserData(); // Refresh the user data
            setUsername(''); // Clear the form fields
            setPassword('');
            setRole('Security Staff'); // Reset role to default
            onSuccess(); // Hide the register form on success
        } catch (error) {
            console.error('Error registering user:', error);
            const errorMessage = 'Error registering user: The user already exists';
            setMessage(errorMessage);
            showSnackbarMessage(errorMessage); // Show error message
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
                    <FormControl fullWidth margin="normal">
                        <InputLabel id="role-label">Role</InputLabel>
                        <Select
                            labelId="role-label"
                            id="role"
                            value={role}
                            label="Role"
                            onChange={(e) => setRole(e.target.value)}
                        >
                            <MenuItem value="Security Staff">Security Staff</MenuItem>
                            <MenuItem value="Assistant Administrator">Assistant Administrator</MenuItem>

                        </Select>
                    </FormControl>
                    <Button
                        type="submit"
                        fullWidth
                        variant="contained"
                        sx={{ mt: 3, mb: 2 }}
                    >
                        Register
                    </Button>
                    {message && <Typography color={message.includes('Error') ? 'error' : 'primary'}>{message}</Typography>}
                </Box>
            </Box>
        </Container>
    );
};

export default Register;
