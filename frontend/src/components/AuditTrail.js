import React, { useState, useEffect } from "react";
import { useNavigate } from 'react-router-dom';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Dialog, DialogTitle, DialogContent, DialogActions, Button } from '@mui/material';
import axios from "axios";

const AuditTrail = ({ onClose }) => {
    const [username, setUsername] = useState('');
    const [role, setRole] = useState('');
    const [auditData, setAuditData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchUserData = async () => {
            const token = localStorage.getItem('token');
            if (!token) {
                navigate('/login');
                return;
            }

            try {
                const response = await axios.get('http://10.242.104.90:5000/protected', {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setUsername(response.data.logged_in_as.username);
                setRole(response.data.logged_in_as.role);
            } catch (error) {
                console.error('Error fetching user data:', error);
                localStorage.removeItem('token');
                navigate('/login');
            }
        };

        const fetchAuditData = async () => {
            const token = localStorage.getItem('token');
            try {
                const response = await axios.get('http://10.242.104.90:5000/video_audit_trail', {
                    headers: { Authorization: `Bearer ${token}` }
                });

                // Sort audit data by deleted_at in descending order
                const sortedData = response.data.sort((a, b) => new Date(b.deleted_at) - new Date(a.deleted_at));
                setAuditData(sortedData);
            } catch (err) {
                setError(err.message || "An error occurred while fetching audit data.");
            } finally {
                setLoading(false);
            }
        };

        fetchUserData();
        fetchAuditData();
    }, [navigate]);

    if (loading) {
        return <div>Loading...</div>;
    }

    if (error) {
        return <div>Error: {error}</div>;
    }

    return (
        <Dialog open onClose={onClose} fullWidth maxWidth="md">
            <DialogTitle>Video Deletion Audit Trail</DialogTitle>
            <DialogContent>
                <TableContainer component={Paper}>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell>ID</TableCell>
                                <TableCell>Video Name</TableCell>
                                <TableCell>Deleted By</TableCell>
                                <TableCell>Deletion Time</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {auditData.map((audit) => (
                                <TableRow key={audit.id}>
                                    <TableCell>{audit.id}</TableCell>
                                    <TableCell>{audit.video_name}</TableCell>
                                    <TableCell>{audit.deleted_by}</TableCell>
                                    <TableCell>{new Date(audit.deleted_at).toLocaleString()}</TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose} color="primary">Close</Button>
            </DialogActions>
        </Dialog>
    );
};

export default AuditTrail;
