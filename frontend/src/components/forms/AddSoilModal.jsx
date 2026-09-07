import React, { useState } from 'react';
import Modal from '../common/Modal';
import { farmService } from '../../services/farmService';
import { Loader2, AlertCircle } from 'lucide-react';

const AddSoilModal = ({ isOpen, onClose, farmId, onSoilAdded }) => {
  const [formData, setFormData] = useState({
    ph: '',
    nitrogen: '',
    phosphorus: '',
    potassium: '',
    moisture: '',
    soil_type: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    const payload = {};
    if (formData.ph !== '') payload.ph = parseFloat(formData.ph);
    if (formData.nitrogen !== '') payload.nitrogen = parseFloat(formData.nitrogen);
    if (formData.phosphorus !== '') payload.phosphorus = parseFloat(formData.phosphorus);
    if (formData.potassium !== '') payload.potassium = parseFloat(formData.potassium);
    if (formData.moisture !== '') payload.moisture = parseFloat(formData.moisture);
    if (formData.soil_type.trim() !== '') payload.soil_type = formData.soil_type.trim();

    if (Object.keys(payload).length === 0) {
      setError('Please provide at least one soil nutrient measurement or soil type.');
      return;
    }

    if (payload.ph !== undefined && (payload.ph < 0 || payload.ph > 14)) {
      setError('pH must be between 0 and 14.');
      return;
    }

    setSubmitting(true);
    try {
      await farmService.addSoilReading(farmId, payload);
      if (onSoilAdded) onSoilAdded();
      onClose();
      setFormData({
        ph: '',
        nitrogen: '',
        phosphorus: '',
        potassium: '',
        moisture: '',
        soil_type: '',
      });
    } catch (err) {
      setError(err.friendlyMessage || 'Failed to record soil data');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Record Soil Data Reading">
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="p-3 bg-red-50 text-red-700 text-xs rounded-xl flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 shrink-0 text-red-500" />
            <span>{error}</span>
          </div>
        )}

        <p className="text-xs text-slate-500">
          Soil readings are utilized by the AI Crop Recommendation engine to determine the most suitable crops for your farm.
        </p>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1">
              Soil pH (0 - 14)
            </label>
            <input
              type="number"
              step="0.1"
              min="0"
              max="14"
              placeholder="e.g. 6.5"
              value={formData.ph}
              onChange={(e) => setFormData({ ...formData, ph: e.target.value })}
              className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-agri-500"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1">
              Moisture (%)
            </label>
            <input
              type="number"
              step="0.1"
              min="0"
              max="100"
              placeholder="e.g. 45"
              value={formData.moisture}
              onChange={(e) => setFormData({ ...formData, moisture: e.target.value })}
              className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-agri-500"
            />
          </div>
        </div>

        <div className="grid grid-cols-3 gap-3">
          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1">
              Nitrogen (N)
            </label>
            <input
              type="number"
              step="any"
              min="0"
              placeholder="e.g. 80"
              value={formData.nitrogen}
              onChange={(e) => setFormData({ ...formData, nitrogen: e.target.value })}
              className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-agri-500"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1">
              Phosphorus (P)
            </label>
            <input
              type="number"
              step="any"
              min="0"
              placeholder="e.g. 40"
              value={formData.phosphorus}
              onChange={(e) => setFormData({ ...formData, phosphorus: e.target.value })}
              className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-agri-500"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1">
              Potassium (K)
            </label>
            <input
              type="number"
              step="any"
              min="0"
              placeholder="e.g. 40"
              value={formData.potassium}
              onChange={(e) => setFormData({ ...formData, potassium: e.target.value })}
              className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-agri-500"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-700 mb-1">
            Soil Type
          </label>
          <select
            value={formData.soil_type}
            onChange={(e) => setFormData({ ...formData, soil_type: e.target.value })}
            className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-agri-500 bg-white"
          >
            <option value="">Select Soil Type (Optional)</option>
            <option value="Loamy">Loamy Soil</option>
            <option value="Clay">Clay Soil</option>
            <option value="Sandy">Sandy Soil</option>
            <option value="Black Cotton">Black Cotton Soil</option>
            <option value="Red Soil">Red Soil</option>
            <option value="Alluvial">Alluvial Soil</option>
          </select>
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
            <span>{submitting ? 'Recording...' : 'Save Soil Reading'}</span>
          </button>
        </div>
      </form>
    </Modal>
  );
};

export default AddSoilModal;
