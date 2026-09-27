// Comprehensive Realistic Mock Data for AgroFlow AI

export const INITIAL_USER = {
  name: "Dr. Rajesh Sharma",
  email: "r.sharma@agroflow.ai",
  role: "Supply Chain Manager",
  organization: "AgroFlow Agri-Logistics Ltd.",
  avatar: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80",
  availableRoles: [
    "Farmer / Producer",
    "Collection Center Manager",
    "Warehouse Cold-Chain Lead",
    "Distributor & Logistics",
    "Retailer",
    "Supply Chain Manager (Admin)",
    "Consumer"
  ]
};

export const METRICS = {
  totalInventoryTons: 14285,
  totalInventoryGrowth: "+12.4% vs last month",
  activeBatchesCount: 342,
  activeBatchesTrend: "48 harvested today",
  pendingOrdersCount: 29,
  pendingOrdersValue: "₹18.4 Lakhs",
  highRiskBatchesCount: 14,
  highRiskTrend: "3 critical spoilage alerts",
  avgTransitHours: 18.5,
  carbonSavedKg: 4210,
  overallQualityScore: "94.2%"
};

export const PIPELINE_NODES = [
  {
    id: "farmer",
    name: "Farmer Harvesting",
    icon: "Sprout",
    count: 120,
    volume: "4,200 Tons",
    status: "Normal",
    color: "emerald",
    locationCount: "45 Cooperatives",
    desc: "Direct field harvesting & initial quality screening"
  },
  {
    id: "collection",
    name: "Collection Centers",
    icon: "Building2",
    count: 42,
    volume: "3,150 Tons",
    status: "Active",
    color: "teal",
    locationCount: "12 Hubs",
    desc: "Weight verification, grading & pre-cooling"
  },
  {
    id: "warehouse",
    name: "Cold Warehouses",
    icon: "Warehouse",
    count: 85,
    volume: "4,800 Tons",
    status: "Optimal",
    color: "green",
    locationCount: "8 Facilities",
    desc: "Atmospheric humidity control & rack storage"
  },
  {
    id: "logistics",
    name: "Distributor & Transit",
    icon: "Truck",
    count: 54,
    volume: "1,550 Tons",
    status: "In-Transit",
    color: "blue",
    locationCount: "24 Fleet Reofers",
    desc: "Refrigerated vehicle transport with real-time IoT tracking"
  },
  {
    id: "retailer",
    name: "Retail Outlets",
    icon: "Store",
    count: 310,
    volume: "585 Tons",
    status: "Stocked",
    color: "indigo",
    locationCount: "115 Stores",
    desc: "Supermarket placement & local grocery distribution"
  },
  {
    id: "consumer",
    name: "Consumer Delivery",
    icon: "ShoppingBag",
    count: 1840,
    volume: "Daily Fulfilled",
    status: "Active",
    color: "purple",
    locationCount: "Direct Market",
    desc: "QR transparency scanning & direct farm-to-table"
  }
];

export const DEMAND_FORECAST_DATA = [
  { month: "Jan", Tomatoes: 420, Mangoes: 120, Potatoes: 850, Onions: 620 },
  { month: "Feb", Tomatoes: 450, Mangoes: 150, Potatoes: 820, Onions: 640 },
  { month: "Mar", Tomatoes: 490, Mangoes: 310, Potatoes: 780, Onions: 680 },
  { month: "Apr", Tomatoes: 540, Mangoes: 680, Potatoes: 750, Onions: 710 },
  { month: "May", Tomatoes: 610, Mangoes: 950, Potatoes: 710, Onions: 740 },
  { month: "Jun (Pred)", Tomatoes: 680, Mangoes: 1100, Potatoes: 690, Onions: 790 },
  { month: "Jul (Pred)", Tomatoes: 720, Mangoes: 980, Potatoes: 670, Onions: 830 },
  { month: "Aug (Pred)", Tomatoes: 650, Mangoes: 620, Potatoes: 730, Onions: 810 }
];

