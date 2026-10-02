import React, { useState, useEffect } from 'react';
import { Badge } from '../components/common/Badge';
import { Search, Plus, Warehouse, Thermometer, Calendar, AlertTriangle, Loader2, AlertCircle, CheckCircle2, X } from 'lucide-react';
import { inventoryAPI, batchesAPI, spoilageAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';

export const Inventory = () => {
  const { user } = useAuth();
  const [inventory, setInventory] = useState([]);
  const [batches, setBatches] = useState([]);

  const [spoilageRisks, setSpoilageRisks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  
  // Modal State
  const [showAddModal, setShowAddModal] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState(null);

  const [formData, setFormData] = useState({
    batch_id: '',
    warehouse_location: 'Mumbai Cold Storage - Bay 4',
    quantity: 500,
    temperature: 18.0,
    humidity: 65.0,
  });

  const categories = ['All', 'Vegetables', 'Fruits', 'Grains & Pulses', 'Leafy Greens'];

  const loadInventoryAndBatches = async () => {
    setLoading(true);
    setError(null);
    try {
      const [invRes, batchRes, spoilageRes] = await Promise.all([
        inventoryAPI.getInventory().catch(() => ({ data: [] })),
        batchesAPI.getBatches().catch(() => ({ data: [] })),
        spoilageAPI.getRisk().catch(() => ({ data: [] })),
      ]);

      const fetchedInv = invRes.data || [];
      const fetchedBatches = batchRes.data || [];
      const fetchedRisks = spoilageRes.data || [];

      setInventory(fetchedInv);
      setBatches(fetchedBatches);
      setSpoilageRisks(fetchedRisks);

      if (fetchedBatches.length > 0 && !formData.batch_id) {
        setFormData((prev) => ({ ...prev, batch_id: fetchedBatches[0].id }));
      }
    } catch (err) {
      console.error("Failed to load inventory data:", err);
      setError("Failed to fetch live inventory from backend.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadInventoryAndBatches();
  }, []);

  const handleCreateInventory = async (e) => {
    e.preventDefault();
    setFormError(null);
    setIsSubmitting(true);

    try {
      const payload = {
        batch_id: parseInt(formData.batch_id || batches[0]?.id || 1),
        warehouse_location: formData.warehouse_location.trim(),
        quantity: parseFloat(formData.quantity),
        temperature: parseFloat(formData.temperature),
        humidity: parseFloat(formData.humidity),
      };

      await inventoryAPI.createInventory(payload);

      setSuccessMessage(`Successfully registered inventory lot at ${payload.warehouse_location}`);
      setShowAddModal(false);

      // Reset form
      setFormData({
        batch_id: batches[0]?.id || '',
        warehouse_location: 'Mumbai Cold Storage - Bay 4',
        quantity: 500,
        temperature: 18.0,
        humidity: 65.0,
      });

      // Refresh inventory list
      await loadInventoryAndBatches();

      setTimeout(() => setSuccessMessage(null), 5000);
    } catch (err) {
      console.error("Error creating inventory record:", err);
      const msg = err.response?.data?.detail || "Failed to create inventory item. Check inputs.";
      setFormError(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Map backend inventory items and attach backend spoilage risk intelligence
  const displayItems = inventory
    .filter((item) => item.quantity > 0)
    .map((item) => {
    const cropName = item.batch?.product?.name || `Batch #${item.batch_id}`;
    const category = item.batch?.product?.category || "Fruits & Vegetables";
    const temp = item.temperature != null ? item.temperature : 18.0;
    const hum = item.humidity != null ? item.humidity : 65.0;

    // Use backend-derived spoilage risk score & risk level
    const riskEval = spoilageRisks.find((r) => r.inventory_id === item.id);
    const riskScore = riskEval ? riskEval.risk_score : 15;
    const riskLevel = riskEval ? riskEval.risk_level : 'Low';
    const status = riskLevel === 'High' ? 'High Risk' : riskLevel === 'Medium' ? 'Moderate Risk' : 'Optimal';

    return {
      id: item.batch?.batch_code ? `INV-${item.batch.batch_code}` : `INV-LOT-${item.id}`,
      rawId: item.id,
      cropName: cropName,
      category: category,
      location: item.warehouse_location,
      quantityKg: item.quantity,
      quantityDisplay: item.quantity >= 1000 ? `${(item.quantity / 1000).toFixed(1)} Tons` : `${item.quantity} kg`,
      storageTemp: `${temp}°C`,
      humidity: `${hum}%`,
      expiryDate: item.batch?.expiry_date || "2026-10-15",
      spoilageRiskScore: riskScore,
      status: status,
      recommendation: riskEval ? riskEval.recommendation : '',
    };
  });

  // Filtering
  const filteredInventory = displayItems.filter((item) => {
    const matchesSearch =
      item.cropName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.location.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'All' || item.category === selectedCategory || selectedCategory === 'Fruits & Vegetables';
    return matchesSearch && matchesCategory;
  });

  // Calculate summary metrics
  const totalStockKg = displayItems.reduce((acc, item) => acc + item.quantityKg, 0);
  const totalStockDisplay = totalStockKg >= 1000 ? `${(totalStockKg / 1000).toFixed(1)} Tons` : `${totalStockKg.toLocaleString()} kg`;
  
  const temps = displayItems.map(i => parseFloat(i.storageTemp) || 18.0);
  const avgTemp = temps.length > 0 ? (temps.reduce((a, b) => a + b, 0) / temps.length).toFixed(1) : "18.0";
  const highRiskCount = displayItems.filter(i => i.status === 'High Risk' || i.spoilageRiskScore >= 60).length;

  return (
    <div className="space-y-6">
      {/* Top Banner Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200/80 flex items-center justify-between shadow-xs">
          <div>
            <div className="flex items-center gap-2">
              <p className="text-xs font-semibold text-slate-500 uppercase">Total Cold Stock</p>
              {inventory.length > 0 && (
                <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800">
                  Real API Data
                </span>
              )}
            </div>
            <p className="text-2xl font-bold text-slate-900 mt-1">{totalStockDisplay}</p>
            <p className="text-[11px] text-emerald-600 font-medium">Across Regional Facilities</p>
          </div>
          <div className="p-3 bg-emerald-50 text-emerald-600 rounded-lg border border-emerald-100">
            <Warehouse className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200/80 flex items-center justify-between shadow-xs">
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase">Avg Storage Temp</p>
            <p className="text-2xl font-bold text-slate-900 mt-1">{avgTemp}°C</p>
            <p className="text-[11px] text-slate-500 font-medium">Target range: 4°C - 20°C</p>
          </div>
          <div className="p-3 bg-blue-50 text-blue-600 rounded-lg border border-blue-100">
            <Thermometer className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200/80 flex items-center justify-between shadow-xs">
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase">Spoilage Risk Alerts</p>
            <p className="text-2xl font-bold text-rose-600 mt-1">{highRiskCount} Batches Alert</p>
            <p className="text-[11px] text-rose-500 font-medium">Backend Rule-based Evaluation</p>
          </div>
          <div className="p-3 bg-rose-50 text-rose-600 rounded-lg border border-rose-100">
            <AlertTriangle className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Control Bar: Search, Category Filter, Add button */}
      <div className="bg-white p-4 rounded-xl border border-slate-200/80 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-xs">
        <div className="flex flex-col sm:flex-row items-center gap-3 flex-1">
          <div className="relative w-full sm:w-72">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Filter by crop, warehouse, SKU..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-slate-50 border border-slate-200 rounded-lg pl-9 pr-3 py-2 text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-hidden"
            />
          </div>

          <div className="flex items-center gap-1 overflow-x-auto w-full sm:w-auto">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-3 py-1.5 text-xs font-semibold rounded-lg whitespace-nowrap transition-colors cursor-pointer ${
                  selectedCategory === cat
                    ? 'bg-emerald-600 text-white shadow-2xs'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        {['admin', 'supply_chain_manager', 'warehouse', 'collection_center', 'farmer'].includes(user?.role) && (
          <button
            onClick={() => {
              setFormError(null);
              setShowAddModal(true);
            }}
            className="flex items-center justify-center gap-1.5 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold transition-all shadow-xs cursor-pointer shrink-0"
          >
            <Plus className="w-4 h-4" /> Add Storage Inventory
          </button>
        )}
      </div>



      {/* Success Banner */}
      {successMessage && (
        <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center justify-between text-emerald-800 text-xs font-medium animate-in fade-in duration-200">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>{successMessage}</span>
          </div>
          <button onClick={() => setSuccessMessage(null)} className="text-slate-400 hover:text-slate-600">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Error Banner */}
      {error && (
        <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 flex items-center gap-2 text-amber-800 text-xs font-medium">
          <AlertCircle className="w-4 h-4 text-amber-600 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Loading State */}
      {loading ? (
        <div className="p-12 rounded-2xl bg-white border border-slate-200/80 shadow-xs flex flex-col items-center justify-center text-slate-500 gap-3">
          <Loader2 className="w-8 h-8 animate-spin text-emerald-600" />
          <p className="text-xs font-semibold text-slate-700">Loading cold-chain inventory from PostgreSQL...</p>
        </div>
      ) : (
        /* Inventory Table */
        <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold uppercase text-[10px]">
                <tr>
                  <th className="py-3 px-4">SKU / ID</th>
                  <th className="py-3 px-4">Crop Name</th>
                  <th className="py-3 px-4">Category</th>
                  <th className="py-3 px-4">Warehouse & Bay</th>
                  <th className="py-3 px-4">Stock Level</th>
                  <th className="py-3 px-4">Temp / Humidity</th>
                  <th className="py-3 px-4">Est. Expiry</th>
                  <th className="py-3 px-4">Spoilage Risk (Backend Rule)</th>
                  <th className="py-3 px-4 text-right">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredInventory.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-50 transition-colors">
                    <td className="py-3.5 px-4 font-mono font-semibold text-slate-500">{item.id}</td>
                    <td className="py-3.5 px-4 font-bold text-slate-900">{item.cropName}</td>
                    <td className="py-3.5 px-4 text-slate-600">{item.category}</td>
                    <td className="py-3.5 px-4 text-slate-700 font-medium">{item.location}</td>
                    <td className="py-3.5 px-4 font-bold text-slate-900">{item.quantityDisplay}</td>
                    <td className="py-3.5 px-4 text-slate-700">
                      <div className="flex flex-col text-[11px]">
                        <span className="font-semibold text-slate-800">{item.storageTemp}</span>
                        <span className="text-slate-400">RH: {item.humidity}</span>
                      </div>
                    </td>
                    <td className="py-3.5 px-4 text-slate-600">
                      <div className="flex items-center gap-1 text-[11px]">
                        <Calendar className="w-3 h-3 text-slate-400" />
                        <span>{item.expiryDate}</span>
                      </div>
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="flex items-center gap-2">
                        <div className="w-16 bg-slate-200 h-2 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full ${
                              item.spoilageRiskScore < 30
                                ? 'bg-emerald-500'
                                : item.spoilageRiskScore < 60
                                ? 'bg-amber-500'
                                : 'bg-rose-500'
                            }`}
                            style={{ width: `${item.spoilageRiskScore}%` }}
                          ></div>
                        </div>
                        <span className="font-mono font-semibold text-[11px]">{item.spoilageRiskScore}%</span>
                      </div>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <Badge
                        variant={
                          item.status === 'Optimal'
                            ? 'emerald'
                            : item.status === 'Moderate Risk'
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
      )}

      {/* CREATE INVENTORY MODAL */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4 my-8 animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-base font-bold text-slate-900">Add Inventory Lot</h3>
                <p className="text-xs text-slate-500">Record storage location in PostgreSQL database</p>
              </div>
              <button
                onClick={() => setShowAddModal(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {formError && (
              <div className="p-3 rounded-lg bg-rose-50 border border-rose-200 flex items-start gap-2 text-rose-700 text-xs font-medium">
                <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-600" />
                <span>{formError}</span>
              </div>
            )}

            <form onSubmit={handleCreateInventory} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Select Harvest Batch <span className="text-rose-500">*</span>
                </label>
                <select
                  value={formData.batch_id}
                  onChange={(e) => setFormData({ ...formData, batch_id: e.target.value })}
                  required
                  className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-900 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden"
                >
                  {batches.map((b) => (
                    <option key={b.id} value={b.id}>
                      {b.batch_code || `Batch #${b.id}`} — {b.product?.name || `Product #${b.product_id}`} ({b.quantity} kg)
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Warehouse Facility & Bay Location <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Mumbai Cold Storage Facility - Bay 4"
                  value={formData.warehouse_location}
                  onChange={(e) => setFormData({ ...formData, warehouse_location: e.target.value })}
                  className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-900 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden"
                />
              </div>

              <div className="grid grid-cols-3 gap-2">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Qty (kg) <span className="text-rose-500">*</span>
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    min="1"
                    required
                    value={formData.quantity}
                    onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-900 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Temp (°C)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    required
                    value={formData.temperature}
                    onChange={(e) => setFormData({ ...formData, temperature: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-900 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Humidity (%)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    required
                    value={formData.humidity}
                    onChange={(e) => setFormData({ ...formData, humidity: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-900 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden"
                  />
                </div>
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 border border-slate-300 rounded-xl text-xs font-semibold text-slate-700 hover:bg-slate-50 cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl text-xs transition-all shadow-md shadow-emerald-950/20 flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" /> Saving...
                    </>
                  ) : (
                    <>Save Lot to PostgreSQL</>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
