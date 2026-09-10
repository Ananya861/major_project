import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Sprout,
  TrendingUp,
  Store,
  Scale,
  CloudSun,
  Tractor,
  Bell,
  User,
  Calculator,
  HelpCircle,
  X,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const navigationGroups = [
  {
    title: 'MAIN',
    items: [
      { name: 'Dashboard', to: '/dashboard', icon: LayoutDashboard },
    ],
  },
  {
    title: 'AI & ADVISORY',
    items: [
      { name: 'Crop Recommendation', to: '/crop-recommendation', icon: Sprout },
      { name: 'Price Prediction', to: '/price-prediction', icon: TrendingUp },
    ],
  },
  {
    title: 'MARKET INTELLIGENCE',
    items: [
      { name: 'Market Prices', to: '/market-prices', icon: Store },
      { name: 'MSP Comparison', to: '/msp-comparison', icon: Scale },
    ],
  },
  {
    title: 'FARM INTELLIGENCE',
    items: [
      { name: 'My Farms & Soil', to: '/farms', icon: Tractor },
      { name: 'Weather Insights', to: '/weather', icon: CloudSun },
    ],
  },
  {
    title: 'TOOLS & SERVICES',
    items: [
      { name: 'Profit Calculator', to: '/profit-calculator', icon: Calculator },
    ],
  },
  {
    title: 'ACCOUNT',
    items: [
      { name: 'Farmer Profile', to: '/profile', icon: User },
      { name: 'Notifications', to: '/notifications', icon: Bell },
      { name: 'Help & Docs', to: '/help', icon: HelpCircle },
    ],
  },
];

const Sidebar = ({ isOpen, onClose }) => {
  const { user } = useAuth();

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/40 backdrop-blur-xs lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar Content */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 w-72 bg-white border-r border-slate-200 flex flex-col transition-transform duration-300 ease-in-out lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Header / Logo */}
        <div className="h-16 flex items-center justify-between px-6 border-b border-slate-100">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-agri-600 flex items-center justify-center text-white shadow-sm shadow-agri-600/30">
              <Sprout className="w-6 h-6" />
            </div>
            <div>
              <span className="font-bold text-slate-800 tracking-tight text-lg">AGRI SMART</span>
              <span className="text-xs font-semibold text-agri-600 ml-1.5 px-1.5 py-0.5 bg-agri-50 rounded-md border border-agri-200">
                AI
              </span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 lg:hidden"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation links */}
        <div className="flex-1 overflow-y-auto px-4 py-4 space-y-6">
          {navigationGroups.map((group) => (
            <div key={group.title}>
              <h4 className="px-3 text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">
                {group.title}
              </h4>
              <div className="space-y-1">
                {group.items.map((item) => {
                  const Icon = item.icon;
                  return (
                    <NavLink
                      key={item.to}
                      to={item.to}
                      onClick={() => {
                        if (window.innerWidth < 1024) onClose();
                      }}
                      className={({ isActive }) =>
                        `flex items-center justify-between px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
                          isActive
                            ? 'bg-agri-50 text-agri-700 font-semibold shadow-xs border border-agri-200/60'
                            : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                        }`
                      }
                    >
                      <div className="flex items-center space-x-3">
                        <Icon className="w-4 h-4 shrink-0 text-slate-500 group-hover:text-agri-600" />
                        <span>{item.name}</span>
                      </div>
                      {item.tag && (
                        <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 bg-slate-100 text-slate-500 rounded">
                          {item.tag}
                        </span>
                      )}
                    </NavLink>
                  );
                })}
              </div>
            </div>
          ))}
        </div>

        {/* Bottom Farmer Mini-Profile */}
        {user && (
          <div className="p-4 border-t border-slate-100 bg-slate-50/50">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-full bg-agri-100 text-agri-800 flex items-center justify-center font-bold text-sm border border-agri-200">
                {user.name?.charAt(0)?.toUpperCase() || 'F'}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-slate-800 truncate">{user.name}</p>
                <p className="text-xs text-slate-500 truncate">{user.phone}</p>
              </div>
            </div>
          </div>
        )}
      </aside>
    </>
  );
};

export default Sidebar;
