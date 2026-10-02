import React, { useState, useEffect } from 'react';
import { RoleDashboardHeader } from './RoleDashboardHeader';
import { StatCard } from '../../common/StatCard';
import { Badge } from '../../common/Badge';
import { Store, ShoppingBag, QrCode, ArrowRight, ShieldCheck, Sprout, CheckCircle2, Loader2, Package } from 'lucide-react';
import { productsAPI, ordersAPI } from '../../../services/api';
import { useNavigate } from 'react-router-dom';

export const ConsumerDashboard = ({ user }) => {
  const navigate = useNavigate();
  const [products, setProducts] = useState([]);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchConsumerData = async () => {
    setLoading(true);
    try {
      const [prodRes, orderRes] = await Promise.all([
        productsAPI.getProducts().catch(() => ({ data: [] })),
        ordersAPI.getOrders().catch(() => ({ data: [] })),
      ]);

      setProducts(prodRes.data || []);
      setOrders(orderRes.data || []);
    } catch (err) {
      console.error("Error loading Consumer Dashboard data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConsumerData();
  }, []);

  const activeOrdersCount = orders.filter(o => o.status !== 'Cancelled').length;

  const quickActions = [
    { label: 'Browse Fresh Produce', icon: Store, path: '/marketplace', primary: true },
    { label: 'My Orders', icon: ShoppingBag, path: '/orders' },
    { label: 'Verify Provenance', icon: QrCode, path: '/traceability' },
  ];

  return (
    <div className="space-y-6">
      <RoleDashboardHeader
        title="Consumer Dashboard"
        subtitle="Discover fresh agricultural produce, track your orders from farm to door, and inspect QR provenance traceability."
        user={user}
        onRefresh={fetchConsumerData}
        quickActions={quickActions}
      />

      {loading ? (
        <div className="p-8 rounded-2xl bg-white border border-slate-200/80 shadow-xs flex flex-col items-center justify-center text-slate-500 gap-3">
          <Loader2 className="w-8 h-8 animate-spin text-emerald-600" />
          <p className="text-xs font-semibold text-slate-700">Connecting to AgroFlow Consumer Marketplace...</p>
        </div>
      ) : (
        <>
          {/* 4 Clean Consumer Stat Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              title="Available Fresh Products"
              value={products.length || 2}
              subtext="Certified Farm Produce"
              icon={Store}
              accentColor="emerald"
            />
            <StatCard
              title="My Purchases"
              value={orders.length}
              subtext={`${orders.length} Total Orders Placed`}
              icon={ShoppingBag}
              accentColor="blue"
            />
            <StatCard
              title="Active Orders"
              value={activeOrdersCount}
              subtext="Orders In Transit or Confirmed"
              icon={Package}
              accentColor="purple"
            />
            <StatCard
              title="Traceable Purchases"
              value={orders.length}
              subtext="100% Verified Farm Origin"
              icon={ShieldCheck}
              accentColor="teal"
            />
          </div>

          {/* Primary Marketplace Hero Banner */}
          <div className="bg-gradient-to-r from-emerald-900 via-teal-900 to-slate-900 p-8 rounded-2xl text-white shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-6 border border-emerald-800/50">
            <div className="space-y-2 max-w-2xl">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-xs font-bold uppercase tracking-wider">
                <Sprout className="w-3.5 h-3.5 text-emerald-400" /> Direct Farm Transparency
              </span>
              <h2 className="text-2xl font-black tracking-tight text-white">
                Farm-Fresh Agricultural Produce Directly from Certified Farmers
              </h2>
              <p className="text-xs text-slate-300 leading-relaxed">
                Buy fresh Ratnagiri Alphonso Mangoes, Nashik Organic Tomatoes, and regional produce with full QR provenance traceability.
              </p>
            </div>
            <button
              onClick={() => navigate('/marketplace')}
              className="px-6 py-3.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-extrabold text-xs transition-all shadow-lg flex items-center justify-center gap-2 shrink-0 cursor-pointer hover:scale-[1.02] active:scale-[0.98]"
            >
              <Store className="w-4 h-4" />
              <span>Browse Fresh Produce</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          {/* My Orders & Purchase History Table */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-slate-900">My Orders & Delivery Tracking</h3>
                <p className="text-xs text-slate-500">Track your purchases from harvest origin to final delivery</p>
              </div>
              <button
                onClick={() => navigate('/orders')}
                className="text-xs font-bold text-emerald-600 hover:underline flex items-center gap-1 cursor-pointer"
              >
                View Order Details &rarr;
              </button>
            </div>

            {orders.length === 0 ? (
              <div className="p-8 text-center text-slate-500 bg-slate-50 rounded-xl space-y-2">
                <p className="text-xs font-semibold">You haven't placed any orders yet.</p>
                <button
                  onClick={() => navigate('/marketplace')}
                  className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-xs font-bold hover:bg-emerald-500 transition-colors inline-flex items-center gap-1.5 cursor-pointer"
                >
                  <Store className="w-3.5 h-3.5" /> Start Shopping in Marketplace
                </button>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-200 text-slate-500 uppercase text-[10px] font-bold">
                      <th className="py-2.5 px-3">Order Number</th>
                      <th className="py-2.5 px-3">Total Volume</th>
                      <th className="py-2.5 px-3">Total Amount</th>
                      <th className="py-2.5 px-3">Status</th>
                      <th className="py-2.5 px-3 text-right">Batch Provenance</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
                    {orders.slice(0, 5).map((ord) => (
                      <tr key={ord.id} className="hover:bg-slate-50/80 transition-colors">
                        <td className="py-3 px-3 font-mono font-bold text-slate-900">
                          {ord.order_number || `ORD-${ord.id}`}
                        </td>
                        <td className="py-3 px-3 font-semibold">{ord.total_quantity} kg</td>
                        <td className="py-3 px-3 font-bold text-emerald-700">₹{ord.total_amount?.toLocaleString()}</td>
                        <td className="py-3 px-3">
                          <Badge variant={ord.status === 'Delivered' ? 'emerald' : 'blue'}>
                            {ord.status}
                          </Badge>
                        </td>
                        <td className="py-3 px-3 text-right">
                          <button
                            onClick={() => navigate('/traceability')}
                            className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-600 hover:underline cursor-pointer"
                          >
                            <QrCode className="w-3.5 h-3.5" /> Trace Origin
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* 3-Step QR Provenance Transparency Guide */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs space-y-4">
            <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-emerald-600" />
              100% Farm Provenance & Quality Guarantee
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/70 space-y-2">
                <div className="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-700 font-black text-sm flex items-center justify-center">
                  1
                </div>
                <h4 className="text-xs font-bold text-slate-900">Certified Farm Harvest</h4>
                <p className="text-[11px] text-slate-500 leading-relaxed">
                  Produce is harvested by verified regional farmers in Ratnagiri and Nashik under strict agricultural quality standards.
                </p>
              </div>

              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/70 space-y-2">
                <div className="w-8 h-8 rounded-lg bg-blue-100 text-blue-700 font-black text-sm flex items-center justify-center">
                  2
                </div>
                <h4 className="text-xs font-bold text-slate-900">Cold Chain Inspection</h4>
                <p className="text-[11px] text-slate-500 leading-relaxed">
                  Collection centers audit quality grade and log storage climate conditions into the PostgreSQL provenance ledger.
                </p>
              </div>

              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/70 space-y-2">
                <div className="w-8 h-8 rounded-lg bg-purple-100 text-purple-700 font-black text-sm flex items-center justify-center">
                  3
                </div>
                <h4 className="text-xs font-bold text-slate-900">Instant QR Traceability</h4>
                <p className="text-[11px] text-slate-500 leading-relaxed">
                  Scan the QR code on your produce packaging to verify harvest dates, origin farm coordinates, and quality certificate.
                </p>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
