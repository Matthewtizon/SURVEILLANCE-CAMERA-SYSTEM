import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import axios from 'axios';
import Login from './components/Login';
import Register from './components/Register';
import AdminDashboard from './components/AdminDashboard';
import SecurityDashboard from './components/SecurityDashboard';

const App = () => {
    const [role, setRole] = useState(null);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (token) {
            axios.get('http://localhost:5000/protected', {
                headers: { Authorization: `Bearer ${token}` }
            }).then(response => {
                setRole(response.data.logged_in_as.role);
                setLoading(false);
            }).catch(() => {
                localStorage.removeItem('token');
                setLoading(false);
            });
        } else {
            setLoading(false);
        }
    }, []);

    if (loading) {
        return <div>Loading...</div>;
    }

    return (
        <Routes>
            <Route path="/login" element={<Login setRole={setRole} />} />
            {role === 'Administrator' && (
                <>
                    <Route path="/admin-dashboard" element={<AdminDashboard />} />
                    <Route path="/register" element={<Register role={role} />} />
                </>
            )}
            {role === 'Security Staff' && (
                <Route path="/security-dashboard" element={<SecurityDashboard />} />
            )}
            <Route path="/" element={role ? <Navigate to={`/${role === 'Administrator' ? 'admin-dashboard' : 'security-dashboard'}`} /> : <Navigate to="/login" />} />
        </Routes>
    );
};

export default App;
