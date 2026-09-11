import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useFarm } from '../context/FarmContext';
import { useTranslation } from '../i18n/LanguageContext';
import { weatherService } from '../services/weatherService';
import { notificationService } from '../services/notificationService';
import StatCard from '../components/common/StatCard';
import Badge from '../components/common/Badge';
import AddFarmModal from '../components/forms/AddFarmModal';
import {
  Tractor,
  Sprout,
  TrendingUp,
  Store,
  Scale,
  CloudSun,
  Bell,
  Plus,
  ArrowRight,
  ShieldAlert,
  Loader2,
  CheckCircle2,
} from 'lucide-react';

const DashboardPage = () => {
  const { user } = useAuth();
  const { farms, loadingFarms, selectedFarm } = useFarm();
  const { t } = useTranslation();

  const [weather, setWeather] = useState(null);
  const [loadingWeather, setLoadingWeather] = useState(false);
  const [unreadNotifications, setUnreadNotifications] = useState(0);
  const [scanningAlerts, setScanningAlerts] = useState(false);
  const [alertFeedback, setAlertFeedback] = useState(null);
  const [addFarmOpen, setAddFarmOpen] = useState(false);

  // Fetch weather if a farm exists
  const farmLat = selectedFarm?.latitude;
  const farmLng = selectedFarm?.longitude;

  useEffect(() => {
    let isMounted = true;
    const fetchWeather = async () => {
      if (farmLat !== undefined && farmLng !== undefined) {
        setLoadingWeather(true);
        try {
          const data = await weatherService.getWeather(farmLat, farmLng);
          if (isMounted) setWeather(data);
        } catch {
          // Weather will remain null
        } finally {
          if (isMounted) setLoadingWeather(false);
        }
      }
    };
    fetchWeather();
    return () => {
      isMounted = false;
    };
  }, [farmLat, farmLng]);

  // Fetch notification count
  useEffect(() => {
    let isMounted = true;
    const fetchNotifs = async () => {
      try {
        const notifs = await notificationService.listNotifications();
        if (isMounted && Array.isArray(notifs)) {
          setUnreadNotifications(notifs.filter((n) => !n.is_read).length);
        }
      } catch {
        // Silently fail
      }
    };
    fetchNotifs();
    return () => {
      isMounted = false;
    };
  }, []);

  const handleRunAlertScan = async () => {
    setScanningAlerts(true);
    setAlertFeedback(null);
    try {
      const res = await notificationService.checkAlerts();
      setAlertFeedback(
        `Scanned successfully. Created ${res.price_alerts_created || 0} price alerts and ${
          res.weather_alerts_created || 0
        } weather alerts.`
      );
      const notifs = await notificationService.listNotifications();
      if (Array.isArray(notifs)) {
        setUnreadNotifications(notifs.filter((n) => !n.is_read).length);
      }
    } catch {
      setAlertFeedback('Could not complete alert scan at this time.');
    } finally {
      setScanningAlerts(false);
    }
  };

  const totalAcres = farms.reduce((acc, f) => acc + (f.area_acres || 0), 0);

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-agri-900 via-agri-800 to-emerald-800 text-white rounded-3xl p-6 md:p-8 shadow-sm relative overflow-hidden">
        <div className="relative z-10 max-w-2xl">
          <Badge variant="primary" className="bg-agri-700/60 text-agri-100 border-agri-600 mb-3">
            {t('nav.decisionActive', 'Farmer Advisory Portal')}
          </Badge>
          <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight">
            {t('dashboard.welcome', 'Welcome back')}, {user?.name || 'Farmer'}!
          </h1>
          <p className="mt-2 text-agri-100 text-sm leading-relaxed">
            {user?.village ? `${user.village}, ` : ''}
            {user?.district ? `${user.district}, ` : ''}
            {user?.state || 'India'}
            {user?.land_size_acres ? ` • ${user.land_size_acres} ${t('common.acres', 'Acres')}` : ''}
          </p>
          <div className="mt-5 flex flex-wrap gap-3">
            <Link
              to="/crop-recommendation"
              className="inline-flex items-center space-x-2 px-4 py-2 bg-white hover:bg-agri-50 text-agri-900 text-xs font-bold rounded-xl shadow-xs transition"
            >
              <Sprout className="w-4 h-4 text-agri-600" />
              <span>{t('cropReco.title', 'Get Crop Recommendation')}</span>
            </Link>
            <button
              onClick={() => setAddFarmOpen(true)}
              className="inline-flex items-center space-x-2 px-4 py-2 bg-agri-700/60 hover:bg-agri-700 text-white border border-agri-500/50 text-xs font-semibold rounded-xl transition"
            >
              <Plus className="w-4 h-4" />
              <span>{t('farms.registerFarmBtn', 'Add Farm Plot')}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Alert Scan Feedback */}
      {alertFeedback && (
        <div className="p-4 bg-emerald-50 text-emerald-800 text-xs rounded-2xl border border-emerald-200 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>{alertFeedback}</span>
          </div>
          <button
            onClick={() => setAlertFeedback(null)}
            className="text-xs font-semibold text-emerald-700 hover:text-emerald-900"
          >
            {t('common.close', 'Dismiss')}
          </button>
        </div>
      )}

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title={t('farms.farmListTitle', 'Registered Farms')}
          value={loadingFarms ? '...' : farms.length}
          subtitle={totalAcres > 0 ? `${totalAcres.toFixed(1)} ${t('common.acres', 'Acres')}` : t('farms.emptyFarmsTitle', 'No land logged yet')}
          icon={Tractor}
          color="agri"
        />

        <StatCard
          title={t('weather.temp', 'Local Temperature')}
          value={
            loadingWeather
              ? t('common.loading', 'Loading...')
              : weather?.temp !== null && weather?.temp !== undefined
              ? `${weather.temp}°C`
              : 'Add Farm GPS'
          }
          subtitle={
            weather?.rainfall !== null && weather?.rainfall !== undefined
              ? `${weather.rainfall} mm • ${weather.humidity ?? '--'}% hum.`
              : 'GPS weather tracking'
          }
          icon={CloudSun}
          color="blue"
        />

        <StatCard
          title={t('notifications.title', 'Decision Alerts')}
          value={unreadNotifications}
          subtitle="Price & MSP alerts"
          icon={Bell}
          color="amber"
          badge={
            unreadNotifications > 0 ? (
              <Badge variant="warning">{unreadNotifications} Unread</Badge>
            ) : (
              <Badge variant="success">All Clear</Badge>
            )
          }
        />

        <StatCard
          title={t('prediction.title', 'Price Forecast')}
          value="1 to 30 Days"
          subtitle="Machine Learning AI"
          icon={TrendingUp}
          color="purple"
        />
      </div>

      {/* Quick Actions Grid */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wider">
            {t('dashboard.quickActionsTitle', 'Decision Support Modules')}
          </h3>
          <button
            onClick={handleRunAlertScan}
            disabled={scanningAlerts}
            className="inline-flex items-center space-x-1.5 text-xs text-agri-600 hover:text-agri-700 font-semibold disabled:opacity-50"
          >
            {scanningAlerts ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <ShieldAlert className="w-3.5 h-3.5" />
            )}
            <span>{scanningAlerts ? t('common.loading', 'Checking...') : 'Scan Price & MSP Alerts'}</span>
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Link
            to="/crop-recommendation"
            className="p-5 bg-white border border-slate-200/80 rounded-2xl shadow-xs hover:shadow-md hover:border-agri-200 transition group"
          >
            <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center mb-3 group-hover:scale-105 transition-transform">
              <Sprout className="w-5 h-5" />
            </div>
            <h4 className="font-bold text-sm text-slate-800">{t('cropReco.title', 'Crop Suitability AI')}</h4>
            <p className="text-xs text-slate-500 mt-1">
              Analyze soil N-P-K, pH & weather to get ranked crops.
            </p>
            <div className="mt-3 flex items-center space-x-1 text-xs font-semibold text-agri-600">
              <span>{t('common.view', 'Launch')}</span>
              <ArrowRight className="w-3 h-3" />
            </div>
          </Link>

          <Link
            to="/market-prices"
            className="p-5 bg-white border border-slate-200/80 rounded-2xl shadow-xs hover:shadow-md hover:border-amber-200 transition group"
          >
            <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center mb-3 group-hover:scale-105 transition-transform">
              <Store className="w-5 h-5" />
            </div>
            <h4 className="font-bold text-sm text-slate-800">{t('market.title', 'Live Mandi Prices')}</h4>
            <p className="text-xs text-slate-500 mt-1">
              Govt. Agmarknet rates for Wheat, Soyabean, Maize & Groundnut.
            </p>
            <div className="mt-3 flex items-center space-x-1 text-xs font-semibold text-amber-600">
              <span>{t('common.view', 'View Mandis')}</span>
              <ArrowRight className="w-3 h-3" />
            </div>
          </Link>

          <Link
            to="/price-prediction"
            className="p-5 bg-white border border-slate-200/80 rounded-2xl shadow-xs hover:shadow-md hover:border-blue-200 transition group"
          >
            <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center mb-3 group-hover:scale-105 transition-transform">
              <TrendingUp className="w-5 h-5" />
            </div>
            <h4 className="font-bold text-sm text-slate-800">{t('prediction.title', 'Price Prediction')}</h4>
            <p className="text-xs text-slate-500 mt-1">
              Time-series ML price forecast with interactive trend charts.
            </p>
            <div className="mt-3 flex items-center space-x-1 text-xs font-semibold text-blue-600">
              <span>{t('common.view', 'Predict')}</span>
              <ArrowRight className="w-3 h-3" />
            </div>
          </Link>

          <Link
            to="/msp-comparison"
            className="p-5 bg-white border border-slate-200/80 rounded-2xl shadow-xs hover:shadow-md hover:border-purple-200 transition group"
          >
            <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center mb-3 group-hover:scale-105 transition-transform">
              <Scale className="w-5 h-5" />
            </div>
            <h4 className="font-bold text-sm text-slate-800">{t('msp.title', 'MSP Benchmark')}</h4>
            <p className="text-xs text-slate-500 mt-1">
              Compare mandi market prices directly to official MSP support.
            </p>
            <div className="mt-3 flex items-center space-x-1 text-xs font-semibold text-purple-600">
              <span>{t('common.view', 'Compare')}</span>
              <ArrowRight className="w-3 h-3" />
            </div>
          </Link>
        </div>
      </div>

      {/* Farms Summary Widget */}
      <div className="bg-white border border-slate-200/80 rounded-3xl p-6 shadow-xs">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-bold text-slate-800">
              {t('farms.farmListTitle', 'Registered Farm Plots')}
            </h3>
            <p className="text-xs text-slate-500">
              {t('farms.subtitle', 'Manage your agricultural lands and soil test readings')}
            </p>
          </div>
          <Link
            to="/farms"
            className="text-xs font-bold text-agri-600 hover:text-agri-700 transition"
          >
            {t('dashboard.viewFarms', 'View All Farms')} &rarr;
          </Link>
        </div>

        {loadingFarms ? (
          <div className="py-8 text-center text-xs text-slate-400">{t('common.loading', 'Loading farms...')}</div>
        ) : farms.length === 0 ? (
          <div className="p-8 text-center bg-slate-50 rounded-2xl border border-dashed border-slate-200">
            <Tractor className="w-8 h-8 text-slate-400 mx-auto mb-2" />
            <p className="text-sm font-semibold text-slate-700">{t('farms.emptyFarmsTitle', 'No farms registered yet')}</p>
            <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
              {t('farms.emptyFarmsDesc', 'Add your farm GPS coordinates and soil data to enable AI crop recommendations and local weather forecasts.')}
            </p>
            <button
              onClick={() => setAddFarmOpen(true)}
              className="mt-4 px-4 py-2 bg-agri-600 hover:bg-agri-700 text-white text-xs font-semibold rounded-xl shadow-xs transition"
            >
              {t('farms.registerFarmBtn', 'Add Your First Farm')}
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-100 text-slate-400 font-semibold uppercase tracking-wider">
                  <th className="pb-3">Farm ID</th>
                  <th className="pb-3">{t('farms.locationLabel', 'Latitude / Longitude')}</th>
                  <th className="pb-3">{t('common.acres', 'Area (Acres)')}</th>
                  <th className="pb-3 text-right">{t('common.actions', 'Action')}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {farms.slice(0, 4).map((farm) => (
                  <tr key={farm.farm_id} className="hover:bg-slate-50/60">
                    <td className="py-3 font-semibold text-slate-800">#{farm.farm_id}</td>
                    <td className="py-3 text-slate-600">
                      {farm.latitude.toFixed(4)}, {farm.longitude.toFixed(4)}
                    </td>
                    <td className="py-3 text-slate-600">{farm.area_acres} {t('common.acres', 'Acres')}</td>
                    <td className="py-3 text-right">
                      <Link
                        to="/farms"
                        className="text-xs font-semibold text-agri-600 hover:text-agri-700"
                      >
                        {t('common.details', 'Details')} &rarr;
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <AddFarmModal isOpen={addFarmOpen} onClose={() => setAddFarmOpen(false)} />
    </div>
  );
};

export default DashboardPage;
