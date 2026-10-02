import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Sprout, Menu, X, ArrowRight } from 'lucide-react';

export const LandingNavbar = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const scrollToSection = (id) => {
    setMobileMenuOpen(false);
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <header className="sticky top-0 z-50 bg-slate-950/90 backdrop-blur-md border-b border-slate-800/80 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
        
        {/* Brand Logo */}
        <Link to="/" className="flex items-center gap-3 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-700 flex items-center justify-center text-white shadow-lg shadow-emerald-950/40 group-hover:scale-105 transition-transform">
            <Sprout className="w-6 h-6 stroke-[2.5]" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="text-xl font-black tracking-tight text-white">AgroFlow</span>
              <span className="text-[10px] font-extrabold px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 uppercase tracking-widest">
                AI
              </span>
            </div>
            <p className="text-[10px] text-slate-400 font-medium hidden sm:block">Supply Chain Intelligence</p>
          </div>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-8 text-sm font-semibold text-slate-300">
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
          <button 
            onClick={() => scrollToSection('traceability')}
            className="hover:text-emerald-400 transition-colors cursor-pointer"
          >
            Traceability
          </button>
        </nav>

        {/* Right CTA Buttons */}
        <div className="hidden md:flex items-center gap-4">
          <Link
            to="/login"
            className="px-4 py-2 text-sm font-semibold text-slate-300 hover:text-white transition-colors"
          >
            Login
          </Link>
          <Link
            to="/register"
            className="px-4 py-2.5 rounded-xl text-sm font-bold text-white bg-emerald-600 hover:bg-emerald-500 shadow-lg shadow-emerald-950/50 hover:shadow-emerald-900/60 transition-all flex items-center gap-2 group"
          >
            <span>Get Started</span>
            <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
          </Link>
        </div>

        {/* Mobile Hamburger Button */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="md:hidden p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-900 focus:outline-hidden"
          aria-label="Toggle Navigation Menu"
        >
          {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Mobile Dropdown Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-slate-900 border-b border-slate-800 px-4 pt-2 pb-6 space-y-4 animate-in slide-in-from-top duration-200">
          <div className="flex flex-col space-y-3 font-medium text-slate-300 text-sm pt-2">
            <button
              onClick={() => scrollToSection('hero')}
              className="text-left py-2 hover:text-emerald-400 border-b border-slate-800/60"
            >
              Home
            </button>
            <button
              onClick={() => scrollToSection('how-it-works')}
              className="text-left py-2 hover:text-emerald-400 border-b border-slate-800/60"
            >
              How It Works
            </button>
            <button
              onClick={() => scrollToSection('ai-intelligence')}
              className="text-left py-2 hover:text-emerald-400 border-b border-slate-800/60"
            >
              AI Intelligence
            </button>
            <button
              onClick={() => scrollToSection('traceability')}
              className="text-left py-2 hover:text-emerald-400 border-b border-slate-800/60"
            >
              Traceability
            </button>
          </div>
          
          <div className="flex flex-col gap-2 pt-2">
            <Link
              to="/login"
              className="w-full text-center py-2.5 rounded-xl border border-slate-700 text-slate-200 font-semibold text-sm hover:bg-slate-800"
            >
              Login
            </Link>
            <Link
              to="/register"
              className="w-full text-center py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-sm shadow-md"
            >
              Get Started
            </Link>
          </div>
        </div>
      )}
    </header>
  );
};
