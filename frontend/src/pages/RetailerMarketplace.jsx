import React, { useState, useEffect } from 'react';
import { Store, ShoppingCart, Star, QrCode, Search, Loader2, AlertCircle, CheckCircle2, X, Truck, Package } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { productsAPI, inventoryAPI, batchesAPI, ordersAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';

export const RetailerMarketplace = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [products, setProducts] = useState([]);
  const [inventory, setInventory] = useState([]);
  const [batches, setBatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');

  // Checkout Modal State
  const [orderModalProduct, setOrderModalProduct] = useState(null);
  const [orderQty, setOrderQty] = useState(100);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState(null);

  const loadUpstreamData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [prodRes, invRes, batchRes] = await Promise.all([
        productsAPI.getProducts().catch(() => ({ data: [] })),
        inventoryAPI.getInventory({ scope: 'upstream' }).catch(() => ({ data: [] })),
        batchesAPI.getBatches({ available_only: true }).catch(() => ({ data: [] })),
      ]);

      setProducts(prodRes.data || []);
      setInventory(invRes.data || []);
      setBatches(batchRes.data || []);
    } catch (err) {
      console.error("Failed to load retailer marketplace data:", err);
      setError("Failed to connect to backend service.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUpstreamData();
  }, []);

  const handleWholesaleOrderSubmit = async (e) => {
    e.preventDefault();
    if (!orderModalProduct) return;

    setFormError(null);
    const qty = parseFloat(orderQty);

    if (isNaN(qty) || qty <= 0) {
      setFormError("Order quantity must be greater than 0.");
      return;
    }
    if (qty > orderModalProduct.availableStock) {
      setFormError(`Requested quantity (${qty} kg) exceeds available stock (${orderModalProduct.availableStock} kg).`);
      return;
    }

    setIsSubmitting(true);

    try {
      const orderNum = `ORD-2026-RET-${Math.floor(1000 + Math.random() * 9000)}`;
      const payload = {
        order_number: orderNum,
        buyer_id: user?.id,
        status: 'Confirmed',
        items: [
          {
            product_id: orderModalProduct.rawId,
            quantity: qty,
            price: orderModalProduct.pricePerKg,
          },
        ],
      };

      await ordersAPI.createOrder(payload);

      setSuccessMessage(`Wholesale Order #${orderNum} successfully placed for ${qty} kg of ${orderModalProduct.name}! Sent to Distributor for fulfillment.`);
      setOrderModalProduct(null);

      await loadUpstreamData();
      setTimeout(() => setSuccessMessage(null), 6000);
    } catch (err) {
      console.error("Error creating retailer wholesale order:", err);
      const msg = err.response?.data?.detail || "Failed to place wholesale order. Please check inputs.";
      setFormError(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  const displayProducts = products.map((p) => {
    const matchingInventory = inventory.filter((inv) => inv.batch?.product_id === p.id && (!inv.owner_id) && inv.quantity > 0);
    let availableStock = matchingInventory.reduce((acc, inv) => acc + (inv.quantity || 0), 0);

    const matchingBatches = batches.filter((b) => b.product_id === p.id && (b.quantity > 0) && b.status !== 'Consumed' && b.status !== 'Depleted');
    if (availableStock <= 0 && matchingBatches.length > 0) {
      availableStock = matchingBatches.reduce((acc, b) => acc + (b.quantity || 0), 0);
    }

    const matchingBatch = matchingBatches[0] || batches[0];
    const farmerName = matchingBatch?.farmer?.name || "Verified Farm Produce";
    const originLocation = matchingBatch?.origin_location || "Regional Farm Hub";

    const pricePerKg = p.price ? p.price : (p.category === 'Fruits' ? 120 : 45);

    const getProductImage = (name, category) => {
      const nameLower = (name || '').toLowerCase().trim();
      if (nameLower.includes('onion')) {
        return "https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?w=500&auto=format&fit=crop&q=80";
      }
      if (nameLower.includes('potato')) {
        return "https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=500&auto=format&fit=crop&q=80";
      }
      if (nameLower.includes('apple')) {
        return "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=500&auto=format&fit=crop&q=80";
      }
      if (nameLower.includes('mango')) {
        return "https://images.unsplash.com/photo-1553279768-865429fa0078?w=500&auto=format&fit=crop&q=80";
      }
      return category === 'Fruits'
        ? "https://images.unsplash.com/photo-1553279768-865429fa0078?w=500&auto=format&fit=crop&q=80"
        : "https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?w=500&auto=format&fit=crop&q=80";
    };

    const image = getProductImage(p.name, p.category);

    return {
      id: p.id.toString(),
      rawId: p.id,
      name: p.name,
      category: p.category,
      unit: p.unit || 'kg',
      pricePerKg: pricePerKg,
      availableStock: Math.max(0, availableStock),
      farmer: `${farmerName} • ${originLocation}`,
      harvestTime: matchingBatch ? `Harvested: ${matchingBatch.harvest_date}` : "Verified Stock",
      batchId: matchingBatch ? matchingBatch.id.toString() : "1",
      batchCode: matchingBatch ? (matchingBatch.batch_code || `BATCH-${matchingBatch.id}`) : "BATCH-2026-001",
      image: image,
    };
  });

  const filteredProducts = displayProducts.filter((p) => {
    const matchesSearch =
      p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.category.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.farmer.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'All' || p.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="space-y-6">
      {/* Retailer Marketplace Hero Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white p-6 rounded-2xl shadow-md flex flex-col md:flex-row md:items-center justify-between gap-4 border border-indigo-500/20">
        <div>
          <div className="flex items-center gap-2">
            <Store className="w-5 h-5 text-indigo-400" />
            <span className="text-xs font-bold uppercase tracking-wider text-indigo-300">Retailer Wholesale Supply Marketplace</span>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-400/30">
              Upstream Supply Chain
            </span>
          </div>
          <h2 className="text-2xl font-black mt-1">Purchase Fresh Produce Stock from Farmers</h2>
          <p className="text-xs text-slate-300 mt-1">
            Place wholesale produce orders for your retail store. Orders are dispatched via cold-chain distributors directly to your store inventory.
          </p>
        </div>
      </div>

      {/* Control Bar: Search & Category Filter */}
      <div className="bg-white p-4 rounded-xl border border-slate-200/80 flex flex-col sm:flex-row items-center justify-between gap-4 shadow-xs">
        <div className="relative w-full sm:w-72">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search crop, category, or farm origin..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-slate-50 border border-slate-200 rounded-lg pl-9 pr-3 py-2 text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-hidden"
          />
        </div>

        <div className="flex items-center gap-1 overflow-x-auto w-full sm:w-auto">
          {['All', 'Fruits', 'Vegetables'].map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg whitespace-nowrap transition-colors cursor-pointer ${
                selectedCategory === cat
                  ? 'bg-indigo-600 text-white shadow-2xs'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Success Banner */}
      {successMessage && (
        <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center justify-between text-emerald-800 text-xs font-medium animate-in fade-in duration-200">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>{successMessage}</span>
          </div>
          <Link to="/orders" className="text-xs font-bold text-emerald-700 hover:underline">
            View Wholesale Orders &rarr;
          </Link>
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
          <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
          <p className="text-xs font-semibold text-slate-700">Loading upstream produce catalog & farm stock...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProducts.map((product) => (
            <div
              key={product.id}
              className="bg-white rounded-2xl border border-slate-200/80 shadow-xs hover:shadow-lg transition-all duration-200 overflow-hidden flex flex-col justify-between"
            >
              <div>
                <div className="relative h-44 w-full bg-slate-100 overflow-hidden">
                  <img
                    src={product.image}
                    alt={product.name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                  <div className="absolute top-3 left-3">
                    <span className="text-[10px] font-bold px-2.5 py-1 rounded-full bg-slate-900/80 text-white backdrop-blur-xs">
                      Upstream Harvest
                    </span>
                  </div>
                </div>

                <div className="p-5 space-y-2">
                  <div className="flex items-center justify-between text-xs text-slate-500">
                    <span className="font-semibold text-indigo-700">{product.harvestTime}</span>
                    <span className="font-mono text-slate-500 text-[11px]">{product.batchCode}</span>
                  </div>

                  <h3 className="text-base font-bold text-slate-900 leading-snug">{product.name}</h3>
                  <p className="text-xs text-slate-500">{product.farmer}</p>

                  <div className="pt-2 flex items-baseline justify-between">
                    <div className="flex items-baseline gap-2">
                      <span className="text-xl font-black text-slate-900">₹{product.pricePerKg}</span>
                      <span className="text-[10px] text-slate-500">/ {product.unit}</span>
                    </div>
                    <span className="text-[11px] font-bold text-slate-600">
                      Upstream Stock: <strong className="text-indigo-700 font-extrabold">{product.availableStock} kg</strong>
                    </span>
                  </div>
                </div>
              </div>

              <div className="p-5 pt-0 flex items-center justify-between gap-2 border-t border-slate-100 mt-2">
                <Link
                  to={`/traceability?batch=${product.batchId}`}
                  className="flex items-center gap-1 px-3 py-2 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
                >
                  <QrCode className="w-3.5 h-3.5 text-indigo-600" />
                  <span>Trace Batch</span>
                </Link>

                <button
                  onClick={() => {
                    setFormError(null);
                    setOrderQty(100);
                    setOrderModalProduct(product);
                  }}
                  disabled={product.availableStock <= 0}
                  className="flex-1 flex items-center justify-center gap-1.5 py-2 px-3 rounded-lg text-xs font-bold transition-all cursor-pointer bg-indigo-600 hover:bg-indigo-500 text-white shadow-xs disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ShoppingCart className="w-3.5 h-3.5" /> {product.availableStock > 0 ? "Place Wholesale Order" : "Out of Stock"}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* RETAILER WHOLESALE ORDER MODAL */}
      {orderModalProduct && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4 my-8 animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-base font-bold text-slate-900">Wholesale Produce Purchase</h3>
                <p className="text-xs text-slate-500">Order upstream stock for retail store fulfillment</p>
              </div>
              <button
                onClick={() => setOrderModalProduct(null)}
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

            <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-1.5 text-xs">
              <div className="flex items-center justify-between">
                <span className="font-bold text-slate-900 text-sm">{orderModalProduct.name}</span>
                <span className="font-mono text-indigo-700 font-bold">₹{orderModalProduct.pricePerKg} / {orderModalProduct.unit}</span>
              </div>
              <p className="text-slate-600">{orderModalProduct.farmer}</p>
              <div className="flex items-center justify-between pt-1 text-[11px] text-slate-500">
                <span>Batch: <strong className="font-mono text-slate-800">{orderModalProduct.batchCode}</strong></span>
                <span>Available Upstream Stock: <strong className="text-indigo-700">{orderModalProduct.availableStock} kg</strong></span>
              </div>
            </div>

            <form onSubmit={handleWholesaleOrderSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Wholesale Quantity ({orderModalProduct.unit}) <span className="text-rose-500">*</span>
                </label>
                <input
                  type="number"
                  step="1"
                  min="1"
                  max={orderModalProduct.availableStock}
                  required
                  value={orderQty}
                  onChange={(e) => setOrderQty(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-900 focus:ring-2 focus:ring-indigo-500 focus:outline-hidden"
                />
              </div>

              <div className="p-3 bg-indigo-50 border border-indigo-200 rounded-xl flex items-center justify-between text-xs font-bold text-indigo-900">
                <span>Total Wholesale Order Amount:</span>
                <span className="text-base text-indigo-700">₹{(parseFloat(orderQty || 0) * orderModalProduct.pricePerKg).toFixed(2)}</span>
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setOrderModalProduct(null)}
                  className="px-4 py-2 border border-slate-300 rounded-xl text-xs font-semibold text-slate-700 hover:bg-slate-50 cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl text-xs transition-all shadow-md shadow-indigo-950/20 flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" /> Submitting Order...
                    </>
                  ) : (
                    <>Submit Wholesale Order</>
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
