import api from './api';

export const notificationService = {
  async listNotifications() {
    const response = await api.get('/notifications');
    return response.data;
  },

  async checkAlerts() {
    const response = await api.post('/notifications/check-alerts');
    return response.data;
  },

  async markAsRead(notifId) {
    const response = await api.patch(`/notifications/${notifId}/read`);
    return response.data;
  },
};
