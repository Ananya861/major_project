/**
 * Supported regional languages for AgriSmart AI platform.
 * Exactly 8 languages supported:
 * English, Kannada, Hindi, Telugu, Tamil, Malayalam, Marathi, Bengali.
 */

export const LANGUAGES = [
  {
    code: 'en',
    name: 'English',
    nativeName: 'English',
    shortCode: 'EN',
  },
  {
    code: 'kn',
    name: 'Kannada',
    nativeName: 'ಕನ್ನಡ',
    shortCode: 'ಕನ್ನ',
  },
  {
    code: 'hi',
    name: 'Hindi',
    nativeName: 'हिन्दी',
    shortCode: 'हिन्',
  },
  {
    code: 'te',
    name: 'Telugu',
    nativeName: 'తెలుగు',
    shortCode: 'తెలు',
  },
  {
    code: 'ta',
    name: 'Tamil',
    nativeName: 'தமிழ்',
    shortCode: 'தமி',
  },
  {
    code: 'ml',
    name: 'Malayalam',
    nativeName: 'മലയാളം',
    shortCode: 'മല',
  },
  {
    code: 'mr',
    name: 'Marathi',
    nativeName: 'मराठी',
    shortCode: 'मरा',
  },
  {
    code: 'bn',
    name: 'Bengali',
    nativeName: 'বাংলা',
    shortCode: 'বাং',
  },
];

export const DEFAULT_LANGUAGE = 'en';

export const getLanguageByCode = (code) => {
  return LANGUAGES.find((l) => l.code === code) || LANGUAGES[0];
};
