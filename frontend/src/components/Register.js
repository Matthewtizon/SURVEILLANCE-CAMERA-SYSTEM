import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';

const Register = ({ role }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [userRole, setUserRole] = useState('');
    const [users, setUsers] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token || role !== 'Administrator') {
            navigate('/login');
        } else {
            fetchUsers(token);
        }
    }, [role, navigate]);

    const fetchUsers = async (token) => {
        try {
            const response = await axios.get('http://localhost:5000/users', {
                headers: { Authorization: `Bearer ${token}` }
            });
            setUsers(response.data);
        } catch (error) {
            console.error('Error fetching users', error);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const token = localStorage.getItem('token'); // Assume token is stored in localStorage
            await axios.post('http://localhost:5000/register', {
                username,
                password,
                role: userRole,
            }, {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });
            fetchUsers(token); // Refresh the user list after registration
        } catch (error) {
            console.error('Error registering user', error);
        }
    };

    const handleDelete = async (userId) => {
        const token = localStorage.getItem('token');
        try {
            await axios.delete(`http://localhost:5000/users/${userId}`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            fetchUsers(token); // Refresh the user list after deletion
        } catch (error) {
            console.error('Error deleting user', error);
        }
    };

    return (
        <div>
            <form onSubmit={handleSubmit}>
                <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Username" />
                <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" />
                <select value={userRole} onChange={(e) => setUserRole(e.target.value)}>
                    <option value="Administrator">Administrator</option>
                    <option value="Security Staff">Security Staff</option>
                </select>
                <button type="submit">Register</button>
            </form>
            <nav>
                <Link to="/admin-dashboard">Go to Admin Dashboard</Link>
            </nav>
            <h2>All Users</h2>
            <ul>
                {users.map(user => (
                    <li key={user.id}>
                        {user.username} - {user.role}
                        <button onClick={() => handleDelete(user.id)}>Delete</button>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default Register;
