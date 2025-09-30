const express = require('express');
const cors = require('cors');
const axios = require('axios'); // For communicating with Django backend

const app = express();
const PORT = process.env.PORT || 5000; // Node.js backend port

// Middleware
app.use(cors()); // Enable CORS for all origins
app.use(express.json()); // For parsing application/json

// Django backend URL (replace with your actual Django backend URL)
const DJANGO_BACKEND_URL = process.env.DJANGO_BACKEND_URL || 'http://localhost:8000';

// Basic route
app.get('/', (req, res) => {
    res.send('Node.js Backend is running!');
});

// AI Matching API endpoint for frontend
app.get('/api/match/projects/:projectId', async (req, res) => {
    const projectId = req.params.projectId;
    try {
        const djangoResponse = await axios.get(`${DJANGO_BACKEND_URL}/teamspace/internal-api/match/projects/${projectId}/`);
        res.json(djangoResponse.data);
    } catch (error) {
        console.error('Error calling Django AI matching API:', error.message);
        if (error.response) {
            // The request was made and the server responded with a status code
            // that falls out of the range of 2xx
            res.status(error.response.status).json(error.response.data);
        } else if (error.request) {
            // The request was made but no response was received
            res.status(500).json({ error: 'No response received from Django backend' });
        } else {
            // Something happened in setting up the request that triggered an Error
            res.status(500).json({ error: error.message });
        }
    }
});

// Start the server
app.listen(PORT, () => {
    console.log(`Node.js Backend running on port ${PORT}`);
});
