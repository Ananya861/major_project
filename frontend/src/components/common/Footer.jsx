import React from 'react';
import { Sprout } from 'lucide-react';
import { useTranslation } from '../../i18n/LanguageContext';

const Footer = () => {
  const { t } = useTranslation();

  return (
    <footer className="bg-white border-t border-slate-200/80 py-6 px-4 md:px-8 text-slate-500 text-xs mt-auto">
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="flex items-center space-x-2">
          <Sprout className="w-4 h-4 text-agri-600" />
          <span className="font-semibold text-slate-700">
            {t('nav.brand', 'AGRI SMART')} {t('nav.aiBadge', 'AI')}
          </span>
          <span>— {t('footer.platformTitle', 'Smart Farming Decision Support Platform')}</span>
        </div>
        <p className="text-slate-400">
          {t('footer.copyright', `© ${new Date().getFullYear()} AgriSmart AI. All rights reserved.`)}
        </p>
      </div>
    </footer>
  );
};

export default Footer;
