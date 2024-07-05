// src/components/SecurityDashboard.js
import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import Header from './Header';
import './Dashboard.css';

const SecurityDashboard = () => {
    const [loading, setLoading] = useState(true);
    const [username, setUsername] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        const fetchUserData = async () => {
            const token = localStorage.getItem('token');
            if (!token) {
                navigate('/login');
                return;
            }
            
            try {
                const response = await axios.get('http://localhost:5000/protected', {
                    headers: { Authorization: `Bearer ${token}` }
                });
                const user = response.data.logged_in_as;
                setUsername(user.username);
                setLoading(false);
            } catch (error) {
                console.error('Error fetching user data:', error);
                localStorage.removeItem('token');
                navigate('/login');
            }
        };

        fetchUserData();
    }, [navigate]);

    if (loading) {
        return <div>Loading...</div>;
    }

    return (
        <div className="dashboard-container">
            <Header dashboardType="Security Staff" username={username} />
            <main className="dashboard-main">
                <Link to="/camera-stream" className="camera-stream-link">View Camera Streams</Link>
            </main>
        </div>
    );
};

export default SecurityDashboard;
