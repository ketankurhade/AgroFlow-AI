import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import {
  Search,
  Bell,
  ShieldCheck,
  ChevronDown,
  LogOut,
  User,
  RefreshCw,
  Sprout,
  PackageCheck,
  Warehouse,
  Truck,
  Store,
} from 'lucide-react';
import { RECENT_SYSTEM_ALERTS } from '../../data/mockData';

export const getRoleDisplayName = (role) => {
  switch ((role || '').toLowerCase()) {
    case 'farmer':
      return 'Farmer / Producer';
    case 'supply_chain_manager':
    case 'collection_center':
    case 'warehouse':
      return 'Supply Chain / Storage Manager';
    case 'distributor':
      return 'Distributor & Logistics';
    case 'retailer':
      return 'Retailer / Merchant';
    case 'consumer':
      return 'Consumer / Buyer';
    case 'admin':
      return 'Administrator';
    default:
      return (role || 'User').replace(/_/g, ' ');
  }
};

const getRoleAvatarConfig = (role) => {
  const normRole = (role || '').toLowerCase();
  switch (normRole) {
    case 'admin':
      return { icon: ShieldCheck, bg: 'bg-indigo-100 text-indigo-700 border-indigo-300' };
    case 'farmer':
      return { icon: Sprout, bg: 'bg-emerald-100 text-emerald-700 border-emerald-300' };
    case 'supply_chain_manager':
    case 'collection_center':
    case 'warehouse':
      return { icon: Warehouse, bg: 'bg-blue-100 text-blue-700 border-blue-300' };
    case 'distributor':
      return { icon: Truck, bg: 'bg-purple-100 text-purple-700 border-purple-300' };
    case 'retailer':
      return { icon: Store, bg: 'bg-teal-100 text-teal-700 border-teal-300' };
    case 'consumer':
    default:
      return { icon: User, bg: 'bg-slate-100 text-slate-700 border-slate-300' };
  }
};

