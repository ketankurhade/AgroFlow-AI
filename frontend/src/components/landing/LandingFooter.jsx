import React from 'react';
import { Link } from 'react-router-dom';
import { Sprout } from 'lucide-react';

export const LandingFooter = () => {
  const scrollToSection = (id) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <footer className="bg-slate-950 text-slate-400 border-t border-slate-800/80 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        <div className="flex flex-col md:flex-row items-center justify-between gap-8 pb-8 border-b border-slate-800/80">
          
          {/* Brand Logo & Tagline */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-700 flex items-center justify-center text-white shadow-md">
              <Sprout className="w-6 h-6 stroke-[2.5]" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="text-xl font-black tracking-tight text-white">AgroFlow</span>
                <span className="text-[10px] font-extrabold px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 uppercase tracking-widest">
                  AI
                </span>
              </div>
              <p className="text-xs text-slate-400 font-medium">Supply Chain Intelligence Platform</p>
            </div>
          </div>

          {/* Navigation Links */}
          <div className="flex flex-wrap items-center justify-center gap-6 text-sm font-semibold text-slate-300">
            <button
              onClick={() => scrollToSection('hero')}
              className="hover:text-emerald-400 transition-colors cursor-pointer"
            >
              Home
            </button>
            <button
              onClick={() => scrollToSection('how-it-works')}
              className="hover:text-emerald-400 transition-colors cursor-pointer"
            >
              How It Works
            </button>
            <button
              onClick={() => scrollToSection('ai-intelligence')}
              className="hover:text-emerald-400 transition-colors cursor-pointer"
            >
              AI Intelligence
            </button>
            <Link
              to="/login"
              className="hover:text-emerald-400 transition-colors"
            >
              Login
            </Link>
            <Link
              to="/register"
              className="hover:text-emerald-400 transition-colors"
            >
              Register
            </Link>
          </div>

        </div>

        {/* Copyright Bar */}
        <div className="pt-8 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400 gap-4">
          <p>© {new Date().getFullYear()} AgroFlow AI. All rights reserved.</p>
          <p className="font-medium text-slate-400">Intelligent Agricultural Supply Chain Management</p>
        </div>

      </div>
    </footer>
  );
};
