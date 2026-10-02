import React from 'react';
import { useAuth } from '../context/AuthContext';
import { AdminDashboard } from '../components/dashboard/roleDashboards/AdminDashboard';
import { FarmerDashboard } from '../components/dashboard/roleDashboards/FarmerDashboard';
import { SupplyChainManagerDashboard } from '../components/dashboard/roleDashboards/SupplyChainManagerDashboard';
import { DistributorDashboard } from '../components/dashboard/roleDashboards/DistributorDashboard';
import { RetailerDashboard } from '../components/dashboard/roleDashboards/RetailerDashboard';
import { ConsumerDashboard } from '../components/dashboard/roleDashboards/ConsumerDashboard';

export const Dashboard = () => {
  const { user } = useAuth();
  const role = (user?.role || 'admin').toLowerCase();

  switch (role) {
    case 'farmer':
      return <FarmerDashboard user={user} />;
    case 'supply_chain_manager':
    case 'collection_center':
    case 'warehouse':
      return <SupplyChainManagerDashboard user={user} />;
    case 'distributor':
      return <DistributorDashboard user={user} />;
    case 'retailer':
      return <RetailerDashboard user={user} />;
    case 'consumer':
      return <ConsumerDashboard user={user} />;
    case 'admin':
    default:
      return <AdminDashboard user={user} />;
  }
};
