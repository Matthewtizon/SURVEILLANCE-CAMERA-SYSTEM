import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const Login = ({ setRole }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post('http://localhost:5000/login', {
                username,
                password,
            });
            console.log("Response data:", response.data);  // Debugging statement
            localStorage.setItem('token', response.data.access_token);
            
            const role = response.data.user_info ? response.data.user_info.role : null;
            setRole(role);
    
            if (role === 'Administrator') {
                navigate('/admin-dashboard');
            } else if (role === 'Security Staff') {
                navigate('/security-dashboard');
            } else {
                setError('Role not found in response data');
            }
        } catch (err) {
            console.error("Error:", err.response.data);  // Debugging statement
            setError('Invalid credentials');
        }
    };

    return (
        <div>
            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="Username"
                />
                <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Password"
                />
                <button type="submit">Login</button>
            </form>
            {error && <p>{error}</p>}
        </div>
    );
};

export default Login;
