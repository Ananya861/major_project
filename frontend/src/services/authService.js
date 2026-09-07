import api from './api';

export const authService = {
  async register(payload) {
    const response = await api.post('/auth/register', payload);
    return response.data;
  },

  async login(phone, password) {
    const response = await api.post('/auth/login', { phone, password });
    return response.data;
  },

  async getMe() {
    const response = await api.get('/auth/me');
    return response.data;
  },
};
