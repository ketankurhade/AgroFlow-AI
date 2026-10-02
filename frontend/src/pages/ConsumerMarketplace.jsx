import React, { useState, useEffect } from 'react';
import { MARKETPLACE_PRODUCTS as MOCK_MARKETPLACE } from '../data/mockData';
import { Badge } from '../components/common/Badge';
import { Store, ShoppingCart, Star, ShieldCheck, QrCode, Check, ArrowRight, Search, Loader2, AlertCircle, CheckCircle2, X } from 'lucide-react';
import { Link } from 'react-router-dom';
import { productsAPI, inventoryAPI, batchesAPI, ordersAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';

export const ConsumerMarketplace = () => {
  const { user } = useAuth();
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
  const [orderQty, setOrderQty] = useState(25);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState(null);

  // Load real PostgreSQL data on mount
  const loadMarketplaceData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [prodRes, invRes, batchRes] = await Promise.all([
        productsAPI.getProducts().catch(() => ({ data: [] })),
        inventoryAPI.getInventory().catch(() => ({ data: [] })),
        batchesAPI.getBatches().catch(() => ({ data: [] })),
      ]);

      setProducts(prodRes.data || []);
      setInventory(invRes.data || []);
      setBatches(batchRes.data || []);
    } catch (err) {
      console.error("Failed to load consumer marketplace data:", err);
      setError("Failed to connect to backend. Displaying demo marketplace catalog.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMarketplaceData();
  }, []);

  const handleCheckoutSubmit = async (e) => {
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
      const orderNum = `AGRO-M8-CONSUMER-${Math.floor(100 + Math.random() * 900)}`;
      const payload = {
        order_number: orderNum,
        buyer_id: user?.id || 3, // Use authenticated user ID or default buyer 3 (FreshMart Retail)
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

      setSuccessMessage(`Order #${orderNum} successfully placed for ${qty} kg of ${orderModalProduct.name}! Track your purchase in My Orders.`);
      setOrderModalProduct(null);

      // Refresh inventory & orders data
      await loadMarketplaceData();

      setTimeout(() => setSuccessMessage(null), 6000);
    } catch (err) {
      console.error("Error creating consumer order:", err);
      const msg = err.response?.data?.detail || "Failed to place order. Check network logs.";
      setFormError(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Map real backend products + PostgreSQL retailer inventory availability
  const displayProducts = products
    .map((p) => {
      // Calculate total retailer stock for this product
      const matchingInventory = inventory.filter((inv) => inv.batch?.product_id === p.id && inv.quantity > 0);
      const availableStock = matchingInventory.reduce((acc, inv) => acc + (inv.quantity || 0), 0);

      const matchingBatches = batches.filter((b) => b.product_id === p.id);
      const matchingBatch = matchingBatches[0] || (matchingInventory[0]?.batch) || batches[0];
      const farmerName = matchingBatch?.farmer?.name || "Verified Farm Origin";
      const originLocation = matchingBatch?.origin_location || "Regional Hub";

      const pricePerKg = p.price ? p.price : (p.category === 'Fruits' ? 120 : 45);
      const discountPrice = Math.round(pricePerKg * 0.9);

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
        discountPrice: discountPrice,
        availableStock: Math.max(0, availableStock),
        farmer: `${farmerName} • ${originLocation}`,
        harvestTime: matchingBatch ? `Harvested: ${matchingBatch.harvest_date}` : "Verified Batch",
        batchId: matchingBatch ? matchingBatch.id.toString() : "1",
        batchCode: matchingBatch ? (matchingBatch.batch_code || `BATCH-${matchingBatch.id}`) : "BATCH-2026-001",
        freshnessIndex: 98,
        rating: 4.9,
        reviews: 124,
        badge: availableStock > 0 ? "In Stock (Retail Store)" : "Out of Stock",
        stockVariant: availableStock > 0 ? "emerald" : "rose",
        image: image,
      };
    });

  // Filtering
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
      {/* Consumer Hero Banner */}
      <div className="bg-gradient-to-r from-emerald-600 via-teal-600 to-emerald-800 text-white p-6 rounded-2xl shadow-md flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Store className="w-5 h-5 text-emerald-200" />
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-200">AgroFlow Direct Marketplace</span>
            {products.length > 0 && (
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-white/20 text-white border border-white/30">
                Real PostgreSQL Catalog
              </span>
            )}
          </div>
          <h2 className="text-2xl font-black mt-1">Farm-Fresh Produce with 100% Provenance</h2>
          <p className="text-xs text-emerald-100 mt-1">
            Buy produce harvested directly by verified farmer co-ops. Scan QR codes on any pack to trace origin.
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
            className="w-full bg-slate-50 border border-slate-200 rounded-lg pl-9 pr-3 py-2 text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-hidden"
          />
        </div>

        <div className="flex items-center gap-1 overflow-x-auto w-full sm:w-auto">
          {['All', 'Fruits', 'Vegetables'].map((cat) => (
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

      {/* Success Banner */}
      {successMessage && (
        <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center justify-between text-emerald-800 text-xs font-medium animate-in fade-in duration-200">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>{successMessage}</span>
          </div>
          <Link to="/orders" className="text-xs font-bold text-emerald-700 hover:underline">
            View My Orders &rarr;
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
          <Loader2 className="w-8 h-8 animate-spin text-emerald-600" />
          <p className="text-xs font-semibold text-slate-700">Loading produce catalog & live inventory from PostgreSQL...</p>
        </div>
      ) : (
        /* Product Cards Grid */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProducts.map((product) => (
            <div
              key={product.id}
              className="bg-white rounded-2xl border border-slate-200/80 shadow-xs hover:shadow-lg transition-all duration-200 overflow-hidden flex flex-col justify-between"
            >
              <div>
                {/* Image & Badge Overlay */}
                <div className="relative h-44 w-full bg-slate-100 overflow-hidden">
                  <img
                    src={product.image}
                    alt={product.name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                  <div className="absolute top-3 left-3">
                    <span className="text-[10px] font-bold px-2.5 py-1 rounded-full bg-emerald-600 text-white shadow-xs">
                      {product.badge}
                    </span>
                  </div>
                  <div className="absolute top-3 right-3">
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-900/80 backdrop-blur-md text-emerald-400 border border-emerald-500/40">
                      {product.freshnessIndex}% Freshness Score
                    </span>
                  </div>
                </div>

                {/* Product Info */}
                <div className="p-5 space-y-2">
                  <div className="flex items-center justify-between text-xs text-slate-500">
                    <span className="font-semibold text-emerald-700">{product.harvestTime}</span>
                    <div className="flex items-center gap-1 text-amber-500 font-bold">
                      <Star className="w-3.5 h-3.5 fill-amber-400" />
                      <span>{product.rating}</span>
                      <span className="text-slate-400 font-normal">({product.reviews})</span>
                    </div>
                  </div>

                  <h3 className="text-base font-bold text-slate-900 leading-snug">{product.name}</h3>
                  <p className="text-xs text-slate-500">{product.farmer}</p>

                  <div className="pt-2 flex items-baseline justify-between">
                    <div className="flex items-baseline gap-2">
                      <span className="text-xl font-black text-slate-900">₹{product.pricePerKg}</span>
                      <span className="text-[10px] text-slate-500">/ {product.unit}</span>
                    </div>
                    <span className="text-[11px] font-bold text-slate-600">
                      Stock: <strong className="text-emerald-700 font-extrabold">{product.availableStock} kg</strong>
                    </span>
                  </div>
                </div>
              </div>

              {/* Card Action Bar */}
              <div className="p-5 pt-0 flex items-center justify-between gap-2 border-t border-slate-100 mt-2">
                <Link
                  to={`/traceability?batch=${product.batchId}`}
                  className="flex items-center gap-1 px-3 py-2 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
                  title="Scan QR Provenance"
                >
                  <QrCode className="w-3.5 h-3.5 text-emerald-600" />
                  <span>Trace Batch</span>
                </Link>

                <button
                  onClick={() => {
                    setFormError(null);
                    setOrderQty(25);
                    setOrderModalProduct(product);
                  }}
                  disabled={product.availableStock <= 0}
                  className="flex-1 flex items-center justify-center gap-1.5 py-2 px-3 rounded-lg text-xs font-bold transition-all cursor-pointer bg-emerald-600 hover:bg-emerald-500 text-white shadow-xs disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ShoppingCart className="w-3.5 h-3.5" /> {product.availableStock > 0 ? "Direct Purchase" : "Out of Stock"}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* CONSUMER ORDER / CHECKOUT MODAL */}
      {orderModalProduct && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4 my-8 animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-base font-bold text-slate-900">Direct Farm Purchase</h3>
                <p className="text-xs text-slate-500">Order from PostgreSQL catalog & create order in supply chain</p>
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
                <span className="font-mono text-emerald-700 font-bold">₹{orderModalProduct.pricePerKg} / {orderModalProduct.unit}</span>
              </div>
              <p className="text-slate-600">{orderModalProduct.farmer}</p>
              <div className="flex items-center justify-between pt-1 text-[11px] text-slate-500">
                <span>Associated Batch: <strong className="font-mono text-slate-800">{orderModalProduct.batchCode}</strong></span>
                <span>Available Stock: <strong className="text-emerald-700">{orderModalProduct.availableStock} kg</strong></span>
              </div>
            </div>

            <form onSubmit={handleCheckoutSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Purchase Quantity ({orderModalProduct.unit}) <span className="text-rose-500">*</span>
                </label>
                <input
                  type="number"
                  step="1"
                  min="1"
                  max={orderModalProduct.availableStock}
                  required
                  value={orderQty}
                  onChange={(e) => setOrderQty(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-900 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden"
                />
              </div>

              <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl flex items-center justify-between text-xs font-bold text-emerald-900">
                <span>Total Calculated Contract Amount:</span>
                <span className="text-base text-emerald-700">₹{(parseFloat(orderQty || 0) * orderModalProduct.pricePerKg).toFixed(2)}</span>
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
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl text-xs transition-all shadow-md shadow-emerald-950/20 flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" /> Placing Order...
                    </>
                  ) : (
                    <>Confirm & Submit Order to PostgreSQL</>
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
