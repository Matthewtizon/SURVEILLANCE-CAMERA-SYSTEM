// src/App.js
import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import Login from './components/Login';
import Register from './components/Register';
import AdminDashboard from './components/AdminDashboard';
import SecurityDashboard from './components/SecurityDashboard';
import CameraStream from './components/CameraStream';
import UserManagement from './components/UserManagement';
import ProfileManagement from './components/ProfileManagement';
import RecordedVideo from './components/RecordedVideo';
import AuditTrail from './components/AuditTrail';


const App = () => {
    const [role, setRole] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (token) {
            axios.get('http://10.242.104.90:5000/protected', {
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
            <Route path="/admin-dashboard" element={role === 'Administrator' || role === 'Assistant Administrator' ? <AdminDashboard /> : <Navigate to="/login" />} />
            <Route path="/security-dashboard" element={role === 'Security Staff' ? <SecurityDashboard /> : <Navigate to="/login" />} />
            <Route path="/camera-stream" element={role ? <CameraStream /> : <Navigate to="/login" />} />
            <Route path="/user-management" element={role ? <UserManagement /> : <Navigate to="/login" />} />
            <Route path="/profile" element={role ? <ProfileManagement /> : <Navigate to="/login" />} />
            <Route path="/video-audit" element={role ? <AuditTrail /> : <Navigate to="/login" />} />
            <Route path="/recorded-videos" element={role ? <RecordedVideo /> : <Navigate to="/login" />} />
            <Route path="/" element={<Navigate to={role ? (role === 'Administrator' ? '/admin-dashboard' : '/security-dashboard') : '/login'} />} />
        </Routes>
    );
};

export default App;
