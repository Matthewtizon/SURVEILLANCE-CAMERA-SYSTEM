import React from 'react';
import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ children, role, allowedRoles }) => {
    if (!role) {
        return <Navigate to="/login" />;
    }

    if (!allowedRoles.includes(role)) {
        return <Navigate to="/login" />;
    }

    return children;
};

export default ProtectedRoute;