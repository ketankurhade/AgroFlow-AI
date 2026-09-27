import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { DashboardLayout } from './layouts/DashboardLayout';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { Inventory } from './pages/Inventory';
import { Batches } from './pages/Batches';
import { Orders } from './pages/Orders';
import { Forecasts } from './pages/Forecasts';
import { RiskManagement } from './pages/RiskManagement';
import { RouteOptimization } from './pages/RouteOptimization';
import { QRTraceability } from './pages/QRTraceability';
import { ConsumerMarketplace } from './pages/ConsumerMarketplace';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center text-slate-300 font-medium text-sm">
        <div className="flex items-center gap-3">
          <div className="w-5 h-5 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
          <span>Authenticating AgroFlow session...</span>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <DashboardLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Dashboard />} />
            <Route path="inventory" element={<Inventory />} />
            <Route path="batches" element={<Batches />} />
            <Route path="orders" element={<Orders />} />
            <Route path="forecasts" element={<Forecasts />} />
            <Route path="risk" element={<RiskManagement />} />
            <Route path="routes" element={<RouteOptimization />} />
            <Route path="traceability" element={<QRTraceability />} />
            <Route path="marketplace" element={<ConsumerMarketplace />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
