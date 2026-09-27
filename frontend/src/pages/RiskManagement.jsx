import React, { useState } from 'react';
import { HIGH_RISK_SPOILAGE_BATCHES, INVENTORY_ITEMS } from '../data/mockData';
import { Badge } from '../components/common/Badge';
import { AlertTriangle, ShieldAlert, Thermometer, Droplets, CheckCircle2, RefreshCw, Flame } from 'lucide-react';

export const RiskManagement = () => {
  const [activeFilter, setActiveFilter] = useState('All');

  const riskItems = INVENTORY_ITEMS.filter((item) => item.spoilageRiskScore > 15);

  return (
    <div className="space-y-6">
      {/* Risk Alert Banner */}
      <div className="bg-rose-50 border border-rose-200 rounded-2xl p-6 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-rose-600 text-white rounded-xl shadow-xs shrink-0">
            <Flame className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-bold text-slate-900">Critical Spoilage Alert Engine</h2>
              <span className="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded bg-rose-200 text-rose-800">
                14 Batches Flagged
              </span>
            </div>
            <p className="text-xs text-slate-600 mt-1">
              AI sensor algorithms detected respiration spikes & temperature anomalies. Immediate rerouting recommended to prevent loss of ₹4.8 Lakhs.
            </p>
          </div>
        </div>
      </div>

      {/* Sensor Telemetry Threshold Indicators */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200/80">
          <span className="text-slate-500 text-[10px] font-bold uppercase">Temp Threshold</span>
          <p className="text-xl font-black text-slate-900 mt-1">Max 12°C</p>
          <p className="text-[11px] text-amber-600 font-semibold mt-0.5">2 Facilities Above Limit</p>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200/80">
          <span className="text-slate-500 text-[10px] font-bold uppercase">Ethylene Gas Level</span>
          <p className="text-xl font-black text-slate-900 mt-1">4.2 ppm</p>
          <p className="text-[11px] text-emerald-600 font-semibold mt-0.5">Ventilation Cycle Active</p>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200/80">
          <span className="text-slate-500 text-[10px] font-bold uppercase">Humidity Level</span>
          <p className="text-xl font-black text-slate-900 mt-1">88% RH</p>
          <p className="text-[11px] text-slate-500 mt-0.5">Optimal Range: 85-92%</p>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200/80">
          <span className="text-slate-500 text-[10px] font-bold uppercase">Waste Prevented</span>
          <p className="text-xl font-black text-emerald-600 mt-1">42.8 Tons</p>
          <p className="text-[11px] text-slate-500 mt-0.5">This Month via AgroFlow</p>
        </div>
      </div>

      {/* High Risk Batches Action Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
        <div className="p-4 border-b border-slate-200 flex items-center justify-between">
          <h3 className="text-base font-bold text-slate-900">Flagged Batches Requiring Mitigation</h3>
          <span className="text-xs text-slate-500 font-medium">Sorted by Risk Score (Descending)</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold uppercase text-[10px]">
              <tr>
                <th className="py-3 px-4">Batch / Crop</th>
                <th className="py-3 px-4">Current Hub Location</th>
                <th className="py-3 px-4">Risk Level</th>
                <th className="py-3 px-4">Detected Root Cause</th>
                <th className="py-3 px-4">Shelf Life Left</th>
                <th className="py-3 px-4">AI Recommended Action</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {HIGH_RISK_SPOILAGE_BATCHES.map((batch) => (
                <tr key={batch.id} className="hover:bg-rose-50/30 transition-colors">
                  <td className="py-3.5 px-4 font-bold text-slate-900">
                    <div>
                      <p>{batch.crop}</p>
                      <p className="font-mono text-[10px] text-slate-500">{batch.batchId}</p>
                    </div>
                  </td>
                  <td className="py-3.5 px-4 text-slate-700">{batch.location}</td>
                  <td className="py-3.5 px-4">
                    <span className="font-extrabold text-rose-600 bg-rose-100 px-2 py-0.5 rounded text-xs">
                      {batch.riskScore}% ({batch.riskLevel})
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-slate-600 max-w-xs">{batch.reason}</td>
                  <td className="py-3.5 px-4 font-bold text-rose-600">{batch.shelfLifeRemaining}</td>
                  <td className="py-3.5 px-4 text-slate-700 italic max-w-xs">{batch.recommendedAction}</td>
                  <td className="py-3.5 px-4 text-right">
                    <button className="px-3 py-1.5 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-xs font-bold transition-colors cursor-pointer">
                      Dispatch Now
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
