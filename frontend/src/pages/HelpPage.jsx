import React from 'react';
import { HelpCircle, BookOpen, Cpu, ShieldCheck, Terminal, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

const HelpPage = () => {
  const faqs = [
    {
      q: 'How does the AI Crop Recommendation work?',
      a: 'The system uses an advanced Machine Learning crop recommendation engine. It takes the farm soil test readings (Nitrogen, Phosphorus, Potassium, pH, Moisture) along with real-time local weather (temperature, precipitation) from OpenWeather to produce confidence-ranked crop recommendations.',
    },
    {
      q: 'Where do the mandi market prices come from?',
      a: 'Market prices are retrieved in real-time from the official Government of India data.gov.in Agmarknet API (Resource ID 9ef84268-d588-465a-a308-a864a43d0070). If the government gateway times out or is unreachable, the system gracefully falls back to the latest recorded price in the local PostgreSQL database.',
    },
    {
      q: 'How does the Price Prediction model forecast future prices?',
      a: 'The system uses a Pan-India HistGradientBoostingRegressor model trained on over 311,000 historical mandi records. It constructs time-series lag features (lag_1, lag_2, lag_3) and rolling averages to iteratively predict prices up to 30 days into the future.',
    },
    {
      q: 'What does MSP Comparison mean?',
      a: 'Minimum Support Price (MSP) is the government benchmark price floor to protect farmers. The system calculates whether current mandi auction rates are above or below the official MSP, alerting farmers to favorable market timings or potential distress sales.',
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
          <span>Documentation &amp; Support</span>
        </div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
          AgriSmart AI — System Guide &amp; FAQ
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Complete guide to platform features, AI architectures, and data capabilities.
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
            <span className="font-bold text-slate-800">Crop Intelligence Engine</span>
            <p className="text-slate-500">
              Crop Recommendation model and feature builder integrating soil nutrients and weather.
            </p>
          </div>

          <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100 space-y-1">
            <span className="font-bold text-slate-800">Price Forecasting Engine</span>
            <p className="text-slate-500">
              Pan-India Mandi price forecasting model (HistGradientBoostingRegressor) and MSP benchmark logic.
            </p>
          </div>

          <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100 space-y-1">
            <span className="font-bold text-slate-800">Platform Infrastructure &amp; API</span>
            <p className="text-slate-500">
              FastAPI orchestration, PostgreSQL async database, JWT security, data.gov.in integration, and modern React interface.
            </p>
          </div>
        </div>
      </div>

      {/* FAQs */}
      <div className="bg-white border border-slate-200/80 rounded-3xl p-6 md:p-8 shadow-xs space-y-6">
        <div className="flex items-center space-x-2 text-slate-900 font-bold text-base">
          <BookOpen className="w-5 h-5 text-agri-600" />
          <span>Frequently Asked Questions</span>
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
