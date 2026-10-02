import React from 'react';
import { Link } from 'react-router-dom';
import { Sprout, ArrowRight, LogIn } from 'lucide-react';

export const FinalCtaSection = () => {
  return (
    <section className="py-20 bg-slate-950 text-white relative overflow-hidden border-b border-slate-800/80">
      {/* Glow Effects */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-emerald-600/15 rounded-full blur-[140px] pointer-events-none" />

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10 space-y-8">
        
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-700 text-white shadow-xl shadow-emerald-950/60 mb-2">
          <Sprout className="w-9 h-9 stroke-[2.2]" />
        </div>

        <h2 className="text-3xl sm:text-4xl lg:text-5xl font-black text-white tracking-tight leading-tight">
          Build a More Connected Agricultural Supply Chain
        </h2>

        <p className="text-slate-300 text-base sm:text-lg max-w-2xl mx-auto leading-relaxed">
          Explore AgroFlow AI and see how intelligent forecasting, optimization and traceability work together across the agricultural supply chain.
        </p>

        <div className="pt-4 flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link
            to="/register"
            className="w-full sm:w-auto px-8 py-4 rounded-xl text-base font-bold text-white bg-emerald-600 hover:bg-emerald-500 shadow-xl shadow-emerald-950/60 transition-all flex items-center justify-center gap-2"
          >
            <span>Get Started</span>
            <ArrowRight className="w-5 h-5" />
          </Link>

          <Link
            to="/login"
            className="w-full sm:w-auto px-8 py-4 rounded-xl text-base font-semibold text-slate-300 hover:text-white bg-slate-900 border border-slate-800 hover:border-slate-700 transition-all flex items-center justify-center gap-2"
          >
            <LogIn className="w-4 h-4 text-emerald-400" />
            <span>Already have an account? Login</span>
          </Link>
        </div>

      </div>
    </section>
  );
};
