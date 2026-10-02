import React from 'react';
import {
  TrendingUp,
  Coins,
  AlertTriangle,
  Route,
  QrCode,
  LayoutDashboard,
  Brain,
  Sparkles
} from 'lucide-react';

export const AiIntelligenceSection = () => {
  const capabilities = [
    {
      title: "Demand Forecasting",
      description: "Predict future demand using historical supply-chain data.",
      icon: TrendingUp,
      tag: "Time-Series Predictive Model"
    },
    {
      title: "Price Forecasting",
      description: "Estimate expected produce prices from historical patterns.",
      icon: Coins,
      tag: "Market Trend Analytics"
    },
    {
      title: "Spoilage Intelligence",
      description: "Identify batches with elevated operational spoilage risk.",
      icon: AlertTriangle,
      tag: "Perishability & Temperature Risk"
    },
    {
      title: "Route Optimization",
      description: "Optimize delivery routes using mathematical optimization.",
      icon: Route,
      tag: "OR-Tools Logistics Engine"
    },
    {
      title: "QR Traceability",
      description: "Track produce through its supply-chain journey.",
      icon: QrCode,
      tag: "Batch Identity & Provenance"
    },
    {
      title: "Supply Chain Dashboard",
      description: "Monitor inventory, orders, shipments and operational insights.",
      icon: LayoutDashboard,
      tag: "Unified Role Telemetry"
    }
  ];

  return (
    <section id="ai-intelligence" className="py-20 bg-slate-900 text-white border-b border-slate-800/80 relative">
      {/* Background Lighting Pill */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[300px] bg-emerald-600/10 rounded-full blur-[100px] pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto space-y-4 mb-16">
          <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-bold uppercase tracking-wider">
            <Brain className="w-3.5 h-3.5" />
            <span>Data-Driven Decision Engine</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
            Intelligence for Better Supply Chain Decisions
          </h2>
          <p className="text-slate-300 text-base leading-relaxed">
            AgroFlow AI combines forecasting, risk analysis and optimization to support supply-chain decisions.
          </p>
        </div>

        {/* 6 Capability Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {capabilities.map((cap) => {
            const IconComponent = cap.icon;
            return (
              <div
                key={cap.title}
                className="bg-slate-950/80 border border-slate-800 rounded-2xl p-6 hover:border-emerald-500/50 transition-all duration-300 group flex flex-col justify-between shadow-xl"
              >
                <div>
                  <div className="flex items-center justify-between mb-5">
                    <div className="w-12 h-12 rounded-xl bg-emerald-950/80 border border-emerald-500/30 flex items-center justify-center text-emerald-400 group-hover:scale-105 group-hover:bg-emerald-600 group-hover:text-white transition-all">
                      <IconComponent className="w-6 h-6 stroke-[2]" />
                    </div>
                    <span className="text-[10px] font-bold text-slate-400 bg-slate-900 border border-slate-800 px-2 py-1 rounded-md">
                      {cap.tag}
                    </span>
                  </div>

                  <h3 className="text-lg font-bold text-white mb-2 group-hover:text-emerald-300 transition-colors">
                    {cap.title}
                  </h3>

                  <p className="text-slate-300 text-sm leading-relaxed mb-4">
                    {cap.description}
                  </p>
                </div>

                <div className="pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
                  <span className="flex items-center gap-1.5 font-medium text-emerald-400">
                    <Sparkles className="w-3.5 h-3.5" /> Core Feature
                  </span>
                  <span className="text-slate-500 text-[11px]">AgroFlow AI Suite</span>
                </div>
              </div>
            );
          })}
        </div>

      </div>
    </section>
  );
};
