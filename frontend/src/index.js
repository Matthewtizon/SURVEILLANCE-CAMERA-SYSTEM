import React from 'react';
import { createRoot } from 'react-dom/client'; // Import createRoot from react-dom/client
import { BrowserRouter as Router } from 'react-router-dom';
import App from './App';

const root = createRoot(document.getElementById('root')); // Create a root
root.render(
  <Router>
    <App />
  </Router>
);
