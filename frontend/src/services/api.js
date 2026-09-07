import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

// Request interceptor: attach token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: handle 401 and parse clean error messages
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const { status, data } = error.response;

      if (status === 401) {
        // Clear token on 401 if it was an authenticated request
        localStorage.removeItem('access_token');
        localStorage.removeItem('farmer_data');
        window.dispatchEvent(new Event('auth:unauthorized'));

        // Don't auto-redirect if already on login/register
        const currentPath = window.location.pathname;
        if (currentPath !== '/login' && currentPath !== '/register' && currentPath !== '/') {
          window.location.href = '/login?session=expired';
        }
      }

      // Format FastAPI 422 or standard detail
      let errorMessage = 'An error occurred. Please try again.';
      if (data?.detail) {
        if (typeof data.detail === 'string') {
          errorMessage = data.detail;
        } else if (Array.isArray(data.detail)) {
          // Pydantic validation error array
          errorMessage = data.detail.map((err) => `${err.loc?.slice(-1)[0] || 'field'}: ${err.msg}`).join(', ');
        }
      }
      error.friendlyMessage = errorMessage;
    } else if (error.request) {
      error.friendlyMessage = 'Unable to connect to the AgriSmart server. Please verify the backend is running at ' + API_BASE_URL;
    } else {
      error.friendlyMessage = error.message || 'An unexpected error occurred.';
    }

    return Promise.reject(error);
  }
);

export default api;
