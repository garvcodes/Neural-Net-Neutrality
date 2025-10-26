// Backend API configuration
// For production, this should point to your Render backend URL
// For local development, use localhost
const API_CONFIG = {
  // Local development
  BACKEND_URL: 'http://localhost:8081',

  // Render backend URL (switch for production)
  // BACKEND_URL: 'https://neural-net-neutrality.onrender.com',

  // API endpoints
  ENDPOINTS: {
    GENERATE_NEWS_SCRIPT: '/api/generate-news-script',
    GENERATE_PODCAST: '/api/generate-podcast',
    PODCASTS: '/podcasts',
    TAKE_TEST: '/api/take_test',
    BATTLE: '/api/battle',
    HEALTH: '/health'
  }
};

// Helper function to construct full API URL
function getApiUrl(endpoint) {
  return `${API_CONFIG.BACKEND_URL}${endpoint}`;
}
