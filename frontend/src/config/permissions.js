/**
 * AgroFlow AI — Role-Based Access Control (RBAC) Permission Matrix
 * Maps each system role to allowed frontend page routes and actions.
 */

export const ROLE_PERMISSIONS = {
  admin: [
    '/',
    '/dashboard',
    '/inventory',
    '/batches',
    '/orders',
    '/forecasts',
    '/risk',
    '/routes',
    '/traceability',
    '/marketplace'
  ],
  farmer: [
    '/',
    '/dashboard',
    '/batches',
    '/orders',
    '/forecasts',
    '/risk',
    '/traceability'
  ],
  supply_chain_manager: [
    '/',
    '/dashboard',
    '/batches',
    '/inventory',
    '/orders',
    '/routes',
    '/forecasts',
    '/risk',
    '/traceability'
  ],
  collection_center: [
    '/',
    '/dashboard',
    '/batches',
    '/inventory',
    '/orders',
    '/routes',
    '/forecasts',
    '/risk',
    '/traceability'
  ],
  warehouse: [
    '/',
    '/dashboard',
    '/batches',
    '/inventory',
    '/orders',
    '/routes',
    '/forecasts',
    '/risk',
    '/traceability'
  ],
  distributor: [
    '/',
    '/dashboard',
    '/orders',
    '/routes',
    '/inventory',
    '/forecasts',
    '/risk',
    '/traceability'
  ],
  retailer: [
    '/',
    '/dashboard',
    '/orders',
    '/inventory',
    '/marketplace',
    '/forecasts',
    '/risk',
    '/traceability'
  ],
  consumer: [
    '/',
    '/dashboard',
    '/marketplace',
    '/orders',
    '/traceability'
  ]
};

export const hasRoutePermission = (role, path) => {
  if (!role) return false;
  const userRole = role.toLowerCase();
  if (userRole === 'admin') return true;
  const allowedPaths = ROLE_PERMISSIONS[userRole] || [];
  return allowedPaths.includes(path);
};
