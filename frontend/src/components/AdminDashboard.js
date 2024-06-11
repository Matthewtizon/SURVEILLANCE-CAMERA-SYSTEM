import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Header from './Header';
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

    return (
        <div className="dashboard-container">
            <Header dashboardType="Administrator" username={username} />
            <main className="dashboard-main">
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
                                    <button onClick={() => deleteUser(user.id)} className="delete-button">Delete</button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </main>
        </div>
    );
};

export default AdminDashboard;