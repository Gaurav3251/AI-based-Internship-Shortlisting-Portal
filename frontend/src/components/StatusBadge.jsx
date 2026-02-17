import React from 'react';

const StatusBadge = ({ status }) => {
  const map = {
    under_review: 'warning',
    shortlisted: 'success',
    not_shortlisted: 'danger'
  };
  const labelMap = {
    under_review: 'Under Review',
    shortlisted: 'Shortlisted',
    not_shortlisted: 'Not Shortlisted'
  };

  return <span className={`badge bg-${map[status] || 'secondary'}`}>{labelMap[status] || status}</span>;
};

export default StatusBadge;
