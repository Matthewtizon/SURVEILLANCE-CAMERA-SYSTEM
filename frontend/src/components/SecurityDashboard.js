import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const SecurityDashboard = () => {
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) {
            navigate('/login');
        } else {
            setLoading(false);
        }
    }, [navigate]);

    const handleLogout = () => {
        localStorage.removeItem('token');
        navigate('/login');
    };

    if (loading) {
        return <div>Loading...</div>;
    }

    return (
        <div>
            <h1>Security Dashboard</h1>
            <button onClick={handleLogout}>Logout</button>
            {/* Your Security Dashboard content */}
        </div>
    );
};

export default SecurityDashboard;