export const Header = ({ title }) => {
  const { user, switchRole, logout } = useAuth();
  const [showRoleMenu, setShowRoleMenu] = useState(false);
  const [showAlertsMenu, setShowAlertsMenu] = useState(false);

  const roleAvatar = getRoleAvatarConfig(user?.role);
  const AvatarIcon = roleAvatar.icon;

  return (
    <header className="sticky top-0 z-30 bg-white border-b border-slate-200 px-6 py-3.5 flex items-center justify-between shadow-xs">
      {/* Title & Search */}
      <div className="flex items-center gap-6">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">{title || "Dashboard"}</h1>
          <p className="text-xs text-slate-500 font-medium">Agricultural Supply Chain Intelligence & Traceability Platform</p>
        </div>

        <div className="hidden md:flex items-center gap-2 bg-slate-50 border border-slate-200 rounded-lg px-3 py-1.5 w-64 text-slate-400 focus-within:border-emerald-500 focus-within:bg-white transition-all">
          <Search className="w-4 h-4" />
          <input
            type="text"
            placeholder="Search crop, batch, order #..."
            className="bg-transparent border-none text-xs text-slate-800 placeholder-slate-400 focus:outline-hidden w-full"
          />
        </div>
      </div>

      {/* Right Action Bar */}
      <div className="flex items-center gap-4">
        {/* Status Indicator */}
        <div className="hidden lg:flex items-center gap-2 px-3 py-1 bg-emerald-50 border border-emerald-200 rounded-full text-xs font-semibold text-emerald-800">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          Telemetry Online
        </div>

        {/* Role Selector Dropdown */}
        <div className="relative">
          <button
            onClick={() => {
              setShowRoleMenu(!showRoleMenu);
              setShowAlertsMenu(false);
            }}
            className="flex items-center gap-2 px-3 py-1.5 bg-slate-100 hover:bg-slate-200/80 border border-slate-200 rounded-lg text-xs font-medium text-slate-700 transition-colors cursor-pointer"
          >
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            <span className="hidden sm:inline">Role:</span>
            <span className="font-bold text-slate-900">{getRoleDisplayName(user?.role)}</span>
            <ChevronDown className="w-3.5 h-3.5 text-slate-500" />
          </button>

          {showRoleMenu && (
            <div className="absolute right-0 mt-2 w-64 bg-white rounded-xl shadow-xl border border-slate-200 py-2 z-50 animate-in fade-in zoom-in-95 duration-100">
              <div className="px-3 py-2 border-b border-slate-100">
                <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">Switch View Role</p>
                <p className="text-[11px] text-slate-400">Simulate role-specific permissions</p>
              </div>
              <div className="max-h-60 overflow-y-auto py-1">
                {user?.availableRoles?.map((r) => (
                  <button
                    key={r}
                    onClick={() => {
                      switchRole(r);
                      setShowRoleMenu(false);
                    }}
                    className={`w-full text-left px-3 py-2 text-xs font-medium flex items-center justify-between hover:bg-emerald-50 hover:text-emerald-700 transition-colors ${
                      user.role === r ? 'bg-emerald-50 text-emerald-800 font-bold' : 'text-slate-700'
                    }`}
                  >
                    <span>{getRoleDisplayName(r)}</span>
                    {user.role === r && <span className="w-1.5 h-1.5 rounded-full bg-emerald-600"></span>}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Notifications Dropdown */}
        <div className="relative">
          <button
            onClick={() => {
              setShowAlertsMenu(!showAlertsMenu);
              setShowRoleMenu(false);
            }}
            className="relative p-2 rounded-lg text-slate-600 hover:bg-slate-100 border border-slate-200 transition-colors cursor-pointer"
          >
            <Bell className="w-4 h-4" />
            <span className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-rose-500 text-[10px] font-bold text-white">
              {RECENT_SYSTEM_ALERTS.length}
            </span>
          </button>

          {showAlertsMenu && (
            <div className="absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-xl border border-slate-200 py-2 z-50">
              <div className="px-4 py-2 border-b border-slate-100 flex items-center justify-between">
                <span className="text-xs font-bold text-slate-800">System Notifications</span>
                <span className="text-[10px] bg-rose-100 text-rose-700 font-bold px-2 py-0.5 rounded-full">
                  {RECENT_SYSTEM_ALERTS.length} New
                </span>
              </div>
              <div className="max-h-72 overflow-y-auto">
                {RECENT_SYSTEM_ALERTS.map((alert) => (
                  <div key={alert.id} className="p-3 border-b border-slate-50 hover:bg-slate-50 text-xs">
                    <div className="flex items-center justify-between text-slate-400 text-[10px] mb-1">
                      <span className={`font-semibold ${alert.type === 'Critical' ? 'text-rose-600' : 'text-amber-600'}`}>
                        {alert.type}
                      </span>
                      <span>{alert.timestamp}</span>
                    </div>
                    <p className="font-semibold text-slate-800">{alert.title}</p>
                    <p className="text-slate-500 text-[11px] mt-0.5 line-clamp-2">{alert.message}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Profile Avatar */}
        <div className="flex items-center gap-2 pl-2 border-l border-slate-200">
          <div
            className={`w-8 h-8 rounded-full border ${roleAvatar.bg} flex items-center justify-center shrink-0 shadow-2xs`}
            title={`${user?.name || 'User'} (${getRoleDisplayName(user?.role)})`}
          >
            <AvatarIcon className="w-4 h-4 stroke-[2.2]" />
          </div>
          <div className="hidden lg:block text-left">
            <p className="text-xs font-bold text-slate-900 leading-tight">{user?.name}</p>
            <p className="text-[10px] text-slate-500">{getRoleDisplayName(user?.role)}</p>
          </div>
          <button
            onClick={logout}
            title="Logout"
            className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors cursor-pointer"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
};
