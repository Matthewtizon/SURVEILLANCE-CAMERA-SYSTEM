// src/components/SecurityDashboard.js
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Header from './Header';
import Sidebar from './SideBar'; // Correctly import Sidebar
import './Dashboard.css';

const SecurityDashboard = () => {
    const [loading, setLoading] = useState(true);
    const [username, setUsername] = useState('');
    const [role, setRole] = useState('');
    const [sidebarOpen, setSidebarOpen] = useState(true); // State to manage sidebar visibility
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
                setRole(user.role);
                setLoading(false);
            } catch (error) {
                console.error('Error fetching user data:', error);
                localStorage.removeItem('token');
                navigate('/login');
            }
        };

        fetchUserData();
    }, [navigate]);

    const toggleSidebar = () => {
        setSidebarOpen(!sidebarOpen);
    };

    if (loading) {
        return <div>Loading...</div>;
    }

    return (
        <div className="dashboard-container">
            <Sidebar isOpen={sidebarOpen} toggleSidebar={toggleSidebar} role={role} /> {/* Add Sidebar */}
            <div className={`main-content ${sidebarOpen ? 'expanded' : 'collapsed'}`}>
                <Header dashboardType="Security Staff" username={username} role={role} />
                <main className="dashboard-main">
                    <h2> Welcome to the Security Staff Dashboard {username}</h2>
                </main>
            </div>
        </div>
    );
};

export default SecurityDashboard;