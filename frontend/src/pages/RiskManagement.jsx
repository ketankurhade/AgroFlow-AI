import React, { useState, useEffect } from 'react';
import { Badge } from '../components/common/Badge';
import {
  AlertTriangle,
  Flame,
  Thermometer,
  Droplets,
  Clock,
  CheckCircle2,
  RefreshCw,
  Loader2,
  AlertCircle,
  ArrowRight,
  Info,
  BrainCircuit,
  Sparkles,
  ShieldCheck,
  ShieldAlert,
} from 'lucide-react';
import { spoilageAPI } from '../services/api';
import { useNavigate } from 'react-router-dom';

export const RiskManagement = () => {
  const navigate = useNavigate();
  const [riskData, setRiskData] = useState([]);
  const [summary, setSummary] = useState(null);
  const [mlSummary, setMlSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeFilter, setActiveFilter] = useState('All');

  // Interactive ML Predictor state
  const [mlPredictInput, setMlPredictInput] = useState({
    product_name: 'Mango',
    category: 'Fruits',
    day_of_week: 2,
    month: 6,
    season: 'Summer',
    temperature: 28.5,
    humidity: 78.0,
    inventory_age_days: 10,
    remaining_shelf_life_days: 2,
    inventory_quantity_kg: 1200.0,
    historical_demand_kg: 1000.0,
    supply_quantity_kg: 1100.0,
  });
  const [mlPredictionResult, setMlPredictionResult] = useState(null);
  const [mlPredictLoading, setMlPredictLoading] = useState(false);

  const loadSpoilageData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [riskRes, summaryRes, mlSummaryRes] = await Promise.all([
        spoilageAPI.getRisk().catch(() => ({ data: [] })),
        spoilageAPI.getSummary().catch(() => ({ data: null })),
        spoilageAPI.getModelSummaryML().catch(() => ({ data: null })),
      ]);

      const items = riskRes.data || [];
      setSummary(summaryRes.data || null);
      setMlSummary(mlSummaryRes.data || null);

      // Enhance inventory rows with individual ML classification predictions
      const enhancedItems = await Promise.all(
        items.map(async (item) => {
          try {
            const mlRes = await spoilageAPI.predictML({
              product_name: item.product_name || 'Mango',
              category: item.category || 'Fruits',
              day_of_week: new Date().getDay(),
              month: new Date().getMonth() + 1,
              season: 'Summer',
              temperature: item.temperature ?? 22.0,
              humidity: item.humidity ?? 65.0,
              inventory_age_days: item.inventory_age_days ?? 5,
              remaining_shelf_life_days: item.remaining_shelf_life_days ?? 10,
              inventory_quantity_kg: item.quantity ?? 1000.0,
              historical_demand_kg: (item.quantity ?? 1000.0) * 0.9,
              supply_quantity_kg: (item.quantity ?? 1000.0) * 1.05,
            });
            return { ...item, ml_prediction: mlRes.data };
          } catch {
            return { ...item, ml_prediction: null };
          }
        })
      );

      setRiskData(enhancedItems);
    } catch (err) {
      console.error("Error loading spoilage risk intelligence:", err);
      setError("Failed to fetch spoilage risk data from backend service.");
    } finally {
      setLoading(false);
    }
  };

  const handleCustomMlPredict = async () => {
    setMlPredictLoading(true);
    try {
      const res = await spoilageAPI.predictML(mlPredictInput);
      setMlPredictionResult(res.data);
    } catch (err) {
      console.error("Custom ML Prediction error:", err);
    } finally {
      setMlPredictLoading(false);
    }
  };

  useEffect(() => {
    loadSpoilageData();
  }, []);

  const filteredItems = riskData.filter((item) => {
    if (activeFilter === 'All') return true;
    if (activeFilter === 'High Risk') return item.risk_level === 'High';
    if (activeFilter === 'Medium Risk') return item.risk_level === 'Medium';
    if (activeFilter === 'Low Risk') return item.risk_level === 'Low';
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Dual Header Banner: Rule-Based + ML Intelligence */}
      <div className="bg-slate-900 text-white rounded-2xl p-6 shadow-md border border-slate-800 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
        <div className="space-y-2 max-w-3xl">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="bg-rose-500 text-white text-[10px] font-black uppercase px-2.5 py-0.5 rounded-full flex items-center gap-1">
              <Flame className="w-3 h-3" /> Rule-Based Engine
            </span>
            <span className="bg-emerald-500 text-slate-950 text-[10px] font-black uppercase px-2.5 py-0.5 rounded-full flex items-center gap-1">
              <BrainCircuit className="w-3 h-3" /> Part 4.6 ML Classification
            </span>
            <span className="bg-slate-800 text-slate-300 text-[10px] font-medium px-2.5 py-0.5 rounded-full border border-slate-700">
              Synthetic Demonstration
            </span>
          </div>
          <h2 className="text-xl font-black tracking-tight text-white">
            Dual Spoilage Intelligence: Heuristics + Random Forest ML
          </h2>
          <p className="text-xs text-slate-300 leading-relaxed">
            Combining deterministic Rule-Based risk analysis with a binary ML Classification Model (RandomForestClassifier).
            Rule-based score calculates cumulative ambient decay, while ML calculates probability of batch spoilage based on 4,000 synthetic observations.
          </p>
        </div>

        <button
          onClick={loadSpoilageData}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2.5 bg-emerald-500 hover:bg-emerald-400 text-slate-950 rounded-xl text-xs font-black transition-all shadow-sm shrink-0 cursor-pointer disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Re-Evaluate All Lots</span>
        </button>
      </div>

      {/* Overview Cards: Rule-Based KPIs + ML Model Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Rule-Based KPI 1 */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs">
          <span className="text-slate-500 text-[10px] font-bold uppercase tracking-wider">Total Inventory Analyzed</span>
          <p className="text-3xl font-black text-slate-900 mt-1">{summary ? summary.total_analyzed : 0} Lots</p>
          <p className="text-[11px] text-slate-500 mt-1">PostgreSQL Live Records</p>
        </div>

        {/* Rule-Based KPI 2 */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs">
          <span className="text-slate-500 text-[10px] font-bold uppercase tracking-wider">Rule-Based High Risk</span>
          <p className="text-3xl font-black text-rose-600 mt-1">{summary ? summary.high_risk_count : 0} Batches</p>
          <p className="text-[11px] text-rose-600 font-semibold mt-1">Heuristic Score &ge; 60/100</p>
        </div>

        {/* ML Model Status KPI */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-slate-500 text-[10px] font-bold uppercase tracking-wider">ML Model Recall</span>
            <span className="text-[10px] font-black px-2 py-0.5 rounded bg-emerald-100 text-emerald-800">RandomForest</span>
          </div>
          <p className="text-3xl font-black text-emerald-600 mt-1">
            {mlSummary ? `${(mlSummary.model_metrics.recall * 100).toFixed(1)}%` : '80.3%'}
          </p>
          <p className="text-[11px] text-slate-500 mt-1">Key Safety Metric (ROC-AUC: {mlSummary ? mlSummary.model_metrics.roc_auc : '0.9154'})</p>
        </div>

        {/* ML Model Accuracy KPI */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs">
          <span className="text-slate-500 text-[10px] font-bold uppercase tracking-wider">ML Test Accuracy</span>
          <p className="text-3xl font-black text-indigo-600 mt-1">
            {mlSummary ? `${(mlSummary.model_metrics.accuracy * 100).toFixed(1)}%` : '84.5%'}
          </p>
          <p className="text-[11px] text-slate-500 mt-1">Chronological Test Split (800 records)</p>
        </div>
      </div>

      {/* Interactive ML Spoilage Predictor Card */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-3">
          <div>
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-indigo-600" />
              <h3 className="text-base font-bold text-slate-900">Interactive ML Spoilage Simulator</h3>
              <span className="text-[10px] font-extrabold uppercase px-2.5 py-0.5 rounded bg-indigo-100 text-indigo-800">
                RandomForestClassifier
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Simulate ambient storage parameters to get real-time ML spoilage classification probabilities.
            </p>
          </div>
          <span className="text-[11px] font-medium text-slate-400 italic">
            ML Prediction — Synthetic Demonstration
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3 text-xs">
          <div>
            <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Crop Product</label>
            <select
              value={mlPredictInput.product_name}
              onChange={(e) => {
                const prod = e.target.value;
                const cat = ['Mango', 'Banana', 'Grapes', 'Apple', 'Orange'].includes(prod) ? 'Fruits' : 'Vegetables';
                setMlPredictInput({ ...mlPredictInput, product_name: prod, category: cat });
              }}
              className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2 font-semibold text-slate-800"
            >
              <option value="Mango">Mango</option>
              <option value="Tomato">Tomato</option>
              <option value="Potato">Potato</option>
              <option value="Onion">Onion</option>
              <option value="Banana">Banana</option>
              <option value="Grapes">Grapes</option>
              <option value="Apple">Apple</option>
              <option value="Orange">Orange</option>
            </select>
          </div>

          <div>
            <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Temp (°C)</label>
            <input
              type="number"
              step="0.5"
              value={mlPredictInput.temperature}
              onChange={(e) => setMlPredictInput({ ...mlPredictInput, temperature: parseFloat(e.target.value) || 25.0 })}
              className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2 font-semibold text-slate-800"
            />
          </div>

          <div>
            <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Humidity (%)</label>
            <input
              type="number"
              step="1"
              value={mlPredictInput.humidity}
              onChange={(e) => setMlPredictInput({ ...mlPredictInput, humidity: parseFloat(e.target.value) || 65.0 })}
              className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2 font-semibold text-slate-800"
            />
          </div>

          <div>
            <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Age (Days)</label>
            <input
              type="number"
              value={mlPredictInput.inventory_age_days}
              onChange={(e) => setMlPredictInput({ ...mlPredictInput, inventory_age_days: parseInt(e.target.value) || 0 })}
              className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2 font-semibold text-slate-800"
            />
          </div>

          <div>
            <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Shelf Life Left</label>
            <input
              type="number"
              value={mlPredictInput.remaining_shelf_life_days}
              onChange={(e) => setMlPredictInput({ ...mlPredictInput, remaining_shelf_life_days: parseInt(e.target.value) || 0 })}
              className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2 font-semibold text-slate-800"
            />
          </div>

          <div className="flex items-end">
            <button
              onClick={handleCustomMlPredict}
              disabled={mlPredictLoading}
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-3 rounded-lg text-xs transition-colors flex items-center justify-center gap-1 cursor-pointer disabled:opacity-50"
            >
              {mlPredictLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <BrainCircuit className="w-3.5 h-3.5" />}
              <span>Predict ML</span>
            </button>
          </div>
        </div>

        {/* Simulator Prediction Output */}
        {mlPredictionResult && (
          <div className="mt-4 p-4 rounded-xl bg-slate-900 text-white flex flex-col sm:flex-row items-center justify-between gap-4 border border-slate-800">
            <div className="flex items-center gap-3">
              {mlPredictionResult.predicted_spoilage === 1 ? (
                <div className="p-3 bg-rose-500/20 text-rose-400 rounded-xl border border-rose-500/30">
                  <ShieldAlert className="w-6 h-6" />
                </div>
              ) : (
                <div className="p-3 bg-emerald-500/20 text-emerald-400 rounded-xl border border-emerald-500/30">
                  <ShieldCheck className="w-6 h-6" />
                </div>
              )}
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-slate-400">ML Classification Result:</span>
                  <span className={`text-xs font-black px-2 py-0.5 rounded ${
                    mlPredictionResult.predicted_spoilage === 1 ? 'bg-rose-500 text-white' : 'bg-emerald-500 text-slate-950'
                  }`}>
                    {mlPredictionResult.predicted_spoilage === 1 ? 'Spoilage Risk Detected' : 'Healthy Batch'}
                  </span>
                </div>
                <p className="text-sm font-bold mt-0.5">
                  Spoilage Probability: <span className="text-rose-400">{(mlPredictionResult.spoilage_probability * 100).toFixed(1)}%</span>
                  {' | '}
                  Healthy Probability: <span className="text-emerald-400">{(mlPredictionResult.healthy_probability * 100).toFixed(1)}%</span>
                </p>
              </div>
            </div>
            <span className="text-[10px] text-slate-400 italic shrink-0">
              Model: {mlPredictionResult.model_name}
            </span>
          </div>
        )}
      </div>

      {/* Filter Tabs */}
      <div className="bg-white p-4 rounded-xl border border-slate-200/80 flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-xs">
        <div className="flex items-center gap-1.5 overflow-x-auto">
          {['All', 'High Risk', 'Medium Risk', 'Low Risk'].map((filter) => (
            <button
              key={filter}
              onClick={() => setActiveFilter(filter)}
              className={`px-3.5 py-1.5 text-xs font-bold rounded-lg transition-colors cursor-pointer whitespace-nowrap ${
                activeFilter === filter
                  ? 'bg-slate-900 text-white shadow-2xs'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {filter}
            </button>
          ))}
        </div>

        <div className="text-[11px] text-slate-400 italic flex items-center gap-1">
          <Info className="w-3.5 h-3.5 text-slate-400 shrink-0" />
          <span>Rule-Based Score (0-100) and ML Spoilage Probability presented side-by-side.</span>
        </div>
      </div>

      {/* Main Table */}
      {loading ? (
        <div className="p-12 rounded-2xl bg-white border border-slate-200/80 shadow-xs flex flex-col items-center justify-center text-slate-500 gap-3">
          <Loader2 className="w-8 h-8 animate-spin text-rose-600" />
          <p className="text-xs font-semibold text-slate-700">Evaluating spoilage intelligence across PostgreSQL inventory lots...</p>
        </div>
      ) : filteredItems.length === 0 ? (
        <div className="p-12 rounded-2xl bg-white border border-slate-200/80 text-center text-slate-500 text-xs shadow-xs space-y-2">
          <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto" />
          <p className="font-bold text-slate-800 text-sm">
            {activeFilter !== 'All' ? `No inventory lots found under "${activeFilter}" category.` : 'No spoilage risk records for your produce yet.'}
          </p>
          <p className="text-slate-500">All cold storage inventory lots are operating within safe parameters.</p>
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
          <div className="p-4 border-b border-slate-200 flex items-center justify-between">
            <h3 className="text-base font-bold text-slate-900">
              Evaluated Inventory Lots ({filteredItems.length})
            </h3>
            <span className="text-xs text-slate-500 font-medium">Sorted by Rule-Based Risk Score</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold uppercase text-[10px]">
                <tr>
                  <th className="py-3 px-4">Batch / Crop</th>
                  <th className="py-3 px-4">Warehouse Location</th>
                  <th className="py-3 px-4">Rule-Based Risk Score</th>
                  <th className="py-3 px-4">ML Spoilage Probability</th>
                  <th className="py-3 px-4">Contributing Factors (Why)</th>
                  <th className="py-3 px-4">Shelf Life Left</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredItems.map((item) => (
                  <tr
                    key={item.inventory_id}
                    className={`hover:bg-slate-50 transition-colors ${
                      item.risk_level === 'High' ? 'bg-rose-50/20' : ''
                    }`}
                  >
                    <td className="py-4 px-4 font-bold text-slate-900">
                      <div>
                        <p>{item.product_name}</p>
                        <p className="font-mono text-[10px] text-slate-500">{item.batch_code}</p>
                        <span className="text-[10px] text-slate-400 font-normal">Qty: {item.quantity} kg</span>
                      </div>
                    </td>
                    <td className="py-4 px-4 text-slate-700 font-medium">{item.warehouse_location}</td>
                    
                    {/* Part 4.2 Rule-Based Risk Score */}
                    <td className="py-4 px-4">
                      <div className="space-y-1">
                        <span
                          className={`font-black text-xs px-2.5 py-1 rounded-md inline-block ${
                            item.risk_level === 'High'
                              ? 'bg-rose-100 text-rose-800'
                              : item.risk_level === 'Medium'
                              ? 'bg-amber-100 text-amber-800'
                              : 'bg-emerald-100 text-emerald-800'
                          }`}
                        >
                          {item.risk_score}/100 ({item.risk_level})
                        </span>
                        <div className="w-20 bg-slate-200 h-1.5 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full ${
                              item.risk_level === 'High'
                                ? 'bg-rose-600'
                                : item.risk_level === 'Medium'
                                ? 'bg-amber-500'
                                : 'bg-emerald-500'
                            }`}
                            style={{ width: `${item.risk_score}%` }}
                          />
                        </div>
                      </div>
                    </td>

                    {/* Part 4.6 ML Spoilage Classifier Probability */}
                    <td className="py-4 px-4">
                      {item.ml_prediction ? (
                        <div className="space-y-1">
                          <div className="flex items-center gap-1.5">
                            <span className={`font-black text-xs px-2.5 py-1 rounded-md inline-block ${
                              item.ml_prediction.predicted_spoilage === 1
                                ? 'bg-rose-600 text-white'
                                : 'bg-emerald-100 text-emerald-800'
                            }`}>
                              {(item.ml_prediction.spoilage_probability * 100).toFixed(1)}% ML Prob
                            </span>
                          </div>
                          <p className="text-[10px] font-semibold text-slate-500">
                            Class: {item.ml_prediction.predicted_spoilage === 1 ? 'Spoilage Risk' : 'Healthy'}
                          </p>
                          <span className="text-[9px] text-slate-400 block italic">
                            ML Prediction — Synthetic Demo
                          </span>
                        </div>
                      ) : (
                        <span className="text-[10px] text-slate-400 italic">ML Evaluating...</span>
                      )}
                    </td>

                    <td className="py-4 px-4 text-slate-700 max-w-xs space-y-1">
                      {item.factors && item.factors.length > 0 ? (
                        item.factors.map((f, idx) => (
                          <div key={idx} className="text-[11px] leading-tight flex items-start gap-1 text-slate-700">
                            <span className="font-semibold text-slate-900 shrink-0">• {f.factor} (+{f.impact}pt):</span>
                            <span className="text-slate-600">{f.message}</span>
                          </div>
                        ))
                      ) : (
                        <span className="text-emerald-600 font-semibold text-[11px]">No risk triggers detected</span>
                      )}
                    </td>
                    <td className="py-4 px-4">
                      <div className="text-[11px]">
                        <span
                          className={`font-bold ${
                            item.remaining_shelf_life_days <= 2
                              ? 'text-rose-600'
                              : item.remaining_shelf_life_days <= 5
                              ? 'text-amber-600'
                              : 'text-emerald-700'
                          }`}
                        >
                          {item.remaining_shelf_life_days <= 0
                            ? 'EXPIRED'
                            : `${item.remaining_shelf_life_days} Days Left`}
                        </span>
                        <p className="text-[10px] text-slate-400">Expires: {item.expiry_date}</p>
                      </div>
                    </td>
                    <td className="py-4 px-4 text-right">
                      <button
                        onClick={() => navigate('/routes')}
                        className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-bold transition-all shadow-xs cursor-pointer shrink-0 inline-flex items-center gap-1"
                      >
                        Dispatch <ArrowRight className="w-3 h-3" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
