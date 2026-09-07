import api from './api';

export const weatherService = {
  async getWeather(lat, lng) {
    const response = await api.get('/weather', {
      params: { lat, lng },
    });
    return response.data;
  },
};
