import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useFarm } from '../context/FarmContext';
import { useTranslation } from '../i18n/LanguageContext';
import { farmService } from '../services/farmService';
import AddFarmModal from '../components/forms/AddFarmModal';
import AddSoilModal from '../components/forms/AddSoilModal';
import Badge from '../components/common/Badge';
import EmptyState from '../components/common/EmptyState';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';
import {
  Tractor,
  Plus,
  FlaskConical,
  Sprout,
  MapPin,
  Calendar,
  CloudSun,
} from 'lucide-react';
import { formatDate } from '../utils/formatters';

const FarmsPage = () => {
  const { t } = useTranslation();
  const { farms, loadingFarms, errorFarms, refreshFarms } = useFarm();
  const [selectedFarmDetail, setSelectedFarmDetail] = useState(null);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [activeFarmId, setActiveFarmId] = useState(null);

  const [addFarmOpen, setAddFarmOpen] = useState(false);
  const [addSoilOpen, setAddSoilOpen] = useState(false);
  const [soilFarmId, setSoilFarmId] = useState(null);

  useEffect(() => {
    if (farms.length > 0 && !activeFarmId) {
      setActiveFarmId(farms[0].farm_id);
    }
  }, [farms, activeFarmId]);

  useEffect(() => {
    let isMounted = true;
    const loadDetail = async () => {
      if (!activeFarmId) return;
      setLoadingDetail(true);
      try {
        const detail = await farmService.getFarm(activeFarmId);
        if (isMounted) setSelectedFarmDetail(detail);
      } catch {
        // Silently fail
      } finally {
        if (isMounted) setLoadingDetail(false);
      }
    };
    loadDetail();
    return () => {
      isMounted = false;
    };
  }, [activeFarmId]);

  const handleOpenAddSoil = (farmId) => {
    setSoilFarmId(farmId);
    setAddSoilOpen(true);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
            {t('farms.title', 'My Farms & Soil Health')}
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            {t('farms.subtitle', 'Manage farm parcels, GPS coordinates, and historical soil fertility tests')}
          </p>
        </div>
        <button
          onClick={() => setAddFarmOpen(true)}
          className="inline-flex items-center space-x-2 px-5 py-2.5 bg-agri-600 hover:bg-agri-700 text-white text-xs font-bold rounded-xl shadow-xs transition"
        >
          <Plus className="w-4 h-4" />
          <span>{t('farms.registerFarmBtn', 'Register New Farm')}</span>
        </button>
      </div>

      <ErrorMessage message={errorFarms} onRetry={refreshFarms} />

      {loadingFarms ? (
        <LoadingSpinner message={t('common.loading', 'Loading your registered farms...')} />
      ) : farms.length === 0 ? (
        <EmptyState
          icon={Tractor}
          title={t('farms.emptyFarmsTitle', 'No farms registered yet')}
          description={t('farms.emptyFarmsDesc', 'Add your first farm plot with latitude, longitude, and acreage to start generating crop recommendations.')}
          actionText={t('farms.registerFarmBtn', 'Register New Farm')}
          onAction={() => setAddFarmOpen(true)}
        />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Farm List Cards */}
          <div className="lg:col-span-1 space-y-3">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider px-1">
              {t('farms.farmListTitle', 'Farm Parcels')} ({farms.length})
            </h3>
            <div className="space-y-2">
              {farms.map((farm) => {
                const isSelected = farm.farm_id === activeFarmId;
                return (
                  <div
                    key={farm.farm_id}
                    onClick={() => setActiveFarmId(farm.farm_id)}
                    className={`p-4 rounded-2xl border cursor-pointer transition-all ${
                      isSelected
                        ? 'bg-agri-50/60 border-agri-300 shadow-xs ring-1 ring-agri-500/20'
                        : 'bg-white border-slate-200/80 hover:border-slate-300'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <div
                          className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                            isSelected ? 'bg-agri-600 text-white' : 'bg-slate-100 text-slate-600'
                          }`}
                        >
                          <Tractor className="w-4 h-4" />
                        </div>
                        <span className="font-bold text-sm text-slate-800">
                          {t('nav.myFarms', 'Farm')} #{farm.farm_id}
                        </span>
                      </div>
                      <Badge variant={isSelected ? 'primary' : 'neutral'}>
                        {farm.area_acres} {t('common.acres', 'Acres')}
                      </Badge>
                    </div>

                    <div className="mt-3 flex items-center space-x-1 text-xs text-slate-500">
                      <MapPin className="w-3.5 h-3.5 shrink-0 text-slate-400" />
                      <span className="truncate">
                        {farm.latitude.toFixed(4)}° N, {farm.longitude.toFixed(4)}° E
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Active Farm Detail & Soil Card */}
          <div className="lg:col-span-2">
            {loadingDetail ? (
              <div className="bg-white border border-slate-200 rounded-3xl p-8 flex items-center justify-center">
                <LoadingSpinner message={t('common.loading', 'Fetching farm profile & soil readings...')} />
              </div>
            ) : selectedFarmDetail ? (
              <div className="bg-white border border-slate-200/80 rounded-3xl p-6 md:p-8 shadow-xs space-y-6">
                {/* Header */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 border-b border-slate-100 gap-4">
                  <div>
                    <div className="flex items-center space-x-3">
                      <h2 className="text-xl font-bold text-slate-900">
                        {t('nav.myFarms', 'Farm Plot')} #{selectedFarmDetail.farm_id}
                      </h2>
                      <Badge variant="success">{selectedFarmDetail.area_acres} {t('common.acres', 'Acres')}</Badge>
                    </div>
                    <p className="text-xs text-slate-500 mt-1 flex items-center space-x-1.5">
                      <Calendar className="w-3.5 h-3.5 text-slate-400" />
                      <span>{t('farms.recordedAt', 'Registered on')} {formatDate(selectedFarmDetail.created_at)}</span>
                    </p>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Link
                      to={`/weather?lat=${selectedFarmDetail.latitude}&lng=${selectedFarmDetail.longitude}`}
                      className="inline-flex items-center space-x-1.5 px-3.5 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-xl transition"
                    >
                      <CloudSun className="w-4 h-4 text-slate-500" />
                      <span>{t('nav.weather', 'Weather')}</span>
                    </Link>

                    <Link
                      to={`/crop-recommendation?farm_id=${selectedFarmDetail.farm_id}`}
                      className="inline-flex items-center space-x-1.5 px-3.5 py-2 bg-agri-600 hover:bg-agri-700 text-white text-xs font-semibold rounded-xl shadow-xs transition"
                    >
                      <Sprout className="w-4 h-4" />
                      <span>{t('nav.cropRecommendation', 'Crop AI')}</span>
                    </Link>
                  </div>
                </div>

                {/* Coordinates Info */}
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                  <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
                    <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                      {t('addFarm.latLabel', 'Latitude')}
                    </span>
                    <p className="text-base font-bold text-slate-800 mt-0.5">
                      {selectedFarmDetail.latitude.toFixed(6)}°
                    </p>
                  </div>

                  <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
                    <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                      {t('addFarm.lonLabel', 'Longitude')}
                    </span>
                    <p className="text-base font-bold text-slate-800 mt-0.5">
                      {selectedFarmDetail.longitude.toFixed(6)}°
                    </p>
                  </div>

                  <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100 col-span-2 sm:col-span-1">
                    <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                      {t('addFarm.areaLabel', 'Area')}
                    </span>
                    <p className="text-base font-bold text-slate-800 mt-0.5">
                      {selectedFarmDetail.area_acres} {t('common.acres', 'Acres')}
                    </p>
                  </div>
                </div>

                {/* Soil Profile Section */}
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-2">
                      <FlaskConical className="w-4 h-4 text-agri-600" />
                      <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wider">
                        {t('farms.soilReadingsTitle', 'Latest Soil Reading')}
                      </h3>
                    </div>
                    <button
                      onClick={() => handleOpenAddSoil(selectedFarmDetail.farm_id)}
                      className="inline-flex items-center space-x-1 text-xs font-semibold text-agri-600 hover:text-agri-700"
                    >
                      <Plus className="w-3.5 h-3.5" />
                      <span>{t('farms.addSoilBtn', 'Log Soil Test')}</span>
                    </button>
                  </div>

                  {selectedFarmDetail.latest_soil ? (
                    <div className="bg-slate-50/70 border border-slate-200/80 rounded-2xl p-5 space-y-4">
                      <div className="flex items-center justify-between text-xs text-slate-500 pb-2 border-b border-slate-200/60">
                        <span>
                          {t('farms.recordedAt', 'Recorded on')} {formatDate(selectedFarmDetail.latest_soil.recorded_at)}
                        </span>
                        {selectedFarmDetail.latest_soil.soil_type && (
                          <Badge variant="primary">
                            {selectedFarmDetail.latest_soil.soil_type} {t('farms.soilType', 'Soil')}
                          </Badge>
                        )}
                      </div>

                      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 text-center">
                        <div className="bg-white p-3 rounded-xl border border-slate-200/60 shadow-xs">
                          <span className="text-[10px] font-bold text-slate-400 uppercase">{t('farms.ph', 'pH')}</span>
                          <p className="text-lg font-extrabold text-slate-800">
                            {selectedFarmDetail.latest_soil.ph ?? '--'}
                          </p>
                          <span className="text-[10px] text-slate-400">0 - 14</span>
                        </div>

                        <div className="bg-white p-3 rounded-xl border border-slate-200/60 shadow-xs">
                          <span className="text-[10px] font-bold text-slate-400 uppercase">
                            {t('farms.nitrogen', 'Nitrogen (N)')}
                          </span>
                          <p className="text-lg font-extrabold text-slate-800">
                            {selectedFarmDetail.latest_soil.nitrogen ?? '--'}
                          </p>
                          <span className="text-[10px] text-slate-400">{t('common.kgHa', 'kg/ha')}</span>
                        </div>

                        <div className="bg-white p-3 rounded-xl border border-slate-200/60 shadow-xs">
                          <span className="text-[10px] font-bold text-slate-400 uppercase">
                            {t('farms.phosphorus', 'Phosphorus (P)')}
                          </span>
                          <p className="text-lg font-extrabold text-slate-800">
                            {selectedFarmDetail.latest_soil.phosphorus ?? '--'}
                          </p>
                          <span className="text-[10px] text-slate-400">{t('common.kgHa', 'kg/ha')}</span>
                        </div>

                        <div className="bg-white p-3 rounded-xl border border-slate-200/60 shadow-xs">
                          <span className="text-[10px] font-bold text-slate-400 uppercase">
                            {t('farms.potassium', 'Potassium (K)')}
                          </span>
                          <p className="text-lg font-extrabold text-slate-800">
                            {selectedFarmDetail.latest_soil.potassium ?? '--'}
                          </p>
                          <span className="text-[10px] text-slate-400">{t('common.kgHa', 'kg/ha')}</span>
                        </div>

                        <div className="bg-white p-3 rounded-xl border border-slate-200/60 shadow-xs col-span-2 sm:col-span-1">
                          <span className="text-[10px] font-bold text-slate-400 uppercase">
                            {t('farms.moisture', 'Moisture')}
                          </span>
                          <p className="text-lg font-extrabold text-slate-800">
                            {selectedFarmDetail.latest_soil.moisture !== null
                              ? `${selectedFarmDetail.latest_soil.moisture}%`
                              : '--'}
                          </p>
                          <span className="text-[10px] text-slate-400">%</span>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="p-6 bg-slate-50 rounded-2xl border border-dashed border-slate-200 text-center">
                      <FlaskConical className="w-7 h-7 text-slate-400 mx-auto mb-1.5" />
                      <p className="text-xs font-semibold text-slate-700">{t('farms.noSoilData', 'No soil reading logged yet')}</p>
                      <p className="text-[11px] text-slate-500 mt-0.5">
                        {t('addSoil.guidanceText', 'Recording nitrogen, phosphorus, potassium, and pH readings enables the AI Crop Recommendation model.')}
                      </p>
                      <button
                        onClick={() => handleOpenAddSoil(selectedFarmDetail.farm_id)}
                        className="mt-3 px-4 py-1.5 bg-agri-600 hover:bg-agri-700 text-white text-xs font-semibold rounded-xl shadow-xs transition"
                      >
                        {t('farms.addSoilBtn', 'Add Soil Reading')}
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ) : null}
          </div>
        </div>
      )}

      {/* Modals */}
      <AddFarmModal isOpen={addFarmOpen} onClose={() => setAddFarmOpen(false)} />
      {soilFarmId && (
        <AddSoilModal
          isOpen={addSoilOpen}
          onClose={() => setAddSoilOpen(false)}
          farmId={soilFarmId}
          onSoilAdded={() => {
            refreshFarms();
            if (activeFarmId === soilFarmId) {
              farmService.getFarm(soilFarmId).then(setSelectedFarmDetail);
            }
          }}
        />
      )}
    </div>
  );
};

export default FarmsPage;
