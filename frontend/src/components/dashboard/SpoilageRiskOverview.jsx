import React from 'react';
import { HIGH_RISK_SPOILAGE_BATCHES, SPOILAGE_RISK_DISTRIBUTION } from '../../data/mockData';
import { AlertTriangle, ShieldAlert, ArrowUpRight, Flame } from 'lucide-react';
import { Link } from 'react-router-dom';

export const SpoilageRiskOverview = () => {
  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-bold text-slate-900">Spoilage-Risk Overview</h3>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-rose-100 text-rose-800 flex items-center gap-1">
                <Flame className="w-3 h-3 text-rose-600" /> 14 High Risk
              </span>
            </div>
            <p className="text-xs text-slate-500">Real-time shelf life decay & ambient temperature alert monitor</p>
          </div>
          <Link
            to="/risk"
            className="text-xs font-semibold text-emerald-600 hover:text-emerald-700 flex items-center gap-0.5 hover:underline"
          >
            View All Risk Alerts <ArrowUpRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {/* Risk Level Distribution Bar */}
        <div className="mb-5">
          <div className="flex justify-between text-xs font-semibold mb-1.5">
            <span className="text-slate-600">Batch Risk Health Spectrum</span>
            <span className="text-slate-400">342 Total Active Batches</span>
          </div>
          <div className="h-3.5 w-full bg-slate-100 rounded-full overflow-hidden flex">
            <div style={{ width: '71.6%' }} className="bg-emerald-500" title="Low Risk: 245 Batches"></div>
            <div style={{ width: '24.3%' }} className="bg-amber-400" title="Moderate Risk: 83 Batches"></div>
            <div style={{ width: '4.1%' }} className="bg-rose-500 animate-pulse" title="High Risk: 14 Batches"></div>
          </div>
          <div className="flex items-center justify-between text-[11px] text-slate-500 mt-2">
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> Low Risk (245)</span>
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-amber-400"></span> Moderate (83)</span>
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span> High Risk (14)</span>
          </div>
        </div>

        {/* Top Critical Spoilage Batches List */}
        <div className="space-y-3">
          <p className="text-xs font-bold text-slate-800 uppercase tracking-wider">Critical Immediate Action Needed</p>
          {HIGH_RISK_SPOILAGE_BATCHES.slice(0, 2).map((batch) => (
            <div key={batch.id} className="p-3 bg-rose-50/60 border border-rose-200/80 rounded-xl">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0" />
                  <span className="text-xs font-bold text-slate-900">{batch.crop}</span>
                  <span className="text-[10px] font-mono text-slate-500">({batch.batchId})</span>
                </div>
                <span className="text-xs font-black text-rose-600 bg-rose-100 px-2 py-0.5 rounded-md">
                  Risk: {batch.riskScore}%
                </span>
              </div>
              <p className="text-[11px] text-slate-600 mt-1">{batch.reason}</p>
              <div className="mt-2 pt-2 border-t border-rose-200/50 flex items-center justify-between text-[10px]">
                <span className="text-rose-700 font-bold">Remaining: {batch.shelfLifeRemaining}</span>
                <span className="text-slate-600 italic">{batch.recommendedAction}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
