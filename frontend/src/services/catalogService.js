import api from './api';

export const catalogService = {
  async getStates() {
    const response = await api.get('/markets/states');
    return response.data;
  },

  async getCrops(state = null) {
    const params = {};
    if (state && state.trim()) {
      params.state = state.trim();
    }
    const response = await api.get('/crops', { params });
    return response.data;
  },

  async getMarkets(state = null, crop = null) {
    const params = {};
    if (state && state.trim()) {
      params.state = state.trim();
    }
    if (crop && crop.trim()) {
      params.crop = crop.trim();
    }
    const response = await api.get('/markets', { params });
    return response.data;
  },
};
