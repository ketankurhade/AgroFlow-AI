import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Sidebar } from '../components/common/Sidebar';
import { Header } from '../components/common/Header';

export const DashboardLayout = () => {
  const location = useLocation();

  const getPageTitle = (path) => {
    switch (path) {
      case '/':
      case '/dashboard':
        return 'Executive Supply Chain Dashboard';
      case '/inventory':
        return 'Cold Chain Inventory Operations';
      case '/batches':
        return 'Harvest Batch Tracking & Provenance';
      case '/orders':
        return 'Fulfillment & Purchase Orders';
      case '/forecasts':
        return 'AI Demand & Price Forecasting';
      case '/risk':
        return 'Spoilage Risk & Quality Analytics';
      case '/routes':
        return 'Route & Fleet Logistics Optimization';
      case '/traceability':
        return 'QR Code Provenance Verification';
      case '/marketplace':
        return 'Direct Farm Consumer Marketplace';
      default:
        return 'AgroFlow AI Portal';
    }
  };

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden font-sans text-slate-800">
      <Sidebar />
      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        <Header title={getPageTitle(location.pathname)} />
        <main className="flex-1 overflow-y-auto p-6 bg-slate-50">
          <div className="max-w-7xl mx-auto space-y-6">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};
