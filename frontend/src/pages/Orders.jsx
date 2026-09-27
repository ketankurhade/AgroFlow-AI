import React, { useState, useEffect } from 'react';
import { ORDERS as MOCK_ORDERS } from '../data/mockData';
import { Badge } from '../components/common/Badge';
import { Plus, Search, Loader2, AlertCircle, CheckCircle2, X } from 'lucide-react';
import { ordersAPI, productsAPI } from '../services/api';

export const Orders = () => {
  const [orders, setOrders] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  const [selectedStatus, setSelectedStatus] = useState('All');
  const [searchTerm, setSearchTerm] = useState('');
  
  // Modal State
  const [showOrderModal, setShowOrderModal] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState(null);

  // Form State
  const [formData, setFormData] = useState({
    order_number: '',
    buyer_id: 3, // Default to FreshMart Retail (ID 3)
    product_id: '',
    quantity: 250,
    price: 3.5,
    status: 'Confirmed',
  });

  // Pre-configured buyers from seeded backend data
  const buyerOptions = [
    { id: 3, name: 'FreshMart Retail', email: 'buyer.freshmart@agroflow.com' },
    { id: 4, name: 'Organic Foods Co', email: 'buyer.organic@agroflow.com' },
  ];

  const loadOrdersAndProducts = async () => {
    setLoading(true);
    setError(null);
    try {
      const [orderRes, prodRes] = await Promise.all([
        ordersAPI.getOrders().catch(() => ({ data: [] })),
        productsAPI.getProducts().catch(() => ({ data: [] })),
      ]);

      const fetchedOrders = orderRes.data || [];
      const fetchedProducts = prodRes.data || [];

      setOrders(fetchedOrders);
      setProducts(fetchedProducts);

      if (fetchedProducts.length > 0 && !formData.product_id) {
        setFormData((prev) => ({ ...prev, product_id: fetchedProducts[0].id }));
      }
    } catch (err) {
      console.error("Failed to load wholesale orders:", err);
      setError("Failed to fetch live orders from backend. Displaying cached orders.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadOrdersAndProducts();
  }, []);

  const handleCreateOrder = async (e) => {
    e.preventDefault();
    setFormError(null);

    // Validation
    const qty = parseFloat(formData.quantity);
    const priceVal = parseFloat(formData.price);

    if (isNaN(qty) || qty <= 0) {
      setFormError("Quantity must be greater than 0.");
      return;
    }
    if (isNaN(priceVal) || priceVal < 0) {
      setFormError("Price cannot be negative.");
      return;
    }
    if (!formData.product_id) {
      setFormError("Please select a product.");
      return;
    }

    setIsSubmitting(true);

    try {
      const orderNum = formData.order_number.trim() || `ORD-2026-${Math.floor(100 + Math.random() * 900)}`;

      const payload = {
        order_number: orderNum,
        buyer_id: parseInt(formData.buyer_id),
        status: formData.status,
        items: [
          {
            product_id: parseInt(formData.product_id),
            quantity: qty,
            price: priceVal,
          },
        ],
      };

      await ordersAPI.createOrder(payload);

      setSuccessMessage(`Successfully created Wholesale Order: ${payload.order_number}`);
      setShowOrderModal(false);

      // Reset form
      setFormData({
        order_number: '',
        buyer_id: 3,
        product_id: products[0]?.id || '',
        quantity: 250,
        price: 3.5,
        status: 'Confirmed',
      });

      // Refresh orders
      await loadOrdersAndProducts();

      setTimeout(() => setSuccessMessage(null), 5000);
    } catch (err) {
      console.error("Error creating order:", err);
      const msg = err.response?.data?.detail || "Failed to create order. Please check inputs.";
      setFormError(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Map real backend orders or fallback to mockData
  const displayOrders = orders.length > 0
    ? orders.map((o) => {
        const cropItems = o.items && o.items.length > 0
          ? o.items.map((i) => `${i.product?.name || 'Crop Produce'} (${i.quantity} kg @ ₹${i.price})`).join(', ')
          : 'Agricultural Produce Order';

        let progressPercent = 35;
        if (o.status === 'Delivered') progressPercent = 100;
        else if (o.status === 'In Transit' || o.status === 'In-Transit' || o.status === 'Dispatched') progressPercent = 70;
        else if (o.status === 'Processing' || o.status === 'Confirmed') progressPercent = 45;

        return {
          id: o.order_number || `ORD-${o.id}`,
          rawId: o.id,
          customer: o.buyer?.name || `Wholesale Buyer #${o.buyer_id}`,
          destination: o.buyer?.email || 'Regional Distribution Hub',
          cropItems: cropItems,
          totalValue: `₹${o.total_amount ? o.total_amount.toLocaleString() : 0}`,
          quantityKg: o.total_quantity,
          assignedFleet: o.status === 'Delivered' ? 'MH-12-CD-5678 (Delivered)' : 'MH-15-AB-1234 (Reefer)',
          progressPercent: progressPercent,
          orderDate: new Date(o.order_date || Date.now()).toLocaleDateString(),
          expectedDelivery: new Date(new Date(o.order_date || Date.now()).getTime() + 2 * 24 * 60 * 60 * 1000).toLocaleDateString(),
          status: o.status,
          priority: 'Standard Contract',
        };
      })
    : MOCK_ORDERS;

  // Filtering
  const filteredOrders = displayOrders.filter((order) => {
    const matchesSearch =
      order.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      order.customer.toLowerCase().includes(searchTerm.toLowerCase()) ||
      order.destination.toLowerCase().includes(searchTerm.toLowerCase()) ||
      order.cropItems.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = selectedStatus === 'All' || order.status === selectedStatus;
    return matchesSearch && matchesStatus;
  });

  // Calculate metrics
  const activeOrdersValue = displayOrders.reduce((acc, o) => {
    const val = parseFloat(o.totalValue.replace(/[^0-9.]/g, '')) || 0;
    return acc + val;
  }, 0);

  return (
    <div className="space-y-6">
      {/* Metrics Banner */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs">
          <div className="flex items-center gap-2">
            <p className="text-xs font-semibold text-slate-500 uppercase">Active Orders Value</p>
            {orders.length > 0 && (
              <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800">
                Real API Data
              </span>
            )}
          </div>
          <p className="text-2xl font-bold text-slate-900 mt-1">₹{activeOrdersValue.toLocaleString()}</p>
          <p className="text-[11px] text-emerald-600 font-medium"> Across {displayOrders.length} Registered Contracts</p>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs">
          <p className="text-xs font-semibold text-slate-500 uppercase">Fulfillment On-Time Rate</p>
          <p className="text-2xl font-bold text-emerald-600 mt-1">98.4%</p>
          <p className="text-[11px] text-slate-500 font-medium">Avg delivery time: 18.5 hrs</p>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs">
          <p className="text-xs font-semibold text-slate-500 uppercase">Cold Fleet In-Transit</p>
          <p className="text-2xl font-bold text-blue-600 mt-1">12 Reefer Trucks</p>
          <p className="text-[11px] text-blue-600 font-medium">IoT temperature synced</p>
        </div>
      </div>

      {/* Control Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200/80 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-xs">
        <div className="flex flex-col sm:flex-row items-center gap-3 flex-1">
          <div className="relative w-full sm:w-72">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search by order #, crop or customer..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-slate-50 border border-slate-200 rounded-lg pl-9 pr-3 py-2 text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-hidden"
            />
          </div>

          <div className="flex items-center gap-1 overflow-x-auto w-full sm:w-auto">
            {['All', 'Confirmed', 'Processing', 'In Transit', 'Delivered'].map((st) => (
              <button
                key={st}
                onClick={() => setSelectedStatus(st)}
                className={`px-3 py-1.5 text-xs font-semibold rounded-lg whitespace-nowrap transition-colors cursor-pointer ${
                  selectedStatus === st
                    ? 'bg-emerald-600 text-white shadow-2xs'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {st}
              </button>
            ))}
          </div>
        </div>

        <button
          onClick={() => {
            setFormError(null);
            setShowOrderModal(true);
          }}
          className="flex items-center justify-center gap-1.5 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold transition-all shadow-xs cursor-pointer shrink-0"
        >
          <Plus className="w-4 h-4" /> Create Wholesale Order
        </button>
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
          <p className="text-xs font-semibold text-slate-700">Loading wholesale orders from PostgreSQL...</p>
        </div>
      ) : (
        /* Order List Cards */
        <div className="space-y-4">
          {filteredOrders.length === 0 ? (
            <div className="p-8 text-center bg-white rounded-2xl border border-slate-200 text-slate-500 text-xs">
              No orders found matching your search filters.
            </div>
          ) : (
            filteredOrders.map((order) => (
              <div
                key={order.id}
                className="bg-white rounded-2xl border border-slate-200/80 p-5 shadow-xs hover:shadow-md transition-shadow"
              >
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-3">
                      <span className="font-mono text-sm font-bold text-slate-900">{order.id}</span>
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
                      <span className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                        {order.priority}
                      </span>
                    </div>

                    <h3 className="text-base font-bold text-slate-900 mt-2">{order.customer}</h3>
                    <p className="text-xs text-slate-500 mt-0.5">Destination Hub: {order.destination}</p>
                    <p className="text-xs font-semibold text-emerald-800 mt-1">Items: {order.cropItems}</p>
                  </div>

                  <div className="text-left md:text-right border-t md:border-t-0 border-slate-100 pt-3 md:pt-0">
                    <p className="text-xs text-slate-400 uppercase font-bold">Total Contract Value</p>
                    <p className="text-xl font-black text-slate-900">{order.totalValue}</p>
                    <p className="text-xs text-slate-500 mt-1">
                      Quantity: <strong className="text-slate-800">{order.quantityKg} kg</strong>
                    </p>
                  </div>
                </div>

                {/* Transit Bar */}
                <div className="mt-4 pt-4 border-t border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
                  <div className="flex-1 flex items-center gap-3">
                    <span className="text-slate-500 font-medium">Delivery Progress:</span>
                    <div className="flex-1 bg-slate-100 h-2.5 rounded-full overflow-hidden max-w-md">
                      <div
                        className="bg-emerald-600 h-full rounded-full transition-all"
                        style={{ width: `${order.progressPercent}%` }}
                      ></div>
                    </div>
                    <span className="font-mono font-bold text-slate-900">{order.progressPercent}%</span>
                  </div>

                  <div className="flex items-center gap-4 text-slate-500 text-[11px]">
                    <span>Ordered: <strong>{order.orderDate}</strong></span>
                    <span>Expected: <strong>{order.expectedDelivery}</strong></span>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* CREATE ORDER MODAL */}
      {showOrderModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4 my-8 animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-base font-bold text-slate-900">Create Wholesale Order</h3>
                <p className="text-xs text-slate-500">Record commercial purchase order in PostgreSQL</p>
              </div>
              <button
                onClick={() => setShowOrderModal(false)}
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

            <form onSubmit={handleCreateOrder} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Order Number <span className="text-slate-400 font-normal">(Auto if empty)</span>
                </label>
                <input
                  type="text"
                  placeholder="ORD-2026-103"
                  value={formData.order_number}
                  onChange={(e) => setFormData({ ...formData, order_number: e.target.value })}
                  className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-900 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Buyer / Customer Retailer <span className="text-rose-500">*</span>
                </label>
                <select
                  value={formData.buyer_id}
                  onChange={(e) => setFormData({ ...formData, buyer_id: e.target.value })}
                  required
                  className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-900 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden"
                >
                  {buyerOptions.map((b) => (
                    <option key={b.id} value={b.id}>
                      {b.name} ({b.email})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Crop Product Item <span className="text-rose-500">*</span>
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
                    Quantity (kg) <span className="text-rose-500">*</span>
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    min="0.1"
                    required
                    value={formData.quantity}
                    onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-900 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Price (₹/kg) <span className="text-rose-500">*</span>
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    required
                    value={formData.price}
                    onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-900 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Initial Order Status
                </label>
                <select
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                  className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-900 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden"
                >
                  <option value="Confirmed">Confirmed</option>
                  <option value="Processing">Processing</option>
                  <option value="In Transit">In Transit</option>
                  <option value="Delivered">Delivered</option>
                </select>
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowOrderModal(false)}
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
                      <Loader2 className="w-4 h-4 animate-spin" /> Saving Order...
                    </>
                  ) : (
                    <>Submit Order to PostgreSQL</>
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
