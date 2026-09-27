import React from 'react';
import { INVENTORY_ITEMS } from '../../data/mockData';
import { Badge } from '../common/Badge';
import { ArrowUpRight, Thermometer, Droplets } from 'lucide-react';
import { Link } from 'react-router-dom';

export const InventoryOverviewWidget = ({ inventory = [] }) => {
  // Use real backend inventory if available; fallback to mockData
  const displayItems = inventory.length > 0
    ? inventory.slice(0, 4).map((item) => ({
        id: item.id,
        cropName: item.batch?.product?.name || `Batch ${item.batch_id}`,
        location: item.warehouse_location,
        quantityDisplay: `${item.quantity} kg`,
        storageTemp: item.temperature != null ? `${item.temperature}°C` : 'N/A',
        humidity: item.humidity != null ? `${item.humidity}%` : 'N/A',
        status: item.temperature > 21 ? 'High Risk' : item.temperature > 19 ? 'Moderate' : 'Optimal',
      }))
    : INVENTORY_ITEMS.slice(0, 4).map((item) => ({
        id: item.id,
        cropName: item.cropName,
        location: item.location,
        quantityDisplay: `${item.quantityTons} Tons`,
        storageTemp: item.storageTemp,
        humidity: item.humidity,
        status: item.status,
      }));

  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-bold text-slate-900">Inventory Overview & Storage Status</h3>
              {inventory.length > 0 && (
                <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">
                  Real API Data
                </span>
              )}
            </div>
            <p className="text-xs text-slate-500">Live storage conditions in regional cold chain hubs</p>
          </div>
          <Link
            to="/inventory"
            className="text-xs font-semibold text-emerald-600 hover:text-emerald-700 flex items-center gap-0.5 hover:underline"
          >
            Manage All Inventory <ArrowUpRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-200 text-slate-500 font-semibold uppercase text-[10px]">
                <th className="pb-2.5">Crop / Commodity</th>
                <th className="pb-2.5">Location</th>
                <th className="pb-2.5">Stock</th>
                <th className="pb-2.5">Storage Temp</th>
                <th className="pb-2.5">Humidity</th>
                <th className="pb-2.5">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {displayItems.map((item) => (
                <tr key={item.id} className="hover:bg-slate-50 transition-colors">
                  <td className="py-2.5 font-bold text-slate-900">{item.cropName}</td>
                  <td className="py-2.5 text-slate-600">{item.location}</td>
                  <td className="py-2.5 font-semibold text-slate-900">{item.quantityDisplay}</td>
                  <td className="py-2.5 text-slate-700">
                    <span className="inline-flex items-center gap-1">
                      <Thermometer className="w-3 h-3 text-emerald-600" /> {item.storageTemp}
                    </span>
                  </td>
                  <td className="py-2.5 text-slate-700">
                    <span className="inline-flex items-center gap-1">
                      <Droplets className="w-3 h-3 text-blue-500" /> {item.humidity}
                    </span>
                  </td>
                  <td className="py-2.5">
                    <Badge
                      variant={
                        item.status === 'Optimal'
                          ? 'emerald'
                          : item.status === 'Moderate' || item.status === 'High Risk'
                          ? 'amber'
                          : 'red'
                      }
                    >
                      {item.status}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
