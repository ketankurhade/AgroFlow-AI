import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { hasRoutePermission } from './config/permissions';
import { DashboardLayout } from './layouts/DashboardLayout';
import { LandingPage } from './pages/LandingPage';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Dashboard } from './pages/Dashboard';
import { Inventory } from './pages/Inventory';
import { Batches } from './pages/Batches';
import { Orders } from './pages/Orders';
import { Forecasts } from './pages/Forecasts';
import { RiskManagement } from './pages/RiskManagement';
import { RouteOptimization } from './pages/RouteOptimization';
import { QRTraceability } from './pages/QRTraceability';
import { Marketplace } from './pages/Marketplace';
import { AccessDenied } from './pages/AccessDenied';

const ProtectedRoute = ({ children, path }) => {
  const { isAuthenticated, loading, user } = useAuth();
  
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

  if (path && !hasRoutePermission(user?.role, path)) {
    return <AccessDenied />;
  }

  return children;
};

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            element={
              <ProtectedRoute>
                <DashboardLayout />
              </ProtectedRoute>
            }
          >
            <Route path="dashboard" element={<ProtectedRoute path="/dashboard"><Dashboard /></ProtectedRoute>} />
            <Route path="inventory" element={<ProtectedRoute path="/inventory"><Inventory /></ProtectedRoute>} />
            <Route path="batches" element={<ProtectedRoute path="/batches"><Batches /></ProtectedRoute>} />
            <Route path="orders" element={<ProtectedRoute path="/orders"><Orders /></ProtectedRoute>} />
            <Route path="forecasts" element={<ProtectedRoute path="/forecasts"><Forecasts /></ProtectedRoute>} />
            <Route path="risk" element={<ProtectedRoute path="/risk"><RiskManagement /></ProtectedRoute>} />
            <Route path="routes" element={<ProtectedRoute path="/routes"><RouteOptimization /></ProtectedRoute>} />
            <Route path="traceability" element={<ProtectedRoute path="/traceability"><QRTraceability /></ProtectedRoute>} />
            <Route path="marketplace" element={<ProtectedRoute path="/marketplace"><Marketplace /></ProtectedRoute>} />
            <Route path="access-denied" element={<AccessDenied />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

