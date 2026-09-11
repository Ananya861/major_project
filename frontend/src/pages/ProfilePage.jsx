import React from 'react';
import { useAuth } from '../context/AuthContext';
import { useTranslation } from '../i18n/LanguageContext';
import Badge from '../components/common/Badge';
import {
  User,
  Phone,
  MapPin,
  Calendar,
  Tractor,
  Languages,
  Shield,
  Layers,
} from 'lucide-react';
import { formatDate } from '../utils/formatters';

const ProfilePage = () => {
  const { t } = useTranslation();
  const { user } = useAuth();

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
          {t('profile.title', 'Farmer Profile & Account Settings')}
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          {t('profile.subtitle', 'View your registration details, primary farm coordinates, and regional language preferences.')}
        </p>
      </div>

      {/* Profile Card */}
      <div className="bg-white border border-slate-200/80 rounded-3xl p-6 md:p-8 shadow-xs space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-100">
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 rounded-2xl bg-agri-600 text-white flex items-center justify-center font-bold text-2xl shadow-md shadow-agri-600/30">
              {user?.name?.charAt(0)?.toUpperCase() || 'F'}
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-xl font-bold text-slate-900">{user?.name}</h2>
                <Badge variant="success">{t('auth.registerTitle', 'Verified Farmer')}</Badge>
              </div>
              <p className="text-xs text-slate-500 mt-1 flex items-center space-x-1.5">
                <Phone className="w-3.5 h-3.5 text-slate-400" />
                <span>{user?.phone}</span>
                <span>•</span>
                <Calendar className="w-3.5 h-3.5 text-slate-400" />
                <span>{t('farms.recordedAt', 'Member since')} {formatDate(user?.created_at)}</span>
              </p>
            </div>
          </div>
        </div>

        {/* Detailed Fields Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100 flex items-start space-x-3">
            <MapPin className="w-5 h-5 text-agri-600 shrink-0 mt-0.5" />
            <div>
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
                {t('profile.location', 'Registered Village & State')}
              </span>
              <p className="text-sm font-semibold text-slate-800 mt-0.5">
                {user?.village ? `${user.village}, ` : ''}
                {user?.district ? `${user.district}, ` : ''}
                {user?.state || 'Not Specified'}
              </p>
            </div>
          </div>

          <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100 flex items-start space-x-3">
            <Tractor className="w-5 h-5 text-agri-600 shrink-0 mt-0.5" />
            <div>
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
                {t('auth.landSizeLabel', 'Total Land Size (Acres)')}
              </span>
              <p className="text-sm font-semibold text-slate-800 mt-0.5">
                {user?.land_size_acres ? `${user.land_size_acres} ${t('common.acres', 'Acres')}` : 'Not Specified'}
              </p>
            </div>
          </div>

          <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100 flex items-start space-x-3">
            <Layers className="w-5 h-5 text-agri-600 shrink-0 mt-0.5" />
            <div>
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
                {t('profile.category', 'Category')}
              </span>
              <p className="text-sm font-semibold text-slate-800 mt-0.5">
                {user?.category || 'General Farmer'}
              </p>
            </div>
          </div>

          <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100 flex items-start space-x-3">
            <Languages className="w-5 h-5 text-agri-600 shrink-0 mt-0.5" />
            <div>
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
                {t('profile.languagePrefTitle', 'Regional Language Preference')}
              </span>
              <p className="text-sm font-semibold text-slate-800 mt-0.5">
                {user?.preferred_language || 'English'}
              </p>
            </div>
          </div>
        </div>

        {/* Security & System Info */}
        <div className="p-5 bg-slate-50 rounded-2xl border border-slate-200/70 flex items-center justify-between text-xs text-slate-500">
          <div className="flex items-center space-x-2">
            <Shield className="w-4 h-4 text-emerald-600" />
            <span>FastAPI JWT Authentication Active</span>
          </div>
          <span>ID: #{user?.farmer_id}</span>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
