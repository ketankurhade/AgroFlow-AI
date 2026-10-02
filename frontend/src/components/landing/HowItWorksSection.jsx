import React from 'react';
import { Sprout, PackageCheck, Warehouse, Truck, Store, Users, ArrowDown, ArrowRight } from 'lucide-react';

export const HowItWorksSection = () => {
  const steps = [
    {
      step: "01",
      role: "Farmer",
      icon: Sprout,
      description: "Create and manage harvest batches",
      details: "Log origin location, crop variety, harvest date, and batch identity."
    },
    {
      step: "02",
      role: "Collection Center",
      icon: PackageCheck,
      description: "Receive, grade and prepare produce",
      details: "Inspect quality, assign initial grading, and aggregate farm produce."
    },
    {
      step: "03",
      role: "Warehouse",
      icon: Warehouse,
      description: "Manage storage and inventory",
      details: "Store under controlled cold-chain conditions and track stock levels."
    },
    {
      step: "04",
      role: "Distributor",
      icon: Truck,
      description: "Coordinate transportation and shipments",
      details: "Dispatch optimized route vehicles for fast, minimal-spoilage transit."
    },
    {
      step: "05",
      role: "Retailer",
      icon: Store,
      description: "Procure and manage fresh produce",
      details: "Receive fresh shipments, manage storefront inventory, and satisfy demand."
    },
    {
      step: "06",
      role: "Consumer",
      icon: Users,
      description: "Purchase and trace produce",
      details: "Scan QR code on produce to view verified origin and journey provenance."
    }
  ];

  return (
    <section id="how-it-works" className="py-20 bg-slate-950 text-white border-b border-slate-800/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto space-y-4 mb-16">
          <span className="text-xs font-bold uppercase tracking-widest text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20">
            End-to-End Workflow
          </span>
          <h2 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
            One Connected Agricultural Supply Chain
          </h2>
          <p className="text-slate-300 text-base leading-relaxed">
            AgroFlow AI seamlessly bridges every participant in the fresh food pipeline through structured workflows and shared intelligence.
          </p>
        </div>

        {/* Role Cards Flow */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 relative">
          {steps.map((item, index) => {
            const IconComponent = item.icon;
            return (
              <div
                key={item.role}
                className="relative bg-slate-900 border border-slate-800 hover:border-emerald-500/50 rounded-2xl p-6 transition-all duration-300 group flex flex-col justify-between shadow-xl"
              >
                <div>
                  {/* Top Bar: Step Number & Role Icon */}
                  <div className="flex items-center justify-between mb-5">
                    <span className="text-xs font-black px-2.5 py-1 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      STAGE {item.step}
                    </span>
                    <div className="w-10 h-10 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-center text-emerald-400 group-hover:bg-emerald-600 group-hover:text-white transition-colors">
                      <IconComponent className="w-5 h-5 stroke-[2]" />
                    </div>
                  </div>

                  {/* Title & Exact Description */}
                  <h3 className="text-xl font-bold text-white mb-2 group-hover:text-emerald-300 transition-colors">
                    {item.role}
                  </h3>
                  <p className="text-emerald-400 text-sm font-semibold mb-3">
                    "{item.description}"
                  </p>
                  <p className="text-slate-400 text-xs leading-relaxed">
                    {item.details}
                  </p>
                </div>

                {/* Connecting Visual Arrow Indicator for visual continuity */}
                <div className="mt-6 pt-4 border-t border-slate-800/80 flex items-center justify-between text-slate-500 text-[11px]">
                  <span>Role Workflow</span>
                  {index < steps.length - 1 ? (
                    <div className="flex items-center gap-1 text-emerald-400 font-bold">
                      <span>Next Stage</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </div>
                  ) : (
                    <span className="text-emerald-400 font-bold">Provenance Complete</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>

      </div>
    </section>
  );
};
