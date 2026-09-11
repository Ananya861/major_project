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
} from 'lucide-react';
import { formatCurrency, formatDate } from '../utils/formatters';

const MspComparisonPage = () => {
  const { t } = useTranslation();
  const [searchParams] = useSearchParams();

  const [crops, setCrops] = useState([]);
  const [markets, setMarkets] = useState([]);
  const [loadingCatalog, setLoadingCatalog] = useState(true);

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
      // Handles both single object and array response (response.data[0])
      const mspRecord = Array.isArray(data) ? data[0] : data;
      if (!mspRecord || mspRecord.modal_price === undefined) {
        setError('No market price data available');
        setMspData(null);
      } else {
        setMspData(mspRecord);
      }
    } catch (err) {
      setError(
        err.friendlyMessage ||
          'MSP comparison data is currently unavailable for this crop. Note: MSP benchmarks are configured for Wheat, Maize, Groundnut, and Soyabean.'
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
        const [cropsData, marketsData] = await Promise.all([
          catalogService.getCrops(),
          catalogService.getMarkets(),
        ]);
        if (isMounted) {
          setCrops(cropsData);
          setMarkets(marketsData);

          // Find preferred initial crop (Wheat if available since it has MSP support, or first crop)
          const wheatCrop = cropsData.find((c) => c.name?.toLowerCase() === 'wheat');
          const defaultCrop = wheatCrop || cropsData[0];

          const initialCropId = cropParam || (defaultCrop ? String(defaultCrop.crop_id) : '');
          const initialMarketId = marketParam || (marketsData.length > 0 ? String(marketsData[0].market_id) : '');

          setSelectedCropId((prev) => cropParam || prev || initialCropId);
          setSelectedMarketId((prev) => marketParam || prev || initialMarketId);

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
        <div className="inline-flex items-center space-x-2 text-xs font-semibold text-purple-700 bg-purple-50 px-3 py-1 rounded-full border border-purple-200 mb-2">
          <Scale className="w-3.5 h-3.5 text-purple-600" />
          <span>{t('msp.benchmarkBadge', 'Government Price Floor Benchmark')}</span>
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
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 items-end">
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                  {t('market.commodityLabel', 'Commodity')}
                </label>
                <select
                  value={selectedCropId}
                  onChange={(e) => setSelectedCropId(e.target.value)}
                  className="w-full px-4 py-3 text-sm font-semibold text-slate-800 border border-slate-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-agri-500 bg-slate-50/50"
                >
                  {crops.map((c) => (
                    <option key={c.crop_id} value={String(c.crop_id)}>
                      {c.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                  {t('market.marketLabel', 'Mandi Market')}
                </label>
                <select
                  value={selectedMarketId}
                  onChange={(e) => setSelectedMarketId(e.target.value)}
                  className="w-full px-4 py-3 text-sm font-semibold text-slate-800 border border-slate-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-agri-500 bg-slate-50/50"
                >
                  {markets.map((m) => (
                    <option key={m.market_id} value={String(m.market_id)}>
                      {m.name} {m.district ? `(${m.district})` : ''}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <button
                  onClick={() => handleCompare(selectedCropId, selectedMarketId)}
                  disabled={loadingMsp}
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
                message="Retrieving latest market price &amp; matching with official MSP benchmarks..."
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
                      {mspData.market} Mandi, {mspData.district} ({mspData.state})
                    </span>
                    <span>•</span>
                    <Calendar className="w-3.5 h-3.5 text-slate-400" />
                    <span>{t('market.arrivalDate', 'Price Date')}: {formatDate(mspData.market_price_date)}</span>
                  </p>
                </div>

                <div className="text-xs text-slate-500 bg-slate-50 px-3.5 py-2 rounded-xl border border-slate-100">
                  <span className="font-semibold text-slate-700">{mspData.season}</span> •{' '}
                  <span>{mspData.marketing_year}</span>
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
                    {formatCurrency(mspData.msp)}
                  </div>
                  <span className="text-xs text-purple-600 mt-1 block">{t('market.perQuintal', 'per Quintal')}</span>
                </div>

                {/* Price Difference */}
                <div
                  className={`p-6 rounded-2xl border ${
                    mspData.difference >= 0
                      ? 'bg-emerald-50/60 border-emerald-200 text-emerald-900'
                      : 'bg-rose-50/60 border-rose-200 text-rose-900'
                  }`}
                >
                  <span className="text-xs font-bold uppercase tracking-wider mb-2 block opacity-80">
                    {t('msp.differenceVsMsp', 'Difference vs MSP')}
                  </span>
                  <div className="text-3xl font-extrabold tracking-tight flex items-center space-x-1">
                    {mspData.difference >= 0 ? (
                      <ArrowUpRight className="w-7 h-7 text-emerald-600" />
                    ) : (
                      <ArrowDownRight className="w-7 h-7 text-rose-600" />
                    )}
                    <span>
                      {mspData.difference >= 0 ? '+' : ''}
                      {formatCurrency(mspData.difference)}
                    </span>
                  </div>
                  <span className="text-xs font-semibold mt-1 block">
                    {mspData.difference >= 0 ? '+' : ''}
                    {mspData.difference_percent}%
                  </span>
                </div>
              </div>

              {/* Advisory Box */}
              <div className="p-5 bg-slate-50 rounded-2xl border border-slate-200/70 text-xs leading-relaxed text-slate-700">
                <div className="flex items-center space-x-2 font-bold text-slate-900 mb-1">
                  {mspData.status === 'ABOVE_MSP' ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  ) : (
                    <AlertTriangle className="w-4 h-4 text-amber-500" />
                  )}
                  <span>{t('cropReco.plantingAdvisoryTitle', 'Farmer Advisory Insight')}</span>
                </div>
                {mspData.status === 'ABOVE_MSP' ? (
                  <p>
                    {t('msp.favorableNotice', 'Market conditions are favorable. Current modal price is above the government floor rate.')}
                  </p>
                ) : (
                  <p>
                    {t('msp.distressNotice', 'Warning: Market rate is currently below MSP. Farmers are advised to sell via government procurement centers.')}
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
