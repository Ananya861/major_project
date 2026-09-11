import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useTranslation } from '../i18n/LanguageContext';
import { catalogService } from '../services/catalogService';
import { marketService, CROP_BENCHMARK_MARKET_MAP } from '../services/marketService';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';
import Badge from '../components/common/Badge';
import {
  TrendingUp,
  Calendar,
  Sparkles,
  BarChart3,
  ArrowUpRight,
  ArrowDownRight,
  HelpCircle,
  MapPin,
} from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Area,
  AreaChart,
} from 'recharts';
import { formatCurrency, formatDate } from '../utils/formatters';

const PricePredictionPage = () => {
  const { t } = useTranslation();
  const [searchParams] = useSearchParams();

  const [states, setStates] = useState([]);
  const [selectedState, setSelectedState] = useState('');
  const [crops, setCrops] = useState([]);
  const [markets, setMarkets] = useState([]);
  const [loadingCatalog, setLoadingCatalog] = useState(true);
  const [loadingMarkets, setLoadingMarkets] = useState(false);

  const [selectedCropId, setSelectedCropId] = useState('');
  const [selectedMarketId, setSelectedMarketId] = useState('');
  const [daysAhead, setDaysAhead] = useState(7);

  const [forecastData, setForecastData] = useState(null);
  const [loadingForecast, setLoadingForecast] = useState(false);
  const [error, setError] = useState(null);

  const initialPredictDone = React.useRef(false);
  const selectedCropIdRef = React.useRef(selectedCropId);
  const selectedMarketIdRef = React.useRef(selectedMarketId);
  const daysAheadRef = React.useRef(daysAhead);

  useEffect(() => {
    selectedCropIdRef.current = selectedCropId;
  }, [selectedCropId]);

  useEffect(() => {
    selectedMarketIdRef.current = selectedMarketId;
  }, [selectedMarketId]);

  useEffect(() => {
    daysAheadRef.current = daysAhead;
  }, [daysAhead]);

  const handlePredict = useCallback(async (cId, mId, horizon) => {
    const cropIdToUse =
      typeof cId === 'string' || typeof cId === 'number'
        ? String(cId)
        : selectedCropIdRef.current;
    const marketIdToUse =
      typeof mId === 'string' || typeof mId === 'number'
        ? String(mId)
        : selectedMarketIdRef.current;
    const horizonToUse =
      typeof horizon === 'number' ? horizon : daysAheadRef.current;

    if (!cropIdToUse || !marketIdToUse) {
      setError('Please select both a crop and a market.');
      return;
    }

    setLoadingForecast(true);
    setError(null);
    setForecastData(null);

    try {
      const data = await marketService.getPricePrediction(
        cropIdToUse,
        marketIdToUse,
        horizonToUse
      );
      setForecastData(data);
    } catch (err) {
      setError(
        err.friendlyMessage ||
        err.message ||
        'Price forecast failed. Note: The ML model currently supports primary agricultural commodities and requires at least 3 historical price records.'
      );
    } finally {
      setLoadingForecast(false);
    }
  }, []);

  const cropParam = searchParams.get('crop_id') || '';
  const marketParam = searchParams.get('market_id') || '';

  // Load catalog
  useEffect(() => {
    let isMounted = true;
    const loadCatalog = async () => {
      setLoadingCatalog(true);
      try {
        const [cropsData, marketsData, statesData] = await Promise.all([
          catalogService.getCrops(),
          catalogService.getMarkets(),
          catalogService.getStates(),
        ]);
        if (isMounted) {
          setCrops(cropsData);
          setMarkets(marketsData);
          setStates(statesData || []);

          const wheatCrop = cropsData.find((c) => c.name?.toLowerCase() === 'wheat');
          const defaultCrop = wheatCrop || cropsData[0];

          const initialCropId = cropParam || (defaultCrop ? String(defaultCrop.crop_id) : '');
          const benchmarkMarketId =
            initialCropId && CROP_BENCHMARK_MARKET_MAP[initialCropId]
              ? String(CROP_BENCHMARK_MARKET_MAP[initialCropId])
              : (marketsData.length > 0 ? String(marketsData[0].market_id) : '');
          const initialMarketId = marketParam || benchmarkMarketId;

          setSelectedCropId((prev) => cropParam || prev || initialCropId);
          setSelectedMarketId((prev) => marketParam || prev || initialMarketId);

          if (marketParam) {
            const foundMarket = marketsData.find((m) => String(m.market_id) === String(marketParam));
            if (foundMarket?.state) {
              setSelectedState(foundMarket.state);
            }
          }

          if (initialCropId && initialMarketId && !initialPredictDone.current) {
            initialPredictDone.current = true;
            handlePredict(initialCropId, initialMarketId, daysAheadRef.current);
          }
        }
      } catch {
        // Silently fail
      } finally {
        if (isMounted) setLoadingCatalog(false);
      }
    };
    loadCatalog();
    return () => {
      isMounted = false;
    };
  }, [cropParam, marketParam, handlePredict]);

  const handleStateChange = async (newState) => {
    setSelectedState(newState);
    setLoadingMarkets(true);
    try {
      const filteredMarkets = await catalogService.getMarkets(newState);
      setMarkets(filteredMarkets);
      if (filteredMarkets.length > 0) {
        const currentStillExists = filteredMarkets.some(
          (m) => String(m.market_id) === String(selectedMarketId)
        );
        if (!currentStillExists) {
          setSelectedMarketId(String(filteredMarkets[0].market_id));
        }
      } else {
        setSelectedMarketId('');
      }
    } catch (err) {
      console.error('Failed to filter markets by state:', err);
    } finally {
      setLoadingMarkets(false);
    }
  };

  const chartData =
    forecastData?.forecast?.map((item) => ({
      date: item.date,
      formattedDate: formatDate(item.date),
      price: item.predicted_price !== undefined ? item.predicted_price : item.predicted_modal_price,
      trend: item.trend,
    })) || [];

  const firstPrice =
    forecastData?.forecast?.[0]?.predicted_price !== undefined
      ? forecastData?.forecast?.[0]?.predicted_price
      : forecastData?.forecast?.[0]?.predicted_modal_price;

  const lastPrice =
    forecastData?.forecast?.length
      ? (forecastData.forecast[forecastData.forecast.length - 1]?.predicted_price !== undefined
          ? forecastData.forecast[forecastData.forecast.length - 1]?.predicted_price
          : forecastData.forecast[forecastData.forecast.length - 1]?.predicted_modal_price)
      : null;

  const priceChange = firstPrice != null && lastPrice != null ? lastPrice - firstPrice : 0;
  const priceChangePct = firstPrice ? (priceChange / firstPrice) * 100 : 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <div className="flex flex-wrap items-center gap-2 mb-2">
          <div className="inline-flex items-center space-x-2 text-xs font-semibold text-blue-700 bg-blue-50 px-3 py-1 rounded-full border border-blue-200">
            <Sparkles className="w-3.5 h-3.5 text-blue-600" />
            <span>{t('prediction.title', 'Mandi Price Forecasting')}</span>
          </div>
          <div className="inline-flex items-center space-x-1.5 text-xs font-medium text-slate-600 bg-slate-100 px-3 py-1 rounded-full border border-slate-200">
            <MapPin className="w-3.5 h-3.5 text-slate-500" />
            <span>Pan-India Mandi Network ({markets.length} Markets)</span>
          </div>
        </div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
          {t('prediction.title', 'Mandi Price Forecasting')}
        </h1>
        <p className="text-xs text-slate-500 mt-1 max-w-2xl">
          {t('prediction.subtitle', 'Time-series machine learning forecast of commodity modal prices for the upcoming 7 to 30 days.')}
        </p>
      </div>

      {loadingCatalog ? (
        <LoadingSpinner message={t('common.loading', 'Loading commodities and markets...')} />
      ) : (
        <div className="space-y-6">
          {/* Inputs Bar */}
          <div className="bg-white border border-slate-200/80 rounded-3xl p-6 shadow-xs">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 items-end">
              {/* State Filter */}
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                  {t('market.stateLabel', 'State / Region')}
                </label>
                <select
                  value={selectedState}
                  onChange={(e) => handleStateChange(e.target.value)}
                  className="w-full px-4 py-3 text-sm font-semibold text-slate-800 border border-slate-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 bg-slate-50/50"
                >
                  <option value="">{t('market.allStates', 'All States / Pan-India')}</option>
                  {states.map((st) => (
                    <option key={st} value={st}>
                      {st}
                    </option>
                  ))}
                </select>
              </div>

              {/* Commodity */}
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                  {t('market.commodityLabel', 'Commodity')}
                </label>
                <select
                  value={selectedCropId}
                  onChange={(e) => {
                    const newCropId = e.target.value;
                    setSelectedCropId(newCropId);
                    if (CROP_BENCHMARK_MARKET_MAP[newCropId]) {
                      setSelectedMarketId(String(CROP_BENCHMARK_MARKET_MAP[newCropId]));
                    }
                  }}
                  className="w-full px-4 py-3 text-sm font-semibold text-slate-800 border border-slate-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 bg-slate-50/50"
                >
                  {crops.map((c) => (
                    <option key={c.crop_id} value={String(c.crop_id)}>
                      {c.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Mandi Market */}
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                  {t('market.marketLabel', 'Mandi Market')} {loadingMarkets ? '...' : `(${markets.length})`}
                </label>
                <select
                  value={selectedMarketId}
                  onChange={(e) => setSelectedMarketId(e.target.value)}
                  disabled={loadingMarkets || markets.length === 0}
                  className="w-full px-4 py-3 text-sm font-semibold text-slate-800 border border-slate-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 bg-slate-50/50 disabled:opacity-50"
                >
                  {markets.map((m) => (
                    <option key={m.market_id} value={String(m.market_id)}>
                      {m.name} {m.district ? `(${m.district}, ${m.state})` : (m.state ? `(${m.state})` : '')}
                    </option>
                  ))}
                </select>
              </div>

              {/* Forecast Horizon */}
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                  {t('prediction.daysAheadLabel', 'Horizon (Days)')}
                </label>
                <select
                  value={daysAhead}
                  onChange={(e) => setDaysAhead(Number(e.target.value))}
                  className="w-full px-4 py-3 text-sm font-semibold text-slate-800 border border-slate-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 bg-slate-50/50"
                >
                  <option value={3}>3 Days Ahead</option>
                  <option value={5}>5 Days Ahead</option>
                  <option value={7}>7 Days Ahead</option>
                  <option value={10}>10 Days Ahead</option>
                  <option value={14}>14 Days Ahead</option>
                  <option value={30}>30 Days Ahead</option>
                </select>
              </div>

              {/* Action Button */}
              <div>
                <button
                  onClick={() => handlePredict(selectedCropId, selectedMarketId, daysAhead)}
                  disabled={loadingForecast || !selectedMarketId}
                  className="w-full py-3 px-5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-bold rounded-2xl shadow-sm shadow-blue-600/20 transition flex items-center justify-center space-x-2 disabled:opacity-50"
                >
                  {loadingForecast ? (
                    <LoadingSpinner size="sm" message="" />
                  ) : (
                    <TrendingUp className="w-4 h-4" />
                  )}
                  <span>{loadingForecast ? t('prediction.evaluating', 'Forecasting...') : t('prediction.predictBtn', 'Generate Forecast')}</span>
                </button>
              </div>
            </div>
          </div>

          <ErrorMessage message={error} onRetry={() => handlePredict(selectedCropId, selectedMarketId, daysAhead)} />

          {loadingForecast && (
            <div className="py-12 bg-white rounded-3xl border border-slate-200/80">
              <LoadingSpinner
                size="lg"
                message={t('prediction.evaluating', 'Running HistGradientBoosting price inference over historical mandi arrivals...')}
              />
            </div>
          )}

          {forecastData && (
            <div className="space-y-6">
              {/* Summary Stats Banner */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="p-5 bg-white border border-slate-200/80 rounded-2xl shadow-xs">
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                    {t('common.date', 'Day')} 1 {t('market.currentModalPrice', 'Predicted Price')}
                  </span>
                  <div className="text-2xl font-extrabold text-slate-800 mt-1">
                    {formatCurrency(firstPrice)}
                  </div>
                  <span className="text-xs text-slate-500">{t('market.perQuintal', 'per Quintal')}</span>
                </div>

                <div className="p-5 bg-white border border-slate-200/80 rounded-2xl shadow-xs">
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                    {t('common.date', 'Day')} {daysAhead} {t('market.currentModalPrice', 'Predicted Price')}
                  </span>
                  <div className="text-2xl font-extrabold text-slate-800 mt-1">
                    {formatCurrency(lastPrice)}
                  </div>
                  <span className="text-xs text-slate-500">{t('market.perQuintal', 'per Quintal')}</span>
                </div>

                <div className="p-5 bg-white border border-slate-200/80 rounded-2xl shadow-xs">
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                    {t('msp.differenceVsMsp', 'Forecast Trend')}
                  </span>
                  <div
                    className={`text-2xl font-extrabold mt-1 flex items-center space-x-1 ${priceChange >= 0 ? 'text-emerald-600' : 'text-rose-600'
                      }`}
                  >
                    {priceChange >= 0 ? (
                      <ArrowUpRight className="w-6 h-6" />
                    ) : (
                      <ArrowDownRight className="w-6 h-6" />
                    )}
                    <span>{Math.abs(priceChangePct).toFixed(2)}%</span>
                  </div>
                  <span className="text-xs text-slate-500">
                    {priceChange >= 0 ? t('msp.statusAboveMsp', 'Expected price rise') : t('msp.statusBelowMsp', 'Expected price dip')}
                  </span>
                </div>
              </div>

              {/* Chart Card */}
              <div className="bg-white border border-slate-200/80 rounded-3xl p-6 md:p-8 shadow-xs">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h3 className="text-lg font-bold text-slate-900">
                      {t('prediction.forecastChartTitle', 'Expected Price Trend (₹/Quintal)')}
                    </h3>
                    <p className="text-xs text-slate-500">
                      {t('market.currentModalPrice', 'Predicted daily modal price')} (₹ / quintal)
                    </p>
                  </div>
                  <Badge variant="primary">ML Model</Badge>
                </div>

                <div className="h-72 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                      <defs>
                        <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#2563eb" stopOpacity={0.2} />
                          <stop offset="95%" stopColor="#2563eb" stopOpacity={0.0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                      <XAxis
                        dataKey="formattedDate"
                        tick={{ fontSize: 11, fill: '#64748b' }}
                        tickLine={false}
                        axisLine={{ stroke: '#e2e8f0' }}
                      />
                      <YAxis
                        domain={['auto', 'auto']}
                        tick={{ fontSize: 11, fill: '#64748b' }}
                        tickLine={false}
                        axisLine={{ stroke: '#e2e8f0' }}
                        tickFormatter={(v) => `₹${v}`}
                      />
                      <Tooltip
                        formatter={(val) => [`₹${val}`, 'Predicted Price']}
                        labelFormatter={(label) => `Date: ${label}`}
                        contentStyle={{
                          borderRadius: '12px',
                          border: '1px solid #e2e8f0',
                          boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.05)',
                        }}
                      />
                      <Area
                        type="monotone"
                        dataKey="price"
                        stroke="#2563eb"
                        strokeWidth={3}
                        fillOpacity={1}
                        fill="url(#priceGradient)"
                        dot={{ r: 4, fill: '#2563eb', strokeWidth: 2, stroke: '#fff' }}
                        activeDot={{ r: 6 }}
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Data Table */}
              <div className="bg-white border border-slate-200/80 rounded-3xl p-6 shadow-xs">
                <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wider mb-4">
                  {t('prediction.forecastTableTitle', 'Daily Forecasted Rates')}
                </h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-slate-100 text-slate-400 font-semibold uppercase tracking-wider">
                        <th className="pb-3">{t('common.date', 'Forecast Date')}</th>
                        <th className="pb-3">{t('market.currentModalPrice', 'Predicted Modal Price')}</th>
                        <th className="pb-3 text-right">{t('msp.differenceVsMsp', 'Shift')}</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {chartData.map((item, idx) => {
                        const prev = idx > 0 ? chartData[idx - 1].price : null;
                        const diff = prev ? item.price - prev : 0;
                        const diffPct = prev ? (diff / prev) * 100 : 0;

                        return (
                          <tr key={item.date} className="hover:bg-slate-50/60">
                            <td className="py-3 font-semibold text-slate-800">
                              {item.formattedDate}
                            </td>
                            <td className="py-3 font-bold text-slate-900">
                              {formatCurrency(item.price)}
                            </td>
                            <td className="py-3 text-right font-medium">
                              {idx === 0 ? (
                                <span className="text-slate-400">Baseline</span>
                              ) : (
                                <span
                                  className={
                                    diff >= 0 ? 'text-emerald-600' : 'text-rose-600'
                                  }
                                >
                                  {diff >= 0 ? '+' : ''}
                                  {formatCurrency(diff)} ({diffPct.toFixed(2)}%)
                                </span>
                              )}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default PricePredictionPage;
