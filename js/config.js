// Backend API configuration
// For production, this should point to your Render backend URL
// For local development, use localhost
const API_CONFIG = {
  // Render backend URL
  BACKEND_URL: 'https://neural-net-neutrality.onrender.com',

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
