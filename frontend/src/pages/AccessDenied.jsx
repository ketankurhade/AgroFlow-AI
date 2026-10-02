import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldAlert, ArrowLeft } from 'lucide-react';

export const AccessDenied = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-[80vh] flex flex-col items-center justify-center p-6 text-center">
      <div className="w-16 h-16 rounded-2xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center mb-6 shadow-xl shadow-rose-950/20">
        <ShieldAlert className="w-8 h-8 text-rose-500 stroke-[2]" />
      </div>

      <h1 className="text-2xl font-bold text-white mb-2">Access Denied</h1>
      <p className="text-sm text-slate-400 max-w-md mb-8 leading-relaxed">
        You do not have permission to access this section. Please contact your system administrator if you believe this is an error.
      </p>

      <button
        onClick={() => navigate('/')}
        className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs transition-all shadow-lg shadow-emerald-950/40 hover:scale-[1.02] active:scale-[0.98]"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Dashboard</span>
      </button>
    </div>
  );
};

export default AccessDenied;
