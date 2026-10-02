import React, { useState, useEffect } from 'react';
import { BrainCircuit, Sparkles, AlertTriangle, ArrowRight, ShieldCheck, ShieldAlert, Loader2 } from 'lucide-react';
import { intelligenceAPI } from '../../services/api';
import { useNavigate } from 'react-router-dom';

export const IntelligenceDecisionWidget = () => {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [product, setProduct] = useState('Mango');

  const fetchIntelligence = async (selectedProduct) => {
    setLoading(true);
    try {
      const payload = {
        product_name: selectedProduct,
        category: ['Mango', 'Banana', 'Grapes', 'Apple', 'Orange'].includes(selectedProduct) ? 'Fruits' : 'Vegetables',
        temperature: selectedProduct === 'Mango' ? 28.5 : 22.0,
        humidity: 75.0,
        inventory_age_days: 8,
        remaining_shelf_life_days: 3,
        inventory_quantity_kg: 1200.0,
        historical_demand_kg: 1400.0,
        supply_quantity_kg: 1100.0,
        day_of_week: 2,
        month: 6,
        season: 'Summer',
      };
      const res = await intelligenceAPI.analyze(payload);
      setData(res.data);
    } catch (err) {
      console.error("Error fetching intelligence analysis:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIntelligence(product);
  }, [product]);

  return (
    <div className="bg-slate-900 text-white rounded-2xl p-6 border border-slate-800 shadow-md space-y-5">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <BrainCircuit className="w-5 h-5 text-emerald-400" />
            <h3 className="text-base font-black tracking-tight text-white">AgroFlow Decision Layer</h3>
            <span className="text-[10px] font-black uppercase px-2.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              Part 4.7 Multi-Module Orchestrator
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Operational recommendations synthesized from Demand ML, Price ML, Rule-Based Risk, and ML Spoilage Classifier.
          </p>
        </div>

        {/* Product selector */}
        <select
          value={product}
          onChange={(e) => setProduct(e.target.value)}
          className="bg-slate-800 text-slate-200 border border-slate-700 rounded-xl px-3 py-1.5 text-xs font-bold shrink-0 cursor-pointer"
        >
          <option value="Mango">Crop: Mango</option>
          <option value="Tomato">Crop: Tomato</option>
          <option value="Potato">Crop: Potato</option>
          <option value="Onion">Crop: Onion</option>
          <option value="Banana">Crop: Banana</option>
          <option value="Grapes">Crop: Grapes</option>
          <option value="Apple">Crop: Apple</option>
          <option value="Orange">Crop: Orange</option>
        </select>
      </div>

      {loading ? (
        <div className="p-8 flex items-center justify-center text-slate-400 text-xs">
          <Loader2 className="w-5 h-5 animate-spin text-emerald-400 mr-2" /> Orchestrating backend intelligence modules...
        </div>
      ) : data ? (
        <div className="space-y-4">
          {/* 4 Multi-Module Signals */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {/* Demand Signal */}
            <div className="bg-slate-800/80 p-3.5 rounded-xl border border-slate-700/80">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Demand Forecast</span>
              <p className="text-lg font-black text-emerald-400 mt-0.5">{data.demand.predicted_demand_kg} kg</p>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 inline-block mt-1">
                {data.demand.signal} DEMAND
              </span>
            </div>

            {/* Price Signal */}
            <div className="bg-slate-800/80 p-3.5 rounded-xl border border-slate-700/80">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Price Forecast</span>
              <p className="text-lg font-black text-blue-400 mt-0.5">₹{data.price.predicted_price_per_kg}/kg</p>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-blue-950 text-blue-400 border border-blue-800 inline-block mt-1">
                {data.price.signal}
              </span>
            </div>

            {/* Rule-Based Risk */}
            <div className="bg-slate-800/80 p-3.5 rounded-xl border border-slate-700/80">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Rule-Based Spoilage</span>
              <p className="text-lg font-black text-amber-400 mt-0.5">{data.rule_based_spoilage.risk_score} / 100</p>
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded inline-block mt-1 ${
                data.rule_based_spoilage.risk_level === 'High' ? 'bg-rose-950 text-rose-400 border border-rose-800' : 'bg-amber-950 text-amber-400 border border-amber-800'
              }`}>
                {data.rule_based_spoilage.risk_level.toUpperCase()} RISK
              </span>
            </div>

            {/* ML Spoilage Probability */}
            <div className="bg-slate-800/80 p-3.5 rounded-xl border border-slate-700/80">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">ML Spoilage Prob</span>
              <p className="text-lg font-black text-rose-400 mt-0.5">{(data.ml_spoilage.spoilage_probability * 100).toFixed(1)}%</p>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-rose-950 text-rose-400 border border-rose-800 inline-block mt-1">
                {data.ml_spoilage.predicted_spoilage === 1 ? 'SPOILED CLASS' : 'HEALTHY CLASS'}
              </span>
            </div>
          </div>

          {/* Synthesized Recommendation Banner */}
          <div className="bg-slate-800 p-4 rounded-xl border border-slate-700 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-slate-400">Synthesized Priority:</span>
                <span className={`text-xs font-black px-2.5 py-0.5 rounded ${
                  data.decision.priority === 'CRITICAL' ? 'bg-rose-500 text-white' : data.decision.priority === 'HIGH' ? 'bg-amber-500 text-slate-950' : 'bg-emerald-500 text-slate-950'
                }`}>
                  {data.decision.priority}
                </span>
              </div>
              <p className="text-sm font-bold text-white leading-tight">
                Recommended Action: <span className="text-emerald-400">{data.decision.recommendation}</span>
              </p>
              <div className="flex flex-wrap gap-2 mt-2">
                {data.decision.reasoning.map((r, idx) => (
                  <span key={idx} className="text-[10px] text-slate-300 bg-slate-900 px-2 py-0.5 rounded border border-slate-700">
                    • {r}
                  </span>
                ))}
              </div>
            </div>

            <button
              onClick={() => navigate('/risk')}
              className="px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-black rounded-xl transition-all flex items-center justify-center gap-1.5 cursor-pointer shrink-0"
            >
              <span>View Full Risk Engine</span> <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          <div className="text-[10px] text-slate-400 italic text-right">
            Note: Rule-Based Risk (0-100) &amp; ML Spoilage Probability are presented separately. {data.disclaimer}
          </div>
        </div>
      ) : null}
    </div>
  );
};
