import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useFarm } from '../context/FarmContext';
import { weatherService } from '../services/weatherService';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';
import Badge from '../components/common/Badge';
import {
  CloudSun,
  Droplets,
  Thermometer,
  CloudRain,
  MapPin,
  Calendar,
  Compass,
  Loader2,
  Database,
  Radio,
  Search,
} from 'lucide-react';
import { formatDateTime } from '../utils/formatters';

const WeatherPage = () => {
  const [searchParams] = useSearchParams();
  const { farms } = useFarm();

  const [lat, setLat] = useState('');
  const [lng, setLng] = useState('');
  const [selectedFarmId, setSelectedFarmId] = useState('');

  const [weatherData, setWeatherData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [locating, setLocating] = useState(false);

  // Initialize lat/lng from URL or first farm
  useEffect(() => {
    const qLat = searchParams.get('lat');
    const qLng = searchParams.get('lng');

    if (qLat && qLng) {
      setLat(qLat);
      setLng(qLng);
    } else if (farms.length > 0 && !lat && !lng) {
      setLat(String(farms[0].latitude));
      setLng(String(farms[0].longitude));
      setSelectedFarmId(String(farms[0].farm_id));
    } else if (!lat && !lng) {
      // Default to central India coordinate
      setLat('23.8340');
      setLng('76.9140');
    }
  }, [searchParams, farms, lat, lng]);

  const handleFetchWeather = useCallback(async (latitude = lat, longitude = lng) => {
    const parsedLat = parseFloat(latitude);
    const parsedLng = parseFloat(longitude);

    if (isNaN(parsedLat) || isNaN(parsedLng)) {
      setError('Please provide valid latitude and longitude coordinates.');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const data = await weatherService.getWeather(parsedLat, parsedLng);
      setWeatherData(data);
    } catch (err) {
      setError(err.friendlyMessage || 'Unable to retrieve weather data for these coordinates.');
    } finally {
      setLoading(false);
    }
  }, [lat, lng]);

  const initialWeatherDone = React.useRef(false);

  useEffect(() => {
    if (lat && lng && !initialWeatherDone.current) {
      initialWeatherDone.current = true;
      handleFetchWeather(lat, lng);
    }
  }, [lat, lng, handleFetchWeather]);

  const handleSelectFarm = (farmId) => {
    setSelectedFarmId(farmId);
    const farm = farms.find((f) => String(f.farm_id) === String(farmId));
    if (farm) {
      setLat(String(farm.latitude));
      setLng(String(farm.longitude));
      handleFetchWeather(farm.latitude, farm.longitude);
    }
  };

  const handleUseCurrentGps = () => {
    if (!navigator.geolocation) {
      setError('Geolocation is not supported by your browser');
      return;
    }
    setLocating(true);
    setSelectedFarmId('');
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const cLat = pos.coords.latitude.toFixed(4);
        const cLng = pos.coords.longitude.toFixed(4);
        setLat(cLat);
        setLng(cLng);
        setLocating(false);
        handleFetchWeather(cLat, cLng);
      },
      (err) => {
        setError(`Location access denied: ${err.message}`);
        setLocating(false);
      }
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <div className="inline-flex items-center space-x-2 text-xs font-semibold text-sky-700 bg-sky-50 px-3 py-1 rounded-full border border-sky-200 mb-2">
          <CloudSun className="w-3.5 h-3.5 text-sky-600" />
          <span>OpenWeather &amp; Agro-Climatic Intelligence</span>
        </div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
          Weather Intelligence &amp; Forecast
        </h1>
        <p className="text-xs text-slate-500 mt-1 max-w-2xl">
          Live agro-climatic readings matched to your farm coordinates. Supplies temperature and
          precipitation data to the Crop Recommendation AI engine.
        </p>
      </div>

      {/* Coordinate & Farm Controls */}
      <div className="bg-white border border-slate-200/80 rounded-3xl p-6 shadow-xs">
        <div className="space-y-4">
          {farms.length > 0 && (
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Quick Select from Registered Farms
              </label>
              <div className="flex flex-wrap gap-2">
                {farms.map((f) => (
                  <button
                    key={f.farm_id}
                    onClick={() => handleSelectFarm(f.farm_id)}
                    className={`px-3.5 py-2 rounded-xl text-xs font-semibold border transition ${
                      String(selectedFarmId) === String(f.farm_id)
                        ? 'bg-agri-600 text-white border-agri-600 shadow-xs'
                        : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
                    }`}
                  >
                    Farm #{f.farm_id} ({f.area_acres} Ac)
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 items-end pt-2">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Latitude</label>
              <input
                type="number"
                step="any"
                value={lat}
                onChange={(e) => {
                  setLat(e.target.value);
                  setSelectedFarmId('');
                }}
                className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-agri-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Longitude</label>
              <input
                type="number"
                step="any"
                value={lng}
                onChange={(e) => {
                  setLng(e.target.value);
                  setSelectedFarmId('');
                }}
                className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-agri-500"
              />
            </div>

            <div>
              <button
                type="button"
                onClick={handleUseCurrentGps}
                disabled={locating}
                className="w-full py-2 px-3 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-xl border border-slate-200 transition flex items-center justify-center space-x-1.5 h-[38px]"
              >
                {locating ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <Compass className="w-3.5 h-3.5 text-slate-500" />
                )}
                <span>{locating ? 'GPS Detecting...' : 'Use My GPS'}</span>
              </button>
            </div>

            <div>
              <button
                onClick={() => handleFetchWeather(lat, lng)}
                disabled={loading}
                className="w-full py-2 px-4 bg-agri-600 hover:bg-agri-700 text-white text-xs font-bold rounded-xl shadow-xs transition flex items-center justify-center space-x-1.5 h-[38px] disabled:opacity-50"
              >
                {loading ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <Search className="w-3.5 h-3.5" />
                )}
                <span>{loading ? 'Fetching...' : 'Query Weather'}</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <ErrorMessage message={error} onRetry={() => handleFetchWeather(lat, lng)} />

      {loading && (
        <div className="py-12 bg-white rounded-3xl border border-slate-200/80">
          <LoadingSpinner
            size="lg"
            message="Querying real-time satellite weather for coordinates..."
          />
        </div>
      )}

      {weatherData && (
        <div className="bg-white border border-slate-200/80 rounded-3xl p-6 md:p-8 shadow-xs space-y-6">
          {/* Weather Status Top Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 border-b border-slate-100 gap-4">
            <div>
              <div className="flex items-center space-x-3">
                <h2 className="text-2xl font-extrabold text-slate-900 tracking-tight">
                  Agro-Weather Report
                </h2>
                {weatherData.cached ? (
                  <Badge variant="neutral" className="flex items-center space-x-1">
                    <Database className="w-3 h-3" />
                    <span>Cached Reading</span>
                  </Badge>
                ) : (
                  <Badge variant="success" className="flex items-center space-x-1">
                    <Radio className="w-3 h-3 animate-pulse text-emerald-600" />
                    <span>Live Weather Sync</span>
                  </Badge>
                )}
              </div>

              <p className="text-xs text-slate-500 mt-1 flex items-center space-x-1.5">
                <MapPin className="w-3.5 h-3.5 text-slate-400" />
                <span>
                  {weatherData.latitude.toFixed(4)}° N, {weatherData.longitude.toFixed(4)}° E
                </span>
                <span>•</span>
                <Calendar className="w-3.5 h-3.5 text-slate-400" />
                <span>Recorded: {formatDateTime(weatherData.date)}</span>
              </p>
            </div>
          </div>

          {/* Core Metrics */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="p-6 bg-gradient-to-br from-amber-50 to-orange-50/50 border border-amber-200/80 rounded-2xl">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-amber-800 uppercase tracking-wider">
                  Temperature
                </span>
                <Thermometer className="w-5 h-5 text-amber-600" />
              </div>
              <div className="text-4xl font-extrabold text-amber-950 tracking-tight">
                {weatherData.temp !== null && weatherData.temp !== undefined
                  ? `${weatherData.temp}°C`
                  : 'N/A'}
              </div>
              <span className="text-xs text-amber-700 mt-1 block">Ambient temperature</span>
            </div>

            <div className="p-6 bg-gradient-to-br from-blue-50 to-sky-50/50 border border-blue-200/80 rounded-2xl">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-blue-800 uppercase tracking-wider">
                  Rainfall / Precipitation
                </span>
                <CloudRain className="w-5 h-5 text-blue-600" />
              </div>
              <div className="text-4xl font-extrabold text-blue-950 tracking-tight">
                {weatherData.rainfall !== null && weatherData.rainfall !== undefined
                  ? `${weatherData.rainfall} mm`
                  : '0.0 mm'}
              </div>
              <span className="text-xs text-blue-700 mt-1 block">Local precipitation</span>
            </div>

            <div className="p-6 bg-gradient-to-br from-teal-50 to-emerald-50/50 border border-teal-200/80 rounded-2xl">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-teal-800 uppercase tracking-wider">
                  Relative Humidity
                </span>
                <Droplets className="w-5 h-5 text-teal-600" />
              </div>
              <div className="text-4xl font-extrabold text-teal-950 tracking-tight">
                {weatherData.humidity !== null && weatherData.humidity !== undefined
                  ? `${weatherData.humidity}%`
                  : 'N/A'}
              </div>
              <span className="text-xs text-teal-700 mt-1 block">Atmospheric moisture</span>
            </div>
          </div>

          {/* Additional Forecast Insights if present */}
          {weatherData.forecast && (
            <div className="p-5 bg-slate-50 rounded-2xl border border-slate-200/70">
              <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Forecast Observations
              </h4>
              <p className="text-xs text-slate-600">
                {typeof weatherData.forecast === 'string'
                  ? weatherData.forecast
                  : JSON.stringify(weatherData.forecast)}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default WeatherPage;
