import React, { useState, useEffect } from 'react';
import { RoleDashboardHeader } from './RoleDashboardHeader';
import { StatCard } from '../../common/StatCard';
import { Badge } from '../../common/Badge';
import { SpoilageRiskOverview } from '../SpoilageRiskOverview';
import { InventoryOverviewWidget } from '../InventoryOverviewWidget';
import { SupplyChainStatusFeed } from '../SupplyChainStatusFeed';
import { DemandForecastChart } from '../DemandForecastChart';
import { PriceForecastChart } from '../PriceForecastChart';
import {
  Warehouse,
  Package,
  Truck,
  AlertTriangle,
  Navigation,
  ArrowRight,
  Thermometer,
  Droplets,
  Plus,
  QrCode,
  Loader2
} from 'lucide-react';
import { inventoryAPI, batchesAPI, shipmentsAPI, spoilageAPI, ordersAPI } from '../../../services/api';
import { useNavigate } from 'react-router-dom';

export const SupplyChainManagerDashboard = ({ user }) => {
  const navigate = useNavigate();
  const [inventory, setInventory] = useState([]);
  const [batches, setBatches] = useState([]);
  const [shipments, setShipments] = useState([]);
  const [orders, setOrders] = useState([]);
  const [spoilageSummary, setSpoilageSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchManagerData = async () => {
    setLoading(true);
    try {
      const [invRes, batchRes, shipRes, spoilRes, orderRes] = await Promise.all([
        inventoryAPI.getInventory().catch(() => ({ data: [] })),
        batchesAPI.getBatches().catch(() => ({ data: [] })),
        shipmentsAPI.getShipments().catch(() => ({ data: [] })),
        spoilageAPI.getSummary().catch(() => ({ data: null })),
        ordersAPI.getOrders().catch(() => ({ data: [] })),
      ]);

      setInventory(invRes.data || []);
      setBatches(batchRes.data || []);
      setShipments(shipRes.data || []);
      setSpoilageSummary(spoilRes.data || null);
      setOrders(orderRes.data || []);
    } catch (err) {
      console.error("Error loading Supply Chain Manager telemetry:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchManagerData();
  }, []);

  const totalInventoryKg = inventory.reduce((acc, item) => acc + (item.quantity || 0), 0);
  const totalInventoryDisplay = totalInventoryKg >= 1000
    ? `${(totalInventoryKg / 1000).toFixed(1)} Tons`
    : `${totalInventoryKg.toLocaleString()} kg`;

  const pendingShipmentsCount = shipments.filter(s => s.status !== 'Delivered').length || shipments.length;
  const highRiskCount = spoilageSummary?.high_risk_count || 0;

  const quickActions = [
    { label: 'Register New Batch', icon: Plus, path: '/batches', primary: true },
    { label: 'Manage Inventory', icon: Warehouse, path: '/inventory' },
    { label: 'Route Optimization', icon: Navigation, path: '/routes' },
    { label: 'Spoilage Risk', icon: AlertTriangle, path: '/risk' },
    { label: 'Inspect Traceability', icon: QrCode, path: '/traceability' },
  ];

  return (
    <div className="space-y-6">
      <RoleDashboardHeader
        title="Supply Chain / Storage Manager Dashboard"
        subtitle="Consolidated regional produce intake, quality inspection grading, cold storage inventory telemetry, and outbound dispatch operations."
        user={user}
        onRefresh={fetchManagerData}
        quickActions={quickActions}
      />

      {loading ? (
        <div className="p-8 rounded-2xl bg-white border border-slate-200/80 shadow-xs flex flex-col items-center justify-center text-slate-500 gap-3">
          <Loader2 className="w-8 h-8 animate-spin text-emerald-600" />
          <p className="text-xs font-semibold text-slate-700">Connecting to Supply Chain Manager telemetry...</p>
        </div>
      ) : (
        <>
          {/* 4 Stat Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              title="Total Stored Inventory"
              value={totalInventoryDisplay}
              subtext={`${inventory.length} Storage Lots`}
              icon={Warehouse}
              accentColor="emerald"
            />
            <StatCard
              title="Intake & Stored Batches"
              value={batches.length}
              subtext={`${batches.length} Registered Batches`}
              icon={Package}
              accentColor="blue"
            />
            <StatCard
              title="High-Risk Spoilage Batches"
              value={highRiskCount}
              subtext={`${highRiskCount} Near Expiry Lots`}
              icon={AlertTriangle}
              accentColor="rose"
            />
            <StatCard
              title="Active Outbound Dispatches"
              value={pendingShipmentsCount}
              subtext={`${shipments.length} Total Shipments`}
              icon={Truck}
              accentColor="purple"
            />
          </div>

          {/* Incoming Batch Intake & Audit Schedule Table */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-slate-900">Produce Intake & Quality Audit Schedule</h3>
                <p className="text-xs text-slate-500">Batches undergoing intake verification, grading, and cold storage assignment</p>
              </div>
              <button
                onClick={() => navigate('/batches')}
                className="text-xs font-bold text-emerald-600 hover:underline flex items-center gap-1 cursor-pointer"
              >
                Batch Register &rarr;
              </button>
            </div>

            {batches.length === 0 ? (
              <div className="p-6 text-center text-slate-500 bg-slate-50 rounded-xl text-xs">
                No active intake batches registered. Use the "Register New Batch" button above.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-200 text-slate-500 uppercase text-[10px] font-bold">
                      <th className="py-2.5 px-3">Batch Code</th>
                      <th className="py-2.5 px-3">Produce</th>
                      <th className="py-2.5 px-3">Intake Qty</th>
                      <th className="py-2.5 px-3">Certified Grade</th>
                      <th className="py-2.5 px-3">Origin Farm</th>
                      <th className="py-2.5 px-3">Harvest Date</th>
                      <th className="py-2.5 px-3">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
                    {batches.slice(0, 5).map((batch) => (
                      <tr key={batch.id} className="hover:bg-slate-50/80 transition-colors">
                        <td className="py-3 px-3 font-mono font-bold text-slate-900">
                          {batch.batch_code || `BATCH-${batch.id}`}
                        </td>
                        <td className="py-3 px-3 font-bold text-slate-900">
                          {batch.product?.name || `Product #${batch.product_id}`}
                        </td>
                        <td className="py-3 px-3 font-semibold">{batch.quantity} kg</td>
                        <td className="py-3 px-3">
                          <Badge variant="emerald">{batch.quality_grade || 'Grade A'}</Badge>
                        </td>
                        <td className="py-3 px-3 text-slate-600">{batch.origin_location}</td>
                        <td className="py-3 px-3 text-slate-500">{batch.harvest_date}</td>
                        <td className="py-3 px-3 font-semibold text-emerald-700">{batch.status}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Cold Storage Bays & Climate Telemetry Table */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-slate-900">Cold Storage Bays & Environmental Telemetry</h3>
                <p className="text-xs text-slate-500">Live storage facility records, ambient temperatures, and humidity readings</p>
              </div>
              <button
                onClick={() => navigate('/inventory')}
                className="text-xs font-bold text-emerald-600 hover:underline flex items-center gap-1 cursor-pointer"
              >
                Inventory Bay Manager &rarr;
              </button>
            </div>

            {inventory.length === 0 ? (
              <div className="p-6 text-center text-slate-500 bg-slate-50 rounded-xl text-xs">
                No active storage inventory records registered.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-200 text-slate-500 uppercase text-[10px] font-bold">
                      <th className="py-2.5 px-3">Lot ID</th>
                      <th className="py-2.5 px-3">Storage Location / Bay</th>
                      <th className="py-2.5 px-3">Associated Batch</th>
                      <th className="py-2.5 px-3">Stock Quantity</th>
                      <th className="py-2.5 px-3">Storage Temp</th>
                      <th className="py-2.5 px-3">Humidity</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
                    {inventory.slice(0, 5).map((item) => (
                      <tr key={item.id} className="hover:bg-slate-50/80 transition-colors">
                        <td className="py-3 px-3 font-mono font-bold text-slate-900">
                          LOT-{item.id}
                        </td>
                        <td className="py-3 px-3 font-bold text-slate-900">
                          {item.warehouse_location}
                        </td>
                        <td className="py-3 px-3 font-mono text-slate-600">
                          {item.batch?.batch_code || `BATCH-${item.batch_id}`}
                        </td>
                        <td className="py-3 px-3 font-semibold">{item.quantity} kg</td>
                        <td className="py-3 px-3">
                          <span className="inline-flex items-center gap-1 font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded-md">
                            <Thermometer className="w-3 h-3 text-blue-600" />
                            {item.temperature}°C
                          </span>
                        </td>
                        <td className="py-3 px-3">
                          <span className="inline-flex items-center gap-1 font-bold text-teal-700 bg-teal-50 px-2 py-0.5 rounded-md">
                            <Droplets className="w-3 h-3 text-teal-600" />
                            {item.humidity}%
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>



          {/* Spoilage & Inventory Overview */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <SpoilageRiskOverview />
            <InventoryOverviewWidget inventory={inventory} />
          </div>

          {/* Forecasts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <DemandForecastChart />
            <PriceForecastChart />
          </div>

          {/* Shipments Status Feed */}
          <SupplyChainStatusFeed shipments={shipments} />
        </>
      )}
    </div>
  );
};
