import React from 'react';
import { useTranslation } from '../i18n/LanguageContext';
import { HelpCircle, BookOpen, Cpu, ShieldCheck, Terminal, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

const HelpPage = () => {
  const { t } = useTranslation();

  const faqs = [
    {
      q: t('help.faq1Q', 'How does the AI Crop Recommendation work?'),
      a: t('help.faq1A', 'The recommendation engine analyzes soil Nitrogen, Phosphorus, Potassium, pH, moisture, and local weather patterns to suggest top-yielding crops.'),
    },
    {
      q: t('help.faq2Q', 'What is the MSP Comparison feature?'),
      a: t('help.faq2A', 'It compares current APMC mandi prices against the official Government of India Minimum Support Price (MSP) so farmers avoid selling at distress prices.'),
    },
    {
      q: t('help.faq3Q', 'How does the Multilingual AI Assistant work?'),
      a: t('help.faq3A', 'The AI Assistant answers questions in 8 Indian languages (English, Kannada, Hindi, Telugu, Tamil, Malayalam, Marathi, Bengali) using your farm soil and weather context.'),
    },
    {
      q: 'Where do the mandi market prices come from?',
      a: 'Market prices are retrieved in real-time from official Government Agmarknet data with database fallback.',
    },
    {
      q: 'How do I add or update soil data for my farm?',
      a: 'Navigate to "My Farms & Soil", select your farm plot, and click "+ Log Soil Test Reading". Once recorded, you can immediately run the Crop Recommendation AI.',
    },
  ];

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <div className="inline-flex items-center space-x-2 text-xs font-semibold text-agri-700 bg-agri-50 px-3 py-1 rounded-full border border-agri-200 mb-2">
          <HelpCircle className="w-3.5 h-3.5 text-agri-600" />
          <span>{t('help.title', 'Documentation & Support')}</span>
        </div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
          {t('help.title', 'Help, Advisory Manuals & Support')}
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          {t('help.subtitle', 'Learn how to use AI crop recommendations, soil testing tools, and mandi price intelligence.')}
        </p>
      </div>

      {/* System Architecture Overview */}
      <div className="bg-white border border-slate-200/80 rounded-3xl p-6 md:p-8 shadow-xs space-y-4">
        <div className="flex items-center space-x-3 text-slate-900 font-bold text-base">
          <Cpu className="w-5 h-5 text-agri-600" />
          <span>Platform Architecture &amp; Core Modules</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
          <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100 space-y-1">
            <span className="font-bold text-slate-800">{t('nav.cropRecommendation', 'Crop Intelligence Engine')}</span>
            <p className="text-slate-500">
              Crop Recommendation model and feature builder integrating soil nutrients and weather.
            </p>
          </div>

          <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100 space-y-1">
            <span className="font-bold text-slate-800">{t('nav.pricePrediction', 'Price Forecasting Engine')}</span>
            <p className="text-slate-500">
              Pan-India Mandi price forecasting model (HistGradientBoostingRegressor) and MSP benchmark logic.
            </p>
          </div>

          <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100 space-y-1">
            <span className="font-bold text-slate-800">{t('nav.brand', 'AgriSmart AI')} Platform</span>
            <p className="text-slate-500">
              FastAPI orchestration, PostgreSQL async database, JWT security, and 8 regional languages support.
            </p>
          </div>
        </div>
      </div>

      {/* FAQs */}
      <div className="bg-white border border-slate-200/80 rounded-3xl p-6 md:p-8 shadow-xs space-y-6">
        <div className="flex items-center space-x-2 text-slate-900 font-bold text-base">
          <BookOpen className="w-5 h-5 text-agri-600" />
          <span>{t('help.faqsTitle', 'Frequently Asked Questions')}</span>
        </div>

        <div className="space-y-4">
          {faqs.map((faq, index) => (
            <div key={index} className="p-4 rounded-2xl bg-slate-50/70 border border-slate-100">
              <h4 className="text-sm font-bold text-slate-800 mb-1">{faq.q}</h4>
              <p className="text-xs text-slate-600 leading-relaxed">{faq.a}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default HelpPage;
