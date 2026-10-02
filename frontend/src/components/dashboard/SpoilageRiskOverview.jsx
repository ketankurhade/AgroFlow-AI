import React, { useState, useEffect } from 'react';
import { AlertTriangle, ArrowUpRight, Flame, Loader2 } from 'lucide-react';
import { Link } from 'react-router-dom';
import { spoilageAPI } from '../../services/api';

export const SpoilageRiskOverview = () => {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    spoilageAPI
      .getSummary()
      .then((res) => setSummary(res.data))
      .catch((err) => console.error("Error loading spoilage summary widget:", err))
      .finally(() => setLoading(false));
  }, []);

  const total = summary?.total_analyzed || 0;
  const low = summary?.low_risk_count || 0;
  const med = summary?.medium_risk_count || 0;
  const high = summary?.high_risk_count || 0;

  const lowPct = total > 0 ? ((low / total) * 100).toFixed(1) : '100';
  const medPct = total > 0 ? ((med / total) * 100).toFixed(1) : '0';
  const highPct = total > 0 ? ((high / total) * 100).toFixed(1) : '0';

  const criticalBatches = summary?.highest_risk_batches ? summary.highest_risk_batches.slice(0, 2) : [];

  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-bold text-slate-900">Spoilage-Risk Overview</h3>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-rose-100 text-rose-800 flex items-center gap-1">
                <Flame className="w-3 h-3 text-rose-600" /> {high} High Risk
              </span>
            </div>
            <p className="text-xs text-slate-500">PostgreSQL rule-based shelf life decay & ambient alert monitor</p>
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
            <span className="text-slate-400">{total} Total Evaluated Lots</span>
          </div>
          <div className="h-3.5 w-full bg-slate-100 rounded-full overflow-hidden flex">
            <div style={{ width: `${lowPct}%` }} className="bg-emerald-500" title={`Low Risk: ${low} Lots`}></div>
            <div style={{ width: `${medPct}%` }} className="bg-amber-400" title={`Moderate Risk: ${med} Lots`}></div>
            <div style={{ width: `${highPct}%` }} className="bg-rose-500 animate-pulse" title={`High Risk: ${high} Lots`}></div>
          </div>
          <div className="flex items-center justify-between text-[11px] text-slate-500 mt-2">
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> Low Risk ({low})</span>
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-amber-400"></span> Moderate ({med})</span>
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span> High Risk ({high})</span>
          </div>
        </div>

        {/* Top Critical Spoilage Batches List */}
        <div className="space-y-3">
          <p className="text-xs font-bold text-slate-800 uppercase tracking-wider">Critical Immediate Action Needed</p>
          {loading ? (
            <div className="p-4 flex items-center justify-center text-slate-400 text-xs">
              <Loader2 className="w-4 h-4 animate-spin text-emerald-600 mr-2" /> Evaluating risk rules...
            </div>
          ) : criticalBatches.length === 0 ? (
            <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-xs text-emerald-800">
              ✅ All inventory lots are currently within safe spoilage thresholds.
            </div>
          ) : (
            criticalBatches.map((batch) => (
              <div key={batch.inventory_id} className="p-3 bg-rose-50/60 border border-rose-200/80 rounded-xl space-y-1">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0" />
                    <span className="text-xs font-bold text-slate-900">{batch.product_name}</span>
                    <span className="text-[10px] font-mono text-slate-500">({batch.batch_code})</span>
                  </div>
                  <span className="text-xs font-black text-rose-600 bg-rose-100 px-2 py-0.5 rounded-md">
                    Risk: {batch.risk_score}%
                  </span>
                </div>
                <p className="text-[11px] text-slate-600">
                  {batch.factors && batch.factors.length > 0 ? batch.factors[0].message : 'High spoilage risk detected.'}
                </p>
                <div className="pt-1.5 border-t border-rose-200/50 flex items-center justify-between text-[10px]">
                  <span className="text-rose-700 font-bold">Remaining: {batch.remaining_shelf_life_days} Days</span>
                  <span className="text-slate-600 italic">{batch.recommendation}</span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
