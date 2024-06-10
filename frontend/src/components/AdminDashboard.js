import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const AdminDashboard = () => {
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) {
            navigate('/login');
        } else {
            axios.get('http://localhost:5000/protected', {
                headers: { Authorization: `Bearer ${token}` }
            }).then(response => {
                if (response.data.logged_in_as.role !== 'Administrator') {
                    navigate('/login');
                } else {
                    setLoading(false);
                }
            }).catch(() => {
                localStorage.removeItem('token');
                navigate('/login');
            });
        }
    }, [navigate]);

    if (loading) {
        return <div>Loading...</div>;
    }

    return (
        <div>
            <h1>Admin Dashboard</h1>
            {/* Your Admin Dashboard content */}
        </div>
    );
};

export default AdminDashboard;