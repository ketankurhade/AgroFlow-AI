import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Warehouse,
  Package,
  ShoppingCart,
  TrendingUp,
  AlertTriangle,
  Navigation,
  QrCode,
  Store,
  Sprout,
  Info
} from 'lucide-react';
import { METRICS } from '../../data/mockData';

export const Sidebar = () => {
  const navItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Inventory', path: '/inventory', icon: Warehouse },
    { name: 'Batches', path: '/batches', icon: Package },
    { name: 'Orders', path: '/orders', icon: ShoppingCart },
    { name: 'AI Forecasts', path: '/forecasts', icon: TrendingUp },
    {
      name: 'Risk Management',
      path: '/risk',
      icon: AlertTriangle,
      badge: METRICS.highRiskBatchesCount,
      badgeColor: 'bg-rose-500 text-white'
    },
    { name: 'Route Optimization', path: '/routes', icon: Navigation },
    { name: 'QR Traceability', path: '/traceability', icon: QrCode },
    { name: 'Marketplace', path: '/marketplace', icon: Store }
  ];

  return (
    <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col shrink-0 min-h-screen border-r border-slate-800">
      {/* Brand Logo */}
      <div className="p-5 border-b border-slate-800/80 flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-700 flex items-center justify-center text-white shadow-lg shadow-emerald-900/30">
          <Sprout className="w-6 h-6 stroke-[2.5]" />
        </div>
        <div>
          <div className="flex items-center gap-1.5">
            <h2 className="text-lg font-black tracking-tight text-white">AgroFlow</h2>
            <span className="text-[10px] font-bold px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 uppercase tracking-widest">
              AI
            </span>
          </div>
          <p className="text-[11px] text-slate-400 font-medium">Agri-Supply Intelligence</p>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        <p className="px-3 text-[10px] font-extrabold uppercase tracking-wider text-slate-500 mb-2">
          Supply Chain Core
        </p>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-all duration-150 ${
                  isActive
                    ? 'bg-emerald-600 text-white shadow-md shadow-emerald-950/40 font-semibold'
                    : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'
                }`
              }
            >
              <div className="flex items-center gap-3">
                <Icon className="w-4 h-4 shrink-0" />
                <span>{item.name}</span>
              </div>
              {item.badge !== undefined && (
                <span className={`px-2 py-0.5 text-[10px] font-bold rounded-full ${item.badgeColor || 'bg-slate-800 text-slate-300'}`}>
                  {item.badge}
                </span>
              )}
            </NavLink>
          );
        })}
      </div>

      {/* Footer System Info */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-950/50">
        <div className="flex items-center gap-2 text-slate-400 text-xs mb-1">
          <Info className="w-3.5 h-3.5 text-emerald-400" />
          <span className="font-semibold text-slate-300">Faculty MVP Demo</span>
        </div>
        <p className="text-[11px] text-slate-500 leading-relaxed">
          Frontend Prototype v1.0 • Built with React & Recharts
        </p>
      </div>
    </aside>
  );
};
