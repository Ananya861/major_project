import React from 'react';
import { Droplets, CheckCircle2 } from 'lucide-react';
import Badge from '../components/common/Badge';

const SmartIrrigationPage = () => {
  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <div className="inline-flex items-center space-x-2 text-xs font-semibold text-blue-700 bg-blue-50 px-3 py-1 rounded-full border border-blue-200 mb-2">
          <Droplets className="w-3.5 h-3.5 text-blue-600" />
          <span>Hydrological Advisory Module</span>
        </div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
          Smart Irrigation &amp; Water Scheduling
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Precision irrigation timing based on real-time soil moisture and evapotranspiration calculations.
        </p>
      </div>

      <div className="bg-white border border-slate-200/80 rounded-3xl p-8 md:p-12 shadow-xs text-center space-y-6">
        <div className="w-16 h-16 rounded-2xl bg-blue-50 border border-blue-100 text-blue-600 flex items-center justify-center mx-auto">
          <Droplets className="w-8 h-8" />
        </div>

        <div className="max-w-lg mx-auto space-y-2">
          <div className="flex items-center justify-center space-x-2">
            <h2 className="text-xl font-bold text-slate-800">
              Feature Under Active Development
            </h2>
            <Badge variant="warning">Coming Soon</Badge>
          </div>
          <p className="text-xs text-slate-500 leading-relaxed">
            AgriSmart AI currently provides real-time agro-climatic intelligence.
            Automated sensor valve telemetry and daily crop-specific millimeter watering calculations
            are scheduled for upcoming platform updates.
          </p>
        </div>

        {/* Feature roadmap preview */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 max-w-2xl mx-auto text-left pt-4 border-t border-slate-100">
          <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
            <div className="flex items-center space-x-2 text-slate-800 font-bold text-xs mb-1">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              <span>Evapotranspiration</span>
            </div>
            <p className="text-[11px] text-slate-500">
              Penman-Monteith equation based water depletion calculation.
            </p>
          </div>

          <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
            <div className="flex items-center space-x-2 text-slate-800 font-bold text-xs mb-1">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              <span>Rainfall Deductions</span>
            </div>
            <p className="text-[11px] text-slate-500">
              Automatic postponement when rain is forecast within 24 hours.
            </p>
          </div>

          <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
            <div className="flex items-center space-x-2 text-slate-800 font-bold text-xs mb-1">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              <span>Drip Optimization</span>
            </div>
            <p className="text-[11px] text-slate-500">
              Zone-wise minutes-of-watering schedule for drip systems.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SmartIrrigationPage;
