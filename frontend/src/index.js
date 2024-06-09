import React from 'react';
import ReactDOM from 'react-dom/client'; // Updated import for createRoot
import { BrowserRouter as Router } from 'react-router-dom';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root')); // Create a root
root.render(
  <Router>
    <App />
  </Router>
);