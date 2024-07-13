// src/App.js
import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import Login from './components/Login';
import Register from './components/Register';
import AdminDashboard from './components/AdminDashboard';
import SecurityDashboard from './components/SecurityDashboard';
import CameraStream from './components/CameraStream';

const App = () => {
    const [role, setRole] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (token) {
            axios.get('http://localhost:5000/protected', {
                headers: { Authorization: `Bearer ${token}` }
            }).then(response => {
                setRole(response.data.logged_in_as.role);
                setLoading(false);
            }).catch(error => {
                console.error('Error fetching authentication data:', error);
                localStorage.removeItem('token');
                setLoading(false);
            });
        } else {
            setLoading(false);
        }
    }, []);

    if (loading) {
        return <div>Loading...</div>; // Show a loading state until the role is determined
    }

    return (
        <Routes>
            <Route path="/login" element={<Login setRole={setRole} />} />
            <Route path="/register" element={role === 'Administrator' ? <Register /> : <Navigate to="/login" />} />
            <Route path="/admin-dashboard" element={role === 'Administrator' ? <AdminDashboard /> : <Navigate to="/login" />} />
            <Route path="/security-dashboard" element={role === 'Security Staff' ? <SecurityDashboard /> : <Navigate to="/login" />} />
            <Route path="/camera-stream" element={role ? <CameraStream /> : <Navigate to="/login" />} />
            <Route path="/" element={<Navigate to={role ? (role === 'Administrator' ? '/admin-dashboard' : '/security-dashboard') : '/login'} />} />
        </Routes>
    );
};

export default App;
