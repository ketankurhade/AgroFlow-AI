import React from 'react';
import {
  TrendingUp,
  AlertTriangle,
  Lightbulb,
  Route,
  QrCode,
  ArrowRight
} from 'lucide-react';

export const DecisionCycleSection = () => {
  const cycleSteps = [
    {
      step: "01",
      name: "Predict",
      description: "Demand and price forecasts",
      icon: TrendingUp,
      color: "from-emerald-500 to-teal-600"
    },
    {
      step: "02",
      name: "Analyze",
      description: "Inventory and spoilage risk",
      icon: AlertTriangle,
      color: "from-teal-500 to-cyan-600"
    },
    {
      step: "03",
      name: "Decide",
      description: "Operational recommendations",
      icon: Lightbulb,
      color: "from-cyan-500 to-sky-600"
    },
    {
      step: "04",
      name: "Optimize",
      description: "Transportation routes",
      icon: Route,
      color: "from-sky-500 to-blue-600"
    },
    {
      step: "05",
      name: "Track",
      description: "QR-based provenance",
      icon: QrCode,
      color: "from-indigo-500 to-emerald-500"
    }
  ];

  return (
    <section className="py-20 bg-slate-950 text-white border-b border-slate-800/80 relative overflow-hidden">
      {/* Background Decorative Gradient Beam */}
      <div className="absolute top-1/2 left-0 right-0 h-1 bg-gradient-to-r from-emerald-500 via-sky-500 to-indigo-500 opacity-20 hidden lg:block" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto space-y-4 mb-16">
          <span className="text-xs font-bold uppercase tracking-widest text-emerald-400 bg-emerald-500/10 px-3.5 py-1 rounded-full border border-emerald-500/20">
            The AgroFlow Intelligence Loop
          </span>
          <h2 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
            Predict → Analyze → Decide → Optimize → Track
          </h2>
          <p className="text-slate-300 text-base leading-relaxed">
            A continuous operational feedback loop driving efficiency, quality assurance, and transparency across every stage of agricultural logistics.
          </p>
        </div>

        {/* Pipeline Container */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 relative">
          {cycleSteps.map((step, idx) => {
            const IconComponent = step.icon;
            return (
              <div key={step.name} className="relative group">
                {/* Step Card */}
                <div className="h-full bg-slate-900 border border-slate-800 group-hover:border-emerald-500/60 p-6 rounded-2xl transition-all duration-300 flex flex-col justify-between shadow-2xl relative overflow-hidden">
                  
                  {/* Subtle Top Accent bar */}
                  <div className={`absolute top-0 left-0 right-0 h-1 bg-gradient-to-r ${step.color}`} />

                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <span className="text-2xl font-black text-slate-400 group-hover:text-emerald-400 transition-colors">
                        {step.step}
                      </span>
                      <div className="w-10 h-10 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-center text-emerald-400 group-hover:bg-emerald-600 group-hover:text-white transition-all">
                        <IconComponent className="w-5 h-5" />
                      </div>
                    </div>

                    <h3 className="text-xl font-bold text-white mb-2 group-hover:text-emerald-300 transition-colors">
                      {step.name}
                    </h3>

                    <p className="text-slate-400 text-xs leading-relaxed">
                      {step.description}
                    </p>
                  </div>

                  <div className="mt-6 pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-semibold text-emerald-400">
                    <span>Phase {step.step}</span>
                    <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>
              </div>
            );
          })}
        </div>

      </div>
    </section>
  );
};
