/**
 * Career-IQ Frontend Configuration
 * This file is used to configure the API URL for production deployment
 * 
 * For Vercel/Netlify deployment:
 * 1. Set environment variable API_BASE_URL in your hosting platform
 * 2. Or update the API_BASE_URL below with your backend URL
 */

// Production API URL - Update this with your deployed backend URL
// Example: https://career-iq-backend.onrender.com
window.API_BASE_URL = window.API_BASE_URL || 'https://career-iq-backend.onrender.com';

// Auto-detect in development
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    window.API_BASE_URL = 'http://localhost:8000';
}

console.log('Career-IQ API URL:', window.API_BASE_URL);


