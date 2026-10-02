import React from 'react';
import { useAuth } from '../context/AuthContext';
import { ConsumerMarketplace } from './ConsumerMarketplace';
import { RetailerMarketplace } from './RetailerMarketplace';
import { AccessDenied } from './AccessDenied';

export const Marketplace = () => {
  const { user } = useAuth();

  if (user?.role === 'retailer') {
    return <RetailerMarketplace />;
  }

  if (user?.role === 'consumer') {
    return <ConsumerMarketplace />;
  }

  if (user?.role === 'admin') {
    return <RetailerMarketplace />;
  }

  return <AccessDenied />;
};

export default Marketplace;
