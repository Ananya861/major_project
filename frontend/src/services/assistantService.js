import api from './api';

export const assistantService = {
  async sendMessage(message, language = 'en', context = null) {
    const response = await api.post('/assistant/chat', {
      message,
      language,
      context,
    });
    return response.data;
  },

  async getSuggestions(language = 'en') {
    const response = await api.get('/assistant/suggestions', {
      params: { language },
    });
    return response.data;
  },
};
