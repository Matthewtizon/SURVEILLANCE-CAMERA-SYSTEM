// src/components/Sidebar.js
import React from 'react';
import { Link } from 'react-router-dom';
import './Sidebar.css'; // Ensure this CSS file includes the necessary styles

const Sidebar = ({ isOpen, toggleSidebar, role }) => {
  return (
    <div className="sidebar-container">
      <div className={`sidebar ${isOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <button onClick={toggleSidebar} className="sidebar-toggle">
            {isOpen ? '<' : '>'}
          </button>
        </div>
        <div className={`sidebar-content ${isOpen ? 'visible' : 'hidden'}`}>
          <h2>Dashboard Menu</h2>
          <ul>
            <li>
              <Link to={`/${role === 'Administrator' ? 'admin-dashboard' : 'security-dashboard'}`}>
                {role === 'Administrator' ? 'Admin Dashboard' : 'Security Dashboard'}
              </Link>
            </li>
            <li>
              <Link to="/user-management">User Management</Link>
            </li>
            <li>
              <Link to="/camera-stream">View Camera Streams</Link>
            </li>
          </ul>
        </div>
      </div>
      <button onClick={toggleSidebar} className="sidebar-show-button">
        {isOpen ? '<' : '>'}
      </button>
    </div>
  );
};

export default Sidebar;
