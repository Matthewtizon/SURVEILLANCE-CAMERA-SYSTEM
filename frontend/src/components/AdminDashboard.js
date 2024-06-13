// src/components/AdminDashboard.js
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Header from './Header';
import CameraFeeds from './CameraFeeds';
import Register from './Register';
import './Dashboard.css';

const AdminDashboard = () => {
    const [loading, setLoading] = useState(true);
    const [username, setUsername] = useState('');
    const [users, setUsers] = useState([]);
    const [showRegisterForm, setShowRegisterForm] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) {
            navigate('/login');
        } else {
            const user = JSON.parse(atob(token.split('.')[1]));
            setUsername(user.username);
            axios.get('http://localhost:5000/users', {
                headers: { Authorization: `Bearer ${token}` }
            }).then(response => {
                setUsers(response.data);
                setLoading(false);
            }).catch(() => {
                localStorage.removeItem('token');
                navigate('/login');
            });
        }
    }, [navigate]);

    if (loading) {
        return <div>Loading...</div>;
    }

    const toggleRegisterForm = () => {
        setShowRegisterForm(!showRegisterForm);
    };

    const deleteUser = async (userId) => {
        const token = localStorage.getItem('token');
        try {
            await axios.delete(`http://localhost:5000/users/${userId}`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setUsers(users.filter(user => user.id !== userId));
        } catch (error) {
            console.error('Error deleting user', error);
        }
    };

    const handleDelete = (userId, userUsername) => {
        if (userUsername === username) {
            alert("You cannot delete your own account.");
            return;
        }

        const confirmation = window.confirm("Are you sure you want to delete this user?");
        if (confirmation) {
            deleteUser(userId);
        }
    };

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
                            <tr key={user.id}>
                                <td>{user.id}</td>
                                <td>{user.username}</td>
                                <td>{user.role}</td>
                                <td>
                                    <button
                                        onClick={() => handleDelete(user.id, user.username)}
                                        className="delete-button"
                                    >
                                        Delete
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                <h2>Camera Feeds</h2>
                <CameraFeeds />
            </main>
        </div>
    );
};

export default AdminDashboard;
