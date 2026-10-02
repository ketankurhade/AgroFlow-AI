import React from 'react';
import { Link } from 'react-router-dom';
import {
  Sprout,
  PackageCheck,
  Warehouse,
  Truck,
  Store,
  Users,
  ArrowRight,
  Sparkles,
  ShieldCheck,
  ChevronRight
} from 'lucide-react';

export const LandingHero = () => {
  const scrollToSection = (id) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const stages = [
    { role: 'Farmer', icon: Sprout, label: 'Harvest Batch', color: 'emerald' },
    { role: 'Collection Center', icon: PackageCheck, label: 'Grading & QC', color: 'teal' },
    { role: 'Warehouse', icon: Warehouse, label: 'Cold Storage', color: 'sky' },
    { role: 'Distributor', icon: Truck, label: 'Optimized Transit', color: 'indigo' },
    { role: 'Retailer', icon: Store, label: 'Store Shelf', color: 'amber' },
    { role: 'Consumer', icon: Users, label: 'QR Provenance', color: 'purple' }
  ];

  return (
    <section id="hero" className="relative bg-slate-950 text-white overflow-hidden pt-12 pb-20 lg:pt-20 lg:pb-28 border-b border-slate-800/60">
      {/* Background Decorative Lighting Gradients */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-emerald-600/15 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute top-1/3 right-10 w-96 h-96 bg-teal-600/10 rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute bottom-10 left-10 w-96 h-96 bg-indigo-600/10 rounded-full blur-[100px] pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* Top Feature Pill */}
        <div className="flex justify-center mb-6">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-slate-900 border border-emerald-500/30 text-xs font-semibold text-emerald-400 shadow-inner">
            <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
            <span>End-to-End Agricultural Supply Chain Intelligence</span>
          </div>
        </div>

        {/* Main Text Container */}
        <div className="max-w-4xl mx-auto text-center space-y-6">
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black tracking-tight text-white leading-[1.15]">
            Smarter Agriculture.{' '}
            <span className="bg-gradient-to-r from-emerald-400 via-teal-300 to-emerald-200 bg-clip-text text-transparent">
              Connected Supply Chains.
            </span>
          </h1>
          
          <p className="text-base sm:text-lg lg:text-xl text-slate-300 max-w-3xl mx-auto font-normal leading-relaxed">
            AgroFlow AI connects farmers, collection centers, warehouses, distributors, retailers and consumers through an intelligent, traceable agricultural supply chain.
          </p>

          {/* Action Buttons */}
          <div className="pt-2 flex flex-col sm:flex-row items-center justify-center gap-4">
            <button
              onClick={() => scrollToSection('how-it-works')}
              className="w-full sm:w-auto px-7 py-3.5 rounded-xl font-bold text-sm bg-slate-800 hover:bg-slate-700/80 text-white border border-slate-700/80 hover:border-emerald-500/50 shadow-lg transition-all flex items-center justify-center gap-2 cursor-pointer"
            >
              <span>Explore AgroFlow AI</span>
              <ChevronRight className="w-4 h-4 text-emerald-400" />
            </button>

            <Link
              to="/register"
              className="w-full sm:w-auto px-7 py-3.5 rounded-xl font-bold text-sm text-white bg-emerald-600 hover:bg-emerald-500 shadow-xl shadow-emerald-950/60 transition-all flex items-center justify-center gap-2"
            >
              <span>Get Started</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>

        {/* Agricultural Supply-Chain Visual Illustration */}
        <div className="mt-16 pt-8 border-t border-slate-800/80">
          <div className="text-center mb-6">
            <span className="text-xs font-bold uppercase tracking-widest text-slate-400">
              The Connected AgroFlow Ecosystem Flow
            </span>
          </div>

          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-2xl backdrop-blur-md relative">
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 relative">
              {stages.map((stage, idx) => {
                const IconComponent = stage.icon;
                return (
                  <div key={stage.role} className="relative group flex flex-col items-center text-center">
                    {/* Node Box */}
                    <div className="w-full bg-slate-950 border border-slate-800 group-hover:border-emerald-500/60 p-4 rounded-xl transition-all duration-300 flex flex-col items-center space-y-2.5 shadow-md">
                      <div className="w-12 h-12 rounded-xl bg-emerald-950/60 border border-emerald-500/30 flex items-center justify-center text-emerald-400 group-hover:scale-110 group-hover:bg-emerald-600 group-hover:text-white transition-all">
                        <IconComponent className="w-6 h-6 stroke-[2]" />
                      </div>
                      
                      <div>
                        <p className="text-xs font-bold text-white group-hover:text-emerald-300 transition-colors">
                          {stage.role}
                        </p>
                        <span className="inline-block mt-1 text-[10px] font-semibold text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                          {stage.label}
                        </span>
                      </div>
                    </div>

                    {/* Desktop Arrow Connector */}
                    {idx < stages.length - 1 && (
                      <div className="hidden lg:flex absolute top-1/2 -right-3 -translate-y-1/2 z-20 items-center justify-center text-emerald-500/60">
                        <ArrowRight className="w-5 h-5 stroke-[2.5] animate-pulse" />
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Bottom Status bar inside illustration */}
            <div className="mt-6 pt-4 border-t border-slate-800/60 flex flex-wrap items-center justify-between text-xs text-slate-400 gap-3">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span>Continuous Batch Telemetry & QR Verification</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
                <span className="font-semibold text-slate-300">Live AI Analytics Active</span>
              </div>
            </div>
          </div>
        </div>

      </div>
    </section>
  );
};
