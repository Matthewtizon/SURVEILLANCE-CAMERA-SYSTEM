import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate, useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import Login from './components/Login';
import Register from './components/Register';
import AdminDashboard from './components/AdminDashboard';
import SecurityDashboard from './components/SecurityDashboard';

const App = () => {
    const [role, setRole] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (token) {
            axios.get('http://localhost:5000/protected', {
                headers: { Authorization: `Bearer ${token}` }
            })
            .then(response => {
                setRole(response.data.logged_in_as.role);
            })
            .catch(() => {
                localStorage.removeItem('token');
                setRole(null);
                navigate('/login');
            });
        } else {
            navigate('/login');
        }
    }, [navigate]);

    const handleLogout = () => {
        localStorage.removeItem('token');
        setRole(null);
        navigate('/login');
    };

    return (
        <>
            <nav>
                {role && (
                    <>
                        {role === 'Administrator' && (
                            <Link to="/register">Register</Link>
                        )}
                        <button onClick={handleLogout}>Logout</button>
                    </>
                )}
            </nav>
            <Routes>
                <Route path="/login" element={<Login setRole={setRole} />} />
                <Route path="/register" element={role === 'Administrator' ? <Register /> : <Navigate to="/login" replace />} />
                {role === 'Administrator' && <Route path="/admin-dashboard" element={<AdminDashboard />} />}
                {role === 'Security Staff' && <Route path="/security-dashboard" element={<SecurityDashboard />} />}
                <Route path="*" element={<Navigate to={role ? (role === 'Administrator' ? "/admin-dashboard" : "/security-dashboard") : "/login"} replace />} />
            </Routes>
        </>
    );
};

export default App;