export const PRICE_FORECAST_DATA = [
  { week: "W1 (Aug)", actualPrice: 42, predictedPrice: 42, lowerBound: 40, upperBound: 44, crop: "Tomatoes (₹/kg)" },
  { week: "W2 (Aug)", actualPrice: 45, predictedPrice: 44, lowerBound: 42, upperBound: 46, crop: "Tomatoes (₹/kg)" },
  { week: "W3 (Aug)", actualPrice: 48, predictedPrice: 47, lowerBound: 44, upperBound: 49, crop: "Tomatoes (₹/kg)" },
  { week: "W4 (Aug)", actualPrice: 52, predictedPrice: 51, lowerBound: 48, upperBound: 53, crop: "Tomatoes (₹/kg)" },
  { week: "W1 (Sep)", actualPrice: 55, predictedPrice: 56, lowerBound: 52, upperBound: 59, crop: "Tomatoes (₹/kg)" },
  { week: "W2 (Sep)", actualPrice: null, predictedPrice: 62, lowerBound: 57, upperBound: 66, crop: "Tomatoes (₹/kg)" },
  { week: "W3 (Sep)", actualPrice: null, predictedPrice: 58, lowerBound: 52, upperBound: 63, crop: "Tomatoes (₹/kg)" },
  { week: "W4 (Sep)", actualPrice: null, predictedPrice: 50, lowerBound: 44, upperBound: 55, crop: "Tomatoes (₹/kg)" }
];

export const CROP_CATEGORY_DISTRIBUTION = [
  { name: "Vegetables", value: 45, color: "#10b981" },
  { name: "Fruits", value: 30, color: "#f59e0b" },
  { name: "Grains & Pulses", value: 15, color: "#3b82f6" },
  { name: "Leafy Greens", value: 10, color: "#8b5cf6" }
];

export const SPOILAGE_RISK_DISTRIBUTION = [
  { name: "Low Risk (< 15%)", count: 245, color: "#10b981" },
  { name: "Moderate Risk (15-35%)", count: 83, color: "#f59e0b" },
  { name: "High Risk (> 35%)", count: 14, color: "#ef4444" }
];

export const INVENTORY_ITEMS = [
  {
    id: "INV-9041",
    cropName: "Roma Tomatoes",
    category: "Vegetables",
    location: "Nashik Hub - Bay C4",
    quantityTons: 140,
    storageTemp: "8°C",
    targetTemp: "7°C - 10°C",
    humidity: "88%",
    harvestDate: "2026-09-22",
    expiryDate: "2026-10-06",
    spoilageRiskScore: 12,
    status: "Optimal",
    shelfLifeDays: 9
  },
  {
    id: "INV-8832",
    cropName: "Alphonso Mangoes",
    category: "Fruits",
    location: "Ratnagiri Facility - Zone A",
    quantityTons: 85,
    storageTemp: "14°C",
    targetTemp: "12°C - 14°C",
    humidity: "90%",
    harvestDate: "2026-09-24",
    expiryDate: "2026-10-04",
    spoilageRiskScore: 42,
    status: "High Risk",
    shelfLifeDays: 4
  },
  {
    id: "INV-7619",
    cropName: "Fresh Spinach",
    category: "Leafy Greens",
    location: "Pune North Collection Hub",
    quantityTons: 24,
    storageTemp: "4°C",
    targetTemp: "2°C - 4°C",
    humidity: "95%",
    harvestDate: "2026-09-26",
    expiryDate: "2026-09-30",
    spoilageRiskScore: 68,
    status: "Critical Spoilage",
    shelfLifeDays: 2
  },
  {
    id: "INV-9402",
    cropName: "Basmati Paddy Rice",
    category: "Grains & Pulses",
    location: "Punjab Grain Storage #2",
    quantityTons: 620,
    storageTemp: "21°C",
    targetTemp: "18°C - 24°C",
    humidity: "55%",
    harvestDate: "2026-08-15",
    expiryDate: "2027-08-15",
    spoilageRiskScore: 3,
    status: "Optimal",
    shelfLifeDays: 320
  },
  {
    id: "INV-6510",
    cropName: "Cavendish Bananas",
    category: "Fruits",
    location: "Solapur Ripening Chamber 3",
    quantityTons: 210,
    storageTemp: "16°C",
    targetTemp: "14°C - 16°C",
    humidity: "85%",
    harvestDate: "2026-09-20",
    expiryDate: "2026-10-05",
    spoilageRiskScore: 24,
    status: "Moderate",
    shelfLifeDays: 7
  },
  {
    id: "INV-4412",
    cropName: "Red Onions",
    category: "Vegetables",
    location: "Lasalgaon Storage Silo B",
    quantityTons: 490,
    storageTemp: "18°C",
    targetTemp: "15°C - 20°C",
    humidity: "65%",
    harvestDate: "2026-09-01",
    expiryDate: "2026-12-01",
    spoilageRiskScore: 8,
    status: "Optimal",
    shelfLifeDays: 65
  },
  {
    id: "INV-3390",
    cropName: "Cold Storage Potatoes",
    category: "Vegetables",
    location: "Agra Cold Complex #1",
    quantityTons: 890,
    storageTemp: "4°C",
    targetTemp: "3°C - 5°C",
    humidity: "92%",
    harvestDate: "2026-08-28",
    expiryDate: "2027-02-28",
    spoilageRiskScore: 11,
    status: "Optimal",
    shelfLifeDays: 150
  },
  {
    id: "INV-2104",
    cropName: "Hass Avocados",
    category: "Fruits",
    location: "Bangalore Logistics Depot",
    quantityTons: 32,
    storageTemp: "9°C",
    targetTemp: "6°C - 8°C",
    humidity: "86%",
    harvestDate: "2026-09-21",
    expiryDate: "2026-10-02",
    spoilageRiskScore: 54,
    status: "High Risk",
    shelfLifeDays: 3
  }
];

