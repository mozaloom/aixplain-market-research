// API Configuration
const getApiBaseUrl = () => {
  // In production (Amplify), use the Amplify API Gateway URL
  if (process.env.NODE_ENV === 'production') {
    return process.env.REACT_APP_API_URL || 'https://your-api-id.execute-api.region.amazonaws.com/dev';
  }
  // In development, use localhost
  return 'http://localhost:8000';
};

export const API_BASE_URL = getApiBaseUrl();
