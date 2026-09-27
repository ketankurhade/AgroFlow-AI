import React, { useState, useEffect } from 'react';
import { METRICS } from '../data/mockData';
import { StatCard } from '../components/common/StatCard';
import { SupplyChainPipeline } from '../components/dashboard/SupplyChainPipeline';
import { DemandForecastChart } from '../components/dashboard/DemandForecastChart';
import { PriceForecastChart } from '../components/dashboard/PriceForecastChart';
import { SpoilageRiskOverview } from '../components/dashboard/SpoilageRiskOverview';
import { InventoryOverviewWidget } from '../components/dashboard/InventoryOverviewWidget';
import { RecentOrdersWidget } from '../components/dashboard/RecentOrdersWidget';
import { SupplyChainStatusFeed } from '../components/dashboard/SupplyChainStatusFeed';
import { Warehouse, Package, ShoppingCart, AlertTriangle, AlertCircle, RefreshCw, Loader2 } from 'lucide-react';
import { inventoryAPI, batchesAPI, ordersAPI, shipmentsAPI } from '../services/api';

export const Dashboard = () => {
  const [inventoryData, setInventoryData] = useState([]);
  const [batchesData, setBatchesData] = useState([]);
  const [ordersData, setOrdersData] = useState([]);
  const [shipmentsData, setShipmentsData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [invRes, batchRes, orderRes, shipRes] = await Promise.all([
        inventoryAPI.getInventory().catch(() => ({ data: [] })),
        batchesAPI.getBatches().catch(() => ({ data: [] })),
        ordersAPI.getOrders().catch(() => ({ data: [] })),
        shipmentsAPI.getShipments().catch(() => ({ data: [] })),
      ]);

      setInventoryData(invRes.data || []);
      setBatchesData(batchRes.data || []);
      setOrdersData(orderRes.data || []);
      setShipmentsData(shipRes.data || []);
    } catch (err) {
      console.error("Error fetching dashboard telemetry:", err);
      setError("Failed to fetch live API data. Displaying cached dashboard state.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  // Compute live KPI values from API data when available
  const hasRealData = inventoryData.length > 0 || batchesData.length > 0 || ordersData.length > 0;

  // 1. Total Cold Inventory (sum of inventory quantities)
  const totalInventoryKg = inventoryData.reduce((acc, item) => acc + (item.quantity || 0), 0);
  const totalInventoryDisplay = hasRealData && inventoryData.length > 0
    ? totalInventoryKg >= 1000
      ? `${(totalInventoryKg / 1000).toLocaleString(undefined, { maximumFractionDigits: 1 })} Tons`
      : `${totalInventoryKg.toLocaleString()} kg`
    : `${METRICS.totalInventoryTons.toLocaleString()} Tons`;

  // 2. Active Harvest Batches
  const activeBatchesDisplay = hasRealData && batchesData.length > 0
    ? batchesData.length
    : METRICS.activeBatchesCount;

  // 3. Pending Wholesale Orders & total value
  const pendingOrdersList = ordersData.filter(o => o.status !== 'Delivered' && o.status !== 'Cancelled');
  const pendingOrdersCountDisplay = hasRealData && ordersData.length > 0
    ? (pendingOrdersList.length || ordersData.length)
    : METRICS.pendingOrdersCount;

  const pendingOrdersValueSum = pendingOrdersList.reduce((acc, o) => acc + (o.total_amount || 0), 0);
  const pendingOrdersValueDisplay = hasRealData && ordersData.length > 0
    ? `₹${pendingOrdersValueSum.toLocaleString()}`
    : METRICS.pendingOrdersValue;

  // 4. High Risk Spoilage Batches (rule-based evaluation on expiry date if available)
  const highRiskBatchesCount = hasRealData && batchesData.length > 0
    ? batchesData.filter(b => {
        if (!b.expiry_date) return false;
        const daysLeft = (new Date(b.expiry_date) - new Date()) / (1000 * 60 * 60 * 24);
        return daysLeft <= 10;
      }).length
    : METRICS.highRiskBatchesCount;

  return (
    <div className="space-y-6">
      {/* Non-intrusive error banner */}
      {error && (
        <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-between text-amber-800 text-xs font-medium">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-amber-600 shrink-0" />
            <span>{error}</span>
          </div>
          <button
            onClick={fetchDashboardData}
            className="flex items-center gap-1 text-xs font-bold text-amber-900 hover:underline cursor-pointer"
          >
            <RefreshCw className="w-3.5 h-3.5" /> Retry Sync
          </button>
        </div>
      )}

      {/* Loading Skeleton / Indicator Overlay during initial load */}
      {loading ? (
        <div className="p-8 rounded-2xl bg-white border border-slate-200/80 shadow-xs flex flex-col items-center justify-center text-slate-500 gap-3">
          <Loader2 className="w-8 h-8 animate-spin text-emerald-600" />
          <p className="text-xs font-semibold text-slate-700">Connecting to AgroFlow FastAPI telemetry...</p>
        </div>
      ) : (
        <>
          {/* 4 Core Stat Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              title="Total Cold Inventory"
              value={totalInventoryDisplay}
              subtext={inventoryData.length > 0 ? `${inventoryData.length} Live Warehouses` : METRICS.totalInventoryGrowth}
              icon={Warehouse}
              trend="+12.4%"
              trendType="positive"
              accentColor="emerald"
            />
            <StatCard
              title="Active Harvest Batches"
              value={activeBatchesDisplay}
              subtext={batchesData.length > 0 ? `${batchesData.length} Registered Batches` : METRICS.activeBatchesTrend}
              icon={Package}
              trend="+48 today"
              trendType="positive"
              accentColor="blue"
            />
            <StatCard
              title="Pending Wholesale Orders"
              value={pendingOrdersCountDisplay}
              subtext={`Valued at ${pendingOrdersValueDisplay}`}
              icon={ShoppingCart}
              accentColor="purple"
            />
            <StatCard
              title="High-Risk Spoilage Batches"
              value={highRiskBatchesCount}
              subtext={hasRealData ? `${highRiskBatchesCount} Batches Near Expiry` : METRICS.highRiskTrend}
              icon={AlertTriangle}
              trend="Action Needed"
              trendType="negative"
              accentColor="rose"
            />
          </div>

          {/* End-to-End Visual Pipeline */}
          <SupplyChainPipeline />

          {/* Charts Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <DemandForecastChart />
            <PriceForecastChart />
          </div>

          {/* Widgets Row 1: Spoilage Risk & Inventory Overview */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <SpoilageRiskOverview />
            <InventoryOverviewWidget inventory={inventoryData} />
          </div>

          {/* Widgets Row 2: Recent Orders & System Status Feed */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <RecentOrdersWidget orders={ordersData} />
            <SupplyChainStatusFeed shipments={shipmentsData} />
          </div>
        </>
      )}
    </div>
  );
};
