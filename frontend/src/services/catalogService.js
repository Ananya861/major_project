import api from './api';

export const catalogService = {
  async getCrops() {
    const response = await api.get('/crops');
    return response.data;
  },

  async getMarkets() {
    const response = await api.get('/markets');
    return response.data;
  },
};
