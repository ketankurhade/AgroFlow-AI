import React, { useState, useEffect } from 'react';
import { BATCHES as MOCK_BATCHES } from '../data/mockData';
import { Badge } from '../components/common/Badge';
import { Package, QrCode, Sprout, Thermometer, MapPin, Calendar, ArrowRight, Plus, X, Loader2, AlertCircle, CheckCircle2 } from 'lucide-react';
import { Link } from 'react-router-dom';
import { batchesAPI, productsAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';

export const Batches = () => {
  const { user } = useAuth();
  const [batches, setBatches] = useState([]);
  const [products, setProducts] = useState([]);
  const [selectedBatch, setSelectedBatch] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  // Modal State
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState(null);

  // Today and default 30 days future expiry for form defaults
  const todayStr = new Date().toISOString().split('T')[0];
  const futureStr = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];

  const [formData, setFormData] = useState({
    batch_code: '',
    product_id: '',
    quantity: 500,
    quality_grade: 'Grade A',
    harvest_date: todayStr,
    expiry_date: futureStr,
    origin_location: 'Nashik Organic Farm, Maharashtra',
    status: 'Harvested',
  });

  const [hasFetched, setHasFetched] = useState(false);

  const loadBatchesAndProducts = async () => {
    setLoading(true);
    setError(null);
    try {
      const [batchRes, prodRes] = await Promise.all([
        batchesAPI.getBatches().catch(() => ({ data: [] })),
        productsAPI.getProducts().catch(() => ({ data: [] })),
      ]);

      const fetchedBatches = batchRes.data || [];
      const fetchedProducts = prodRes.data || [];

      setBatches(fetchedBatches);
      setProducts(fetchedProducts);
      setHasFetched(true);

      if (fetchedProducts.length > 0 && !formData.product_id) {
        setFormData((prev) => ({ ...prev, product_id: fetchedProducts[0].id }));
      }
    } catch (err) {
      console.error("Failed to fetch batch data:", err);
      setError("Failed to connect to backend. Displaying cached batches.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBatchesAndProducts();
  }, []);

  const handleCreateSubmit = async (e) => {
    e.preventDefault();
    setFormError(null);
    setIsSubmitting(true);

    try {
      const payload = {
        batch_code: formData.batch_code.trim() || `BATCH-2026-${Math.floor(100 + Math.random() * 900)}`,
        product_id: parseInt(formData.product_id || products[0]?.id || 1),
        farmer_id: user?.id || 1, // Use authenticated user ID
        quantity: parseFloat(formData.quantity),
        quality_grade: formData.quality_grade,
        harvest_date: formData.harvest_date,
        expiry_date: formData.expiry_date,
        origin_location: formData.origin_location,
        status: formData.status,
      };

      await batchesAPI.createBatch(payload);

      setSuccessMessage(`Successfully registered new harvest batch: ${payload.batch_code}`);
      setShowCreateModal(false);
      
      // Reset form
      setFormData({
        batch_code: '',
        product_id: products[0]?.id || '',
        quantity: 500,
        quality_grade: 'Grade A',
        harvest_date: todayStr,
        expiry_date: futureStr,
        origin_location: 'Nashik Organic Farm, Maharashtra',
        status: 'Harvested',
      });

      // Refresh list from API
      await loadBatchesAndProducts();

      // Clear success message after 5 seconds
      setTimeout(() => setSuccessMessage(null), 5000);
    } catch (err) {
      console.error("Error creating batch:", err);
      const msg = err.response?.data?.detail || "Failed to create batch. Please check inputs.";
      setFormError(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Prepare display items: use real batches from backend
  const displayBatches = hasFetched
    ? batches.map((b) => ({
        id: b.batch_code || `BATCH-${b.id}`,
        rawId: b.id,
        cropName: b.product?.name || `Product #${b.product_id}`,
        qualityGrade: b.quality_grade,
        farmerName: b.farmer?.name || user?.name || "Ramesh Kumar",
        farmLocation: b.origin_location,
        harvestDate: b.harvest_date,
        expiryDate: b.expiry_date,
        temperatureLog: b.status === 'In Cold Storage' ? '18.5°C (Optimal)' : '20.0°C (Normal)',
        quantityKg: b.quantity,
        status: b.status,
        qrCodeUrl: `https://agroflow.ai/trace/${b.batch_code || b.id}`,
        timeline: [
          { stage: 'Harvesting', location: b.origin_location, date: b.harvest_date, details: 'Harvested under optimal conditions.' },
          { stage: 'Quality Inspection', location: 'Farm Audit Center', date: b.harvest_date, details: `Certified ${b.quality_grade}.` },
        ]
      }))
    : (batches.length > 0 ? batches.map((b) => ({
        id: b.batch_code || `BATCH-${b.id}`,
        rawId: b.id,
        cropName: b.product?.name || `Product #${b.product_id}`,
        qualityGrade: b.quality_grade,
        farmerName: b.farmer?.name || user?.name || "Ramesh Kumar",
        farmLocation: b.origin_location,
        harvestDate: b.harvest_date,
        expiryDate: b.expiry_date,
        temperatureLog: b.status === 'In Cold Storage' ? '18.5°C (Optimal)' : '20.0°C (Normal)',
        quantityKg: b.quantity,
        status: b.status,
        qrCodeUrl: `https://agroflow.ai/trace/${b.batch_code || b.id}`,
        timeline: [
          { stage: 'Harvesting', location: b.origin_location, date: b.harvest_date, details: 'Harvested under optimal conditions.' },
          { stage: 'Quality Inspection', location: 'Farm Audit Center', date: b.harvest_date, details: `Certified ${b.quality_grade}.` },
        ]
      })) : []);

  return (
    <div className="space-y-6">
      {/* Header Info & Action Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-bold text-slate-900">Harvest Batch Traceability & Provenance</h2>
            {batches.length > 0 && (
              <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">
                Real Backend Data
              </span>
            )}
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Monitor farm harvest origin, quality grades, temperature history, and QR traceability codes
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs font-semibold px-3 py-1.5 bg-emerald-100 text-emerald-800 rounded-full">
            {displayBatches.length} Registered Batches
          </span>
          {['admin', 'farmer', 'supply_chain_manager', 'collection_center'].includes(user?.role) && (
            <button
              onClick={() => {
                setFormError(null);
                setShowCreateModal(true);
              }}
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl text-xs transition-all shadow-md shadow-emerald-950/20 flex items-center gap-1.5 cursor-pointer"
            >
              <Plus className="w-4 h-4" /> Create New Batch
            </button>
          )}
        </div>
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
          <p className="text-xs font-semibold text-slate-700">Loading harvest batches from PostgreSQL...</p>
        </div>
      ) : (
        /* Batches Grid */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {displayBatches.map((batch) => (
            <div
              key={batch.id}
              className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-5 hover:shadow-md transition-shadow flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="font-mono text-xs font-extrabold text-slate-900 bg-slate-100 px-2.5 py-1 rounded-md">
                    {batch.id}
                  </span>
                  <Badge
                    variant={
                      batch.status === 'In Cold Storage' || batch.status === 'Stored'
                        ? 'emerald'
                        : batch.status === 'Temperature Alert'
                        ? 'red'
                        : batch.status === 'Priority Dispatch' || batch.status === 'In Transit'
                        ? 'amber'
                        : 'blue'
                    }
                  >
                    {batch.status}
                  </Badge>
                </div>

                <h3 className="text-base font-bold text-slate-900">{batch.cropName}</h3>
                <p className="text-xs font-semibold text-emerald-700 mt-0.5">{batch.qualityGrade}</p>

                <div className="mt-4 space-y-2 text-xs text-slate-600">
                  <div className="flex items-center gap-2">
                    <Sprout className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                    <span>Farmer: <strong>{batch.farmerName}</strong></span>
                  </div>
                  <div className="flex items-center gap-2">
                    <MapPin className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                    <span>Origin: <strong>{batch.farmLocation}</strong></span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Calendar className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                    <span>Harvested: <strong>{batch.harvestDate}</strong></span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Thermometer className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                    <span>Telemetry: <strong>{batch.temperatureLog}</strong></span>
                  </div>
                </div>
              </div>

              <div className="mt-5 pt-4 border-t border-slate-100 flex items-center justify-between">
                <div>
                  <span className="text-[10px] text-slate-400 block uppercase font-bold">Quantity</span>
                  <span className="text-xs font-bold text-slate-900">
                    {batch.quantityKg >= 1000
                      ? `${(batch.quantityKg / 1000).toFixed(1)} Tons`
                      : `${batch.quantityKg} kg`}
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setSelectedBatch(batch)}
                    className="p-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 transition-colors cursor-pointer"
                    title="Inspect Batch Timeline"
                  >
                    <QrCode className="w-4 h-4 text-emerald-600" />
                  </button>
                  <Link
                    to={`/traceability?batch=${batch.id}`}
                    className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-lg text-xs transition-colors flex items-center gap-1"
                  >
                    Trace <ArrowRight className="w-3 h-3" />
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Detail & QR Modal */}
      {selectedBatch && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-base font-bold text-slate-900">{selectedBatch.cropName}</h3>
                <p className="text-xs font-mono text-slate-500">{selectedBatch.id}</p>
              </div>
              <Badge variant="emerald">{selectedBatch.qualityGrade}</Badge>
            </div>

            {/* QR graphic */}
            <div className="flex items-center justify-center p-4 bg-slate-50 border border-slate-200 rounded-xl">
              <div className="text-center space-y-2">
                <div className="w-32 h-32 mx-auto bg-white p-2 rounded-xl border border-slate-300 shadow-xs flex items-center justify-center">
                  <div className="w-full h-full bg-slate-900 p-2 rounded flex flex-col justify-between">
                    <div className="flex justify-between">
                      <div className="w-6 h-6 bg-white border-2 border-slate-900"></div>
                      <div className="w-6 h-6 bg-white border-2 border-slate-900"></div>
                    </div>
                    <div className="text-center font-mono text-[8px] text-emerald-400 font-bold">AGROFLOW</div>
                    <div className="flex justify-between">
                      <div className="w-6 h-6 bg-white border-2 border-slate-900"></div>
                      <div className="w-2 h-2 bg-emerald-400 rounded-full"></div>
                    </div>
                  </div>
                </div>
                <p className="text-[11px] font-mono text-slate-600 font-bold">{selectedBatch.qrCodeUrl}</p>
              </div>
            </div>

            {/* Timeline */}
            <div className="space-y-2 text-xs">
              <p className="font-bold text-slate-800 uppercase text-[10px] tracking-wider">Proven Provenance Steps</p>
              {selectedBatch.timeline?.map((step, idx) => (
                <div key={idx} className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                  <div className="flex items-center justify-between font-bold text-slate-900">
                    <span>{step.stage} - {step.location}</span>
                    <span className="text-[10px] text-slate-400 font-normal">{step.date}</span>
                  </div>
                  <p className="text-[11px] text-slate-600 mt-0.5">{step.details}</p>
                </div>
              ))}
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setSelectedBatch(null)}
                className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-bold cursor-pointer"
              >
                Close Modal
              </button>
            </div>
          </div>
        </div>
      )}

      {/* CREATE BATCH MODAL */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4 my-8 animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-base font-bold text-slate-900">Register New Harvest Batch</h3>
                <p className="text-xs text-slate-500">Record farm provenance in FastAPI & PostgreSQL</p>
              </div>
              <button
                onClick={() => setShowCreateModal(false)}
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

            <form onSubmit={handleCreateSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Crop Commodity Product <span className="text-rose-500">*</span>
                </label>
                <select
                  value={formData.product_id}
                  onChange={(e) => setFormData({ ...formData, product_id: e.target.value })}
                  required
                  className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-900 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden"
                >
                  {products.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name} ({p.category})
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Batch Code <span className="text-slate-400 font-normal">(Auto if empty)</span>
                  </label>
                  <input
                    type="text"
                    placeholder="BATCH-2026-005"
                    value={formData.batch_code}
                    onChange={(e) => setFormData({ ...formData, batch_code: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-900 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Quantity (kg) <span className="text-rose-500">*</span>
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
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Quality Grade <span className="text-rose-500">*</span>
                  </label>
                  <select
                    value={formData.quality_grade}
                    onChange={(e) => setFormData({ ...formData, quality_grade: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-900 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden"
                  >
                    <option value="Grade A+">Grade A+</option>
                    <option value="Grade A">Grade A</option>
                    <option value="Grade B">Grade B</option>
                    <option value="Premium Export">Premium Export</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Initial Status
                  </label>
                  <select
                    value={formData.status}
                    onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-900 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden"
                  >
                    <option value="Harvested">Harvested</option>
                    <option value="In Cold Storage">In Cold Storage</option>
                    <option value="Stored">Stored</option>
                    <option value="In Transit">In Transit</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Harvest Date <span className="text-rose-500">*</span>
                  </label>
                  <input
                    type="date"
                    required
                    value={formData.harvest_date}
                    onChange={(e) => setFormData({ ...formData, harvest_date: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-900 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Expiry Date <span className="text-rose-500">*</span>
                  </label>
                  <input
                    type="date"
                    required
                    value={formData.expiry_date}
                    onChange={(e) => setFormData({ ...formData, expiry_date: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-900 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Origin Farm Location <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  placeholder="Nashik Organic Farm, Maharashtra"
                  value={formData.origin_location}
                  onChange={(e) => setFormData({ ...formData, origin_location: e.target.value })}
                  className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-900 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden"
                />
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
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
                      <Loader2 className="w-4 h-4 animate-spin" /> Saving to Database...
                    </>
                  ) : (
                    <>Save Batch to PostgreSQL</>
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
