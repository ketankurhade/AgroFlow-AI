import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Badge } from '../components/common/Badge';
import { QrCode, Search, CheckCircle2, ShieldCheck, MapPin, Calendar, Sprout, Plus, Loader2, AlertCircle, X, ExternalLink } from 'lucide-react';
import { QRCodeSVG } from 'qrcode.react';
import { batchesAPI, traceabilityAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';

export const QRTraceability = () => {
  const { user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();

  const urlBatchParam = searchParams.get('batch') || '';

  const [batches, setBatches] = useState([]);
  const [activeBatch, setActiveBatch] = useState(null);
  const [events, setEvents] = useState([]);
  const [loadingBatches, setLoadingBatches] = useState(true);
  const [loadingEvents, setLoadingEvents] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  const [searchQuery, setSearchQuery] = useState('');

  // Modal State for Admin Manual Provenance Creation
  const [showAddEventModal, setShowAddEventModal] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState(null);

  const [eventFormData, setEventFormData] = useState({
    stage: 'Cold Storage Intake',
    location: 'Pune Regional Hub - Cold Section 3',
    description: 'Received and verified cold storage entry temperature.',
  });

  // Load all batches on mount
  const loadBatches = async () => {
    setLoadingBatches(true);
    setError(null);
    try {
      const res = await batchesAPI.getBatches().catch(() => ({ data: [] }));
      const fetchedBatches = res.data || [];
      setBatches(fetchedBatches);

      if (fetchedBatches.length > 0) {
        let initial = null;
        if (urlBatchParam) {
          initial = fetchedBatches.find(
            (b) =>
              b.id.toString() === urlBatchParam ||
              (b.batch_code && b.batch_code.toLowerCase() === urlBatchParam.toLowerCase())
          );
        }
        const selected = initial || fetchedBatches[0];
        setActiveBatch(selected);
        setSearchQuery(selected.batch_code || `BATCH-${selected.id}`);
      }
    } catch (err) {
      console.error("Failed to load batches:", err);
      setError("Failed to fetch batches from backend. Check network or permissions.");
    } finally {
      setLoadingBatches(false);
    }
  };

  useEffect(() => {
    loadBatches();
  }, []);

  // Load traceability events whenever activeBatch changes
  const loadTraceabilityEvents = async (batchId) => {
    if (!batchId) return;
    setLoadingEvents(true);
    try {
      const res = await traceabilityAPI.getBatchTraceability(batchId).catch(() => ({ data: [] }));
      setEvents(res.data || []);
    } catch (err) {
      console.error(`Failed to load traceability events for batch ${batchId}:`, err);
      setEvents([]);
    } finally {
      setLoadingEvents(false);
    }
  };

  useEffect(() => {
    if (activeBatch && activeBatch.id) {
      loadTraceabilityEvents(activeBatch.id);
    }
  }, [activeBatch]);

  const handleSelectBatch = (batch) => {
    if (!batch) return;
    setActiveBatch(batch);
    setSearchQuery(batch.batch_code || `BATCH-${batch.id}`);
    setSearchParams({ batch: batch.id.toString() });
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    const found = batches.find(
      (b) =>
        (b.batch_code && b.batch_code.toLowerCase().includes(searchQuery.toLowerCase())) ||
        b.id.toString() === searchQuery.trim() ||
        (b.product && b.product.name && b.product.name.toLowerCase().includes(searchQuery.toLowerCase()))
    );

    if (found) {
      handleSelectBatch(found);
    } else {
      setError(`No matching batch found for "${searchQuery}".`);
      setTimeout(() => setError(null), 4000);
    }
  };

  const handleAddEventSubmit = async (e) => {
    e.preventDefault();
    if (!activeBatch) return;

    setFormError(null);
    if (!eventFormData.stage.trim()) {
      setFormError("Event stage is required.");
      return;
    }
    if (!eventFormData.location.trim()) {
      setFormError("Event location is required.");
      return;
    }

    setIsSubmitting(true);

    try {
      const payload = {
        batch_id: activeBatch.id,
        stage: eventFormData.stage.trim(),
        location: eventFormData.location.trim(),
        description: eventFormData.description.trim() || null,
      };

      await traceabilityAPI.createTraceabilityEvent(payload);

      setSuccessMessage(`Successfully recorded new provenance step: ${payload.stage}`);
      setShowAddEventModal(false);

      // Reset form
      setEventFormData({
        stage: 'Quality Inspection',
        location: 'Central Quality Lab',
        description: 'Passed sweetness, acidity, and grade inspection.',
      });

      // Refresh events
      await loadTraceabilityEvents(activeBatch.id);

      setTimeout(() => setSuccessMessage(null), 5000);
    } catch (err) {
      console.error("Error creating traceability event:", err);
      const msg = err.response?.data?.detail || "Failed to save event. Check backend log.";
      setFormError(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Stable QR reference URL
  const qrReferenceUrl = activeBatch
    ? `${window.location.origin}/traceability?batch=${activeBatch.id}`
    : `${window.location.origin}/traceability`;

  return (
    <div className="space-y-6">
      {/* Search & Selection Header */}
      <div className="bg-gradient-to-r from-emerald-800 to-teal-900 text-white p-6 rounded-2xl shadow-md border border-emerald-700 space-y-4">
        <div className="max-w-2xl mx-auto text-center space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-xs font-bold">
            <QrCode className="w-4 h-4" /> QR Provenance Traceability Engine
          </div>
          <h2 className="text-2xl font-black">Select Agricultural Batch to View Traceability</h2>
          <p className="text-xs text-emerald-100">
            Verify 100% farm-to-fork origin transparency, harvest date, temperature logs, and transport provenance stored in PostgreSQL.
          </p>
        </div>

        {/* Primary Batch Dropdown Selector */}
        <div className="max-w-xl mx-auto bg-emerald-950/70 p-4 rounded-xl border border-emerald-600/50 space-y-3">
          <div>
            <label className="block text-xs font-bold text-emerald-200 mb-1.5 uppercase tracking-wider">
              Select Batch for Traceability Inspection <span className="text-emerald-400">*</span>
            </label>
            <select
              value={activeBatch?.id || ''}
              onChange={(e) => {
                const b = batches.find((item) => item.id === parseInt(e.target.value));
                if (b) handleSelectBatch(b);
              }}
              className="w-full bg-white text-slate-900 font-semibold rounded-xl px-3 py-2.5 text-xs focus:ring-2 focus:ring-emerald-400 focus:outline-hidden"
            >
              <option value="">-- Select Harvest Batch --</option>
              {batches.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.batch_code || `BATCH-${b.id}`} — {b.product?.name || `Product #${b.product_id}`} ({b.quantity} kg | Origin: {b.origin_location} | Status: {b.status})
                </option>
              ))}
            </select>
          </div>

          {/* Quick Batch Selector Pills */}
          {batches.length > 0 && (
            <div className="flex flex-wrap items-center justify-center gap-2 pt-1">
              <span className="text-[11px] text-emerald-300 font-semibold">Available Stock:</span>
              {batches.map((b) => (
                <button
                  key={b.id}
                  onClick={() => handleSelectBatch(b)}
                  className={`px-2.5 py-1 rounded-lg text-xs font-mono font-bold transition-all cursor-pointer ${
                    activeBatch?.id === b.id
                      ? 'bg-white text-emerald-950 shadow-xs ring-2 ring-emerald-400'
                      : 'bg-emerald-900/80 text-emerald-200 hover:bg-emerald-800'
                  }`}
                >
                  {b.batch_code || `BATCH-${b.id}`}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Secondary Manual Search */}
        <form onSubmit={handleSearchSubmit} className="flex items-center gap-2 max-w-lg mx-auto pt-1">
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Or search by Batch Code / ID..."
              className="w-full bg-white/90 text-slate-900 rounded-xl pl-9 pr-3 py-2 text-xs font-semibold focus:outline-hidden focus:bg-white"
            />
          </div>
          <button
            type="submit"
            className="px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black rounded-xl text-xs transition-colors cursor-pointer"
          >
            Search Batch
          </button>
        </form>
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
      {loadingBatches ? (
        <div className="p-12 rounded-2xl bg-white border border-slate-200/80 shadow-xs flex flex-col items-center justify-center text-slate-500 gap-3">
          <Loader2 className="w-8 h-8 animate-spin text-emerald-600" />
          <p className="text-xs font-semibold text-slate-700">Loading batch provenance from PostgreSQL...</p>
        </div>
      ) : activeBatch ? (
        /* Batch Trace Detail & QR Code Card */
        <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-xs space-y-6">
          <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-6 border-b border-slate-100 pb-6">
            <div className="space-y-3 flex-1">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="font-mono text-xs font-extrabold px-3 py-1 bg-slate-100 text-slate-900 rounded-md">
                  {activeBatch.batch_code || `BATCH-${activeBatch.id}`}
                </span>
                <span className="inline-flex items-center gap-1 text-xs font-bold text-emerald-700 bg-emerald-50 px-3 py-1 rounded-full border border-emerald-200">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" /> Verified AgroFlow PostgreSQL Origin
                </span>
                <Badge variant="emerald">{activeBatch.quality_grade || "Grade A"}</Badge>
              </div>

              <h3 className="text-2xl font-black text-slate-900">{activeBatch.product?.name || `Product #${activeBatch.product_id}`}</h3>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-slate-600 pt-1">
                <div className="flex items-center gap-2">
                  <Sprout className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span>Farmer / Producer: <strong className="text-slate-900">{activeBatch.farmer?.name || "Verified Farmer"}</strong></span>
                </div>
                <div className="flex items-center gap-2">
                  <MapPin className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span>Origin Location: <strong className="text-slate-900">{activeBatch.origin_location}</strong></span>
                </div>
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span>Harvest Date: <strong className="text-slate-900">{activeBatch.harvest_date}</strong></span>
                </div>
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-rose-500 shrink-0" />
                  <span>Est. Expiry: <strong className="text-slate-900">{activeBatch.expiry_date}</strong></span>
                </div>
              </div>

              <div className="pt-2 flex items-center gap-4 text-xs">
                <span className="text-slate-400">Total Harvest Volume: <strong className="text-slate-900 font-bold">{activeBatch.quantity} kg</strong></span>
                <span className="text-slate-400">Batch Status: <strong className="text-emerald-700 font-bold">{activeBatch.status}</strong></span>
              </div>
            </div>

            {/* Generated QR Code Box */}
            <div className="bg-slate-50 border border-slate-200 p-4 rounded-2xl flex flex-col items-center justify-center text-center gap-2 shrink-0">
              <div className="p-2 bg-white rounded-xl shadow-xs border border-slate-200">
                <QRCodeSVG
                  value={qrReferenceUrl}
                  size={135}
                  level="M"
                  includeMargin={true}
                />
              </div>
              <p className="text-[10px] font-mono text-slate-500 font-bold max-w-[160px] truncate">
                {activeBatch.batch_code || `BATCH-${activeBatch.id}`}
              </p>
              <a
                href={qrReferenceUrl}
                target="_blank"
                rel="noreferrer"
                className="text-[11px] font-bold text-emerald-600 hover:underline flex items-center gap-1"
              >
                Open Trace Reference <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </div>

          {/* Interactive Provenance Timeline */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <h4 className="text-sm font-bold text-slate-900">Chronological Provenance Timeline</h4>
                {events.length > 0 && (
                  <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">
                    {events.length} Recorded Stage{events.length > 1 ? 's' : ''}
                  </span>
                )}
              </div>
              {/* Strictly View-Only for Operational Users. Only Admin can manually record provenance */}
              {user?.role === 'admin' && (
                <button
                  onClick={() => {
                    setFormError(null);
                    setShowAddEventModal(true);
                  }}
                  className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold transition-all flex items-center gap-1 cursor-pointer"
                >
                  <Plus className="w-3.5 h-3.5" /> Add Provenance Step
                </button>
              )}
            </div>

            {loadingEvents ? (
              <div className="p-8 text-center text-slate-400 text-xs flex items-center justify-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin text-emerald-600" />
                <span>Loading timeline events from PostgreSQL...</span>
              </div>
            ) : events.length > 0 ? (
              <div className="space-y-4 relative before:absolute before:left-5 before:top-3 before:bottom-3 before:w-0.5 before:bg-emerald-200">
                {events.map((evt) => (
                  <div key={evt.id} className="relative pl-12">
                    <div className="absolute left-3 top-0 -translate-x-1/2 w-4 h-4 rounded-full bg-emerald-600 border-2 border-white ring-2 ring-emerald-100 flex items-center justify-center text-white">
                      <CheckCircle2 className="w-3 h-3" />
                    </div>

                    <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-1 hover:bg-white hover:shadow-2xs transition-all">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-xs text-slate-900">
                          {evt.stage} • <span className="text-emerald-800">{evt.location}</span>
                        </span>
                        <span className="text-[10px] text-slate-400 font-medium">
                          {new Date(evt.timestamp).toLocaleString()}
                        </span>
                      </div>
                      {evt.description && (
                        <p className="text-xs text-slate-600">{evt.description}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-6 bg-slate-50 border border-slate-200 rounded-xl text-center space-y-2">
                <p className="text-xs text-slate-600 font-medium">No provenance events recorded for this batch yet.</p>
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="bg-white p-8 text-center rounded-2xl border border-slate-200 text-slate-500 text-xs">
          {batches.length === 0
            ? "No eligible batches available in database."
            : "Select a batch from the dropdown above to view its complete provenance timeline."}
        </div>
      )}

      {/* ADD TRACEABILITY EVENT MODAL (ADMIN-ONLY) */}
      {showAddEventModal && user?.role === 'admin' && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4 my-8 animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-base font-bold text-slate-900">Record Admin Provenance Step</h3>
                <p className="text-xs text-slate-500">
                  Batch: {activeBatch?.batch_code || `BATCH-${activeBatch?.id}`}
                </p>
              </div>
              <button
                onClick={() => setShowAddEventModal(false)}
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

            <form onSubmit={handleAddEventSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Supply Chain Stage <span className="text-rose-500">*</span>
                </label>
                <select
                  value={eventFormData.stage}
                  onChange={(e) => setEventFormData({ ...eventFormData, stage: e.target.value })}
                  required
                  className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-900 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden"
                >
                  <option value="Farmer Harvest">Farmer Harvest</option>
                  <option value="Quality Inspection">Quality Inspection</option>
                  <option value="Cold Storage Intake">Cold Storage Intake</option>
                  <option value="Dispatch & Transport">Dispatch & Transport</option>
                  <option value="Distributor Receive">Distributor Receive</option>
                  <option value="Retail Outlet Delivery">Retail Outlet Delivery</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Location Facility / Hub <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Pune Regional Hub - Cold Section 3"
                  value={eventFormData.location}
                  onChange={(e) => setEventFormData({ ...eventFormData, location: e.target.value })}
                  className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-900 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Log Description / Verification Details
                </label>
                <textarea
                  rows="3"
                  placeholder="e.g. Passed grade inspection and placed in cold storage bay."
                  value={eventFormData.description}
                  onChange={(e) => setEventFormData({ ...eventFormData, description: e.target.value })}
                  className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-900 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden"
                ></textarea>
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowAddEventModal(false)}
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
                    <>Save Provenance Step</>
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
