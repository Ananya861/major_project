import React from 'react';
import { Link } from 'react-router-dom';
import {
  Sprout,
  TrendingUp,
  Store,
  CloudSun,
  Scale,
  ShieldCheck,
  ArrowRight,
  Sparkles,
  CheckCircle2,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const features = [
  {
    icon: Sprout,
    title: 'Crop Recommendation AI',
    description:
      'Advanced Machine Learning model evaluates your soil N-P-K nutrients, pH, moisture, and local weather to recommend the highest-yielding crops.',
    link: '/crop-recommendation',
    color: 'bg-emerald-50 text-emerald-600 border-emerald-100',
  },
  {
    icon: TrendingUp,
    title: 'Pan-India Price Prediction',
    description:
      'Advanced HistGradientBoostingRegressor machine learning model forecasts mandi modal prices up to 30 days ahead based on historical market trends.',
    link: '/price-prediction',
    color: 'bg-blue-50 text-blue-600 border-blue-100',
  },
  {
    icon: Store,
    title: 'Live Mandi Market Intelligence',
    description:
      'Real-time commodity arrivals and modal prices directly from the Government of India data.gov.in Agmarknet gateway with database fallback.',
    link: '/market-prices',
    color: 'bg-amber-50 text-amber-600 border-amber-100',
  },
  {
    icon: Scale,
    title: 'MSP Benchmark Comparison',
    description:
      'Instant comparison between actual mandi market prices and official Government Minimum Support Prices (MSP) for Rabi and Kharif crops.',
    link: '/msp-comparison',
    color: 'bg-purple-50 text-purple-600 border-purple-100',
  },
  {
    icon: CloudSun,
    title: 'Agro-Weather Intelligence',
    description:
      'Accurate temperature, precipitation, and humidity insights based on farm GPS coordinates powered by OpenWeather integration.',
    link: '/weather',
    color: 'bg-sky-50 text-sky-600 border-sky-100',
  },
  {
    icon: ShieldCheck,
    title: 'Automated Price & Weather Alerts',
    description:
      'Smart notifications generated whenever daily mandi prices deviate by 5%+ or future forecasts drop below MSP thresholds.',
    link: '/notifications',
    color: 'bg-rose-50 text-rose-600 border-rose-100',
  },
];

const LandingPage = () => {
  const { isAuthenticated } = useAuth();

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* Top Navbar */}
      <header className="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-slate-200/80 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-agri-600 flex items-center justify-center text-white shadow-sm shadow-agri-600/30">
              <Sprout className="w-6 h-6" />
            </div>
            <div>
              <span className="font-bold text-slate-900 tracking-tight text-lg">AGRI SMART</span>
              <span className="text-xs font-semibold text-agri-600 ml-1.5 px-1.5 py-0.5 bg-agri-50 rounded-md border border-agri-200">
                AI
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            {isAuthenticated ? (
              <Link
                to="/dashboard"
                className="inline-flex items-center space-x-2 px-5 py-2.5 bg-agri-600 hover:bg-agri-700 text-white text-sm font-semibold rounded-xl shadow-sm transition"
              >
                <span>Go to Dashboard</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            ) : (
              <>
                <Link
                  to="/login"
                  className="px-4 py-2 text-sm font-semibold text-slate-700 hover:text-agri-700 transition"
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  className="inline-flex items-center space-x-2 px-5 py-2.5 bg-agri-600 hover:bg-agri-700 text-white text-sm font-semibold rounded-xl shadow-sm shadow-agri-600/20 transition"
                >
                  <span>Get Started</span>
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative pt-16 pb-20 md:pt-24 md:pb-28 overflow-hidden bg-gradient-to-b from-white via-agri-50/20 to-slate-50 border-b border-slate-200/60">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-agri-50 border border-agri-200 text-agri-800 text-xs font-semibold mb-6 shadow-xs">
            <Sparkles className="w-4 h-4 text-agri-600" />
            <span>AI-Powered Smart Agriculture &amp; Farmer Assistance Platform</span>
          </div>

          <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold text-slate-900 tracking-tight max-w-4xl mx-auto leading-tight md:leading-tight">
            Smart Farming.{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-agri-600 to-emerald-500">
              Better Decisions.
            </span>{' '}
            Better Yields.
          </h1>

          <p className="mt-6 text-base sm:text-lg text-slate-600 max-w-2xl mx-auto leading-relaxed">
            An integrated decision support system helping farmers maximize profits through AI crop
            suitability recommendations, Pan-India mandi price forecasting, weather insights, and
            real-time market alerts.
          </p>

          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              to={isAuthenticated ? '/dashboard' : '/register'}
              className="w-full sm:w-auto inline-flex items-center justify-center space-x-2 px-8 py-3.5 bg-agri-600 hover:bg-agri-700 text-white text-base font-semibold rounded-2xl shadow-md shadow-agri-600/30 transition transform hover:-translate-y-0.5"
            >
              <span>{isAuthenticated ? 'Open Dashboard' : 'Get Started Free'}</span>
              <ArrowRight className="w-5 h-5" />
            </Link>

            <Link
              to="/market-prices"
              className="w-full sm:w-auto inline-flex items-center justify-center space-x-2 px-7 py-3.5 bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 text-base font-semibold rounded-2xl shadow-xs transition"
            >
              <span>Explore Live Market Prices</span>
            </Link>
          </div>

          {/* Value Badges */}
          <div className="mt-12 flex flex-wrap items-center justify-center gap-6 text-xs font-semibold text-slate-500">
            <div className="flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 text-agri-600" />
              <span>Govt. of India Mandi Data (Agmarknet)</span>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 text-agri-600" />
              <span>Machine Learning Crop Recommendation</span>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 text-agri-600" />
              <span>HistGradientBoosting Price Forecasting</span>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Cards Grid */}
      <section className="py-20 max-w-7xl mx-auto px-6 flex-1">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <h2 className="text-xs font-bold text-agri-600 uppercase tracking-widest mb-2">
            INTEGRATED PLATFORM MODULES
          </h2>
          <p className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Comprehensive Decision Support for Modern Agriculture
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((item) => {
            const Icon = item.icon;
            return (
              <div
                key={item.title}
                className="bg-white border border-slate-200/80 rounded-3xl p-7 shadow-xs hover:shadow-md transition flex flex-col justify-between"
              >
                <div>
                  <div className={`w-12 h-12 rounded-2xl flex items-center justify-center border ${item.color} mb-5`}>
                    <Icon className="w-6 h-6" />
                  </div>
                  <h3 className="text-lg font-bold text-slate-800 mb-2">{item.title}</h3>
                  <p className="text-sm text-slate-600 leading-relaxed">{item.description}</p>
                </div>
                <div className="mt-6 pt-4 border-t border-slate-100">
                  <Link
                    to={item.link}
                    className="inline-flex items-center space-x-1.5 text-xs font-bold text-agri-600 hover:text-agri-700 transition"
                  >
                    <span>Launch Feature</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200/80 py-8 px-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-2">
            <Sprout className="w-4 h-4 text-agri-600" />
            <span className="font-bold text-slate-800">AGRI SMART AI</span>
            <span>— Smart Farming Decision Support Platform</span>
          </div>
          <p className="text-slate-400">
            &copy; {new Date().getFullYear()} AgriSmart AI. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