export const BATCHES = [
  {
    id: "BATCH-2026-TOM-042",
    cropName: "Organic Field Tomatoes",
    farmerName: "Ramesh Farmer Co-op",
    farmLocation: "Khed, Maharashtra",
    harvestDate: "2026-09-23",
    quantityKg: 12500,
    qualityGrade: "Grade A Premium",
    currentNode: "Nashik Central Warehouse",
    temperatureLog: "7.8°C avg (Stable)",
    riskScore: 8,
    qrCodeUrl: "AGROFLOW-BATCH-2026-TOM-042",
    status: "In Cold Storage",
    timeline: [
      { stage: "Harvested", date: "2026-09-23 06:30 AM", location: "Khed Farm #12", details: "Tested 98% Brix firmness grade A." },
      { stage: "Collection", date: "2026-09-23 11:00 AM", location: "Nashik Collection Hub 2", details: "Pre-cooled to 8°C & washed." },
      { stage: "Warehouse", date: "2026-09-24 02:15 PM", location: "Nashik Central Cold Bay C4", details: "Stored under monitored RH 88%." }
    ]
  },
  {
    id: "BATCH-2026-MNG-109",
    cropName: "Ratnagiri Alphonso Mangoes",
    farmerName: "Devgad Orchard Society",
    farmLocation: "Ratnagiri, Maharashtra",
    harvestDate: "2026-09-24",
    quantityKg: 8500,
    qualityGrade: "Export Quality",
    currentNode: "Mumbai Export Reefer Unit",
    temperatureLog: "14.2°C (Elevated +2°C)",
    riskScore: 42,
    qrCodeUrl: "AGROFLOW-BATCH-2026-MNG-109",
    status: "Temperature Alert",
    timeline: [
      { stage: "Harvested", date: "2026-09-24 05:00 AM", location: "Devgad Orchard #4", details: "Tree-ripened select picking." },
      { stage: "Collection", date: "2026-09-24 01:30 PM", location: "Ratnagiri Sea Hub", details: "Fungicide treatment & grading." },
      { stage: "In-Transit", date: "2026-09-25 08:00 AM", location: "Truck MH-04-AX-9912", details: "En-route to Nhava Sheva port." }
    ]
  },
  {
    id: "BATCH-2026-SPN-881",
    cropName: "Hydroponic Spinach",
    farmerName: "GreenAgro Farms",
    farmLocation: "Pune Outskirts",
    harvestDate: "2026-09-26",
    quantityKg: 2400,
    qualityGrade: "Grade A",
    currentNode: "Pune Distribution Hub",
    temperatureLog: "4.1°C (Optimal)",
    riskScore: 68,
    qrCodeUrl: "AGROFLOW-BATCH-2026-SPN-881",
    status: "Priority Dispatch",
    timeline: [
      { stage: "Harvested", date: "2026-09-26 04:00 AM", location: "Hydroponic Bay 3", details: "Pesticide-free certified." },
      { stage: "Collection", date: "2026-09-26 07:45 AM", location: "Pune Packhouse", details: "Vacuum packed in 500g pouches." }
    ]
  },
  {
    id: "BATCH-2026-RIC-304",
    cropName: "Super Basmati Rice",
    farmerName: "Punjab Agro Collective",
    farmLocation: "Amritsar, Punjab",
    harvestDate: "2026-08-15",
    quantityKg: 620000,
    qualityGrade: "Extra Long Grain",
    currentNode: "Punjab Grain Storage #2",
    temperatureLog: "21.0°C (Controlled)",
    riskScore: 3,
    qrCodeUrl: "AGROFLOW-BATCH-2026-RIC-304",
    status: "Aged & Stored",
    timeline: [
      { stage: "Harvested", date: "2026-08-15 10:00 AM", location: "Amritsar Field Plot B", details: "Combine harvested at 14% moisture." },
      { stage: "Collection", date: "2026-08-16 02:00 PM", location: "Mandi Gate #3", details: "Moisture reduction drying applied." },
      { stage: "Warehouse", date: "2026-08-18 09:00 AM", location: "Grain Silo #2", details: "Sealed storage under N2 purging." }
    ]
  },
  {
    id: "BATCH-2026-BAN-512",
    cropName: "Grand Naine Bananas",
    farmerName: "Jalgaon Banana Growers",
    farmLocation: "Jalgaon, Maharashtra",
    harvestDate: "2026-09-20",
    quantityKg: 21000,
    qualityGrade: "Grade A",
    currentNode: "Solapur Ripening Chamber 3",
    temperatureLog: "15.8°C (Ethylene dosing)",
    riskScore: 24,
    qrCodeUrl: "AGROFLOW-BATCH-2026-BAN-512",
    status: "Ripening Phase",
    timeline: [
      { stage: "Harvested", date: "2026-09-20 07:00 AM", location: "Jalgaon Sector 8", details: "De-handed & latex washed." },
      { stage: "Collection", date: "2026-09-21 12:00 PM", location: "Jalgaon Packing Hub", details: "Box packed with ethylene absorbers." },
      { stage: "Warehouse", date: "2026-09-22 04:00 PM", location: "Solapur Chamber 3", details: "Ripening cycle day 3 active." }
    ]
  }
];

