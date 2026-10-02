import React from 'react';
import { Link } from 'react-router-dom';
import {
  QrCode,
  Sprout,
  PackageCheck,
  Warehouse,
  Truck,
  Store,
  Users,
  CheckCircle2,
  ArrowRight,
  ShieldCheck
} from 'lucide-react';

export const QrTraceabilitySection = () => {
  const timelineStages = [
    { name: "Harvest", desc: "Farmer logs crop yield & origin details", icon: Sprout },
    { name: "Collection", desc: "Inspection, grading & batch tag generated", icon: PackageCheck },
    { name: "Storage", desc: "Cold storage temperature telemetry logged", icon: Warehouse },
    { name: "Distribution", desc: "Optimized route dispatch & tracking", icon: Truck },
    { name: "Retail", desc: "Store receiving & shelf inventory registration", icon: Store },
    { name: "Consumer", desc: "Scan QR code to view end-to-end journey", icon: Users }
  ];

  return (
    <section id="traceability" className="py-20 bg-slate-900 text-white border-b border-slate-800/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          
          {/* Left Text Column */}
          <div className="lg:col-span-5 space-y-6">
            <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-bold uppercase tracking-wider">
              <QrCode className="w-3.5 h-3.5" />
              <span>Full Provenance Verification</span>
            </div>

            <h2 className="text-3xl sm:text-4xl font-black text-white tracking-tight leading-tight">
              Know Where Your Produce Comes From
            </h2>

            <p className="text-slate-300 text-base leading-relaxed">
              Every traceable batch can carry a QR-based identity that connects its journey from harvest through storage, transportation and delivery.
            </p>

            <div className="space-y-3 pt-2">
              <div className="flex items-start gap-3 text-slate-300 text-sm">
                <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                <span>Unique serial batch QR tags generated at collection</span>
              </div>
              <div className="flex items-start gap-3 text-slate-300 text-sm">
                <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                <span>Instant verification of harvest origin and storage conditions</span>
              </div>
              <div className="flex items-start gap-3 text-slate-300 text-sm">
                <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                <span>Transparent consumer trust without third-party complexity</span>
              </div>
            </div>

            <div className="pt-4">
              <Link
                to="/login"
                className="inline-flex items-center gap-2 px-6 py-3.5 rounded-xl font-bold text-sm text-white bg-emerald-600 hover:bg-emerald-500 shadow-xl shadow-emerald-950/60 transition-all cursor-pointer"
              >
                <span>Explore Traceability</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>

          {/* Right Visual Timeline Column */}
          <div className="lg:col-span-7">
            <div className="bg-slate-950 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-2xl space-y-6">
              <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-emerald-950 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                    <QrCode className="w-5 h-5" />
                  </div>
                  <div>
                    <p className="text-sm font-bold text-white">Batch Identity Verification</p>
                    <p className="text-xs text-slate-400">Sample Serial: AGR-2026-ORG-8849</p>
                  </div>
                </div>
                <span className="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-md border border-emerald-500/20">
                  Verified Active
                </span>
              </div>

              {/* Timeline Items */}
              <div className="space-y-4 relative before:absolute before:inset-0 before:left-5 before:w-0.5 before:bg-slate-800">
                {timelineStages.map((stage, idx) => {
                  const IconComponent = stage.icon;
                  return (
                    <div key={stage.name} className="relative flex items-start gap-4 z-10 group">
                      <div className="w-10 h-10 rounded-xl bg-slate-900 border border-slate-700 group-hover:border-emerald-500/60 flex items-center justify-center text-emerald-400 shrink-0 transition-colors">
                        <IconComponent className="w-5 h-5" />
                      </div>
                      <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3 flex-1 group-hover:border-slate-700 transition-colors">
                        <div className="flex items-center justify-between">
                          <p className="text-sm font-bold text-white group-hover:text-emerald-300 transition-colors">
                            {stage.name}
                          </p>
                          <span className="text-[10px] text-slate-500 font-semibold">Step 0{idx + 1}</span>
                        </div>
                        <p className="text-xs text-slate-400 mt-0.5">{stage.desc}</p>
                      </div>
                    </div>
                  );
                })}
              </div>

              <div className="pt-2 border-t border-slate-800 flex items-center gap-2 text-xs text-slate-400">
                <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>Complete transparent audit log across supply chain handoffs</span>
              </div>
            </div>
          </div>

        </div>

      </div>
    </section>
  );
};
