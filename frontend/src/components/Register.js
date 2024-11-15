// src/components/Register.js
import React, { useState } from 'react';
import axios from 'axios';
import { Box, Button, Container, TextField, Typography, MenuItem, Select, InputLabel, FormControl } from '@mui/material';

const Register = ({ refreshUserData, showSnackbarMessage, onSuccess }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [role, setRole] = useState('');
    const [full_name, setFullname ] = useState('');
    const [email, setEmail ] = useState('');
    const [phone_number, setPhonenumber ] = useState('');
    const [message, setMessage] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const token = localStorage.getItem('token'); // Assume token is stored in localStorage
            const response = await axios.post('http://10.242.104.90:5000/api/register', {
                username,
                password,
                role,
                full_name,
                email,
                phone_number
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
            setRole(''); // Reset role to default
            setFullname('');
            setEmail('');
            setPhonenumber('');
            onSuccess(); // Hide the register form on success
        } catch (error) {
            console.error('Error registering user:', error);
            const errorMessage = error.response?.data?.message || 'Error registering user';
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
                    <TextField
                        margin="normal"
                        required
                        fullWidth
                        name="full_name"
                        label="full_name"
                        type="full_name"
                        id="full_name"
                        autoComplete="full_name"
                        value={full_name}
                        onChange={(e) => setFullname(e.target.value)}
                    />
                    <TextField
                        margin="normal"
                        required
                        fullWidth
                        name="email"
                        label="email"
                        type="email"
                        id="email"
                        autoComplete="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                    />
                    <TextField
                        margin="normal"
                        required
                        fullWidth
                        name="phone_number"
                        label="phone_number"
                        type="phone_number"
                        id="phone_number"
                        autoComplete="phone_number"
                        value={phone_number}
                        onChange={(e) => setPhonenumber(e.target.value)}
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
                            <MenuItem value="" disabled>Please select a role</MenuItem>
                            <MenuItem value="Security Staff">Security Staff</MenuItem>
                            <MenuItem value="Assistant Administrator">Assistant Administrator</MenuItem>
                        </Select>
                    </FormControl>
                    <Button
                        type="submit"
                        fullWidth
                        variant="contained"
                        color="primary"
                        sx={{ mt: 3, mb: 2 }}
                    >
                        Register
                    </Button>
                    {message && (
                        <Typography variant="body2" color="error">
                            {message}
                        </Typography>
                    )}
                </Box>
            </Box>
        </Container>
    );
};

export default Register;
