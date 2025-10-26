// Backend API configuration
// For production, this should point to your Render backend URL
// For local development, use localhost
const API_CONFIG = {
  // Change this to your Render backend URL once deployed
  // Example: 'https://your-app-name.onrender.com'
  BACKEND_URL: window.location.hostname === 'localhost'
    ? 'http://localhost:3001'
    : 'https://your-render-backend-url.onrender.com', // UPDATE THIS after deploying to Render

  // API endpoints
  ENDPOINTS: {
    GENERATE_NEWS_SCRIPT: '/api/generate-news-script',
    TAKE_TEST: '/api/take_test',
    HEALTH: '/health'
  }
};

// Helper function to construct full API URL
function getApiUrl(endpoint) {
  return `${API_CONFIG.BACKEND_URL}${endpoint}`;
}
