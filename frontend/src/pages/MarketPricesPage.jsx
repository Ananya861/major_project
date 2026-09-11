import React, { useState, useEffect, useCallback } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { useTranslation } from '../i18n/LanguageContext';
import { catalogService } from '../services/catalogService';
import { marketService } from '../services/marketService';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';
import Badge from '../components/common/Badge';
import {
  Store,
  Calendar,
  IndianRupee,
  Scale,
  TrendingUp,
  ArrowRight,
  Database,
  Radio,
  Search,
} from 'lucide-react';
import { formatCurrency, formatDate } from '../utils/formatters';

const MarketPricesPage = () => {
  const { t } = useTranslation();
  const [searchParams] = useSearchParams();

  const [crops, setCrops] = useState([]);
  const [markets, setMarkets] = useState([]);
  const [loadingCatalog, setLoadingCatalog] = useState(true);

  const [selectedCropId, setSelectedCropId] = useState('');
  const [selectedMarketId, setSelectedMarketId] = useState('');

  const [priceRecords, setPriceRecords] = useState(null);
  const [loadingPrices, setLoadingPrices] = useState(false);
  const [error, setError] = useState(null);

  const initialFetchDone = React.useRef(false);
  const selectedCropIdRef = React.useRef(selectedCropId);
  const selectedMarketIdRef = React.useRef(selectedMarketId);

  useEffect(() => {
    selectedCropIdRef.current = selectedCropId;
  }, [selectedCropId]);

  useEffect(() => {
    selectedMarketIdRef.current = selectedMarketId;
  }, [selectedMarketId]);

  const handleFetchPrices = useCallback(async (cId, mId) => {
    const cropIdToUse =
      typeof cId === 'string' || typeof cId === 'number'
        ? String(cId)
        : selectedCropIdRef.current;
    const marketIdToUse =
      typeof mId === 'string' || typeof mId === 'number'
        ? String(mId)
        : selectedMarketIdRef.current;

    if (!cropIdToUse || !marketIdToUse) {
      setError('Please select both a commodity and a target market.');
      return;
    }

    setLoadingPrices(true);
    setError(null);
    setPriceRecords(null);

    try {
      const data = await marketService.getMarketPrices(cropIdToUse, marketIdToUse);
      // GET /market/prices returns an ARRAY of MarketPrice objects. Ensure response.data / array is handled cleanly
      const records = Array.isArray(data) ? data : (data ? [data] : []);
      if (records.length === 0) {
        setError('No market price data available');
        setPriceRecords(null);
      } else {
        setPriceRecords(records);
      }
    } catch (err) {
      setError(err.friendlyMessage || 'No market price data available');
      setPriceRecords(null);
    } finally {
      setLoadingPrices(false);
    }
  }, []);

  const cropParam = searchParams.get('crop_id') || '';
  const marketParam = searchParams.get('market_id') || '';

  // Load crops and markets catalogs
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

          const wheatCrop = cropsData.find((c) => c.name?.toLowerCase() === 'wheat');
          const defaultCrop = wheatCrop || cropsData[0];

          const initialCropId = cropParam || (defaultCrop ? String(defaultCrop.crop_id) : '');
          const initialMarketId = marketParam || (marketsData.length > 0 ? String(marketsData[0].market_id) : '');

          setSelectedCropId((prev) => cropParam || prev || initialCropId);
          setSelectedMarketId((prev) => marketParam || prev || initialMarketId);

          if (initialCropId && initialMarketId && !initialFetchDone.current) {
            initialFetchDone.current = true;
            handleFetchPrices(initialCropId, initialMarketId);
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
  }, [cropParam, marketParam, handleFetchPrices]);

  const selectedCrop = crops.find((c) => String(c.crop_id) === String(selectedCropId));
  const selectedMarket = markets.find((m) => String(m.market_id) === String(selectedMarketId));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <div className="inline-flex items-center space-x-2 text-xs font-semibold text-agri-700 bg-agri-50 px-3 py-1 rounded-full border border-agri-200 mb-2">
          <Store className="w-3.5 h-3.5 text-agri-600" />
          <span>{t('market.liveBadge', 'Official Agmarknet Live')}</span>
        </div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
          {t('market.title', 'Live Mandi Prices & Arrivals')}
        </h1>
        <p className="text-xs text-slate-500 mt-1 max-w-2xl">
          {t('market.subtitle', 'Track official Government Agmarknet prices across APMC mandis and compare rates.')}
        </p>
      </div>

      {loadingCatalog ? (
        <LoadingSpinner message={t('common.loading', 'Loading commodity catalog & markets...')} />
      ) : (
        <div className="space-y-6">
          {/* Filters Bar */}
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
                      {c.name} {c.season ? `(${c.season})` : ''}
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
                      {m.name} {m.district ? `(${m.district}, ${m.state})` : ''}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <button
                  onClick={() => handleFetchPrices(selectedCropId, selectedMarketId)}
                  disabled={loadingPrices}
                  className="w-full py-3 px-5 bg-agri-600 hover:bg-agri-700 text-white text-sm font-bold rounded-2xl shadow-sm shadow-agri-600/20 transition flex items-center justify-center space-x-2 disabled:opacity-50"
                >
                  {loadingPrices ? (
                    <LoadingSpinner size="sm" message="" />
                  ) : (
                    <Search className="w-4 h-4" />
                  )}
                  <span>{loadingPrices ? t('common.loading', 'Querying Mandi...') : t('market.searchBtn', 'Fetch Latest Price')}</span>
                </button>
              </div>
            </div>
          </div>

          <ErrorMessage message={error} onRetry={() => handleFetchPrices(selectedCropId, selectedMarketId)} />

          {/* Loading */}
          {loadingPrices && (
            <div className="py-12 bg-white rounded-3xl border border-slate-200/80">
              <LoadingSpinner
                size="lg"
                message={t('common.loading', 'Connecting to data.gov.in Agmarknet gateway & verifying cache...')}
              />
            </div>
          )}

          {/* Results Display */}
          {priceRecords && priceRecords.length > 0 && (
            <div className="space-y-6">
              {priceRecords.map((price) => {
                const itemMarket = markets.find((m) => String(m.market_id) === String(price.market_id)) || selectedMarket;
                const itemCrop = crops.find((c) => String(c.crop_id) === String(price.crop_id)) || selectedCrop;
                return (
                <div
                  key={price.price_id}
                  className="bg-white border border-slate-200/80 rounded-3xl p-6 md:p-8 shadow-xs space-y-6"
                >
                  {/* Status Banner */}
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 border-b border-slate-100 gap-4">
                    <div>
                      <div className="flex items-center space-x-3">
                        <h2 className="text-2xl font-extrabold text-slate-900 tracking-tight">
                          {itemCrop?.name || selectedCrop?.name || 'Commodity'} {t('market.title', 'Rates')}
                        </h2>
                        {price.cached ? (
                          <Badge variant="neutral" className="flex items-center space-x-1">
                            <Database className="w-3 h-3" />
                            <span>{t('market.cachedBadge', 'Archived Database Record')}</span>
                          </Badge>
                        ) : (
                          <Badge variant="success" className="flex items-center space-x-1">
                            <Radio className="w-3 h-3 animate-pulse text-emerald-600" />
                            <span>{t('market.liveBadge', 'Official Agmarknet Live')}</span>
                          </Badge>
                        )}
                      </div>

                      <p className="text-xs text-slate-500 mt-1 flex items-center space-x-1.5">
                        <Store className="w-3.5 h-3.5 text-slate-400" />
                        <span>
                          {itemMarket?.name || selectedMarket?.name} Mandi ({itemMarket?.district || selectedMarket?.district},{' '}
                          {itemMarket?.state || selectedMarket?.state})
                        </span>
                        <span>•</span>
                        <Calendar className="w-3.5 h-3.5 text-slate-400" />
                        <span>{t('market.arrivalDate', 'Arrival Date')}: {formatDate(price.date)}</span>
                      </p>
                    </div>

                    <div className="flex items-center space-x-2">
                      <Link
                        to={`/price-prediction?crop_id=${price.crop_id}&market_id=${price.market_id}`}
                        className="inline-flex items-center space-x-1.5 px-4 py-2 bg-blue-50 hover:bg-blue-100 text-blue-700 text-xs font-bold rounded-xl transition"
                      >
                        <TrendingUp className="w-4 h-4" />
                        <span>{t('nav.pricePrediction', 'Predict Price')}</span>
                      </Link>

                      <Link
                        to={`/msp-comparison?crop_id=${price.crop_id}&market_id=${price.market_id}`}
                        className="inline-flex items-center space-x-1.5 px-4 py-2 bg-purple-50 hover:bg-purple-100 text-purple-700 text-xs font-bold rounded-xl transition"
                      >
                        <Scale className="w-4 h-4" />
                        <span>{t('nav.mspComparison', 'Compare MSP')}</span>
                      </Link>
                    </div>
                  </div>

                  {/* Price Cards Grid */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {/* Modal Price */}
                    <div className="p-6 bg-gradient-to-br from-agri-50 to-emerald-50/60 border border-agri-200/80 rounded-2xl shadow-xs">
                      <div className="flex items-center justify-between text-xs font-bold text-agri-800 uppercase tracking-wider mb-2">
                        <span>{t('market.currentModalPrice', 'Actual Market Modal Price')}</span>
                        <Badge variant="primary">{t('msp.benchmarkBadge', 'Benchmark')}</Badge>
                      </div>
                      <div className="text-3xl font-extrabold text-agri-900 tracking-tight">
                        {formatCurrency(price.modal_price)}
                      </div>
                      <span className="text-xs text-agri-700 mt-1 block">{t('market.perQuintal', 'per Quintal (100 kg)')}</span>
                    </div>

                    {/* Minimum Price */}
                    <div className="p-6 bg-slate-50 border border-slate-200/80 rounded-2xl shadow-xs">
                      <span className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 block">
                        {t('market.minPrice', 'Minimum Price')}
                      </span>
                      <div className="text-3xl font-extrabold text-slate-800 tracking-tight">
                        {formatCurrency(price.min_price)}
                      </div>
                      <span className="text-xs text-slate-500 mt-1 block">{t('market.perQuintal', 'per Quintal')}</span>
                    </div>

                    {/* Maximum Price */}
                    <div className="p-6 bg-slate-50 border border-slate-200/80 rounded-2xl shadow-xs">
                      <span className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 block">
                        {t('market.maxPrice', 'Maximum Price')}
                      </span>
                      <div className="text-3xl font-extrabold text-slate-800 tracking-tight">
                        {formatCurrency(price.max_price)}
                      </div>
                      <span className="text-xs text-slate-500 mt-1 block">{t('market.perQuintal', 'per Quintal')}</span>
                    </div>
                  </div>
                </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default MarketPricesPage;
