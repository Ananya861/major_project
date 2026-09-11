import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTranslation } from '../i18n/LanguageContext';
import { User, Phone, Lock, Loader2, AlertCircle } from 'lucide-react';

const RegisterPage = () => {
  const { register } = useAuth();
  const { t, language, setLanguage, languages } = useTranslation();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    password: '',
    state: '',
    district: '',
    village: '',
    land_size_acres: '',
    category: 'Small Farmer',
    preferred_language: 'English',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleLanguageChange = (langName, langCode) => {
    setFormData((prev) => ({ ...prev, preferred_language: langName }));
    if (langCode) {
      setLanguage(langCode);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (formData.name.trim().length < 1) {
      setError(t('auth.errorRequired', 'Farmer name is required'));
      return;
    }
    if (formData.phone.trim().length < 8) {
      setError(t('auth.errorPhoneDigits', 'Phone number must be at least 8 digits'));
      return;
    }
    if (formData.password.length < 6) {
      setError(t('auth.errorPasswordLength', 'Password must be at least 6 characters long'));
      return;
    }

    const payload = {
      name: formData.name.trim(),
      phone: formData.phone.trim(),
      password: formData.password,
      state: formData.state.trim() || null,
      district: formData.district.trim() || null,
      village: formData.village.trim() || null,
      land_size_acres: formData.land_size_acres ? parseFloat(formData.land_size_acres) : null,
      category: formData.category || null,
      preferred_language: formData.preferred_language || null,
    };

    setLoading(true);
    try {
      await register(payload);
      navigate('/login', { state: { registered: true } });
    } catch (err) {
      setError(err.friendlyMessage || 'Registration failed. A farmer with this phone number may already exist.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="mb-6 text-center">
        <h2 className="text-2xl font-bold text-slate-800 tracking-tight">
          {t('auth.registerTitle', 'Farmer Registration')}
        </h2>
        <p className="text-xs text-slate-500 mt-1">
          {t('auth.registerSubtitle', 'Create an AgriSmart account for AI advisory & price prediction')}
        </p>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 text-red-700 text-xs rounded-xl border border-red-200 flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 shrink-0 text-red-500" />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-3.5">
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">
            {t('auth.nameLabel', 'Full Name')} <span className="text-red-500">*</span>
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
              <User className="w-4 h-4" />
            </div>
            <input
              type="text"
              placeholder={t('auth.namePlaceholder', 'e.g. Ramesh Patel')}
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
              className="w-full pl-9 pr-3 py-2 text-sm border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-agri-500"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              {t('auth.phoneLabel', 'Phone Number')} <span className="text-red-500">*</span>
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                <Phone className="w-4 h-4" />
              </div>
              <input
                type="tel"
                placeholder={t('auth.phonePlaceholder', 'e.g. 9876543210')}
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                required
                className="w-full pl-9 pr-3 py-2 text-sm border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-agri-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              {t('auth.passwordLabel', 'Password')} <span className="text-red-500">*</span>
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                <Lock className="w-4 h-4" />
              </div>
              <input
                type="password"
                placeholder={t('auth.passwordPlaceholder', 'Min 6 chars')}
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                required
                className="w-full pl-9 pr-3 py-2 text-sm border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-agri-500"
              />
            </div>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-2">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              {t('auth.stateLabel', 'State')}
            </label>
            <input
              type="text"
              placeholder={t('auth.statePlaceholder', 'e.g. Madhya Pradesh')}
              value={formData.state}
              onChange={(e) => setFormData({ ...formData, state: e.target.value })}
              className="w-full px-2.5 py-2 text-xs border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-agri-500"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              {t('auth.districtLabel', 'District')}
            </label>
            <input
              type="text"
              placeholder={t('auth.districtPlaceholder', 'e.g. Rajgarh')}
              value={formData.district}
              onChange={(e) => setFormData({ ...formData, district: e.target.value })}
              className="w-full px-2.5 py-2 text-xs border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-agri-500"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              {t('auth.villageLabel', 'Village')}
            </label>
            <input
              type="text"
              placeholder={t('auth.villagePlaceholder', 'e.g. Khilchipur')}
              value={formData.village}
              onChange={(e) => setFormData({ ...formData, village: e.target.value })}
              className="w-full px-2.5 py-2 text-xs border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-agri-500"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              {t('auth.landSizeLabel', 'Land (Acres)')}
            </label>
            <input
              type="number"
              step="0.1"
              placeholder={t('auth.landSizePlaceholder', 'e.g. 5')}
              value={formData.land_size_acres}
              onChange={(e) => setFormData({ ...formData, land_size_acres: e.target.value })}
              className="w-full px-2.5 py-2 text-xs border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-agri-500"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              {t('auth.categoryLabel', 'Farmer Category')}
            </label>
            <select
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              className="w-full px-2 py-2 text-xs border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-agri-500 bg-white"
            >
              <option value="Marginal (< 2.5 acres)">Marginal (&lt; 2.5 ac)</option>
              <option value="Small Farmer">Small Farmer</option>
              <option value="Medium Farmer">Medium Farmer</option>
              <option value="Large Farmer">Large Farmer</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              {t('auth.languageLabel', 'Preferred Language')}
            </label>
            <select
              value={formData.preferred_language}
              onChange={(e) => {
                const selectedName = e.target.value;
                const matchLang = languages.find((l) => l.name === selectedName);
                handleLanguageChange(selectedName, matchLang?.code);
              }}
              className="w-full px-2 py-2 text-xs border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-agri-500 bg-white"
            >
              {languages.map((l) => (
                <option key={l.code} value={l.name}>
                  {l.nativeName} ({l.name})
                </option>
              ))}
            </select>
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full mt-2 py-2.5 px-4 bg-agri-600 hover:bg-agri-700 text-white text-sm font-semibold rounded-xl shadow-sm transition disabled:opacity-50 flex items-center justify-center space-x-2"
        >
          {loading && <Loader2 className="w-4 h-4 animate-spin" />}
          <span>{loading ? t('auth.registering', 'Creating Account...') : t('auth.submitRegister', 'Complete Registration')}</span>
        </button>
      </form>

      <div className="mt-5 text-center text-xs text-slate-500">
        {t('auth.hasAccount', 'Already registered?')}{' '}
        <Link to="/login" className="font-semibold text-agri-600 hover:text-agri-700 transition">
          {t('auth.loginNow', 'Sign In')}
        </Link>
      </div>
    </div>
  );
};

export default RegisterPage;