export const ORDERS = [
  {
    id: "ORD-2026-8812",
    customer: "BigBasket Distribution Center",
    destination: "Bangalore Logistics Hub",
    cropItems: "Organic Tomatoes (50 Tons), Spinach (5 Tons)",
    totalValue: "₹14,50,000",
    orderDate: "2026-09-26",
    expectedDelivery: "2026-09-28",
    priority: "High (Perishable)",
    status: "In-Transit",
    assignedFleet: "Fleet Reefer MH-12-RS-4410",
    progressPercent: 70
  },
  {
    id: "ORD-2026-8813",
    customer: "Reliance Fresh Stores",
    destination: "Mumbai Regional Marts",
    cropItems: "Alphonso Mangoes (20 Tons), Bananas (30 Tons)",
    totalValue: "₹28,20,000",
    orderDate: "2026-09-27",
    expectedDelivery: "2026-09-29",
    priority: "Express Urgent",
    status: "Processing",
    assignedFleet: "Fleet Reefer MH-04-AX-9912",
    progressPercent: 35
  },
  {
    id: "ORD-2026-8814",
    customer: "Nature's Basket Retail",
    destination: "Pune City Outlets",
    cropItems: "Hydroponic Spinach (2 Tons), Hass Avocados (3 Tons)",
    totalValue: "₹6,80,000",
    orderDate: "2026-09-27",
    expectedDelivery: "2026-09-28",
    priority: "Standard",
    status: "Pending Allocation",
    assignedFleet: "Unassigned",
    progressPercent: 10
  },
  {
    id: "ORD-2026-8810",
    customer: "More Supermarkets Ltd.",
    destination: "Hyderabad Central Depot",
    cropItems: "Red Onions (100 Tons), Potatoes (150 Tons)",
    totalValue: "₹38,00,000",
    orderDate: "2026-09-24",
    expectedDelivery: "2026-09-27",
    priority: "Medium",
    status: "Delivered",
    assignedFleet: "Fleet Heavy TS-07-UB-3001",
    progressPercent: 100
  },
  {
    id: "ORD-2026-8809",
    customer: "Swiggy Instamart Warehouse",
    destination: "Delhi NCR Dark Stores",
    cropItems: "Basmati Rice (200 Tons)",
    totalValue: "₹1,20,00,000",
    orderDate: "2026-09-22",
    expectedDelivery: "2026-09-26",
    priority: "Standard",
    status: "Delivered",
    assignedFleet: "Fleet Heavy PB-10-CZ-8821",
    progressPercent: 100
  }
];

