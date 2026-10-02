import React, { useState, useEffect } from 'react';
import { RoleDashboardHeader } from './RoleDashboardHeader';
import { StatCard } from '../../common/StatCard';
import { Badge } from '../../common/Badge';
import { DemandForecastChart } from '../DemandForecastChart';
import { PriceForecastChart } from '../PriceForecastChart';
import { ShoppingCart, Warehouse, Store, Truck, ArrowRight, QrCode, Plus, Loader2 } from 'lucide-react';
import { ordersAPI, inventoryAPI, productsAPI, shipmentsAPI } from '../../../services/api';
import { useNavigate } from 'react-router-dom';

export const RetailerDashboard = ({ user }) => {
  const navigate = useNavigate();
  const [orders, setOrders] = useState([]);
  const [inventory, setInventory] = useState([]);
  const [products, setProducts] = useState([]);
  const [shipments, setShipments] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchRetailerData = async () => {
    setLoading(true);
    try {
      const [orderRes, invRes, prodRes, shipRes] = await Promise.all([
        ordersAPI.getOrders().catch(() => ({ data: [] })),
        inventoryAPI.getInventory().catch(() => ({ data: [] })),
        productsAPI.getProducts().catch(() => ({ data: [] })),
        shipmentsAPI.getShipments().catch(() => ({ data: [] })),
      ]);

      setOrders(orderRes.data || []);
      setInventory(invRes.data || []);
      setProducts(prodRes.data || []);
      setShipments(shipRes.data || []);
    } catch (err) {
      console.error("Error loading Retailer Dashboard telemetry:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRetailerData();
  }, []);

  const totalInventoryKg = inventory.reduce((acc, item) => acc + (item.quantity || 0), 0);
  const totalInventoryDisplay = totalInventoryKg >= 1000
    ? `${(totalInventoryKg / 1000).toFixed(1)} Tons`
    : `${totalInventoryKg.toLocaleString()} kg`;

  const quickActions = [
    { label: 'Create Wholesale Order', icon: ShoppingCart, path: '/orders', primary: true },
    { label: 'Consumer Marketplace', icon: Store, path: '/marketplace' },
    { label: 'Store Inventory', icon: Warehouse, path: '/inventory' },
    { label: 'Verify Batch Origin', icon: QrCode, path: '/traceability' },
  ];

  return (
    <div className="space-y-6">
      <RoleDashboardHeader
        title="Retailer Dashboard"
        subtitle="Manage wholesale produce orders, retail store inventory, incoming dispatches, and consumer marketplace offerings."
        user={user}
        onRefresh={fetchRetailerData}
        quickActions={quickActions}
      />

      {loading ? (
        <div className="p-8 rounded-2xl bg-white border border-slate-200/80 shadow-xs flex flex-col items-center justify-center text-slate-500 gap-3">
          <Loader2 className="w-8 h-8 animate-spin text-emerald-600" />
          <p className="text-xs font-semibold text-slate-700">Connecting to Retailer inventory telemetry...</p>
        </div>
      ) : (
        <>
          {/* 4 Stat Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              title="My Wholesale Orders"
              value={orders.length}
              subtext={`${orders.length} Placed Orders`}
              icon={ShoppingCart}
              accentColor="emerald"
            />
            <StatCard
              title="Available Stock"
              value={totalInventoryDisplay}
              subtext={`${inventory.length} Warehouse Lots`}
              icon={Warehouse}
              accentColor="blue"
            />
            <StatCard
              title="Inbound Shipments"
              value={shipments.length}
              subtext={`${shipments.length} Dispatched Reefer Trucks`}
              icon={Truck}
              accentColor="purple"
            />
            <StatCard
              title="Marketplace Products"
              value={products.length}
              subtext={`${products.length} Active Catalog Items`}
              icon={Store}
              accentColor="teal"
            />
          </div>

          {/* Marketplace Procurement Hero Banner */}
          <div className="bg-gradient-to-r from-teal-900 via-slate-900 to-emerald-950 p-6 rounded-2xl text-white shadow-lg flex flex-col md:flex-row md:items-center justify-between gap-4 border border-teal-900/50">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="p-1.5 rounded-lg bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                  <Store className="w-4 h-4" />
                </span>
                <h4 className="text-base font-bold text-white">Direct Farm Produce Procurement</h4>
              </div>
              <p className="text-xs text-slate-300 max-w-xl">
                Source Grade-A Alphonso Mangoes, Tomatoes, and fresh produce directly from verified farmers in the AgroFlow Marketplace.
              </p>
            </div>
            <button
              onClick={() => navigate('/marketplace')}
              className="flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs transition-all shadow-md shrink-0 cursor-pointer"
            >
              <span>Browse Consumer Marketplace</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          {/* My Wholesale Orders Table */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-slate-900">My Wholesale Orders & Delivery Status</h3>
                <p className="text-xs text-slate-500">Retail store supply orders placed with collection centers and distributors</p>
              </div>
              <button
                onClick={() => navigate('/orders')}
                className="text-xs font-bold text-emerald-600 hover:underline flex items-center gap-1 cursor-pointer"
              >
                View All Orders &rarr;
              </button>
            </div>

            {orders.length === 0 ? (
              <div className="p-6 text-center text-slate-500 bg-slate-50 rounded-xl text-xs">
                No wholesale orders placed yet. Click "Create Wholesale Order" above to place your first order.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-200 text-slate-500 uppercase text-[10px] font-bold">
                      <th className="py-2.5 px-3">Order Number</th>
                      <th className="py-2.5 px-3">Total Quantity</th>
                      <th className="py-2.5 px-3">Total Amount</th>
                      <th className="py-2.5 px-3">Status</th>
                      <th className="py-2.5 px-3">Order Date</th>
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
                        <td className="py-3 px-3 text-slate-500">
                          {ord.created_at ? new Date(ord.created_at).toLocaleDateString() : 'Recent'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Forecasts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <PriceForecastChart />
            <DemandForecastChart />
          </div>
        </>
      )}
    </div>
  );
};
