import React, { useState } from 'react';
import { PIPELINE_NODES } from '../../data/mockData';
import { Sprout, Building2, Warehouse, Truck, Store, ShoppingBag, ChevronRight, ArrowRight, CheckCircle2 } from 'lucide-react';

const iconMap = {
  Sprout: Sprout,
  Building2: Building2,
  Warehouse: Warehouse,
  Truck: Truck,
  Store: Store,
  ShoppingBag: ShoppingBag,
};

export const SupplyChainPipeline = () => {
  const [selectedNode, setSelectedNode] = useState(PIPELINE_NODES[2]); // Warehouse by default

  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-6">
        <div>
          <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <span>End-to-End Supply Chain Pipeline</span>
            <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">
              6 Active Nodes
            </span>
          </h2>
          <p className="text-xs text-slate-500">
            Real-time batch transit volume across: Farmer → Collection → Warehouse → Distribution → Retailer → Consumer
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs font-medium text-slate-500">
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-emerald-500"></span> Optimal</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-amber-500"></span> Active</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-blue-500"></span> In-Transit</span>
        </div>
      </div>

      {/* Visual Pipeline Horizontal Flow */}
      <div className="grid grid-cols-1 md:grid-cols-6 gap-3 relative">
        {PIPELINE_NODES.map((node, idx) => {
          const Icon = iconMap[node.icon] || Sprout;
          const isSelected = selectedNode.id === node.id;

          return (
            <div key={node.id} className="relative group">
              <button
                onClick={() => setSelectedNode(node)}
                className={`w-full text-left p-4 rounded-xl border transition-all duration-200 cursor-pointer ${
                  isSelected
                    ? 'border-emerald-600 bg-emerald-50/60 ring-2 ring-emerald-500/20 shadow-sm'
                    : 'border-slate-200 bg-slate-50/60 hover:bg-white hover:border-emerald-300'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className={`p-2 rounded-lg ${isSelected ? 'bg-emerald-600 text-white' : 'bg-slate-200/70 text-slate-700 group-hover:bg-emerald-100 group-hover:text-emerald-700'}`}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <span className="text-[10px] font-extrabold uppercase px-1.5 py-0.5 rounded bg-white text-slate-600 border border-slate-200 shadow-2xs">
                    Step 0{idx + 1}
                  </span>
                </div>

                <p className="text-xs font-bold text-slate-900 truncate">{node.name}</p>
                <p className="text-[11px] font-semibold text-emerald-700 mt-1">{node.volume}</p>
                <p className="text-[10px] text-slate-500 mt-0.5">{node.locationCount}</p>
              </button>

              {/* Arrow Connector between nodes */}
              {idx < PIPELINE_NODES.length - 1 && (
                <div className="hidden md:flex absolute -right-3.5 top-1/2 -translate-y-1/2 z-10 w-4 h-4 rounded-full bg-white border border-slate-300 items-center justify-center text-slate-400">
                  <ChevronRight className="w-3 h-3" />
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Node Detail Card */}
      {selectedNode && (
        <div className="mt-5 p-4 rounded-xl bg-slate-50 border border-slate-200/80 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-emerald-600 text-white rounded-xl shadow-xs">
              <CheckCircle2 className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-bold text-slate-900">{selectedNode.name} Status</span>
                <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">
                  {selectedNode.status}
                </span>
              </div>
              <p className="text-xs text-slate-600 mt-0.5">{selectedNode.desc}</p>
            </div>
          </div>

          <div className="flex items-center gap-6 text-xs border-t md:border-t-0 border-slate-200 pt-3 md:pt-0">
            <div>
              <span className="text-slate-400 block text-[10px]">Active Batches</span>
              <span className="font-bold text-slate-900">{selectedNode.count} Batches</span>
            </div>
            <div>
              <span className="text-slate-400 block text-[10px]">Total Capacity</span>
              <span className="font-bold text-slate-900">{selectedNode.volume}</span>
            </div>
            <div>
              <span className="text-slate-400 block text-[10px]">Network Coverage</span>
              <span className="font-bold text-emerald-700">{selectedNode.locationCount}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
