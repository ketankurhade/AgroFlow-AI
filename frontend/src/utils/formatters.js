/**
 * AgroFlow AI — Utility Formatters for Currency, Quantity, and Dates
 */

// Currency Formatter — Always formats to Indian Rupees (₹)
export const formatCurrency = (amount, decimals = 0) => {
  if (amount === undefined || amount === null || isNaN(amount)) return '₹0';
  const val = Number(amount);
  return `₹${val.toLocaleString('en-IN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  })}`;
};

// Quantity Formatter — kg for smaller amounts, tons for >= 1000 kg
export const formatQuantity = (kgAmount, preferTons = false) => {
  if (kgAmount === undefined || kgAmount === null || isNaN(kgAmount)) return '0 kg';
  const val = Number(kgAmount);
  if (val >= 1000 || preferTons) {
    const tons = val / 1000;
    return `${tons.toLocaleString('en-IN', { maximumFractionDigits: 1 })} tons`;
  }
  return `${val.toLocaleString('en-IN')} kg`;
};

// Date Formatter — e.g. "28 Sep 2026"
export const formatDate = (dateStr) => {
  if (!dateStr || dateStr === 'N/A') return 'N/A';
  try {
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) return dateStr;
    return date.toLocaleDateString('en-GB', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    });
  } catch (err) {
    return dateStr;
  }
};

// Date-Time Formatter — e.g. "28 Sep 2026, 10:30 AM"
export const formatDateTime = (dateStr) => {
  if (!dateStr || dateStr === 'N/A') return 'N/A';
  try {
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) return dateStr;
    return date.toLocaleString('en-GB', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true,
    });
  } catch (err) {
    return dateStr;
  }
};

// Status Badge Variant Helper
export const getStatusVariant = (status) => {
  if (!status) return 'slate';
  const s = status.toLowerCase();
  if (s.includes('deliver') || s.includes('confirm') || s.includes('harvested')) return 'emerald';
  if (s.includes('transit') || s.includes('process')) return 'blue';
  if (s.includes('cold') || s.includes('storage') || s.includes('pending')) return 'purple';
  if (s.includes('cancel') || s.includes('high') || s.includes('spoil')) return 'rose';
  return 'slate';
};
