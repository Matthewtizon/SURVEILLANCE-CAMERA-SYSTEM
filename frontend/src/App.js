import React, { useState, useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import axios from 'axios';
import Login from './components/Login';
import Register from './components/Register';
import AdminDashboard from './components/AdminDashboard';
import SecurityDashboard from './components/SecurityDashboard';
import { Navigate } from 'react-router-dom';

const App = () => {
    const [role, setRole] = useState(null);

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (token) {
            axios.get('http://localhost:5000/protected', {
                headers: { Authorization: `Bearer ${token}` }
            }).then(response => {
                setRole(response.data.logged_in_as.role);
            }).catch(() => {
                localStorage.removeItem('token');
            });
        }
    }, []);

    return (
        <>
            {role === null && <Navigate to="/login" replace />}
            <Routes>
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                {role === 'Administrator' && (
                    <Route path="/admin-dashboard" element={<AdminDashboard />} />
                )}
                {role === 'Security Staff' && (
                    <Route path="/security-dashboard" element={<SecurityDashboard />} />
                )}
            </Routes>
        </>
    );
};

export default App;