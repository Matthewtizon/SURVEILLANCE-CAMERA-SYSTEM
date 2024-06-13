// src/components/Header.js
import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Header.css';

const Header = ({ dashboardType, username }) => {
    const navigate = useNavigate();

    const handleLogout = () => {
        localStorage.removeItem('token');
        navigate('/login');
    };

    return (
        <header className="dashboard-header">
            <h1>{dashboardType} Dashboard</h1>
            <div>
                <span>Logged in as: {username}</span>
                <button onClick={handleLogout} className="logout-button">Logout</button>
            </div>
        </header>
    );
};

export default Header;
