import React from 'react';
import { useNavigate } from 'react-router-dom';
import { RefreshCw, UserCheck } from 'lucide-react';

export const RoleDashboardHeader = ({ title, subtitle, user, onRefresh, quickActions = [] }) => {
  const navigate = useNavigate();

  return (
    <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs space-y-4">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 flex-wrap mb-1">
            <h1 className="text-xl font-extrabold text-slate-900 tracking-tight">{title}</h1>
            {user?.role && (
              <span className="inline-flex items-center gap-1 text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200 capitalize">
                <UserCheck className="w-3 h-3 text-emerald-600" />
                {user.role.replace('_', ' ')}
              </span>
            )}
          </div>
          <p className="text-xs text-slate-500 max-w-2xl">{subtitle}</p>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          {onRefresh && (
            <button
              onClick={onRefresh}
              className="p-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-600 text-xs font-semibold transition-all cursor-pointer"
              title="Refresh Dashboard Data"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Role Quick Actions */}
      {quickActions.length > 0 && (
        <div className="pt-3 border-t border-slate-100 flex items-center gap-2 flex-wrap">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mr-1">
            Quick Actions:
          </span>
          {quickActions.map((action, idx) => {
            const Icon = action.icon;
            return (
              <button
                key={idx}
                onClick={() => {
                  if (action.path) navigate(action.path);
                  if (action.onClick) action.onClick();
                }}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                  action.primary
                    ? 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-xs'
                    : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
                }`}
              >
                {Icon && <Icon className="w-3.5 h-3.5" />}
                <span>{action.label}</span>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
};
