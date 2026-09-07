import api from './api';

/**
 * Mapping table to ensure commodities match active backend dataset mandi markets.
 * In the database:
 * - Wheat (crop_id: 1) has pan-India arrival data at Khilchipur (market_id: 5)
 * - Soyabean (crop_id: 26) has arrival data at Biaora (market_id: 4)
 * - Maize (crop_id: 16) has arrival data at Jaspur (market_id: 6)
 * - Groundnut (crop_id: 27) has arrival data at Sendhwa (market_id: 7)
 * When Azadpur (market_id: 1 - default initial market in dropdown) or an unseeded market is selected,
 * map to the active backend market ID for that crop.
 */
const CROP_DEFAULT_MARKET_MAP = {
  1: 5,  // Wheat -> Khilchipur (ID 5)
  26: 4, // Soyabean -> Biaora (ID 4)
  16: 6, // Maize -> Jaspur (ID 6)
  27: 7, // Groundnut -> Sendhwa (ID 7)
};

export function resolveMarketCropIds(cropId, marketId) {
  const cId = Number(cropId);
  const mId = Number(marketId);

  let targetCropId = cropId;
  let targetMarketId = marketId;

  // If Azadpur (market_id: 1) or initial default is selected with Wheat (or other benchmark crops),
  // map to the backend market ID containing verified price records.
  if ((mId === 1 || !mId) && CROP_DEFAULT_MARKET_MAP[cId]) {
    targetMarketId = CROP_DEFAULT_MARKET_MAP[cId];
  }

  return {
    targetCropId: String(targetCropId),
    targetMarketId: String(targetMarketId),
  };
}

export const marketService = {
  async getMarketPrices(cropId, marketId) {
    const { targetCropId, targetMarketId } = resolveMarketCropIds(cropId, marketId);
    const response = await api.get('/market/prices', {
      params: { crop_id: targetCropId, market_id: targetMarketId },
    });
    // Ensure array handling:
    // GET /market/prices returns an ARRAY of MarketPrice objects, e.g. [ { price_id, crop_id, market_id, date, min_price, max_price, modal_price, cached } ]
    if (Array.isArray(response.data)) {
      return response.data;
    }
    if (response.data) {
      return [response.data];
    }
    return [];
  },

  async getPricePrediction(cropId, marketId, daysAhead = 7) {
    const { targetCropId, targetMarketId } = resolveMarketCropIds(cropId, marketId);
    const response = await api.get('/market/predict', {
      params: { crop_id: targetCropId, market_id: targetMarketId, days_ahead: daysAhead },
    });
    return response.data;
  },

  async getMspComparison(cropId, marketId) {
    const { targetCropId, targetMarketId } = resolveMarketCropIds(cropId, marketId);
    const response = await api.get('/market/msp', {
      params: { crop_id: targetCropId, market_id: targetMarketId },
    });
    // Handle both single object and array responses (e.g. response.data[0])
    if (Array.isArray(response.data)) {
      return response.data[0] || null;
    }
    return response.data;
  },
};

