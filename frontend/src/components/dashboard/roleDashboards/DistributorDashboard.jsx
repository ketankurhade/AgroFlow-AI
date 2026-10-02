import React, { useState, useEffect } from 'react';
import { RoleDashboardHeader } from './RoleDashboardHeader';
import { StatCard } from '../../common/StatCard';
import { Badge } from '../../common/Badge';
import { RecentOrdersWidget } from '../RecentOrdersWidget';
import { DemandForecastChart } from '../DemandForecastChart';
import { Truck, ShoppingCart, Navigation, Warehouse, ArrowRight, MapPin, QrCode, Loader2 } from 'lucide-react';
import { ordersAPI, shipmentsAPI, inventoryAPI, routesAPI } from '../../../services/api';
import { useNavigate } from 'react-router-dom';

export const DistributorDashboard = ({ user }) => {
  const navigate = useNavigate();
  const [orders, setOrders] = useState([]);
  const [shipments, setShipments] = useState([]);
  const [inventory, setInventory] = useState([]);
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchDistributorData = async () => {
    setLoading(true);
    try {
      const [orderRes, shipRes, invRes, locRes] = await Promise.all([
        ordersAPI.getOrders().catch(() => ({ data: [] })),
        shipmentsAPI.getShipments().catch(() => ({ data: [] })),
        inventoryAPI.getInventory().catch(() => ({ data: [] })),
        routesAPI.getSupportedLocations().catch(() => ({ data: [] })),
      ]);

      setOrders(orderRes.data || []);
      setShipments(shipRes.data || []);
      setInventory(invRes.data || []);
      setLocations(locRes.data || []);
    } catch (err) {
      console.error("Error loading Distributor Dashboard telemetry:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDistributorData();
  }, []);

  const totalInventoryKg = inventory.reduce((acc, item) => acc + (item.quantity || 0), 0);
  const totalInventoryDisplay = totalInventoryKg >= 1000
    ? `${(totalInventoryKg / 1000).toFixed(1)} Tons`
    : `${totalInventoryKg.toLocaleString()} kg`;

  const activeShipmentsCount = shipments.filter(s => s.status !== 'Delivered').length || shipments.length;

  const quickActions = [
    { label: 'Wholesale Orders', icon: ShoppingCart, path: '/orders', primary: true },
    { label: 'Route Optimization', icon: Navigation, path: '/routes' },
    { label: 'QR Traceability', icon: QrCode, path: '/traceability' },
  ];

  return (
    <div className="space-y-6">
      <RoleDashboardHeader
        title="Distributor Dashboard"
        subtitle="Manage wholesale order dispatch, cold-chain transport fleet, route sequence optimization, and regional node deliveries."
        user={user}
        onRefresh={fetchDistributorData}
        quickActions={quickActions}
      />

      {loading ? (
        <div className="p-8 rounded-2xl bg-white border border-slate-200/80 shadow-xs flex flex-col items-center justify-center text-slate-500 gap-3">
          <Loader2 className="w-8 h-8 animate-spin text-emerald-600" />
          <p className="text-xs font-semibold text-slate-700">Connecting to Distribution Fleet telemetry...</p>
        </div>
      ) : (
        <>
          {/* 4 Stat Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              title="Pending Wholesale Orders"
              value={orders.length}
              subtext={`${orders.length} Registered Orders`}
              icon={ShoppingCart}
              accentColor="purple"
            />
            <StatCard
              title="Active Shipments"
              value={activeShipmentsCount}
              subtext={`${shipments.length} Total Logistics Shipments`}
              icon={Truck}
              accentColor="emerald"
            />
            <StatCard
              title="Stock In Distribution"
              value={totalInventoryDisplay}
              subtext={`${inventory.length} Stock Batches`}
              icon={Warehouse}
              accentColor="blue"
            />
            <StatCard
              title="Supported Route Stops"
              value={locations.length || 9}
              subtext="Maharashtra Transport Grid"
              icon={Navigation}
              accentColor="teal"
            />
          </div>

          {/* Route Optimization Prominent Hero Banner */}
          <div className="bg-gradient-to-br from-emerald-950 via-slate-900 to-slate-950 p-6 rounded-2xl text-white border border-emerald-900/50 shadow-lg flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <span className="p-1.5 rounded-lg bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                  <Navigation className="w-5 h-5" />
                </span>
                <h3 className="text-lg font-extrabold text-white">Google OR-Tools Route Optimizer</h3>
              </div>
              <p className="text-xs text-slate-300 max-w-xl leading-relaxed">
                Solve the Traveling Salesperson Problem (TSP) across Ratnagiri, Pune, Mumbai, Nashik, and regional hubs to minimize transit duration and cold chain spoilage.
              </p>
            </div>
            <button
              onClick={() => navigate('/routes')}
              className="px-5 py-3 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-extrabold text-xs transition-all shadow-lg flex items-center justify-center gap-2 cursor-pointer shrink-0"
            >
              <span>Optimize Route Sequence</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          {/* Active Shipments Table */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-slate-900">Distribution Logistics & Shipments</h3>
                <p className="text-xs text-slate-500">Live outbound shipment dispatches and reefer vehicle tracking</p>
              </div>
              <button
                onClick={() => navigate('/orders')}
                className="text-xs font-bold text-emerald-600 hover:underline flex items-center gap-1 cursor-pointer"
              >
                View Orders & Shipments &rarr;
              </button>
            </div>

            {shipments.length === 0 ? (
              <div className="p-6 text-center text-slate-500 bg-slate-50 rounded-xl text-xs">
                No active logistics shipments recorded.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-200 text-slate-500 uppercase text-[10px] font-bold">
                      <th className="py-2.5 px-3">Shipment ID</th>
                      <th className="py-2.5 px-3">Order #</th>
                      <th className="py-2.5 px-3">Source Facility</th>
                      <th className="py-2.5 px-3">Destination Node</th>
                      <th className="py-2.5 px-3">Reefer Vehicle</th>
                      <th className="py-2.5 px-3">Dispatch Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
                    {shipments.slice(0, 5).map((ship) => (
                      <tr key={ship.id} className="hover:bg-slate-50/80 transition-colors">
                        <td className="py-3 px-3 font-mono font-bold text-slate-900">
                          SHIP-{ship.id}
                        </td>
                        <td className="py-3 px-3 font-mono text-slate-600">
                          {ship.order?.order_number || `ORD-${ship.order_id}`}
                        </td>
                        <td className="py-3 px-3 font-semibold text-slate-900">{ship.source}</td>
                        <td className="py-3 px-3 text-slate-900 font-bold">{ship.destination}</td>
                        <td className="py-3 px-3">
                          <span className="font-mono text-slate-600">{ship.vehicle_number}</span>
                        </td>
                        <td className="py-3 px-3">
                          <Badge variant={ship.status === 'In Transit' ? 'emerald' : 'blue'}>
                            {ship.status}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Orders & Demand Forecast */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <RecentOrdersWidget orders={orders} />
            <DemandForecastChart />
          </div>
        </>
      )}
    </div>
  );
};
