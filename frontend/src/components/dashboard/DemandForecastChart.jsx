import React, { useState } from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from 'recharts';
import { DEMAND_FORECAST_DATA } from '../../data/mockData';
import { TrendingUp, Filter } from 'lucide-react';

export const DemandForecastChart = () => {
  const [selectedCrop, setSelectedCrop] = useState('Tomatoes');

  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs flex flex-col justify-between">
      <div className="flex items-center justify-between mb-4">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-base font-bold text-slate-900">Crop Demand Forecast</h3>
            <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 flex items-center gap-1">
              <TrendingUp className="w-3 h-3 text-amber-600" /> Demo Forecast Data
            </span>
          </div>
          <p className="text-xs text-slate-500">Historical demand vs 3-month forward forecast (in Tons)</p>
        </div>

        {/* Filter selector */}
        <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-lg border border-slate-200">
          {['Tomatoes', 'Mangoes', 'Potatoes', 'Onions'].map((crop) => (
            <button
              key={crop}
              onClick={() => setSelectedCrop(crop)}
              className={`px-2.5 py-1 text-xs font-semibold rounded-md transition-colors cursor-pointer ${
                selectedCrop === crop ? 'bg-white text-emerald-700 shadow-2xs' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              {crop}
            </button>
          ))}
        </div>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={DEMAND_FORECAST_DATA} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="colorDemand" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
            <Tooltip
              contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
              itemStyle={{ color: '#34d399' }}
            />
            <Area
              type="monotone"
              dataKey={selectedCrop}
              stroke="#10b981"
              strokeWidth={2.5}
              fillOpacity={1}
              fill="url(#colorDemand)"
              name={`${selectedCrop} Demand (Tons)`}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
        <span>Confidence Index: <strong className="text-slate-800 font-semibold">94.8% Accuracy</strong></span>
        <span>Predicted Demand Peak: <strong className="text-emerald-700 font-bold">720 Tons (July)</strong></span>
      </div>
    </div>
  );
};
