import React, { useState, useEffect } from 'react';
import { RoleDashboardHeader } from './RoleDashboardHeader';
import { StatCard } from '../../common/StatCard';
import { Badge } from '../../common/Badge';
import { SpoilageRiskOverview } from '../SpoilageRiskOverview';
import { InventoryOverviewWidget } from '../InventoryOverviewWidget';
import { RecentOrdersWidget } from '../RecentOrdersWidget';
import { Package, Warehouse, ShoppingCart, AlertTriangle, Plus, QrCode, ClipboardCheck, Loader2 } from 'lucide-react';
import { batchesAPI, inventoryAPI, ordersAPI, spoilageAPI } from '../../../services/api';
import { useNavigate } from 'react-router-dom';

export const CollectionCenterDashboard = ({ user }) => {
  const navigate = useNavigate();
  const [batches, setBatches] = useState([]);
  const [inventory, setInventory] = useState([]);
  const [orders, setOrders] = useState([]);
  const [spoilageSummary, setSpoilageSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchCollectionCenterData = async () => {
    setLoading(true);
    try {
      const [batchRes, invRes, orderRes, spoilRes] = await Promise.all([
        batchesAPI.getBatches().catch(() => ({ data: [] })),
        inventoryAPI.getInventory().catch(() => ({ data: [] })),
        ordersAPI.getOrders().catch(() => ({ data: [] })),
        spoilageAPI.getSummary().catch(() => ({ data: null })),
      ]);

      setBatches(batchRes.data || []);
      setInventory(invRes.data || []);
      setOrders(orderRes.data || []);
      setSpoilageSummary(spoilRes.data || null);
    } catch (err) {
      console.error("Error loading Collection Center telemetry:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCollectionCenterData();
  }, []);

  const totalInventoryKg = inventory.reduce((acc, item) => acc + (item.quantity || 0), 0);
  const totalInventoryDisplay = totalInventoryKg >= 1000
    ? `${(totalInventoryKg / 1000).toFixed(1)} Tons`
    : `${totalInventoryKg.toLocaleString()} kg`;

  const highRiskCount = spoilageSummary?.high_risk_count || 0;

  const quickActions = [
    { label: 'Register New Batch', icon: Plus, path: '/batches', primary: true },
    { label: 'Add Storage Inventory', icon: Warehouse, path: '/inventory' },
    { label: 'Inspect Traceability', icon: QrCode, path: '/traceability' },
  ];

  return (
    <div className="space-y-6">
      <RoleDashboardHeader
        title="Collection Center Dashboard"
        subtitle="Manage regional produce intake, quality inspection grading, cold storage inventory, and distribution dispatches."
        user={user}
        onRefresh={fetchCollectionCenterData}
        quickActions={quickActions}
      />

      {loading ? (
        <div className="p-8 rounded-2xl bg-white border border-slate-200/80 shadow-xs flex flex-col items-center justify-center text-slate-500 gap-3">
          <Loader2 className="w-8 h-8 animate-spin text-emerald-600" />
          <p className="text-xs font-semibold text-slate-700">Connecting to Collection Center intake telemetry...</p>
        </div>
      ) : (
        <>
          {/* 4 Stat Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              title="Incoming / Active Batches"
              value={batches.length}
              subtext={`${batches.length} Registered Lots`}
              icon={Package}
              accentColor="emerald"
            />
            <StatCard
              title="Inventory Under Handling"
              value={totalInventoryDisplay}
              subtext={`${inventory.length} Storage Lots`}
              icon={Warehouse}
              accentColor="blue"
            />
            <StatCard
              title="Orders Requiring Attention"
              value={orders.length}
              subtext={`${orders.length} Active Orders`}
              icon={ShoppingCart}
              accentColor="purple"
            />
            <StatCard
              title="High Spoilage Risk Lots"
              value={highRiskCount}
              subtext={`${highRiskCount} Lots Require Priority`}
              icon={AlertTriangle}
              accentColor="rose"
            />
          </div>

          {/* Batch Intake & Quality Grading Section */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-slate-900">Produce Intake & Quality Audit Schedule</h3>
                <p className="text-xs text-slate-500">Batches undergoing intake verification and cold storage assignment</p>
              </div>
              <button
                onClick={() => navigate('/batches')}
                className="text-xs font-bold text-emerald-600 hover:underline flex items-center gap-1 cursor-pointer"
              >
                Intake Register &rarr;
              </button>
            </div>

            {batches.length === 0 ? (
              <div className="p-6 text-center text-slate-500 bg-slate-50 rounded-xl text-xs">
                No active intake batches registered. Use the "Register New Batch" button above to record intake.
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

          {/* Spoilage & Storage Monitoring */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <SpoilageRiskOverview />
            <InventoryOverviewWidget inventory={inventory} />
          </div>

          {/* Orders Section */}
          <RecentOrdersWidget orders={orders} />
        </>
      )}
    </div>
  );
};
