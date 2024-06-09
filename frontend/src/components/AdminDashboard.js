import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const AdminDashboard = () => {
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) {
            navigate.push('/login');
        } else {
            setLoading(false);
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