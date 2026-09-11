import React from 'react';
import { Outlet, Link } from 'react-router-dom';
import { Sprout } from 'lucide-react';
import { useTranslation } from '../i18n/LanguageContext';
import LanguageSelector from '../components/common/LanguageSelector';

const AuthLayout = () => {
  const { t } = useTranslation();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-agri-50/30 to-emerald-50/40 flex flex-col justify-center py-12 sm:px-6 lg:px-8 relative">
      {/* Top right language switcher */}
      <div className="absolute top-6 right-6 z-20">
        <LanguageSelector variant="auth" />
      </div>

      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <Link to="/" className="inline-flex items-center space-x-3 group">
          <div className="w-12 h-12 rounded-2xl bg-agri-600 flex items-center justify-center text-white shadow-md shadow-agri-600/30 group-hover:scale-105 transition-transform">
            <Sprout className="w-7 h-7" />
          </div>
          <span className="font-extrabold text-2xl text-slate-900 tracking-tight">
            {t('nav.brand', 'AGRI SMART')} {t('nav.aiBadge', 'AI')}
          </span>
        </Link>
        <h2 className="mt-4 text-center text-sm font-medium text-slate-500">
          {t('footer.platformTitle', 'Smart Farming Decision Support Platform')}
        </h2>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md px-4">
        <div className="bg-white py-8 px-6 shadow-xl shadow-slate-200/50 rounded-3xl border border-slate-100 sm:px-10">
          <Outlet />
        </div>

        <div className="mt-6 text-center">
          <Link
            to="/"
            className="text-xs font-medium text-slate-400 hover:text-agri-600 transition"
          >
            &larr; {t('auth.backToHome', 'Back to Home')}
          </Link>
        </div>
      </div>
    </div>
  );
};

export default AuthLayout;
