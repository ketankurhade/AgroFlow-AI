import React from 'react';
import {
  Sprout,
  PackageCheck,
  Warehouse,
  Truck,
  Store,
  Users,
  ShieldCheck,
  CheckCircle2
} from 'lucide-react';

export const PlatformRolesSection = () => {
  const roles = [
    {
      title: "Farmer",
      icon: Sprout,
      scope: "Harvest & Batch Management",
      description: "Log crops, harvest volume, location tags, and track price/spoilage risks for farm produce."
    },
    {
      title: "Collection Center",
      icon: PackageCheck,
      scope: "Receiving & Grading Operations",
      description: "Receive farm harvests, perform quality grading, aggregate produce batches, and issue QR tags."
    },
    {
      title: "Warehouse",
      icon: Warehouse,
      scope: "Cold Chain Storage & Inventory",
      description: "Monitor inventory levels, ambient temperatures, storage duration, and automated spoilage risk alerts."
    },
    {
      title: "Distributor",
      icon: Truck,
      scope: "Logistics & Fleet Optimization",
      description: "Manage transit shipments, optimize vehicle routes, and ensure timely temperature-controlled dispatch."
    },
    {
      title: "Retailer",
      icon: Store,
      scope: "Produce Procurement & Sales",
      description: "Order fresh produce batches, manage store inventory, track consumer demand, and verify origin."
    },
    {
      title: "Consumer",
      icon: Users,
      scope: "Marketplace & QR Provenance",
      description: "Browse fresh produce marketplace, trace crop harvest history, and verify farm-to-table authenticity."
    }
  ];

  return (
    <section className="py-20 bg-slate-950 text-white border-b border-slate-800/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto space-y-4 mb-16">
          <span className="text-xs font-bold uppercase tracking-widest text-emerald-400 bg-emerald-500/10 px-3.5 py-1 rounded-full border border-emerald-500/20">
            Tailored User Portals
          </span>
          <h2 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
            One Platform. Every Supply Chain Role.
          </h2>
          <p className="text-slate-300 text-base leading-relaxed">
            AgroFlow AI provides customized interfaces, permissions, and operational tools tailored to the specific responsibilities of each supply chain participant.
          </p>
        </div>

        {/* Roles Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {roles.map((r) => {
            const IconComponent = r.icon;
            return (
              <div
                key={r.title}
                className="bg-slate-900 border border-slate-800 rounded-2xl p-6 hover:border-emerald-500/50 transition-all duration-300 flex flex-col justify-between shadow-xl group"
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-12 h-12 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-center text-emerald-400 group-hover:bg-emerald-600 group-hover:text-white transition-all">
                      <IconComponent className="w-6 h-6" />
                    </div>
                    <span className="text-[10px] font-bold text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-1 rounded-md">
                      {r.scope}
                    </span>
                  </div>

                  <h3 className="text-xl font-bold text-white mb-2 group-hover:text-emerald-300 transition-colors">
                    {r.title}
                  </h3>

                  <p className="text-slate-400 text-xs leading-relaxed mb-4">
                    {r.description}
                  </p>
                </div>

                <div className="pt-4 border-t border-slate-800/80 flex items-center gap-2 text-xs text-slate-300 font-medium">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  <span>Role-specific workflow access</span>
                </div>
              </div>
            );
          })}
        </div>

      </div>
    </section>
  );
};
