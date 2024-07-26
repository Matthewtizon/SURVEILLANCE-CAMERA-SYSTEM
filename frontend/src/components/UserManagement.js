// src/components/UserManagement.js
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Header from './Header';
import Sidebar from './SideBar'; // Import Sidebar
import Register from './Register';
import './UserManagement.css';

const UserManagement = () => {
    const [loading, setLoading] = useState(true);
    const [users, setUsers] = useState([]);
    const [showRegisterForm, setShowRegisterForm] = useState(false);
    const [username, setUsername] = useState('');
    const [role, setRole] = useState(''); // State for role
    const [sidebarOpen, setSidebarOpen] = useState(true); // State for sidebar
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
                setUsername(response.data.logged_in_as.username);
                setRole(response.data.logged_in_as.role);
                
                const userResponse = await axios.get('http://localhost:5000/users', {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setUsers(userResponse.data);
                setLoading(false);
            } catch (error) {
                console.error('Error fetching user data:', error);
                localStorage.removeItem('token');
                navigate('/login');
            }
        };

        fetchUserData();
    }, [navigate]);

    const deleteUser = async (userId) => {
        if (role !== 'Administrator') {
            alert('Only Administrators can delete users');
            return;
        }

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
        if (role !== 'Administrator') {
            alert('Only Administrators can register new users');
            return;
        }
        setShowRegisterForm(!showRegisterForm);
    };

    const toggleSidebar = () => {
        setSidebarOpen(!sidebarOpen);
    };

    if (loading) {
        return <div>Loading...</div>;
    }

    return (
        <div className="user-management-container">
            <Sidebar isOpen={sidebarOpen} toggleSidebar={toggleSidebar} role={role} /> {/* Add Sidebar */}
            <div className={`main-content ${sidebarOpen ? 'expanded' : 'collapsed'}`}>
                <Header dashboardType="User Management" username={username} role={role} />
                {role === 'Administrator' && (
                    <button onClick={toggleRegisterForm} className="toggle-button">
                        {showRegisterForm ? 'Hide Register Form' : 'Show Register Form'}
                    </button>
                )}
                {showRegisterForm && <Register />}
                <h2>User List</h2>
                <table className="user-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Username</th>
                            <th>Role</th>
                            {role === 'Administrator' && <th>Actions</th>}
                        </tr>
                    </thead>
                    <tbody>
                        {users.map(user => (
                            <tr key={user.user_id}>
                                <td>{user.user_id}</td>
                                <td>{user.username}</td>
                                <td>{user.role}</td>
                                {role === 'Administrator' && (
                                    <td>
                                        <button
                                            onClick={() => deleteUser(user.user_id)}
                                            className="delete-button"
                                        >
                                            Delete
                                        </button>
                                    </td>
                                )}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default UserManagement;