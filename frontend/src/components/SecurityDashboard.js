import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Header from './Header';
import './Dashboard.css';

const SecurityDashboard = () => {
    const [loading, setLoading] = useState(true);
    const [username, setUsername] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) {
            navigate('/login');
        } else {
            const user = JSON.parse(atob(token.split('.')[1]));
            setUsername(user.username);
            setLoading(false);
        }
    }, [navigate]);

    if (loading) {
        return <div>Loading...</div>;
    }

    return (
        <div className="dashboard-container">
            <Header dashboardType="Security Staff" username={username} />
            <main className="dashboard-main">
                <h1>Security Dashboard</h1>
                {/* Your Security Dashboard content */}
            </main>
        </div>
    );
};

export default SecurityDashboard;