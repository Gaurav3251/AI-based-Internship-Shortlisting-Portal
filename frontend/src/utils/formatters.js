export const formatDate = (iso) => {
  if (!iso) return '-';
  return new Date(iso).toLocaleDateString();
};

export const daysRemaining = (dateStr) => {
  if (!dateStr) return '-';
  const end = new Date(dateStr);
  const now = new Date();
  const diff = Math.ceil((end - now) / (1000 * 60 * 60 * 24));
  return diff < 0 ? 'Closed' : `${diff} days remaining`;
};

export const formatPercentage = (value) => {
  if (value === null || value === undefined) return '-';
  return `${Number(value).toFixed(2)}%`;
};