export const HIGH_RISK_SPOILAGE_BATCHES = [
  {
    id: "INV-7619",
    batchId: "BATCH-2026-SPN-881",
    crop: "Fresh Spinach",
    location: "Pune North Collection Hub",
    riskScore: 68,
    riskLevel: "Critical",
    reason: "Respiration rate spike + ambient temp breach (5.8°C)",
    shelfLifeRemaining: "36 Hours",
    recommendedAction: "Reroute to immediate local retail or juice processors within 12h."
  },
  {
    id: "INV-2104",
    batchId: "BATCH-2026-AVO-301",
    crop: "Hass Avocados",
    location: "Bangalore Logistics Depot",
    riskScore: 54,
    riskLevel: "High",
    reason: "Chilling injury vulnerability & ethylene accumulation",
    shelfLifeRemaining: "3 Days",
    recommendedAction: "Adjust storage temp to 7.0°C and apply dynamic ventilation cycle."
  },
  {
    id: "INV-8832",
    batchId: "BATCH-2026-MNG-109",
    crop: "Alphonso Mangoes",
    location: "Ratnagiri Facility - Zone A",
    riskScore: 42,
    riskLevel: "Elevated",
    reason: "Humidity fluctuation in Bay 2 (+8% RH over target)",
    shelfLifeRemaining: "4 Days",
    recommendedAction: "Dispatch via priority reefer to cold storage hub in Mumbai."
  }
];

export const RECENT_SYSTEM_ALERTS = [
  {
    id: 1,
    timestamp: "10 mins ago",
    type: "Critical",
    title: "Temperature Anomaly in Truck MH-04-AX-9912",
    message: "Reefer compartment temperature rose to 14.2°C (Target: 10°C - 12°C). Batch BATCH-2026-MNG-109 affected."
  },
  {
    id: 2,
    timestamp: "28 mins ago",
    type: "Warning",
    title: "High Demand Surge Predicted: Tomatoes (Pune Region)",
    message: "ML engine forecasts +38% demand spike over next 7 days due to upcoming festival season."
  },
  {
    id: 3,
    timestamp: "1 hour ago",
    type: "Success",
    title: "Route Optimized for Order ORD-2026-8812",
    message: "AI route optimization cut transit time by 2.4 hours and saved 42 kg CO2 emissions."
  },
  {
    id: 4,
    timestamp: "3 hours ago",
    type: "Info",
    title: "Batch Received at Nashik Cold Hub",
    message: "12.5 Tons Organic Field Tomatoes checked in with 98% quality grade score."
  }
];

export const ROUTES_DATA = [
  {
    id: "ROUTE-MH-01",
    name: "Nashik Farm → Mumbai Central Wholesale",
    distanceKm: 168,
    estimatedTime: "4h 15m",
    optimizedTime: "3h 30m",
    timeSaved: "45 mins",
    fuelSavedLiters: 18.5,
    co2SavedKg: 46.2,
    driver: "Suresh Kumar (MH-12-RS-4410)",
    status: "Active - Optimal",
    waypoints: ["Nashik Farm Co-op", "Igatpuri Checkpoint", "Bhiwandi Cold Hub", "Mumbai Vashi Market"],
    trafficStatus: "Light Traffic on NH-160",
    tempStatus: "Normal (7.5°C)"
  },
  {
    id: "ROUTE-KA-04",
    name: "Ratnagiri Orchard → Bangalore Distribution Hub",
    distanceKm: 580,
    estimatedTime: "12h 30m",
    optimizedTime: "10h 40m",
    timeSaved: "1h 50m",
    fuelSavedLiters: 42.0,
    co2SavedKg: 105.0,
    driver: "Venkatesh R. (MH-04-AX-9912)",
    status: "Rerouted (Temp Bypass)",
    waypoints: ["Ratnagiri Hub", "Kolhapur Bypass", "Belgaum Transit", "Bangalore North Depot"],
    trafficStatus: "Moderate Highway Hold",
    tempStatus: "Warning (14.2°C)"
  },
  {
    id: "ROUTE-PB-02",
    name: "Amritsar Silo → Delhi NCR Dark Stores",
    distanceKm: 450,
    estimatedTime: "8h 45m",
    optimizedTime: "7h 20m",
    timeSaved: "1h 25m",
    fuelSavedLiters: 35.0,
    co2SavedKg: 87.5,
    driver: "Gurpreet Singh (PB-10-CZ-8821)",
    status: "Scheduled",
    waypoints: ["Amritsar Storage", "Jalandhar Depot", "Panipat Toll", "NCR Distribution"],
    trafficStatus: "Clear Expressway",
    tempStatus: "Controlled Ambient (21°C)"
  }
];

