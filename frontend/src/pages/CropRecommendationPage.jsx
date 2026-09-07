import React, { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { useFarm } from '../context/FarmContext';
import { farmService } from '../services/farmService';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';
import Badge from '../components/common/Badge';
import AddSoilModal from '../components/forms/AddSoilModal';
import {
  Sprout,
  Tractor,
  Sparkles,
  FlaskConical,
  Award,
  Calendar,
  AlertTriangle,
  ArrowRight,
  TrendingUp,
} from 'lucide-react';
import { formatDateTime } from '../utils/formatters';

const CropRecommendationPage = () => {
  const { farms, loadingFarms } = useFarm();
  const [searchParams] = useSearchParams();

  const [selectedFarmId, setSelectedFarmId] = useState('');
  const [farmDetail, setFarmDetail] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [generatedAt, setGeneratedAt] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [addSoilOpen, setAddSoilOpen] = useState(false);

  // Initialize selected farm from URL query or first farm
  useEffect(() => {
    const paramId = searchParams.get('farm_id');
    if (paramId) {
      setSelectedFarmId(paramId);
    } else if (farms.length > 0 && !selectedFarmId) {
      setSelectedFarmId(String(farms[0].farm_id));
    }
  }, [farms, searchParams, selectedFarmId]);

  // Load farm details when selectedFarmId changes to check soil status
  useEffect(() => {
    let isMounted = true;
    if (selectedFarmId) {
      farmService
        .getFarm(selectedFarmId)
        .then((detail) => {
          if (isMounted) setFarmDetail(detail);
        })
        .catch(() => {});
    }
    return () => {
      isMounted = false;
    };
  }, [selectedFarmId]);

  const handleRunRecommendation = async () => {
    if (!selectedFarmId) {
      setError('Please select a farm plot first.');
      return;
    }

    setLoading(true);
    setError(null);
    setRecommendations(null);

    try {
      const data = await farmService.getCropRecommendation(selectedFarmId);
      setRecommendations(data.recommendations || []);
      setGeneratedAt(data.generated_at || new Date().toISOString());
    } catch (err) {
      setError(
        err.friendlyMessage ||
          'Failed to generate recommendation. Please ensure the farm has logged soil test data.'
      );
    } finally {
      setLoading(false);
    }
  };

  const hasSoil = !!farmDetail?.latest_soil;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <div className="inline-flex items-center space-x-2 text-xs font-semibold text-agri-700 bg-agri-50 px-3 py-1 rounded-full border border-agri-200 mb-2">
          <Sparkles className="w-3.5 h-3.5 text-agri-600" />
          <span>AI-Powered Crop Recommendation</span>
        </div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
          AI Crop Recommendation
        </h1>
        <p className="text-xs text-slate-500 mt-1 max-w-2xl">
          Uses soil nutrient chemistry (Nitrogen, Phosphorus, Potassium, pH, Moisture) alongside
          real-time temperature and precipitation from OpenWeather to predict optimal crop yields.
        </p>
      </div>

      {loadingFarms ? (
        <LoadingSpinner message="Loading registered farms..." />
      ) : farms.length === 0 ? (
        <div className="bg-white border border-slate-200/80 rounded-3xl p-8 text-center max-w-md mx-auto">
          <Tractor className="w-10 h-10 text-slate-400 mx-auto mb-3" />
          <h3 className="text-base font-bold text-slate-800">No Farm Registered</h3>
          <p className="text-xs text-slate-500 mt-1 mb-4">
            You must register a farm plot before requesting AI crop advice.
          </p>
          <Link
            to="/farms"
            className="inline-flex items-center space-x-2 px-5 py-2.5 bg-agri-600 hover:bg-agri-700 text-white text-xs font-bold rounded-xl shadow-xs transition"
          >
            <span>Go to My Farms</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Farm Selector Card */}
          <div className="bg-white border border-slate-200/80 rounded-3xl p-6 shadow-xs">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
              <div className="md:col-span-2">
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                  Select Farm for AI Recommendation
                </label>
                <div className="relative">
                  <select
                    value={selectedFarmId}
                    onChange={(e) => {
                      setSelectedFarmId(e.target.value);
                      setRecommendations(null);
                    }}
                    className="w-full px-4 py-3 text-sm font-semibold text-slate-800 border border-slate-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-agri-500 bg-slate-50/50"
                  >
                    {farms.map((f) => (
                      <option key={f.farm_id} value={f.farm_id}>
                        Farm #{f.farm_id} — {f.area_acres} Acres ({f.latitude.toFixed(4)}°N,{' '}
                        {f.longitude.toFixed(4)}°E)
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <button
                  onClick={handleRunRecommendation}
                  disabled={loading}
                  className="w-full py-3 px-5 bg-agri-600 hover:bg-agri-700 text-white text-sm font-bold rounded-2xl shadow-sm shadow-agri-600/20 transition flex items-center justify-center space-x-2 disabled:opacity-50"
                >
                  {loading ? (
                    <LoadingSpinner size="sm" message="" />
                  ) : (
                    <Sparkles className="w-4 h-4" />
                  )}
                  <span>{loading ? 'Evaluating Model...' : 'Run Recommendation'}</span>
                </button>
              </div>
            </div>

            {/* Soil Status Notice */}
            {farmDetail && (
              <div className="mt-4 pt-4 border-t border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
                <div className="flex items-center space-x-2 text-slate-600">
                  <FlaskConical className="w-4 h-4 text-agri-600" />
                  {hasSoil ? (
                    <span>
                      Soil data available (pH: {farmDetail.latest_soil.ph ?? '--'}, N:{' '}
                      {farmDetail.latest_soil.nitrogen ?? '--'}, P:{' '}
                      {farmDetail.latest_soil.phosphorus ?? '--'}, K:{' '}
                      {farmDetail.latest_soil.potassium ?? '--'})
                    </span>
                  ) : (
                    <span className="text-amber-700 font-medium flex items-center space-x-1">
                      <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />
                      <span>No soil test reading recorded yet for this farm.</span>
                    </span>
                  )}
                </div>

                <button
                  type="button"
                  onClick={() => setAddSoilOpen(true)}
                  className="text-xs font-bold text-agri-600 hover:text-agri-700 self-start sm:self-auto"
                >
                  {hasSoil ? 'Update Soil Test' : '+ Log Soil Test Reading'}
                </button>
              </div>
            )}
          </div>

          <ErrorMessage message={error} onRetry={handleRunRecommendation} />

          {/* Results Display */}
          {loading && (
            <div className="py-12 bg-white rounded-3xl border border-slate-200/80">
              <LoadingSpinner
                size="lg"
                message="Processing soil nutrients &amp; live weather through crop recommendation model..."
              />
            </div>
          )}

          {recommendations && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-base font-extrabold text-slate-900">
                    Recommended Crops for Farm #{selectedFarmId}
                  </h3>
                  <p className="text-xs text-slate-500 flex items-center space-x-1 mt-0.5">
                    <Calendar className="w-3.5 h-3.5 text-slate-400" />
                    <span>Inference generated on {formatDateTime(generatedAt)}</span>
                  </p>
                </div>
                <Badge variant="success">Confidence Ranked</Badge>
              </div>

              {recommendations.length === 0 ? (
                <div className="p-8 bg-white rounded-3xl border border-slate-200 text-center text-xs text-slate-500">
                  No crop recommendation returned. Verify soil reading values.
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {recommendations.map((item, index) => {
                    const rank = index + 1;
                    const confidencePct = (item.confidence * 100).toFixed(1);

                    return (
                      <div
                        key={`${item.crop}-${index}`}
                        className={`p-6 bg-white border rounded-3xl shadow-xs transition flex flex-col justify-between ${
                          rank === 1
                            ? 'border-agri-300 ring-2 ring-agri-500/20 shadow-md'
                            : 'border-slate-200/80 hover:border-slate-300'
                        }`}
                      >
                        <div>
                          <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center space-x-2">
                              <span
                                className={`w-7 h-7 rounded-xl text-xs font-extrabold flex items-center justify-center ${
                                  rank === 1
                                    ? 'bg-agri-600 text-white'
                                    : 'bg-slate-100 text-slate-600'
                                }`}
                              >
                                #{rank}
                              </span>
                              {rank === 1 && (
                                <Badge variant="primary" className="text-[10px]">
                                  Top Recommendation
                                </Badge>
                              )}
                            </div>
                            <div className="text-right">
                              <span className="text-sm font-extrabold text-slate-800">
                                {confidencePct}%
                              </span>
                              <span className="block text-[10px] text-slate-400 font-semibold uppercase">
                                Match Score
                              </span>
                            </div>
                          </div>

                          <div className="flex items-center space-x-3 mb-3">
                            <div className="w-10 h-10 rounded-xl bg-agri-50 text-agri-600 flex items-center justify-center">
                              <Sprout className="w-5 h-5" />
                            </div>
                            <div>
                              <h4 className="text-lg font-bold text-slate-900">{item.crop}</h4>
                              <p className="text-xs text-slate-500">
                                Crop ID: {item.crop_id ?? 'General'}
                              </p>
                            </div>
                          </div>

                          {/* Progress bar */}
                          <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden mb-4">
                            <div
                              className={`h-full rounded-full ${
                                rank === 1 ? 'bg-agri-600' : 'bg-agri-400'
                              }`}
                              style={{ width: `${Math.min(100, Math.max(5, item.confidence * 100))}%` }}
                            />
                          </div>
                        </div>

                        <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs font-semibold">
                          <Link
                            to={`/market-prices`}
                            className="text-slate-500 hover:text-agri-600 transition inline-flex items-center space-x-1"
                          >
                            <span>Check Prices</span>
                            <ArrowRight className="w-3 h-3" />
                          </Link>

                          <Link
                            to={`/price-prediction`}
                            className="text-agri-600 hover:text-agri-700 transition inline-flex items-center space-x-1"
                          >
                            <TrendingUp className="w-3.5 h-3.5" />
                            <span>Forecast Yield Price</span>
                          </Link>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {selectedFarmId && (
        <AddSoilModal
          isOpen={addSoilOpen}
          onClose={() => setAddSoilOpen(false)}
          farmId={Number(selectedFarmId)}
          onSoilAdded={() => {
            farmService.getFarm(selectedFarmId).then(setFarmDetail);
          }}
        />
      )}
    </div>
  );
};

export default CropRecommendationPage;
