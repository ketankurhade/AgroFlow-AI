import React from 'react';
import { RECENT_SYSTEM_ALERTS } from '../../data/mockData';
import { Activity } from 'lucide-react';

export const SupplyChainStatusFeed = ({ shipments = [] }) => {
  const displayAlerts = shipments.length > 0
    ? shipments.map((s) => ({
        id: s.id,
        type: s.status === 'In Transit' ? 'Warning' : 'Success',
        title: `Shipment #${s.vehicle_number} — ${s.status}`,
        timestamp: new Date(s.dispatched_at || Date.now()).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        message: `Transporting ${s.batch?.product?.name || 'Produce'} from ${s.source} to ${s.destination}.`,
      }))
    : RECENT_SYSTEM_ALERTS;

  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-emerald-600" />
            <h3 className="text-base font-bold text-slate-900">Supply-Chain Health & Telemetry Feed</h3>
          </div>
          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">
            {shipments.length > 0 ? 'Live API Shipments' : 'Real-time IoT Sync'}
          </span>
        </div>

        <div className="space-y-3 relative before:absolute before:left-3 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
          {displayAlerts.map((alert) => (
            <div key={alert.id} className="relative pl-7 text-xs">
              <div
                className={`absolute left-1.5 top-1 -translate-x-1/2 w-3.5 h-3.5 rounded-full border-2 border-white flex items-center justify-center ${
                  alert.type === 'Critical'
                    ? 'bg-rose-500'
                    : alert.type === 'Warning'
                    ? 'bg-amber-500'
                    : alert.type === 'Success'
                    ? 'bg-emerald-500'
                    : 'bg-blue-500'
                }`}
              ></div>
              <div className="flex items-center justify-between">
                <span className="font-bold text-slate-900">{alert.title}</span>
                <span className="text-[10px] text-slate-400">{alert.timestamp}</span>
              </div>
              <p className="text-slate-600 mt-0.5 text-[11px] leading-relaxed">{alert.message}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
