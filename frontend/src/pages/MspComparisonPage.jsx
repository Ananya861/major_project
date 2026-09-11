import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useTranslation } from '../i18n/LanguageContext';
import { catalogService } from '../services/catalogService';
import { marketService } from '../services/marketService';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';
import Badge from '../components/common/Badge';
import {
  Scale,
  Calendar,
  CheckCircle2,
  AlertTriangle,
  ArrowUpRight,
  ArrowDownRight,
  Search,
  MapPin,
  Info,
} from 'lucide-react';
import { formatCurrency, formatDate } from '../utils/formatters';

const MSP_SUPPORTED_CROPS = new Set([
  'wheat',
  'maize',
  'soyabean',
  'groundnut',
  'rice',
  'paddy',
  'paddy(common)',
  'mustard',
  'chickpea',
  'bengal gram',
  'mungbean',
  'green gram',
  'blackgram',
  'cotton',
  'pigeonpeas',
  'lentil',
  'jute',
]);

const MspComparisonPage = () => {
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

  const [mspData, setMspData] = useState(null);
  const [loadingMsp, setLoadingMsp] = useState(false);
  const [error, setError] = useState(null);

  const initialCompareDone = React.useRef(false);
  const selectedCropIdRef = React.useRef(selectedCropId);
  const selectedMarketIdRef = React.useRef(selectedMarketId);

  useEffect(() => {
    selectedCropIdRef.current = selectedCropId;
  }, [selectedCropId]);

  useEffect(() => {
    selectedMarketIdRef.current = selectedMarketId;
  }, [selectedMarketId]);

  const handleCompare = useCallback(async (cId, mId) => {
    const cropIdToUse =
      typeof cId === 'string' || typeof cId === 'number'
        ? String(cId)
        : selectedCropIdRef.current;
    const marketIdToUse =
      typeof mId === 'string' || typeof mId === 'number'
        ? String(mId)
        : selectedMarketIdRef.current;

    if (!cropIdToUse || !marketIdToUse) {
      setError('Please select both a crop and a market.');
      return;
    }

    setLoadingMsp(true);
    setError(null);
    setMspData(null);

    try {
      const data = await marketService.getMspComparison(cropIdToUse, marketIdToUse);
      const mspRecord = Array.isArray(data) ? data[0] : data;
      if (!mspRecord || mspRecord.modal_price === undefined) {
        setError('No mandi price data available for this crop and market.');
        setMspData(null);
      } else {
        setMspData(mspRecord);
      }
    } catch (err) {
      setError(
        err.friendlyMessage ||
          'No mandi price data available for this crop and market.'
      );
      setMspData(null);
    } finally {
      setLoadingMsp(false);
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

          // Preferred default: Wheat (has verified MSP)
          const wheatCrop = cropsData.find((c) => c.name?.toLowerCase() === 'wheat');
          const defaultCrop = wheatCrop || cropsData[0];

          const initialCropId = cropParam || (defaultCrop ? String(defaultCrop.crop_id) : '');
          const initialMarketId = marketParam || (marketsData.length > 0 ? String(marketsData[0].market_id) : '');

          setSelectedCropId((prev) => cropParam || prev || initialCropId);
          setSelectedMarketId((prev) => marketParam || prev || initialMarketId);

          if (marketParam) {
            const foundMarket = marketsData.find((m) => String(m.market_id) === String(marketParam));
            if (foundMarket?.state) {
              setSelectedState(foundMarket.state);
            }
          }

          if (initialCropId && initialMarketId && !initialCompareDone.current) {
            initialCompareDone.current = true;
            handleCompare(initialCropId, initialMarketId);
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
  }, [cropParam, marketParam, handleCompare]);

  // Handle state change
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

  const getStatusBadge = (status) => {
    if (status === 'ABOVE_MSP') {
      return (
        <Badge variant="success" className="text-xs px-3 py-1">
          {t('msp.statusAboveMsp', 'Trading Above MSP')}
        </Badge>
      );
    }
    if (status === 'BELOW_MSP') {
      return (
        <Badge variant="danger" className="text-xs px-3 py-1">
          {t('msp.statusBelowMsp', 'Trading Below MSP')}
        </Badge>
      );
    }
    if (status === 'NOT_APPLICABLE') {
      return (
        <Badge variant="neutral" className="text-xs px-3 py-1">
          Market Driven (No Statutory MSP)
        </Badge>
      );
    }
    return (
      <Badge variant="neutral" className="text-xs px-3 py-1">
        {t('msp.statusAtMsp', 'At Par with MSP')}
      </Badge>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <div className="flex flex-wrap items-center gap-2 mb-2">
          <div className="inline-flex items-center space-x-2 text-xs font-semibold text-purple-700 bg-purple-50 px-3 py-1 rounded-full border border-purple-200">
            <Scale className="w-3.5 h-3.5 text-purple-600" />
            <span>{t('msp.benchmarkBadge', 'Government Price Floor Benchmark')}</span>
          </div>
          <div className="inline-flex items-center space-x-1.5 text-xs font-medium text-slate-600 bg-slate-100 px-3 py-1 rounded-full border border-slate-200">
            <MapPin className="w-3.5 h-3.5 text-slate-500" />
            <span>Pan-India Mandi Network ({markets.length} Markets)</span>
          </div>
        </div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
          {t('msp.title', 'MSP Comparison & Fair Price Analysis')}
        </h1>
        <p className="text-xs text-slate-500 mt-1 max-w-2xl">
          {t('msp.subtitle', 'Compares current daily mandi modal prices with official Government of India Minimum Support Prices (MSP).')}
        </p>
      </div>

      {loadingCatalog ? (
        <LoadingSpinner message={t('common.loading', 'Loading commodity catalog & markets...')} />
      ) : (
        <div className="space-y-6">
          {/* Controls Bar */}
          <div className="bg-white border border-slate-200/80 rounded-3xl p-6 shadow-xs">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 items-end">
              {/* State Filter */}
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                  {t('market.stateLabel', 'State / Region')}
                </label>
                <select
                  value={selectedState}
                  onChange={(e) => handleStateChange(e.target.value)}
                  className="w-full px-4 py-3 text-sm font-semibold text-slate-800 border border-slate-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-agri-500 bg-slate-50/50"
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
                  onChange={(e) => setSelectedCropId(e.target.value)}
                  className="w-full px-4 py-3 text-sm font-semibold text-slate-800 border border-slate-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-purple-500 bg-slate-50/50"
                >
                  {crops.map((c) => {
                    const hasMsp = MSP_SUPPORTED_CROPS.has(c.name.toLowerCase());
                    return (
                      <option key={c.crop_id} value={String(c.crop_id)}>
                        {c.name} {hasMsp ? '★ (Govt MSP)' : ''}
                      </option>
                    );
                  })}
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
                  className="w-full px-4 py-3 text-sm font-semibold text-slate-800 border border-slate-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-purple-500 bg-slate-50/50 disabled:opacity-50"
                >
                  {markets.map((m) => (
                    <option key={m.market_id} value={String(m.market_id)}>
                      {m.name} {m.district ? `(${m.district}, ${m.state})` : (m.state ? `(${m.state})` : '')}
                    </option>
                  ))}
                </select>
              </div>

              {/* Action Button */}
              <div>
                <button
                  onClick={() => handleCompare(selectedCropId, selectedMarketId)}
                  disabled={loadingMsp || !selectedMarketId}
                  className="w-full py-3 px-5 bg-purple-600 hover:bg-purple-700 text-white text-sm font-bold rounded-2xl shadow-sm shadow-purple-600/20 transition flex items-center justify-center space-x-2 disabled:opacity-50"
                >
                  {loadingMsp ? (
                    <LoadingSpinner size="sm" message="" />
                  ) : (
                    <Search className="w-4 h-4" />
                  )}
                  <span>{loadingMsp ? t('msp.evaluating', 'Evaluating Market...') : t('msp.compareBtn', 'Run MSP Comparison')}</span>
                </button>
              </div>
            </div>
          </div>

          <ErrorMessage message={error} onRetry={() => handleCompare(selectedCropId, selectedMarketId)} />

          {loadingMsp && (
            <div className="py-12 bg-white rounded-3xl border border-slate-200/80">
              <LoadingSpinner
                size="lg"
                message="Retrieving latest market price & matching with official MSP benchmarks..."
              />
            </div>
          )}

          {mspData && (
            <div className="bg-white border border-slate-200/80 rounded-3xl p-6 md:p-8 shadow-xs space-y-6">
              {/* Header Status */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 border-b border-slate-100 gap-4">
                <div>
                  <div className="flex items-center space-x-3">
                    <h2 className="text-2xl font-extrabold text-slate-900 tracking-tight">
                      {mspData.crop} {t('msp.benchmarkBadge', 'MSP Benchmark')}
                    </h2>
                    {getStatusBadge(mspData.status)}
                  </div>
                  <p className="text-xs text-slate-500 mt-1 flex items-center space-x-1.5">
                    <span>
                      {mspData.market} Mandi{mspData.district ? `, ${mspData.district}` : ''} ({mspData.state})
                    </span>
                    <span>•</span>
                    <Calendar className="w-3.5 h-3.5 text-slate-400" />
                    <span>{t('market.arrivalDate', 'Price Date')}: {formatDate(mspData.market_price_date)}</span>
                  </p>
                </div>

                <div className="text-xs text-slate-500 bg-slate-50 px-3.5 py-2 rounded-xl border border-slate-100">
                  <span className="font-semibold text-slate-700">{mspData.season || 'Standard'}</span> •{' '}
                  <span>{mspData.marketing_year || '2026-27'}</span>
                </div>
              </div>

              {/* Numerical Comparison Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Mandi Modal Price */}
                <div className="p-6 bg-slate-50 border border-slate-200/80 rounded-2xl">
                  <span className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 block">
                    {t('msp.mandiModalPrice', 'Actual Market Modal Price')}
                  </span>
                  <div className="text-3xl font-extrabold text-slate-900 tracking-tight">
                    {formatCurrency(mspData.modal_price)}
                  </div>
                  <span className="text-xs text-slate-500 mt-1 block">{t('market.perQuintal', 'per Quintal (100 kg)')}</span>
                </div>

                {/* MSP Price */}
                <div className="p-6 bg-purple-50/60 border border-purple-200/80 rounded-2xl">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold text-purple-700 uppercase tracking-wider block">
                      {t('msp.govtMspFloor', 'Government MSP Floor')}
                    </span>
                    <Badge variant="neutral">{t('msp.benchmarkBadge', 'Benchmark')}</Badge>
                  </div>
                  <div className="text-3xl font-extrabold text-purple-900 tracking-tight">
                    {mspData.msp !== null && mspData.msp !== undefined
                      ? formatCurrency(mspData.msp)
                      : 'N/A (Market Driven)'}
                  </div>
                  <span className="text-xs text-purple-600 mt-1 block">
                    {mspData.msp ? t('market.perQuintal', 'per Quintal') : 'No statutory price floor'}
                  </span>
                </div>

                {/* Price Difference */}
                <div
                  className={`p-6 rounded-2xl border ${
                    mspData.status === 'NOT_APPLICABLE'
                      ? 'bg-slate-50 border-slate-200 text-slate-800'
                      : mspData.difference >= 0
                      ? 'bg-emerald-50/60 border-emerald-200 text-emerald-900'
                      : 'bg-rose-50/60 border-rose-200 text-rose-900'
                  }`}
                >
                  <span className="text-xs font-bold uppercase tracking-wider mb-2 block opacity-80">
                    {t('msp.differenceVsMsp', 'Difference vs MSP')}
                  </span>
                  <div className="text-3xl font-extrabold tracking-tight flex items-center space-x-1">
                    {mspData.status === 'NOT_APPLICABLE' ? (
                      <Info className="w-7 h-7 text-slate-500" />
                    ) : mspData.difference >= 0 ? (
                      <ArrowUpRight className="w-7 h-7 text-emerald-600" />
                    ) : (
                      <ArrowDownRight className="w-7 h-7 text-rose-600" />
                    )}
                    <span>
                      {mspData.status === 'NOT_APPLICABLE'
                        ? 'Market Open'
                        : `${mspData.difference >= 0 ? '+' : ''}${formatCurrency(mspData.difference)}`}
                    </span>
                  </div>
                  <span className="text-xs font-semibold mt-1 block">
                    {mspData.status === 'NOT_APPLICABLE'
                      ? 'Demand & Supply Driven'
                      : `${mspData.difference >= 0 ? '+' : ''}${mspData.difference_percent}%`}
                  </span>
                </div>
              </div>

              {/* Advisory Box */}
              <div className="p-5 bg-slate-50 rounded-2xl border border-slate-200/70 text-xs leading-relaxed text-slate-700">
                <div className="flex items-center space-x-2 font-bold text-slate-900 mb-1">
                  {mspData.status === 'ABOVE_MSP' ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  ) : mspData.status === 'BELOW_MSP' ? (
                    <AlertTriangle className="w-4 h-4 text-amber-500" />
                  ) : (
                    <Info className="w-4 h-4 text-blue-500" />
                  )}
                  <span>{t('cropReco.plantingAdvisoryTitle', 'Farmer Advisory Insight')}</span>
                </div>
                {mspData.status === 'ABOVE_MSP' ? (
                  <p>
                    {t('msp.favorableNotice', 'Market conditions are favorable. Current modal price is above the government floor rate.')}
                  </p>
                ) : mspData.status === 'BELOW_MSP' ? (
                  <p>
                    {t('msp.distressNotice', 'Warning: Market rate is currently below MSP. Farmers are advised to sell via government procurement centers.')}
                  </p>
                ) : (
                  <p>
                    This commodity is traded on open market prices without statutory government MSP procurement. Farmers should time their harvest sales by tracking daily arrival volumes and local demand.
                  </p>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default MspComparisonPage;
