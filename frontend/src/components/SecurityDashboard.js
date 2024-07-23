// src/components/SecurityDashboard.js
import React, { useEffect, useState, Link } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Header from './Header';
import Sidebar from './SideBar'; // Import Sidebar
import './Dashboard.css';

const SecurityDashboard = () => {
    const [loading, setLoading] = useState(true);
    const [username, setUsername] = useState('');
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
            <Sidebar isOpen={sidebarOpen} toggleSidebar={toggleSidebar} /> {/* Add Sidebar */}
            <div className={`main-content ${sidebarOpen ? 'expanded' : 'collapsed'}`}>
                <Header dashboardType="Security Staff" username={username} />
                <main className="dashboard-main">
                    <Link to="/camera-stream" className="camera-stream-link">View Camera Streams</Link>
                </main>
            </div>
        </div>
    );
};

export default SecurityDashboard;
