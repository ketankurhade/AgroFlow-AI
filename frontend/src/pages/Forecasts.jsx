import React, { useState } from 'react';
import { DemandForecastChart } from '../components/dashboard/DemandForecastChart';
import { PriceForecastChart } from '../components/dashboard/PriceForecastChart';
import { TrendingUp, Cpu, Calendar, BarChart2, ShieldCheck, Zap } from 'lucide-react';

export const Forecasts = () => {
  const [activeTab, setActiveTab] = useState('demand');

  return (
    <div className="space-y-6">
      {/* AI Engine Status Banner */}
      <div className="bg-gradient-to-r from-slate-900 to-slate-800 text-white rounded-2xl p-6 shadow-md border border-slate-700/80 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Cpu className="w-5 h-5 text-emerald-400" />
            <h2 className="text-lg font-bold">AgroFlow Predictive AI Analytics Hub</h2>
          </div>
          <p className="text-xs text-slate-300 mt-1">
            Machine-learning pipeline ready for FastAPI integration. Forecasting regional crop demand & APMC market prices.
          </p>
        </div>
        <div className="flex items-center gap-3 text-xs shrink-0">
          <div className="bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700 text-center">
            <span className="text-slate-400 block text-[10px]">Model Accuracy</span>
            <span className="font-bold text-emerald-400">94.8% R² Score</span>
          </div>
          <div className="bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700 text-center">
            <span className="text-slate-400 block text-[10px]">Forecast Horizon</span>
            <span className="font-bold text-blue-400">90 Days Forward</span>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-200 pb-2">
        <button
          onClick={() => setActiveTab('demand')}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
            activeTab === 'demand'
              ? 'bg-emerald-600 text-white shadow-xs'
              : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
          }`}
        >
          <TrendingUp className="w-4 h-4" /> Demand Volume Forecast
        </button>
        <button
          onClick={() => setActiveTab('price')}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
            activeTab === 'price'
              ? 'bg-emerald-600 text-white shadow-xs'
              : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
          }`}
        >
          <BarChart2 className="w-4 h-4" /> Price Volatility & Trend Forecast
        </button>
      </div>

      {/* Main Chart Section */}
      <div className="grid grid-cols-1 gap-6">
        {activeTab === 'demand' ? <DemandForecastChart /> : <PriceForecastChart />}
      </div>

      {/* ML Insights Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs">
          <div className="flex items-center gap-2 text-emerald-700 font-bold text-xs mb-2">
            <Zap className="w-4 h-4" /> Weather & Monsoon Impact
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            Upcoming unseasonal rains in Western Maharashtra expected to reduce tomato yield by ~12%, driving local price surge in September.
          </p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs">
          <div className="flex items-center gap-2 text-blue-700 font-bold text-xs mb-2">
            <Calendar className="w-4 h-4" /> Seasonal Festival Spike
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            Ganesh Chaturthi festival in mid-September projected to boost mango and fruit demand by +45% across urban retail centers.
          </p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs">
          <div className="flex items-center gap-2 text-purple-700 font-bold text-xs mb-2">
            <ShieldCheck className="w-4 h-4" /> Optimal Harvest Window
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            AI recommends harvesting Ratnagiri Alphonso crop between Sep 28–Oct 02 to maximize market clearing price before regional oversupply.
          </p>
        </div>
      </div>
    </div>
  );
};
