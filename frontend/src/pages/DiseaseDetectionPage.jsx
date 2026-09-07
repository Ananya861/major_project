import React from 'react';
import { ScanLine, AlertCircle, Clock, CheckCircle2 } from 'lucide-react';
import Badge from '../components/common/Badge';

const DiseaseDetectionPage = () => {
  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <div className="inline-flex items-center space-x-2 text-xs font-semibold text-purple-700 bg-purple-50 px-3 py-1 rounded-full border border-purple-200 mb-2">
          <ScanLine className="w-3.5 h-3.5 text-purple-600" />
          <span>Computer Vision Module</span>
        </div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
          Plant Disease Detection
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          AI leaf diagnosis for early detection of blight, rust, and insect damage.
        </p>
      </div>

      <div className="bg-white border border-slate-200/80 rounded-3xl p-8 md:p-12 shadow-xs text-center space-y-6">
        <div className="w-16 h-16 rounded-2xl bg-purple-50 border border-purple-100 text-purple-600 flex items-center justify-center mx-auto">
          <ScanLine className="w-8 h-8" />
        </div>

        <div className="max-w-lg mx-auto space-y-2">
          <div className="flex items-center justify-center space-x-2">
            <h2 className="text-xl font-bold text-slate-800">
              Feature Under Active Development
            </h2>
            <Badge variant="warning">Coming Soon</Badge>
          </div>
          <p className="text-xs text-slate-500 leading-relaxed">
            AgriSmart AI currently integrates AI Crop Recommendation and Pan-India Mandi Price
            Forecasting. Leaf image pathology inference via convolutional neural networks (CNN) is
            scheduled for an upcoming platform release.
          </p>
        </div>

        {/* Feature roadmap preview */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 max-w-2xl mx-auto text-left pt-4 border-t border-slate-100">
          <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
            <div className="flex items-center space-x-2 text-slate-800 font-bold text-xs mb-1">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              <span>PlantVillage Dataset</span>
            </div>
            <p className="text-[11px] text-slate-500">
              Trained on 54,000+ healthy and diseased crop leaf images.
            </p>
          </div>

          <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
            <div className="flex items-center space-x-2 text-slate-800 font-bold text-xs mb-1">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              <span>Camera Upload</span>
            </div>
            <p className="text-[11px] text-slate-500">
              Real-time smartphone photo capture directly in field.
            </p>
          </div>

          <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
            <div className="flex items-center space-x-2 text-slate-800 font-bold text-xs mb-1">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              <span>Treatment Advice</span>
            </div>
            <p className="text-[11px] text-slate-500">
              Organic and chemical remedy recommendations with dosages.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DiseaseDetectionPage;
