import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Badge } from '../components/common/Badge';
import { RouteMap } from '../components/RouteMap';
import {
  Truck,
  MapPin,
  ArrowRight,
  Plus,
  Loader2,
  AlertCircle,
  CheckCircle2,
  X,
  Navigation,
  Sparkles,
  Clock,
  Compass,
  Trash2,
  RefreshCw,
  Send,
} from 'lucide-react';
import { shipmentsAPI, ordersAPI, batchesAPI, routesAPI } from '../services/api';

export const RouteOptimization = () => {
  const [searchParams] = useSearchParams();
  const paramOrderId = searchParams.get('order_id');
  const paramOpenModal = searchParams.get('open_modal');

  // Existing Shipments & Database State
  const [shipments, setShipments] = useState([]);
  const [orders, setOrders] = useState([]);
  const [batches, setBatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  // Supported Locations from Backend
  const [supportedLocations, setSupportedLocations] = useState([]);

  // Route Optimizer Interactive State
  const [selectedStops, setSelectedStops] = useState([
    { name: 'Ratnagiri' },
    { name: 'Pune' },
    { name: 'Navi Mumbai' },
    { name: 'Mumbai' },
  ]);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [optimizationResult, setOptimizationResult] = useState(null);
  const [optimizationError, setOptimizationError] = useState(null);

  // Modal State for Dispatch Creation
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState(null);

  // Form State
  const [formData, setFormData] = useState({
    order_id: '',
    batch_id: '',
    source: 'Pune Regional Hub - Cold Section 3',
    destination: 'FreshMart Retail Hub',
    vehicle_number: 'MH-15-AB-1234',
    status: 'In Transit',
  });

  const loadInitialData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [shipRes, orderRes, batchRes, locRes] = await Promise.all([
        shipmentsAPI.getShipments().catch(() => ({ data: [] })),
        ordersAPI.getOrders().catch(() => ({ data: [] })),
        batchesAPI.getBatches().catch(() => ({ data: [] })),
        routesAPI.getSupportedLocations().catch(() => ({ data: [] })),
      ]);

      const fetchedShipments = shipRes.data || [];
      const fetchedOrders = orderRes.data || [];
      const fetchedBatches = batchRes.data || [];
      const fetchedLocations = locRes.data || [];

      setShipments(fetchedShipments);
      setOrders(fetchedOrders);
      setBatches(fetchedBatches);
      setSupportedLocations(fetchedLocations);

      // Determine initial order_id
      const initialOrderId = paramOrderId
        ? parseInt(paramOrderId)
        : fetchedOrders.length > 0
        ? fetchedOrders[0].id
        : '';

      const matchedOrder = fetchedOrders.find((o) => o.id === parseInt(initialOrderId));
      const orderProdId = matchedOrder?.items?.[0]?.product_id;

      const eligible = orderProdId
        ? fetchedBatches.filter((b) => b.product_id === orderProdId)
        : fetchedBatches;

      const initialBatchId = eligible.length > 0 ? eligible[0].id : fetchedBatches[0]?.id || '';
      const initialSource = eligible.length > 0 ? eligible[0].origin_location : 'Pune Regional Hub - Cold Section 3';
      const initialDestination = matchedOrder?.buyer?.name ? `${matchedOrder.buyer.name} Hub` : 'FreshMart Retail Hub';

      setFormData({
        order_id: initialOrderId,
        batch_id: initialBatchId,
        source: initialSource,
        destination: initialDestination,
        vehicle_number: 'MH-15-AB-1234',
        status: 'In Transit',
      });

      if (paramOpenModal === 'true') {
        setShowCreateModal(true);
      }

      // Auto-run initial optimization on default locations
      handleRunOptimization([
        { name: 'Ratnagiri' },
        { name: 'Pune' },
        { name: 'Navi Mumbai' },
        { name: 'Mumbai' },
      ]);
    } catch (err) {
      console.error("Failed to load initial data:", err);
      setError("Failed to fetch live shipments or supported locations from backend.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadInitialData();
  }, []);

  // When order changes in modal, auto-update destination and batch selection
  const handleOrderChange = (newOrderIdStr) => {
    const newOrderId = parseInt(newOrderIdStr);
    const matchedOrder = orders.find((o) => o.id === newOrderId);
    const orderProdId = matchedOrder?.items?.[0]?.product_id;

    const eligible = orderProdId
      ? batches.filter((b) => b.product_id === orderProdId)
      : batches;

    const newBatchId = eligible.length > 0 ? eligible[0].id : batches[0]?.id || '';
    const newSource = eligible.length > 0 ? eligible[0].origin_location : formData.source;
    const newDest = matchedOrder?.buyer?.name ? `${matchedOrder.buyer.name} Hub` : formData.destination;

    setFormData({
      ...formData,
      order_id: newOrderIdStr,
      batch_id: newBatchId,
      source: newSource,
      destination: newDest,
    });
  };

  // Run OR-Tools Route Optimization API
  const handleRunOptimization = async (stopsToOptimize = selectedStops) => {
    if (!stopsToOptimize || stopsToOptimize.length < 2) {
      setOptimizationError("Please select at least 2 delivery locations for route optimization.");
      return;
    }

    setIsOptimizing(true);
    setOptimizationError(null);

    try {
      const payload = {
        stops: stopsToOptimize.map((s) => ({
          name: s.name,
          latitude: s.latitude || null,
          longitude: s.longitude || null,
        })),
        start_location_index: 0,
      };

      const res = await routesAPI.optimizeRoute(payload);
      setOptimizationResult(res.data);
    } catch (err) {
      console.error("Route optimization failed:", err);
      const msg = err.response?.data?.detail || "Failed to execute OR-Tools route optimization.";
      setOptimizationError(msg);
    } finally {
      setIsOptimizing(false);
    }
  };

  // Add Stop Handler
  const handleAddStop = (locationName) => {
    if (!locationName) return;
    if (selectedStops.some((s) => s.name.toLowerCase() === locationName.toLowerCase())) {
      return;
    }
    const updated = [...selectedStops, { name: locationName }];
    setSelectedStops(updated);
  };

  // Remove Stop Handler
  const handleRemoveStop = (index) => {
    if (selectedStops.length <= 2) {
      setOptimizationError("At least 2 stops are required for optimization.");
      return;
    }
    const updated = selectedStops.filter((_, idx) => idx !== index);
    setSelectedStops(updated);
  };

  // Create Shipment Form Submit
  const handleCreateShipment = async (e) => {
    e.preventDefault();
    setFormError(null);

    if (!formData.order_id) {
      setFormError("Please select a valid order.");
      return;
    }
    if (!formData.batch_id) {
      setFormError("Please select a valid batch.");
      return;
    }
    if (!formData.source.trim()) {
      setFormError("Source location is required.");
      return;
    }
    if (!formData.destination.trim()) {
      setFormError("Destination location is required.");
      return;
    }
    if (!formData.vehicle_number.trim()) {
      setFormError("Vehicle number is required.");
      return;
    }

    setIsSubmitting(true);

    try {
      const payload = {
        order_id: parseInt(formData.order_id),
        batch_id: parseInt(formData.batch_id),
        source: formData.source.trim(),
        destination: formData.destination.trim(),
        vehicle_number: formData.vehicle_number.trim(),
        status: formData.status,
      };

      await shipmentsAPI.createShipment(payload);

      setSuccessMessage(`Successfully registered & dispatched shipment for Vehicle: ${payload.vehicle_number}. Transport provenance event recorded!`);
      setShowCreateModal(false);

      // Refresh list
      await loadInitialData();

      setTimeout(() => setSuccessMessage(null), 6000);
    } catch (err) {
      console.error("Error creating shipment:", err);
      const msg = err.response?.data?.detail || "Failed to create shipment. Please check selections.";
      setFormError(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDispatchShipment = async (shipmentId) => {
    try {
      await shipmentsAPI.updateShipmentStatus(shipmentId, 'In Transit');
      setSuccessMessage(`Shipment #${shipmentId} dispatched! Status set to In Transit.`);
      await loadInitialData();
      setTimeout(() => setSuccessMessage(null), 5000);
    } catch (err) {
      console.error("Failed to dispatch shipment:", err);
      setError("Failed to dispatch shipment.");
    }
  };

  // Compute eligible batches for current form order_id
  const currentSelectedOrder = orders.find((o) => o.id === parseInt(formData.order_id));
  const currentOrderProdId = currentSelectedOrder?.items?.[0]?.product_id;
  const eligibleBatches = currentOrderProdId
    ? batches.filter((b) => b.product_id === currentOrderProdId)
    : batches;

  const displayRoutes = shipments.length > 0
    ? shipments.map((s) => {
        const orderNum = s.order?.order_number || `Order #${s.order_id}`;
        const cropName = s.batch?.product?.name || `Batch #${s.batch_id}`;
        const buyerName = s.order?.buyer?.name || "Wholesale Buyer";

        return {
          id: `SHIP-${s.id}`,
          rawId: s.id,
          name: `${cropName} — ${orderNum}`,
          driver: `Vehicle ${s.vehicle_number} (${buyerName})`,
          status: s.status,
          waypoints: [s.source, 'Cold Chain Reefer Transit', s.destination],
          optimizedTime: 'Estimated via Haversine',
          distanceKm: 'Calculated',
          source: s.source,
          destination: s.destination,
          batchCode: s.batch?.batch_code || `Batch #${s.batch_id}`,
          dispatchedAt: s.dispatched_at ? new Date(s.dispatched_at).toLocaleString() : null,
        };
      })
    : [];

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-bold text-slate-900">AgroFlow Route Optimization & Dispatch</h2>
            <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 flex items-center gap-1">
              <Sparkles className="w-3 h-3" /> Powered by Google OR-Tools
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Compute optimal multi-stop visit sequences, trip distance, and travel duration using Python OR-Tools TSP solver
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => {
              setFormError(null);
              setShowCreateModal(true);
            }}
            className="flex items-center justify-center gap-1.5 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold transition-all shadow-xs cursor-pointer shrink-0"
          >
            <Plus className="w-4 h-4" /> Create Shipment Dispatch
          </button>
        </div>
      </div>

      {/* Global Alerts */}
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

      {error && (
        <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 flex items-center gap-2 text-amber-800 text-xs font-medium">
          <AlertCircle className="w-4 h-4 text-amber-600 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* OR-TOOLS ROUTE OPTIMIZATION ENGINE SECTION */}
      <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-xs space-y-6">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-slate-100 pb-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-emerald-50 rounded-xl text-emerald-600 border border-emerald-100">
              <Navigation className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-900">Multi-Stop Route Optimizer</h3>
              <p className="text-xs text-slate-500">
                Select stops to solve Traveling Salesperson Problem (TSP) using Google OR-Tools in FastAPI
              </p>
            </div>
          </div>

          <button
            onClick={() => handleRunOptimization(selectedStops)}
            disabled={isOptimizing}
            className="flex items-center gap-2 px-5 py-2.5 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-bold transition-all shadow-md cursor-pointer disabled:opacity-50 shrink-0"
          >
            {isOptimizing ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin text-emerald-400" />
                <span>Solving OR-Tools TSP...</span>
              </>
            ) : (
              <>
                <RefreshCw className="w-4 h-4 text-emerald-400" />
                <span>Optimize Route Sequence</span>
              </>
            )}
          </button>
        </div>

        {optimizationError && (
          <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 flex items-center gap-2 text-rose-700 text-xs font-medium">
            <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
            <span>{optimizationError}</span>
          </div>
        )}

        {/* Location Selection Controls */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="space-y-3 md:col-span-1 border-r border-slate-100 pr-0 md:pr-6">
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
              Selected Delivery Stops ({selectedStops.length})
            </label>

            <div className="space-y-2">
              {selectedStops.map((stop, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-2.5 bg-slate-50 rounded-xl border border-slate-200/80 text-xs"
                >
                  <div className="flex items-center gap-2 font-medium text-slate-800">
                    <span className="w-5 h-5 rounded-full bg-slate-200 text-slate-700 font-bold text-[10px] flex items-center justify-center">
                      {idx + 1}
                    </span>
                    <span>{stop.name}</span>
                    {idx === 0 && (
                      <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800">
                        Start
                      </span>
                    )}
                  </div>
                  <button
                    onClick={() => handleRemoveStop(idx)}
                    className="p-1 text-slate-400 hover:text-rose-600 transition-colors"
                    title="Remove Stop"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
            </div>

            {/* Quick Add Supported Location */}
            <div className="pt-2">
              <label className="block text-[11px] font-semibold text-slate-500 mb-1">
                Add Supported AgroFlow Hub
              </label>
              <select
                onChange={(e) => {
                  handleAddStop(e.target.value);
                  e.target.value = '';
                }}
                className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-800 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden"
              >
                <option value="">-- Select Location to Add --</option>
                {supportedLocations.map((loc) => (
                  <option key={loc.name} value={loc.name}>
                    {loc.name} ({loc.city})
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Results Summary Metrics & Map */}
          <div className="md:col-span-2 space-y-4">
            {optimizationResult && (
              <>
                {/* Result KPI Grid */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                  <div className="p-3 bg-emerald-50 rounded-xl border border-emerald-100 text-center">
                    <span className="text-slate-500 text-[10px] block font-bold">Total Distance</span>
                    <span className="font-extrabold text-base text-emerald-800">
                      {optimizationResult.total_distance_km} km
                    </span>
                  </div>
                  <div className="p-3 bg-blue-50 rounded-xl border border-blue-100 text-center">
                    <span className="text-slate-500 text-[10px] block font-bold">Estimated Duration</span>
                    <span className="font-extrabold text-base text-blue-800">
                      {optimizationResult.estimated_duration_formatted}
                    </span>
                  </div>
                  <div className="p-3 bg-indigo-50 rounded-xl border border-indigo-100 text-center">
                    <span className="text-slate-500 text-[10px] block font-bold">Optimized Sequence</span>
                    <span className="font-extrabold text-base text-indigo-800">
                      {optimizationResult.optimized_route.length} Stops
                    </span>
                  </div>
                  <div className="p-3 bg-amber-50 rounded-xl border border-amber-100 text-center">
                    <span className="text-slate-500 text-[10px] block font-bold">Avg Fleet Speed</span>
                    <span className="font-extrabold text-base text-amber-800">
                      {optimizationResult.average_speed_kmh} km/h
                    </span>
                  </div>
                </div>

                {/* Leaflet Route Map Component */}
                <RouteMap stops={optimizationResult.optimized_route} height="320px" />

                {/* Leg Details Table */}
                <div className="bg-slate-50 rounded-xl p-4 border border-slate-200/80 space-y-3">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                      Optimized Route Legs Breakdown
                    </h4>
                    <span className="text-[10px] text-slate-500 font-medium">
                      {optimizationResult.algorithm}
                    </span>
                  </div>

                  <div className="space-y-2">
                    {optimizationResult.legs.map((leg) => (
                      <div
                        key={leg.leg_number}
                        className="bg-white p-3 rounded-lg border border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between text-xs gap-2 shadow-2xs"
                      >
                        <div className="flex items-center gap-2">
                          <span className="w-5 h-5 rounded-full bg-emerald-100 text-emerald-800 font-extrabold text-[10px] flex items-center justify-center shrink-0">
                            {leg.leg_number}
                          </span>
                          <span className="font-bold text-slate-800">{leg.from_stop}</span>
                          <ArrowRight className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                          <span className="font-bold text-slate-800">{leg.to_stop}</span>
                        </div>
                        <div className="flex items-center gap-4 text-slate-600 text-[11px] font-medium pl-7 sm:pl-0">
                          <span>📏 {leg.distance_km} km</span>
                          <span>⏱️ {leg.estimated_duration_minutes} mins</span>
                        </div>
                      </div>
                    ))}
                  </div>

                  <p className="text-[10px] text-slate-400 italic">
                    * {optimizationResult.disclaimer}
                  </p>
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* DISPATCHES / SHIPMENTS LIST FROM POSTGRESQL */}
      <div className="space-y-4">
        <div className="flex items-center justify-between px-1">
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Truck className="w-4 h-4 text-emerald-600" /> PostgreSQL Shipment Dispatches ({displayRoutes.length})
          </h3>
        </div>

        {loading ? (
          <div className="p-12 rounded-2xl bg-white border border-slate-200/80 shadow-xs flex flex-col items-center justify-center text-slate-500 gap-3">
            <Loader2 className="w-8 h-8 animate-spin text-emerald-600" />
            <p className="text-xs font-semibold text-slate-700">Loading shipment dispatches from PostgreSQL...</p>
          </div>
        ) : displayRoutes.length === 0 ? (
          <div className="p-8 rounded-2xl bg-white border border-slate-200/80 text-center text-slate-500 text-xs">
            No active shipment dispatches registered yet. Click "Create Shipment Dispatch" above to register a new cold chain transit.
          </div>
        ) : (
          <div className="space-y-4">
            {displayRoutes.map((route) => (
              <div
                key={route.id}
                className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-xs hover:shadow-md transition-shadow"
              >
                <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-extrabold text-slate-900 bg-slate-100 px-2 py-0.5 rounded">
                        {route.id}
                      </span>
                      <Badge
                        variant={
                          route.status === 'In Transit' || route.status === 'Dispatched'
                            ? 'blue'
                            : route.status === 'Delivered'
                            ? 'emerald'
                            : 'amber'
                        }
                      >
                        {route.status}
                      </Badge>
                      <span className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                        Batch: {route.batchCode}
                      </span>
                    </div>

                    <h3 className="text-base font-bold text-slate-900 mt-2">{route.name}</h3>
                    <p className="text-xs text-slate-600 mt-0.5">{route.driver}</p>
                    {route.dispatchedAt && (
                      <p className="text-[11px] text-slate-400 mt-1">Dispatched: {route.dispatchedAt}</p>
                    )}
                  </div>

                  <div className="flex items-center gap-3 text-xs">
                    {route.status === 'Pending' && (
                      <button
                        onClick={() => handleDispatchShipment(route.rawId)}
                        className="px-3.5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold transition-all shadow-xs cursor-pointer flex items-center gap-1.5"
                      >
                        <Send className="w-3.5 h-3.5" /> Dispatch Shipment
                      </button>
                    )}
                    <button
                      onClick={() => {
                        const stops = [{ name: route.source }, { name: route.destination }];
                        setSelectedStops(stops);
                        handleRunOptimization(stops);
                        window.scrollTo({ top: 300, behavior: 'smooth' });
                      }}
                      className="px-3 py-2 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 rounded-xl border border-emerald-200 text-xs font-bold transition-colors cursor-pointer flex items-center gap-1.5"
                    >
                      <Navigation className="w-3.5 h-3.5" /> Optimize Shipment Route
                    </button>
                  </div>
                </div>

                <div className="mt-5 pt-4 border-t border-slate-100">
                  <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">Transit Locations</p>
                  <div className="flex flex-wrap items-center gap-2 text-xs">
                    {route.waypoints.map((point, idx) => (
                      <React.Fragment key={idx}>
                        <span className="px-3 py-1 bg-slate-100 rounded-lg font-semibold text-slate-700 flex items-center gap-1.5">
                          <MapPin className="w-3.5 h-3.5 text-emerald-600" />
                          {point}
                        </span>
                        {idx < route.waypoints.length - 1 && <ArrowRight className="w-3.5 h-3.5 text-slate-300" />}
                      </React.Fragment>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* CREATE SHIPMENT MODAL */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4 my-8 animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-base font-bold text-slate-900">Create & Dispatch Shipment</h3>
                <p className="text-xs text-slate-500">Link order, harvest batch & reefer vehicle in PostgreSQL</p>
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

            <form onSubmit={handleCreateShipment} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Select Retailer Wholesale Order <span className="text-rose-500">*</span>
                </label>
                <select
                  value={formData.order_id}
                  onChange={(e) => handleOrderChange(e.target.value)}
                  required
                  className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-900 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden"
                >
                  <option value="">-- Select Retailer Order --</option>
                  {orders.map((o) => (
                    <option key={o.id} value={o.id}>
                      {o.order_number || `Order #${o.id}`} — {o.buyer?.name || `Buyer #${o.buyer_id}`} ({o.total_quantity} kg, ₹{o.total_amount}) [{o.status}]
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Select Eligible Harvest Batch <span className="text-rose-500">*</span>
                </label>
                <select
                  value={formData.batch_id}
                  onChange={(e) => {
                    const selectedB = batches.find((b) => b.id === parseInt(e.target.value));
                    setFormData({
                      ...formData,
                      batch_id: e.target.value,
                      source: selectedB ? selectedB.origin_location : formData.source,
                    });
                  }}
                  required
                  className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-900 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden"
                >
                  <option value="">-- Select Harvest Batch --</option>
                  {eligibleBatches.map((b) => (
                    <option key={b.id} value={b.id}>
                      {b.batch_code || `Batch #${b.id}`} — {b.product?.name || `Product #${b.product_id}`} ({b.quantity} kg | {b.origin_location} | {b.quality_grade})
                    </option>
                  ))}
                </select>
                {eligibleBatches.length === 0 && (
                  <p className="text-[11px] text-amber-600 font-medium mt-1">
                    ⚠️ No eligible batches match the product of the selected order.
                  </p>
                )}
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Source Facility / Origin <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Pune Regional Hub - Cold Section 3"
                  value={formData.source}
                  onChange={(e) => setFormData({ ...formData, source: e.target.value })}
                  className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-900 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Destination Retail Hub <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. FreshMart Retail Hub"
                  value={formData.destination}
                  onChange={(e) => setFormData({ ...formData, destination: e.target.value })}
                  className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-900 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Reefer Vehicle # <span className="text-rose-500">*</span>
                  </label>
                  <select
                    value={formData.vehicle_number}
                    onChange={(e) => setFormData({ ...formData, vehicle_number: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-900 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden"
                  >
                    <option value="MH-15-AB-1234">MH-15-AB-1234 (Reefer Truck)</option>
                    <option value="MH-12-CD-5678">MH-12-CD-5678 (Cold Van)</option>
                    <option value="MH-14-EF-9012">MH-14-EF-9012 (Temperature Controlled)</option>
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
                    <option value="In Transit">In Transit</option>
                    <option value="Dispatched">Dispatched</option>
                    <option value="Pending">Pending</option>
                  </select>
                </div>
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
                  disabled={isSubmitting || eligibleBatches.length === 0}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl text-xs transition-all shadow-md shadow-emerald-950/20 flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" /> Saving & Dispatching...
                    </>
                  ) : (
                    <>
                      <Send className="w-3.5 h-3.5" /> Dispatch Shipment
                    </>
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
