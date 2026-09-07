import api from './api';

export const farmService = {
  async listFarms() {
    const response = await api.get('/farms');
    return response.data;
  },

  async getFarm(farmId) {
    const response = await api.get(`/farms/${farmId}`);
    return response.data;
  },

  async createFarm(payload) {
    const response = await api.post('/farms', payload);
    return response.data;
  },

  async addSoilReading(farmId, payload) {
    const response = await api.post(`/farms/${farmId}/soil`, payload);
    return response.data;
  },

  async getCropRecommendation(farmId) {
    // Both /recommend/crops/{farm_id} and /recommend/crop?farm_id= exist in backend
    const response = await api.get(`/recommend/crops/${farmId}`);
    return response.data;
  },
};
