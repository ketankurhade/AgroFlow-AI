import React, { useState, useEffect } from 'react';
import { RoleDashboardHeader } from './RoleDashboardHeader';
import { StatCard } from '../../common/StatCard';
import { Badge } from '../../common/Badge';
import { DemandForecastChart } from '../DemandForecastChart';
import { PriceForecastChart } from '../PriceForecastChart';
import { SpoilageRiskOverview } from '../SpoilageRiskOverview';
import { InventoryOverviewWidget } from '../InventoryOverviewWidget';
import { Package, Warehouse, ShoppingCart, AlertTriangle, Plus, QrCode, Sprout, Calendar, ExternalLink, Loader2 } from 'lucide-react';
import { batchesAPI, inventoryAPI, ordersAPI, spoilageAPI } from '../../../services/api';
import { useNavigate } from 'react-router-dom';

export const FarmerDashboard = ({ user }) => {
  const navigate = useNavigate();
  const [batches, setBatches] = useState([]);
  const [inventory, setInventory] = useState([]);
  const [orders, setOrders] = useState([]);
  const [spoilageSummary, setSpoilageSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchFarmerData = async () => {
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
      console.error("Error loading Farmer Dashboard telemetry:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFarmerData();
  }, []);

  const totalHarvestedKg = batches.reduce((acc, item) => acc + (item.quantity || 0), 0);
  const totalHarvestedDisplay = totalHarvestedKg >= 1000
    ? `${(totalHarvestedKg / 1000).toFixed(1)} Tons`
    : `${totalHarvestedKg.toLocaleString()} kg`;

  const highRiskCount = spoilageSummary?.high_risk_count ?? batches.filter(b => {
    if (!b.expiry_date) return false;
    const daysLeft = (new Date(b.expiry_date) - new Date()) / (1000 * 60 * 60 * 24);
    return daysLeft <= 5;
  }).length;

  const quickActions = [
    { label: 'Create Harvest Batch', icon: Plus, path: '/batches', primary: true },
    { label: 'My Batches', icon: Package, path: '/batches' },
    { label: 'QR Traceability', icon: QrCode, path: '/traceability' },
  ];

  return (
    <div className="space-y-6">
      <RoleDashboardHeader
        title="Farmer Dashboard"
        subtitle="Monitor your registered harvest produce, crop batches, price trends, and batch provenance."
        user={user}
        onRefresh={fetchFarmerData}
        quickActions={quickActions}
      />

      {loading ? (
        <div className="p-8 rounded-2xl bg-white border border-slate-200/80 shadow-xs flex flex-col items-center justify-center text-slate-500 gap-3">
          <Loader2 className="w-8 h-8 animate-spin text-emerald-600" />
          <p className="text-xs font-semibold text-slate-700">Loading farmer harvest telemetry...</p>
        </div>
      ) : (
        <>
          {/* 4 Stat Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              title="My Active Batches"
              value={batches.length}
              subtext={`${batches.length} Registered Lots`}
              icon={Package}
              accentColor="emerald"
            />
            <StatCard
              title="Total Produce Harvested"
              value={totalHarvestedDisplay}
              subtext={`${batches.length} Harvest Batches`}
              icon={Sprout}
              accentColor="blue"
            />
            <StatCard
              title="Produce Near Expiry / Risk"
              value={highRiskCount}
              subtext={`${highRiskCount} Batches Require Attention`}
              icon={AlertTriangle}
              accentColor="rose"
            />
            <StatCard
              title="Produce Orders"
              value={orders.length}
              subtext={`${orders.length} Buyer Orders`}
              icon={ShoppingCart}
              accentColor="purple"
            />
          </div>

          {/* My Harvest Batches Table */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-slate-900">My Registered Harvest Batches</h3>
                <p className="text-xs text-slate-500">Live harvest origin records stored in PostgreSQL</p>
              </div>
              <button
                onClick={() => navigate('/batches')}
                className="text-xs font-bold text-emerald-600 hover:underline flex items-center gap-1"
              >
                View All Batches &rarr;
              </button>
            </div>

            {batches.length === 0 ? (
              <div className="p-6 text-center text-slate-500 bg-slate-50 rounded-xl text-xs">
                No active harvest batches registered yet. Click "Create Harvest Batch" above to add your first lot.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-200 text-slate-500 uppercase text-[10px] font-bold">
                      <th className="py-2.5 px-3">Batch Code</th>
                      <th className="py-2.5 px-3">Crop / Product</th>
                      <th className="py-2.5 px-3">Quantity</th>
                      <th className="py-2.5 px-3">Grade</th>
                      <th className="py-2.5 px-3">Harvest Date</th>
                      <th className="py-2.5 px-3">Expiry Date</th>
                      <th className="py-2.5 px-3">Status</th>
                      <th className="py-2.5 px-3 text-right">Traceability</th>
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
                        <td className="py-3 px-3 text-slate-500">{batch.harvest_date}</td>
                        <td className="py-3 px-3 text-slate-500">{batch.expiry_date}</td>
                        <td className="py-3 px-3 font-semibold text-emerald-700">{batch.status}</td>
                        <td className="py-3 px-3 text-right">
                          <button
                            onClick={() => navigate(`/traceability?batch=${batch.batch_code || batch.id}`)}
                            className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-600 hover:underline cursor-pointer"
                          >
                            <QrCode className="w-3.5 h-3.5" /> Trace
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Forecasting Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <DemandForecastChart />
            <PriceForecastChart />
          </div>

          {/* Spoilage & Inventory */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <SpoilageRiskOverview />
            <InventoryOverviewWidget inventory={inventory} />
          </div>
        </>
      )}
    </div>
  );
};
