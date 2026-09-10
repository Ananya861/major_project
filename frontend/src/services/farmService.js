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

  async getRecommendationHistory(farmId = null) {
    const url = farmId ? `/recommendations/history?farm_id=${farmId}` : '/recommendations/history';
    const response = await api.get(url);
    return response.data;
  },
};

export const recommendationService = {
  getHistory(farmId = null) {
    return farmService.getRecommendationHistory(farmId);
  },
  getCropRecommendation(farmId) {
    return farmService.getCropRecommendation(farmId);
  },
};
