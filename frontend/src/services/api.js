import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: Attach JWT Token if present in localStorage
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response Interceptor: Handle 401 Unauthorized cleanly
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token');
      // Optional: dispatch custom event or allow AuthContext/caller to react
    }
    return Promise.reject(error);
  }
);

// AUTH API Services
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  getCurrentUser: () => api.get('/auth/me'),
};

// PRODUCTS API Services
export const productsAPI = {
  getProducts: (params) => api.get('/products', { params }),
  getProduct: (id) => api.get(`/products/${id}`),
};

// BATCHES API Services
export const batchesAPI = {
  getBatches: (params) => api.get('/batches', { params }),
  getBatch: (id) => api.get(`/batches/${id}`),
  createBatch: (data) => api.post('/batches', data),
};

// INVENTORY API Services
export const inventoryAPI = {
  getInventory: (params) => api.get('/inventory', { params }),
  getInventoryItem: (id) => api.get(`/inventory/${id}`),
  createInventory: (data) => api.post('/inventory', data),
};

// ORDERS API Services
export const ordersAPI = {
  getOrders: (params) => api.get('/orders', { params }),
  getOrder: (id) => api.get(`/orders/${id}`),
  createOrder: (data) => api.post('/orders', data),
  updateOrderStatus: (id, data) => api.patch(`/orders/${id}/status`, data),
};

// SHIPMENTS API Services
export const shipmentsAPI = {
  getShipments: (params) => api.get('/shipments', { params }),
  getShipment: (id) => api.get(`/shipments/${id}`),
  createShipment: (data) => api.post('/shipments', data),
  updateShipmentStatus: (id, status) => api.patch(`/shipments/${id}/status`, { status }),
};

// TRACEABILITY API Services
export const traceabilityAPI = {
  getBatchTraceability: (batchId) => api.get(`/traceability/batch/${batchId}`),
  createTraceabilityEvent: (data) => api.post('/traceability/events', data),
};

// ROUTE OPTIMIZATION API Services
export const routesAPI = {
  optimizeRoute: (data) => api.post('/routes/optimize', data),
  getSupportedLocations: () => api.get('/routes/locations'),
};

// SPOILAGE INTELLIGENCE API Services
export const spoilageAPI = {
  getRisk: (params) => api.get('/spoilage/risk', { params }),
  getSummary: () => api.get('/spoilage/summary'),
  predictML: (data) => api.post('/spoilage/ml-predict', data),
  getModelSummaryML: () => api.get('/spoilage/ml-model-summary'),
  analyzeCombined: (data) => api.post('/spoilage/analyze', data),
};

// ML DEMAND FORECASTING API Services
export const demandAPI = {
  predict: (data) => api.post('/demand/predict', data),
  getModelSummary: () => api.get('/demand/model-summary'),
  getForecast: (productName) => api.get('/demand/forecast', { params: { product_name: productName } }),
};

// ML PRICE FORECASTING API Services
export const priceAPI = {
  predict: (data) => api.post('/price/predict', data),
  getModelSummary: () => api.get('/price/model-summary'),
  getForecast: (productName) => api.get('/price/forecast', { params: { product_name: productName } }),
};

// INTELLIGENCE INTEGRATION & DECISION LAYER API Services
export const intelligenceAPI = {
  analyze: (data) => api.post('/intelligence/analyze', data),
};

export default api;
