import api from './api';

/**
 * Benchmark markets with verified historical mandi records in the database:
 * - Wheat (crop_id: 1) -> Khilchipur (market_id: 5)
 * - Soyabean (crop_id: 26) -> Biaora (market_id: 4)
 * - Maize (crop_id: 16) -> Jaspur (market_id: 6)
 * - Groundnut (crop_id: 27) -> Sendhwa (market_id: 7)
 */
export const CROP_BENCHMARK_MARKET_MAP = {
  1: 5,  // Wheat -> Khilchipur (ID 5)
  26: 4, // Soyabean -> Biaora (ID 4)
  16: 6, // Maize -> Jaspur (ID 6)
  27: 7, // Groundnut -> Sendhwa (ID 7)
};

// Maintained for backward compatibility without silent remapping
export function resolveMarketCropIds(cropId, marketId) {
  return {
    targetCropId: String(cropId),
    targetMarketId: String(marketId),
  };
}

export const marketService = {
  async getMarketPrices(cropId, marketId) {
    const response = await api.get('/market/prices', {
      params: { crop_id: cropId, market_id: marketId },
    });
    if (Array.isArray(response.data)) {
      return response.data;
    }
    if (response.data) {
      return [response.data];
    }
    return [];
  },

  async getPricePrediction(cropId, marketId, daysAhead = 7) {
    const response = await api.get('/market/predict', {
      params: { crop_id: cropId, market_id: marketId, days_ahead: daysAhead },
    });
    return response.data;
  },

  async getMspComparison(cropId, marketId) {
    const response = await api.get('/market/msp', {
      params: { crop_id: cropId, market_id: marketId },
    });
    if (Array.isArray(response.data)) {
      return response.data[0] || null;
    }
    return response.data;
  },
};

