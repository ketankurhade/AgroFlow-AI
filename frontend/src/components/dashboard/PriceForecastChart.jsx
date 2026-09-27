import React from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from 'recharts';
import { PRICE_FORECAST_DATA } from '../../data/mockData';
import { DollarSign, AlertCircle } from 'lucide-react';

export const PriceForecastChart = () => {
  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs flex flex-col justify-between">
      <div className="flex items-center justify-between mb-4">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-base font-bold text-slate-900">Wholesale Price Trend & Prediction</h3>
            <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700">
              Tomatoes (₹/kg) — Demo Trend
            </span>
          </div>
          <p className="text-xs text-slate-500">Actual APMC prices vs predicted bounds with 90% CI</p>
        </div>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={PRICE_FORECAST_DATA} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis dataKey="week" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
            <YAxis domain={[30, 75]} tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
            <Tooltip
              contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
            />
            <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
            
            {/* Confidence Interval Area */}
            <Area
              type="monotone"
              dataKey="upperBound"
              stroke="none"
              fill="#cbd5e1"
              fillOpacity={0.25}
              name="Upper Price Bound (₹)"
            />
            <Area
              type="monotone"
              dataKey="lowerBound"
              stroke="none"
              fill="#fff"
              fillOpacity={1.0}
            />

            {/* Actual Price */}
            <Line
              type="monotone"
              dataKey="actualPrice"
              stroke="#0f172a"
              strokeWidth={3}
              dot={{ r: 4, fill: '#0f172a' }}
              name="Actual Market Price"
              connectNulls={false}
            />

            {/* Predicted Price */}
            <Line
              type="monotone"
              dataKey="predictedPrice"
              stroke="#2563eb"
              strokeWidth={2.5}
              strokeDasharray="5 5"
              dot={{ r: 4, fill: '#2563eb' }}
              name="Predicted Price Trend"
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
        <span className="flex items-center gap-1.5 text-amber-700 font-medium">
          <AlertCircle className="w-3.5 h-3.5" />
          Price Peak Expected W2 Sep (₹62/kg)
        </span>
        <span className="text-slate-400">APMC Lasalgaon Benchmark</span>
      </div>
    </div>
  );
};