export const MARKETPLACE_PRODUCTS = [
  {
    id: "PROD-01",
    name: "Farm Fresh Organic Roma Tomatoes",
    farmer: "Ramesh Farmer Collective, Nashik",
    pricePerKg: 52,
    discountPrice: 46,
    unit: "1 kg pack",
    freshnessIndex: 98,
    harvestTime: "Harvested 24h ago",
    badge: "Grade A Organic",
    rating: 4.9,
    reviews: 124,
    image: "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=400&auto=format&fit=crop&q=80",
    batchId: "BATCH-2026-TOM-042",
    inStock: true
  },
  {
    id: "PROD-02",
    name: "GI-Tagged Ratnagiri Alphonso Mangoes",
    farmer: "Devgad Orchard Society, Ratnagiri",
    pricePerKg: 340,
    discountPrice: 299,
    unit: "1 Dozen (approx 3 kg)",
    freshnessIndex: 94,
    harvestTime: "Harvested 48h ago",
    badge: "GI Certified",
    rating: 5.0,
    reviews: 310,
    image: "https://images.unsplash.com/photo-1553279768-865429fa0078?w=400&auto=format&fit=crop&q=80",
    batchId: "BATCH-2026-MNG-109",
    inStock: true
  },
  {
    id: "PROD-03",
    name: "Pesticide-Free Hydroponic Baby Spinach",
    farmer: "GreenAgro Farms, Pune",
    pricePerKg: 120,
    discountPrice: 95,
    unit: "250g eco-pack",
    freshnessIndex: 99,
    harvestTime: "Harvested 6h ago",
    badge: "Residue Free",
    rating: 4.8,
    reviews: 86,
    image: "https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=400&auto=format&fit=crop&q=80",
    batchId: "BATCH-2026-SPN-881",
    inStock: true
  },
  {
    id: "PROD-04",
    name: "Aged Organic Super Basmati Rice",
    farmer: "Punjab Grain Producers Co-op",
    pricePerKg: 160,
    discountPrice: 145,
    unit: "5 kg cloth bag",
    freshnessIndex: 100,
    harvestTime: "Aged 12 Months",
    badge: "Export Grade",
    rating: 4.9,
    reviews: 540,
    image: "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400&auto=format&fit=crop&q=80",
    batchId: "BATCH-2026-RIC-304",
    inStock: true
  },
  {
    id: "PROD-05",
    name: "Fresh Grand Naine Bananas",
    farmer: "Jalgaon Farmers Group",
    pricePerKg: 45,
    discountPrice: 38,
    unit: "1 Bunch (approx 1.5 kg)",
    freshnessIndex: 92,
    harvestTime: "Harvested 3 days ago",
    badge: "Naturally Ripened",
    rating: 4.7,
    reviews: 95,
    image: "https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=400&auto=format&fit=crop&q=80",
    batchId: "BATCH-2026-BAN-512",
    inStock: true
  },
  {
    id: "PROD-06",
    name: "Organic Red Lasalgaon Onions",
    farmer: "Lasalgaon Agri Cooperative",
    pricePerKg: 35,
    discountPrice: 30,
    unit: "5 kg mesh bag",
    freshnessIndex: 96,
    harvestTime: "Harvested 2 weeks ago",
    badge: "Direct Farm Pick",
    rating: 4.8,
    reviews: 215,
    image: "https://images.unsplash.com/photo-1618512496248-a07fe83aa8ce?w=400&auto=format&fit=crop&q=80",
    batchId: "INV-4412",
    inStock: true
  }
];
