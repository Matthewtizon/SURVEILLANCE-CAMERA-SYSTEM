// src/components/Sidebar.js
import React from 'react';
import { Link } from 'react-router-dom';
import './Sidebar.css'; // Ensure this CSS file includes the necessary styles

const Sidebar = ({ isOpen, toggleSidebar }) => {
  return (
    <div className="sidebar-container">
      <div className={`sidebar ${isOpen ? 'open' : 'closed'}`}>
        <button onClick={toggleSidebar} className="sidebar-toggle">
          {isOpen ? 'Hide Menu' : 'Show Menu'}
        </button>
        {isOpen && (
          <div className="sidebar-content">
            <h2>Dashboard Menu</h2>
            <ul>
              <li><Link to="/admin/dashboard">Dashboard</Link></li>
              <li><Link to="/admin/users">Users</Link></li>
              <li><Link to="/admin/settings">Settings</Link></li>
              <li><Link to="/camera-stream">View Camera Streams</Link></li>
            </ul>
          </div>
        )}
      </div>
      {!isOpen && (
        <button onClick={toggleSidebar} className="sidebar-show-button">
          Show Menu
        </button>
      )}
    </div>
  );
};

export default Sidebar;
