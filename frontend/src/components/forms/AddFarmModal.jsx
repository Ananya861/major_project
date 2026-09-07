import React, { useState } from 'react';
import Modal from '../common/Modal';
import { farmService } from '../../services/farmService';
import { useFarm } from '../../context/FarmContext';
import { MapPin, Loader2, AlertCircle } from 'lucide-react';

const AddFarmModal = ({ isOpen, onClose }) => {
  const { refreshFarms } = useFarm();
  const [formData, setFormData] = useState({
    latitude: '',
    longitude: '',
    area_acres: '',
  });
  const [locating, setLocating] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const handleGetCurrentLocation = () => {
    if (!navigator.geolocation) {
      setError('Geolocation is not supported by your browser');
      return;
    }
    setLocating(true);
    setError(null);
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setFormData((prev) => ({
          ...prev,
          latitude: position.coords.latitude.toFixed(6),
          longitude: position.coords.longitude.toFixed(6),
        }));
        setLocating(false);
      },
      (err) => {
        setError(`Unable to retrieve location: ${err.message}`);
        setLocating(false);
      },
      { timeout: 10000 }
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    const lat = parseFloat(formData.latitude);
    const lng = parseFloat(formData.longitude);
    const acres = parseFloat(formData.area_acres);

    if (isNaN(lat) || lat < -90 || lat > 90) {
      setError('Latitude must be a valid number between -90 and 90');
      return;
    }
    if (isNaN(lng) || lng < -180 || lng > 180) {
      setError('Longitude must be a valid number between -180 and 180');
      return;
    }
    if (isNaN(acres) || acres <= 0) {
      setError('Farm land area must be greater than 0 acres');
      return;
    }

    setSubmitting(true);
    try {
      await farmService.createFarm({
        latitude: lat,
        longitude: lng,
        area_acres: acres,
      });
      await refreshFarms();
      onClose();
      setFormData({ latitude: '', longitude: '', area_acres: '' });
    } catch (err) {
      setError(err.friendlyMessage || 'Failed to create farm');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Register New Farm">
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="p-3 bg-red-50 text-red-700 text-xs rounded-xl flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 shrink-0 text-red-500" />
            <span>{error}</span>
          </div>
        )}

        <div className="flex justify-between items-center pb-1">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
            Location Coordinates
          </span>
          <button
            type="button"
            onClick={handleGetCurrentLocation}
            disabled={locating}
            className="inline-flex items-center space-x-1.5 text-xs text-agri-600 hover:text-agri-700 font-medium disabled:opacity-50"
          >
            {locating ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <MapPin className="w-3.5 h-3.5" />
            )}
            <span>{locating ? 'Detecting...' : 'Use Current GPS'}</span>
          </button>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1">
              Latitude <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              step="any"
              placeholder="e.g. 23.83"
              value={formData.latitude}
              onChange={(e) => setFormData({ ...formData, latitude: e.target.value })}
              required
              className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-agri-500 focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1">
              Longitude <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              step="any"
              placeholder="e.g. 76.91"
              value={formData.longitude}
              onChange={(e) => setFormData({ ...formData, longitude: e.target.value })}
              required
              className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-agri-500 focus:border-transparent"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-700 mb-1">
            Total Farm Area (Acres) <span className="text-red-500">*</span>
          </label>
          <input
            type="number"
            step="0.1"
            min="0.1"
            placeholder="e.g. 4.5"
            value={formData.area_acres}
            onChange={(e) => setFormData({ ...formData, area_acres: e.target.value })}
            required
            className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-agri-500 focus:border-transparent"
          />
        </div>

        <div className="pt-3 flex items-center justify-end space-x-3 border-t border-slate-100">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-xl transition"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={submitting}
            className="inline-flex items-center space-x-2 px-5 py-2 text-sm font-semibold bg-agri-600 hover:bg-agri-700 text-white rounded-xl shadow-sm transition disabled:opacity-50"
          >
            {submitting && <Loader2 className="w-4 h-4 animate-spin" />}
            <span>{submitting ? 'Saving Farm...' : 'Add Farm'}</span>
          </button>
        </div>
      </form>
    </Modal>
  );
};

export default AddFarmModal;
