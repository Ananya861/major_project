import React, { useState, useRef, useEffect } from 'react';
import { Globe, ChevronDown, Check } from 'lucide-react';
import { useTranslation } from '../../i18n/LanguageContext';

const LanguageSelector = ({ variant = 'default', className = '' }) => {
  const { language, setLanguage, languages, currentLanguage } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (code) => {
    setLanguage(code);
    setIsOpen(false);
  };

  return (
    <div className={`relative inline-block text-left ${className}`} ref={dropdownRef}>
      {/* Trigger Button */}
      <button
        type="button"
        onClick={() => setIsOpen((prev) => !prev)}
        className={`flex items-center space-x-2 px-3 py-1.5 rounded-xl border text-xs font-semibold transition shadow-xs focus:outline-none focus:ring-2 focus:ring-agri-500/30 ${
          variant === 'compact'
            ? 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'
            : variant === 'auth'
            ? 'bg-white/90 backdrop-blur-md border-slate-200 text-slate-800 hover:bg-white shadow-sm'
            : 'bg-slate-50 border-slate-200/80 text-slate-700 hover:bg-slate-100'
        }`}
        aria-label="Change language"
        aria-expanded={isOpen}
      >
        <Globe className="w-3.5 h-3.5 text-agri-600 shrink-0" />
        <span className="truncate max-w-[80px] sm:max-w-none">
          {currentLanguage?.nativeName || 'English'}
        </span>
        <ChevronDown
          className={`w-3.5 h-3.5 text-slate-400 transition-transform duration-200 ${
            isOpen ? 'rotate-180' : ''
          }`}
        />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-56 bg-white rounded-2xl shadow-xl border border-slate-100 py-1.5 z-50 animate-fadeIn">
          <div className="px-3 py-1.5 border-b border-slate-100 text-[10px] font-bold uppercase tracking-wider text-slate-400">
            Select Language / ಭಾಷೆ / भाषा
          </div>
          <div className="max-h-72 overflow-y-auto py-1">
            {languages.map((lang) => {
              const isSelected = lang.code === language;
              return (
                <button
                  key={lang.code}
                  type="button"
                  onClick={() => handleSelect(lang.code)}
                  className={`w-full flex items-center justify-between px-3.5 py-2 text-left text-xs transition ${
                    isSelected
                      ? 'bg-agri-50 text-agri-800 font-bold'
                      : 'text-slate-700 hover:bg-slate-50 hover:text-slate-900 font-medium'
                  }`}
                >
                  <div className="flex items-center space-x-2.5">
                    <span className="w-6 text-center text-[11px] font-semibold text-slate-400 bg-slate-100 rounded px-1 py-0.5">
                      {lang.shortCode}
                    </span>
                    <div>
                      <div className="text-xs font-semibold">{lang.nativeName}</div>
                      <div className="text-[10px] text-slate-400">{lang.name}</div>
                    </div>
                  </div>
                  {isSelected && (
                    <Check className="w-4 h-4 text-agri-600 shrink-0" />
                  )}
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default LanguageSelector;
