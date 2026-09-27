import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

export const StatCard = ({ title, value, subtext, icon: Icon, trend, trendType = 'positive', accentColor = 'emerald' }) => {
  const accentClasses = {
    emerald: 'bg-emerald-50 text-emerald-600 border-emerald-100',
    amber: 'bg-amber-50 text-amber-600 border-amber-100',
    rose: 'bg-rose-50 text-rose-600 border-rose-100',
    blue: 'bg-blue-50 text-blue-600 border-blue-100',
    purple: 'bg-purple-50 text-purple-600 border-purple-100',
  };

  return (
    <div className="bg-white rounded-xl p-5 border border-slate-200/80 shadow-xs hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">{title}</span>
        {Icon && (
          <div className={`p-2.5 rounded-lg border ${accentClasses[accentColor] || accentClasses.emerald}`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>
      <div className="mt-3 flex items-baseline justify-between">
        <span className="text-2xl font-bold tracking-tight text-slate-900">{value}</span>
      </div>
      {subtext && (
        <div className="mt-2 flex items-center gap-1.5 text-xs">
          {trend && (
            <span className={`inline-flex items-center font-medium ${trendType === 'positive' ? 'text-emerald-600' : 'text-rose-600'}`}>
              {trendType === 'positive' ? <TrendingUp className="w-3.5 h-3.5 mr-0.5" /> : <TrendingDown className="w-3.5 h-3.5 mr-0.5" />}
              {trend}
            </span>
          )}
          <span className="text-slate-500">{subtext}</span>
        </div>
      )}
    </div>
  );
};
