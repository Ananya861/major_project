import React, { useState } from 'react';
import { useTranslation } from '../i18n/LanguageContext';
import { Calculator, AlertCircle, TrendingUp, IndianRupee, PieChart } from 'lucide-react';
import { formatCurrency } from '../utils/formatters';

const ProfitCalculatorPage = () => {
  const { t } = useTranslation();
  const [inputs, setInputs] = useState({
    cropName: 'Wheat',
    acres: 3,
    yieldPerAcre: 18, // quintals per acre
    sellingPricePerQuintal: 2500, // INR
    seedCost: 4500,
    fertilizerCost: 8000,
    irrigationCost: 3500,
    laborCost: 6000,
    otherCost: 2000,
  });

  const totalYieldQuintals = (inputs.acres || 0) * (inputs.yieldPerAcre || 0);
  const grossRevenue = totalYieldQuintals * (inputs.sellingPricePerQuintal || 0);
  const totalCost =
    (inputs.seedCost || 0) +
    (inputs.fertilizerCost || 0) +
    (inputs.irrigationCost || 0) +
    (inputs.laborCost || 0) +
    (inputs.otherCost || 0);

  const netProfit = grossRevenue - totalCost;
  const roiPercent = totalCost > 0 ? ((netProfit / totalCost) * 100).toFixed(1) : 0;
  const breakEvenPrice = totalYieldQuintals > 0 ? (totalCost / totalYieldQuintals).toFixed(2) : 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <div className="inline-flex items-center space-x-2 text-xs font-semibold text-agri-700 bg-agri-50 px-3 py-1 rounded-full border border-agri-200 mb-2">
          <Calculator className="w-3.5 h-3.5 text-agri-600" />
          <span>{t('calculator.title', 'Crop Profitability & Yield Calculator')}</span>
        </div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
          {t('calculator.title', 'Crop Profitability & Yield Calculator')}
        </h1>
        <p className="text-xs text-slate-500 mt-1 max-w-2xl">
          {t('calculator.subtitle', 'Estimate production costs, gross revenue, and net profit per acre before sowing.')}
        </p>
      </div>

      {/* Mandatory Disclaimer Badge */}
      <div className="p-4 bg-amber-50/80 border border-amber-200 rounded-2xl flex items-start space-x-3 text-xs text-amber-900">
        <AlertCircle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
        <div>
          <span className="font-bold">Client-Side Estimation Tool:</span> All financial outputs are
          calculated directly in your browser using the values entered below. These figures are
          planning estimates and are not derived from AI or backend models.
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Inputs Column */}
        <div className="lg:col-span-2 bg-white border border-slate-200/80 rounded-3xl p-6 md:p-8 shadow-xs space-y-6">
          <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wider pb-2 border-b border-slate-100">
            1. {t('calculator.revenueTitle', 'Yield & Revenue Assumptions')}
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                {t('calculator.cropLabel', 'Select Crop')}
              </label>
              <input
                type="text"
                value={inputs.cropName}
                onChange={(e) => setInputs({ ...inputs, cropName: e.target.value })}
                className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-agri-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                {t('calculator.landSizeLabel', 'Cultivation Area (Acres)')}
              </label>
              <input
                type="number"
                min="0.1"
                step="0.5"
                value={inputs.acres}
                onChange={(e) => setInputs({ ...inputs, acres: parseFloat(e.target.value) || 0 })}
                className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-agri-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                {t('calculator.yieldLabel', 'Expected Yield (Quintals/Acre)')}
              </label>
              <input
                type="number"
                min="1"
                step="1"
                value={inputs.yieldPerAcre}
                onChange={(e) =>
                  setInputs({ ...inputs, yieldPerAcre: parseFloat(e.target.value) || 0 })
                }
                className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-agri-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                {t('calculator.priceLabel', 'Expected Selling Price (₹/Quintal)')}
              </label>
              <input
                type="number"
                min="100"
                step="50"
                value={inputs.sellingPricePerQuintal}
                onChange={(e) =>
                  setInputs({
                    ...inputs,
                    sellingPricePerQuintal: parseFloat(e.target.value) || 0,
                  })
                }
                className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-agri-500"
              />
            </div>
          </div>

          <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wider pb-2 border-b border-slate-100 pt-2">
            2. {t('calculator.costTitle', 'Total Cultivation Expenses')} (₹)
          </h3>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            <div>
              <label className="block text-[11px] font-semibold text-slate-600 mb-1">
                Seeds Cost (₹)
              </label>
              <input
                type="number"
                min="0"
                step="500"
                value={inputs.seedCost}
                onChange={(e) =>
                  setInputs({ ...inputs, seedCost: parseFloat(e.target.value) || 0 })
                }
                className="w-full px-2.5 py-1.5 text-xs border border-slate-200 rounded-xl"
              />
            </div>

            <div>
              <label className="block text-[11px] font-semibold text-slate-600 mb-1">
                Fertilizers &amp; Spray (₹)
              </label>
              <input
                type="number"
                min="0"
                step="500"
                value={inputs.fertilizerCost}
                onChange={(e) =>
                  setInputs({ ...inputs, fertilizerCost: parseFloat(e.target.value) || 0 })
                }
                className="w-full px-2.5 py-1.5 text-xs border border-slate-200 rounded-xl"
              />
            </div>

            <div>
              <label className="block text-[11px] font-semibold text-slate-600 mb-1">
                Irrigation &amp; Power (₹)
              </label>
              <input
                type="number"
                min="0"
                step="500"
                value={inputs.irrigationCost}
                onChange={(e) =>
                  setInputs({ ...inputs, irrigationCost: parseFloat(e.target.value) || 0 })
                }
                className="w-full px-2.5 py-1.5 text-xs border border-slate-200 rounded-xl"
              />
            </div>

            <div>
              <label className="block text-[11px] font-semibold text-slate-600 mb-1">
                Labor &amp; Harvesting (₹)
              </label>
              <input
                type="number"
                min="0"
                step="500"
                value={inputs.laborCost}
                onChange={(e) =>
                  setInputs({ ...inputs, laborCost: parseFloat(e.target.value) || 0 })
                }
                className="w-full px-2.5 py-1.5 text-xs border border-slate-200 rounded-xl"
              />
            </div>

            <div className="col-span-2 sm:col-span-1">
              <label className="block text-[11px] font-semibold text-slate-600 mb-1">
                Machinery &amp; Other (₹)
              </label>
              <input
                type="number"
                min="0"
                step="500"
                value={inputs.otherCost}
                onChange={(e) => setInputs({ ...inputs, otherCost: parseFloat(e.target.value) || 0 })}
                className="w-full px-2.5 py-1.5 text-xs border border-slate-200 rounded-xl"
              />
            </div>
          </div>
        </div>

        {/* Results Column */}
        <div className="space-y-4">
          <div className="bg-white border border-slate-200/80 rounded-3xl p-6 shadow-xs space-y-4">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
              {t('calculator.title', 'Financial Summary')}
            </h3>

            <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
              <span className="text-[11px] text-slate-500 uppercase font-semibold">
                {t('calculator.yieldLabel', 'Total Production Yield')}
              </span>
              <p className="text-2xl font-extrabold text-slate-900 mt-0.5">
                {totalYieldQuintals.toFixed(1)} <span className="text-sm font-semibold">Quintals</span>
              </p>
            </div>

            <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
              <span className="text-[11px] text-slate-500 uppercase font-semibold">
                {t('calculator.revenueTitle', 'Estimated Gross Revenue')}
              </span>
              <p className="text-2xl font-extrabold text-slate-900 mt-0.5">
                {formatCurrency(grossRevenue)}
              </p>
            </div>

            <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
              <span className="text-[11px] text-slate-500 uppercase font-semibold">
                {t('calculator.costTitle', 'Total Cultivation Expenses')}
              </span>
              <p className="text-2xl font-extrabold text-slate-900 mt-0.5">
                {formatCurrency(totalCost)}
              </p>
            </div>

            <div
              className={`p-5 rounded-2xl border ${
                netProfit >= 0
                  ? 'bg-emerald-50/80 border-emerald-200 text-emerald-950'
                  : 'bg-rose-50/80 border-rose-200 text-rose-950'
              }`}
            >
              <span className="text-xs font-bold uppercase tracking-wider block opacity-80">
                {t('calculator.netProfitTitle', 'Estimated Net Profit')}
              </span>
              <div className="text-3xl font-extrabold tracking-tight mt-1">
                {formatCurrency(netProfit)}
              </div>
              <span className="text-xs font-semibold mt-1 block">
                {t('calculator.roiTitle', 'Return on Investment (ROI)')}: {roiPercent}%
              </span>
            </div>

            <div className="pt-2 text-xs text-slate-500 flex justify-between">
              <span>{t('market.currentModalPrice', 'Break-even Rate')}:</span>
              <span className="font-bold text-slate-800">{formatCurrency(breakEvenPrice)} / q</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfitCalculatorPage;
