import React from 'react';
import { ORDERS } from '../../data/mockData';
import { Badge } from '../common/Badge';
import { ArrowUpRight } from 'lucide-react';
import { Link } from 'react-router-dom';

export const RecentOrdersWidget = ({ orders = [] }) => {
  const displayOrders = orders.length > 0
    ? orders.slice(0, 3).map((order) => {
        let progressPercent = 35;
        if (order.status === 'Delivered') progressPercent = 100;
        else if (order.status === 'In Transit' || order.status === 'Dispatched') progressPercent = 70;
        else if (order.status === 'Processing') progressPercent = 45;

        const cropItems = order.items && order.items.length > 0
          ? order.items.map(item => item.product?.name || 'Agro Produce').join(', ')
          : 'Produce Wholesale Batch';

        return {
          id: order.order_number || `ORD-${order.id}`,
          status: order.status,
          customer: order.buyer?.name || 'Retail Partner',
          totalValue: `₹${order.total_amount ? order.total_amount.toLocaleString() : 0}`,
          cropItems: cropItems,
          expectedDelivery: new Date(order.order_date || Date.now()).toLocaleDateString(),
          progressPercent: progressPercent,
        };
      })
    : ORDERS.slice(0, 3);

  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-bold text-slate-900">Recent Purchase & Retail Orders</h3>
              {orders.length > 0 && (
                <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">
                  Real API Data
                </span>
              )}
            </div>
            <p className="text-xs text-slate-500">Live order fulfillment and transit status</p>
          </div>
          <Link
            to="/orders"
            className="text-xs font-semibold text-emerald-600 hover:text-emerald-700 flex items-center gap-0.5 hover:underline"
          >
            View All Orders <ArrowUpRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="space-y-3">
          {displayOrders.map((order) => (
            <div
              key={order.id}
              className="p-3.5 rounded-xl border border-slate-200/80 bg-slate-50/50 hover:bg-white hover:shadow-xs transition-all"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs font-bold text-slate-900">{order.id}</span>
                  <Badge
                    variant={
                      order.status === 'In-Transit' || order.status === 'In Transit' || order.status === 'Dispatched'
                        ? 'blue'
                        : order.status === 'Processing' || order.status === 'Confirmed'
                        ? 'amber'
                        : order.status === 'Delivered'
                        ? 'emerald'
                        : 'purple'
                    }
                  >
                    {order.status}
                  </Badge>
                </div>
                <span className="text-xs font-extrabold text-slate-900">{order.totalValue}</span>
              </div>

              <div className="mt-2 flex items-center justify-between text-xs text-slate-600">
                <span className="font-semibold text-slate-800 truncate max-w-[200px]">{order.customer}</span>
                <span className="text-[11px] text-slate-500">Order Date: {order.expectedDelivery}</span>
              </div>

              <p className="text-[11px] text-slate-500 mt-1 line-clamp-1">{order.cropItems}</p>

              {/* Transit progress bar */}
              <div className="mt-2.5 flex items-center gap-2 text-[10px] text-slate-500">
                <div className="flex-1 bg-slate-200 h-1.5 rounded-full overflow-hidden">
                  <div
                    className="bg-emerald-600 h-full rounded-full transition-all"
                    style={{ width: `${order.progressPercent}%` }}
                  ></div>
                </div>
                <span className="font-mono font-bold text-slate-700">{order.progressPercent}%</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
