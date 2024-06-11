// src/components/Register.js
import React, { useState } from 'react';
import axios from 'axios';
import './Register.css'; // Create and import a CSS file for styling

const Register = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [userRole, setUserRole] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const token = localStorage.getItem('token');
            const response = await axios.post('http://localhost:5000/register', {
                username,
                password,
                role: userRole,
            }, {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });
            setSuccess('User registered successfully!');
            setError('');
        } catch (error) {
            setError('Error registering user');
            setSuccess('');
        }
    };

    return (
        <div className="register-container">
            <form onSubmit={handleSubmit} className="register-form">
                <h2>Register New User</h2>
                {error && <p className="error-message">{error}</p>}
                {success && <p className="success-message">{success}</p>}
                <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="Username"
                    className="register-input"
                />
                <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Password"
                    className="register-input"
                />
                <select
                    value={userRole}
                    onChange={(e) => setUserRole(e.target.value)}
                    className="register-input"
                >
                    <option value="">Select Role</option>
                    <option value="Administrator">Administrator</option>
                    <option value="Security Staff">Security Staff</option>
                </select>
                <button type="submit" className="register-button">Register</button>
            </form>
        </div>
    );
};

export default Register;
