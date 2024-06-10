import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const Register = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [userRole, setUserRole] = useState('Security Staff');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const token = localStorage.getItem('token');
            const response = await axios.post('http://localhost:5000/register', {
                username,
                password,
                role: userRole,
            }, {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });
            console.log(response.data);
            navigate('/admin-dashboard');
        } catch (error) {
            console.error('Error registering user', error);
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Username" />
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" />
            <select value={userRole} onChange={(e) => setUserRole(e.target.value)}>
                <option value="Administrator">Administrator</option>
                <option value="Security Staff">Security Staff</option>
            </select>
            <button type="submit">Register</button>
        </form>
    );
};

export default Register;
