// src/components/AdminDashboard.js
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Header from './Header';
import CameraStream from './CameraStream';
import Register from './Register';
import './Dashboard.css';

const AdminDashboard = () => {
    const [loading, setLoading] = useState(true);
    const [username, setUsername] = useState('');
    const [users, setUsers] = useState([]);
    const [showRegisterForm, setShowRegisterForm] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchUserData = async () => {
            const token = localStorage.getItem('token');
            if (!token) {
                navigate('/login');
                return;
            }
            
            try {
                const response = await axios.get('http://localhost:5000/users', {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setUsers(response.data);
                setLoading(false);
                
                const user = JSON.parse(atob(token.split('.')[1]));
                setUsername(user.username);
            } catch (error) {
                console.error('Error fetching users:', error);
                localStorage.removeItem('token');
                navigate('/login');
            }
        };

        fetchUserData();
    }, [navigate]);

    const deleteUser = async (userId, username) => {
        const token = localStorage.getItem('token');
        
        try {
            const response = await axios.delete(`http://localhost:5000/users/${userId}`, {
                headers: { Authorization: `Bearer ${token}` }
            });

            if (response.status === 200) {
                setUsers(users.filter(user => user.user_id !== userId));
            }
        } catch (error) {
            console.error('Error deleting user:', error);
        }
    };

    const toggleRegisterForm = () => {
        setShowRegisterForm(!showRegisterForm);
    };

    if (loading) {
        return <div>Loading...</div>;
    }

    return (
        <div className="dashboard-container">
            <Header dashboardType="Administrator" username={username} />
            <main className="dashboard-main">
                <h1>Admin Dashboard</h1>
                <button onClick={toggleRegisterForm} className="toggle-button">
                    {showRegisterForm ? 'Hide Register Form' : 'Show Register Form'}
                </button>
                {showRegisterForm && <Register />}
                <h2>User List</h2>
                <table className="user-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Username</th>
                            <th>Role</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {users.map(user => (
                            <tr key={user.user_id}>
                                <td>{user.user_id}</td>
                                <td>{user.username}</td>
                                <td>{user.role}</td>
                                <td>
                                    <button
                                        onClick={() => deleteUser(user.user_id, user.username)}
                                        className="delete-button"
                                    >
                                        Delete
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                <CameraStream cameraId={1} /> {/* Example camera ID */}
            </main>
        </div>
    );
};

export default AdminDashboard;
