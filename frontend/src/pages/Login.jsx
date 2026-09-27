import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Sprout, Lock, Mail, Shield, CheckCircle2, ArrowRight, AlertCircle, Loader2 } from 'lucide-react';
import { INITIAL_USER } from '../data/mockData';

export const Login = () => {
  const navigate = useNavigate();
  const { login, error, setError } = useAuth();
  const [selectedRole, setSelectedRole] = useState("Supply Chain Manager (Admin)");
  const [email, setEmail] = useState("farmer.ramesh@agroflow.com");
  const [password, setPassword] = useState("password123");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleLoginSubmit = async (emailToUse, passwordToUse, targetPath = '/') => {
    setIsSubmitting(true);
    setError(null);
    try {
      await login(emailToUse, passwordToUse);
      navigate(targetPath);
    } catch (err) {
      console.error("Login submit error:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    handleLoginSubmit(email, password, '/');
  };

  return (
    <div className="min-h-screen bg-slate-900 flex flex-col justify-center py-12 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Background Subtle Gradient Blobs */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-emerald-600/10 rounded-full blur-3xl pointer-events-none"></div>
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-teal-600/10 rounded-full blur-3xl pointer-events-none"></div>

      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center z-10">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-emerald-600 text-white shadow-xl shadow-emerald-950/50 mb-4">
          <Sprout className="w-10 h-10 stroke-[2.2]" />
        </div>
        <h2 className="text-3xl font-black tracking-tight text-white">AgroFlow AI</h2>
        <p className="mt-2 text-sm text-slate-400 font-medium">
          Intelligent Agricultural Supply Chain Management System
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md z-10">
        <div className="bg-slate-800/80 backdrop-blur-md border border-slate-700/80 py-8 px-6 shadow-2xl rounded-2xl sm:px-10">
          
          {error && (
            <div className="mb-4 p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 flex items-start gap-2.5 text-rose-400 text-xs font-medium">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <form className="space-y-5" onSubmit={handleSubmit}>
            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">
                Select Portal Role (Demo)
              </label>
              <select
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2.5 text-xs text-white focus:ring-2 focus:ring-emerald-500 focus:outline-hidden"
              >
                {INITIAL_USER.availableRoles.map((role) => (
                  <option key={role} value={role}>
                    {role}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1">
                Email Address
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                  <Mail className="w-4 h-4" />
                </div>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  placeholder="farmer.ramesh@agroflow.com"
                  className="block w-full pl-10 pr-3 py-2.5 border border-slate-700 rounded-lg bg-slate-900 text-white placeholder-slate-500 text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-hidden"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  placeholder="password123"
                  className="block w-full pl-10 pr-3 py-2.5 border border-slate-700 rounded-lg bg-slate-900 text-white placeholder-slate-500 text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-hidden"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-500 focus:outline-hidden focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 shadow-lg shadow-emerald-950/50 transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Authenticating...
                </>
              ) : (
                <>
                  Sign In to AgroFlow AI Portal <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Preset Demo Roles Quick Access */}
          <div className="mt-6 pt-6 border-t border-slate-700/80">
            <p className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2 text-center">
              Quick Role Test Launchers
            </p>
            <div className="grid grid-cols-2 gap-2 text-[11px]">
              <button
                type="button"
                onClick={() => {
                  setEmail("farmer.ramesh@agroflow.com");
                  setPassword("password123");
                  setSelectedRole("Farmer / Producer");
                  handleLoginSubmit("farmer.ramesh@agroflow.com", "password123", '/');
                }}
                className="p-2 rounded-lg bg-slate-900 hover:bg-slate-700 text-slate-300 border border-slate-700 text-left font-medium transition-colors cursor-pointer"
              >
                🌱 Farmer View
              </button>
              <button
                type="button"
                onClick={() => {
                  setEmail("farmer.suresh@agroflow.com");
                  setPassword("password123");
                  setSelectedRole("Warehouse Cold-Chain Lead");
                  handleLoginSubmit("farmer.suresh@agroflow.com", "password123", '/');
                }}
                className="p-2 rounded-lg bg-slate-900 hover:bg-slate-700 text-slate-300 border border-slate-700 text-left font-medium transition-colors cursor-pointer"
              >
                🏭 Warehouse Lead
              </button>
              <button
                type="button"
                onClick={() => {
                  setEmail("buyer.organic@agroflow.com");
                  setPassword("password123");
                  setSelectedRole("Distributor & Logistics");
                  handleLoginSubmit("buyer.organic@agroflow.com", "password123", '/');
                }}
                className="p-2 rounded-lg bg-slate-900 hover:bg-slate-700 text-slate-300 border border-slate-700 text-left font-medium transition-colors cursor-pointer"
              >
                🚛 Fleet Manager
              </button>
              <button
                type="button"
                onClick={() => {
                  setEmail("buyer.freshmart@agroflow.com");
                  setPassword("password123");
                  setSelectedRole("Consumer");
                  handleLoginSubmit("buyer.freshmart@agroflow.com", "password123", '/marketplace');
                }}
                className="p-2 rounded-lg bg-slate-900 hover:bg-slate-700 text-slate-300 border border-slate-700 text-left font-medium transition-colors cursor-pointer"
              >
                🛒 Consumer Portal
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
