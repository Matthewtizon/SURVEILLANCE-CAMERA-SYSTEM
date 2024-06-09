import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate  } from 'react-router-dom';

const Register = ({ role }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [userRole, setUserRole] = useState('');
    const navigate  = useNavigate ();

    useEffect(() => {
        if (role !== 'Administrator') {
            navigate.push('/login');
        }
    }, [role, navigate]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const token = localStorage.getItem('token'); // Assume token is stored in localStorage
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