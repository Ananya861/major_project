import React, { createContext, useContext, useState, useEffect, useCallback, useMemo } from 'react';
import { LANGUAGES, DEFAULT_LANGUAGE, getLanguageByCode } from './languages';

import en from './translations/en';
import kn from './translations/kn';
import hi from './translations/hi';
import te from './translations/te';
import ta from './translations/ta';
import ml from './translations/ml';
import mr from './translations/mr';
import bn from './translations/bn';

const TRANSLATIONS = {
  en,
  kn,
  hi,
  te,
  ta,
  ml,
  mr,
  bn,
};

// Map full English name or variations to language code
const NAME_TO_CODE = {
  english: 'en',
  kannada: 'kn',
  hindi: 'hi',
  telugu: 'te',
  tamil: 'ta',
  malayalam: 'ml',
  marathi: 'mr',
  bengali: 'bn',
};

const LanguageContext = createContext(null);

export const LanguageProvider = ({ children }) => {
  const [language, setLanguageState] = useState(() => {
    try {
      const saved = localStorage.getItem('agri_lang');
      if (saved && TRANSLATIONS[saved]) {
        return saved;
      }
      // Check farmer_data in localStorage
      const farmerData = localStorage.getItem('farmer_data');
      if (farmerData) {
        const parsed = JSON.parse(farmerData);
        if (parsed.preferred_language) {
          const mapped = NAME_TO_CODE[parsed.preferred_language.toLowerCase()];
          if (mapped) return mapped;
        }
      }
    } catch {
      // Ignore parse error
    }
    return DEFAULT_LANGUAGE;
  });

  // Keep document lang attribute in sync
  useEffect(() => {
    try {
      document.documentElement.lang = language;
    } catch {
      // Ignore
    }
  }, [language]);

  const setLanguage = useCallback((code) => {
    const targetCode = TRANSLATIONS[code] ? code : DEFAULT_LANGUAGE;
    setLanguageState(targetCode);
    try {
      localStorage.setItem('agri_lang', targetCode);
      document.documentElement.lang = targetCode;
      window.dispatchEvent(
        new CustomEvent('agri:language_changed', { detail: targetCode })
      );
    } catch {
      // Ignore storage errors
    }
  }, []);

  /**
   * Translate key with fallback and interpolation.
   * e.g. t('dashboard.welcome') or t('common.save')
   */
  const t = useCallback(
    (keyPath, defaultText = '', variables = {}) => {
      if (!keyPath) return defaultText || '';

      const keys = keyPath.split('.');

      const lookup = (dict) => {
        if (!dict) return undefined;
        let current = dict;
        for (const k of keys) {
          if (current && typeof current === 'object' && k in current) {
            current = current[k];
          } else {
            return undefined;
          }
        }
        return current;
      };

      // 1. Check active language
      let result = lookup(TRANSLATIONS[language]);

      // 2. Fall back to English
      if (result === undefined && language !== 'en') {
        result = lookup(TRANSLATIONS.en);
      }

      // 3. Fall back to defaultText or key
      if (result === undefined || result === null) {
        result = defaultText || keyPath;
      }

      // 4. String interpolation: {variable}
      if (typeof result === 'string' && variables && Object.keys(variables).length > 0) {
        for (const [varKey, varVal] of Object.entries(variables)) {
          result = result.replace(new RegExp(`\\{${varKey}\\}`, 'g'), String(varVal));
        }
      }

      return result;
    },
    [language]
  );

  const currentLanguage = useMemo(() => getLanguageByCode(language), [language]);

  const value = useMemo(
    () => ({
      language,
      setLanguage,
      t,
      languages: LANGUAGES,
      currentLanguage,
    }),
    [language, setLanguage, t, currentLanguage]
  );

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useTranslation = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useTranslation must be used within a LanguageProvider');
  }
  return context;
};

export default LanguageContext;
