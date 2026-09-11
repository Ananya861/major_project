import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { FarmProvider } from './context/FarmContext';
import { LanguageProvider } from './i18n/LanguageContext';
import AiAssistant from './components/assistant/AiAssistant';

// Layouts
import MainLayout from './layouts/MainLayout';
import AuthLayout from './layouts/AuthLayout';
import ProtectedRoute from './components/common/ProtectedRoute';

// Pages
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import FarmsPage from './pages/FarmsPage';
import CropRecommendationPage from './pages/CropRecommendationPage';
import MarketPricesPage from './pages/MarketPricesPage';
import PricePredictionPage from './pages/PricePredictionPage';
import MspComparisonPage from './pages/MspComparisonPage';
import WeatherPage from './pages/WeatherPage';
import NotificationsPage from './pages/NotificationsPage';
import ProfilePage from './pages/ProfilePage';
import ProfitCalculatorPage from './pages/ProfitCalculatorPage';
import HelpPage from './pages/HelpPage';
import NotFoundPage from './pages/NotFoundPage';

function App() {
  return (
    <LanguageProvider>
      <AuthProvider>
        <FarmProvider>
          <Routes>
            {/* Public Landing Page */}
            <Route path="/" element={<LandingPage />} />

            {/* Authentication Pages */}
            <Route element={<AuthLayout />}>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
            </Route>

            {/* Protected Application Pages */}
            <Route
              element={
                <ProtectedRoute>
                  <MainLayout />
                </ProtectedRoute>
              }
            >
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/farms" element={<FarmsPage />} />
              <Route path="/crop-recommendation" element={<CropRecommendationPage />} />
              <Route path="/market-prices" element={<MarketPricesPage />} />
              <Route path="/price-prediction" element={<PricePredictionPage />} />
              <Route path="/msp-comparison" element={<MspComparisonPage />} />
              <Route path="/weather" element={<WeatherPage />} />
              <Route path="/notifications" element={<NotificationsPage />} />
              <Route path="/profile" element={<ProfilePage />} />
              <Route path="/profit-calculator" element={<ProfitCalculatorPage />} />
              <Route path="/help" element={<HelpPage />} />
            </Route>

            {/* Fallback 404 Route */}
            <Route path="/404" element={<NotFoundPage />} />
            <Route path="*" element={<Navigate to="/404" replace />} />
          </Routes>

          {/* Floating Multilingual AI Assistant */}
          <AiAssistant />
        </FarmProvider>
      </AuthProvider>
    </LanguageProvider>
  );
}

export default App;
