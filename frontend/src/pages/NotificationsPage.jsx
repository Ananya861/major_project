import React, { useState, useEffect, useCallback } from 'react';
import { notificationService } from '../services/notificationService';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';
import EmptyState from '../components/common/EmptyState';
import Badge from '../components/common/Badge';
import {
  Bell,
  CheckCircle2,
  AlertTriangle,
  CloudLightning,
  TrendingDown,
  TrendingUp,
  Clock,
  ShieldCheck,
  Loader2,
  CheckCheck,
} from 'lucide-react';
import { formatDateTime } from '../utils/formatters';

const NotificationsPage = () => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all'); // 'all' | 'unread'

  const [checkingAlerts, setCheckingAlerts] = useState(false);
  const [actionMessage, setActionMessage] = useState(null);

  const fetchNotifications = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await notificationService.listNotifications();
      setNotifications(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.friendlyMessage || 'Failed to load notifications');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchNotifications();
  }, [fetchNotifications]);

  const handleMarkAsRead = async (notifId) => {
    try {
      await notificationService.markAsRead(notifId);
      setNotifications((prev) =>
        prev.map((n) => (n.notif_id === notifId ? { ...n, is_read: true } : n))
      );
    } catch {
      // Silently fail
    }
  };

  const handleTriggerAlertCheck = async () => {
    setCheckingAlerts(true);
    setActionMessage(null);
    try {
      const res = await notificationService.checkAlerts();
      setActionMessage(
        `Scanned successfully. Created ${res.price_alerts_created || 0} price alerts and ${
          res.weather_alerts_created || 0
        } weather alerts.`
      );
      await fetchNotifications();
    } catch (err) {
      setError(err.friendlyMessage || 'Failed to run alert scan.');
    } finally {
      setCheckingAlerts(false);
    }
  };

  const filteredNotifications = notifications.filter((n) => {
    if (filter === 'unread') return !n.is_read;
    return true;
  });

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'PRICE_ALERT':
        return <TrendingUp className="w-5 h-5 text-amber-600" />;
      case 'WEATHER_ALERT':
        return <CloudLightning className="w-5 h-5 text-blue-600" />;
      default:
        return <Bell className="w-5 h-5 text-agri-600" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
            Notifications &amp; Alerts
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Automated alerts triggered by mandi price shifts (&ge; 5%), MSP divergence, or extreme weather.
          </p>
        </div>

        <button
          onClick={handleTriggerAlertCheck}
          disabled={checkingAlerts}
          className="inline-flex items-center space-x-2 px-5 py-2.5 bg-agri-600 hover:bg-agri-700 text-white text-xs font-bold rounded-xl shadow-xs transition disabled:opacity-50"
        >
          {checkingAlerts ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <ShieldCheck className="w-4 h-4" />
          )}
          <span>{checkingAlerts ? 'Scanning Alerts...' : 'Scan Now For Alerts'}</span>
        </button>
      </div>

      {actionMessage && (
        <div className="p-4 bg-emerald-50 text-emerald-800 text-xs rounded-2xl border border-emerald-200 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>{actionMessage}</span>
          </div>
          <button
            onClick={() => setActionMessage(null)}
            className="text-xs font-semibold text-emerald-700 hover:text-emerald-900"
          >
            Dismiss
          </button>
        </div>
      )}

      <ErrorMessage message={error} onRetry={fetchNotifications} />

      {/* Tabs */}
      <div className="flex items-center space-x-2 border-b border-slate-200/80 pb-2">
        <button
          onClick={() => setFilter('all')}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition ${
            filter === 'all'
              ? 'bg-slate-900 text-white'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
          }`}
        >
          All Notifications ({notifications.length})
        </button>
        <button
          onClick={() => setFilter('unread')}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition ${
            filter === 'unread'
              ? 'bg-slate-900 text-white'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
          }`}
        >
          Unread ({notifications.filter((n) => !n.is_read).length})
        </button>
      </div>

      {/* Content */}
      {loading ? (
        <LoadingSpinner message="Loading notifications..." />
      ) : filteredNotifications.length === 0 ? (
        <EmptyState
          icon={Bell}
          title={filter === 'unread' ? 'No unread notifications' : 'No notifications yet'}
          description="Your notifications regarding price updates and weather warnings will appear here."
          actionText="Run Price &amp; Weather Scan"
          onAction={handleTriggerAlertCheck}
        />
      ) : (
        <div className="space-y-3">
          {filteredNotifications.map((notif) => (
            <div
              key={notif.notif_id}
              className={`p-5 rounded-2xl border transition-all flex items-start justify-between gap-4 ${
                notif.is_read
                  ? 'bg-white border-slate-200/70 text-slate-700'
                  : 'bg-agri-50/40 border-agri-200 text-slate-900 shadow-xs'
              }`}
            >
              <div className="flex items-start space-x-3.5">
                <div
                  className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${
                    notif.is_read ? 'bg-slate-100' : 'bg-agri-100'
                  }`}
                >
                  {getNotificationIcon(notif.type)}
                </div>

                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <Badge variant={notif.is_read ? 'neutral' : 'primary'}>
                      {notif.type || 'ALERT'}
                    </Badge>
                    <span className="text-[11px] text-slate-400 flex items-center space-x-1">
                      <Clock className="w-3 h-3" />
                      <span>{formatDateTime(notif.created_at)}</span>
                    </span>
                  </div>

                  <p className="text-sm font-medium leading-relaxed">{notif.message}</p>
                </div>
              </div>

              {!notif.is_read && (
                <button
                  onClick={() => handleMarkAsRead(notif.notif_id)}
                  className="shrink-0 p-2 rounded-xl text-agri-700 hover:bg-agri-100 text-xs font-semibold flex items-center space-x-1 transition"
                  title="Mark as read"
                >
                  <CheckCheck className="w-4 h-4" />
                  <span className="hidden sm:inline">Mark Read</span>
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default NotificationsPage;
