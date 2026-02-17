import React from 'react';

const Pagination = ({ page, totalPages, onPageChange }) => {
  if (totalPages <= 1) return null;
  return (
    <nav>
      <ul className="pagination">
        <li className={`page-item ${page === 1 ? 'disabled' : ''}`}>
          <button className="page-link" onClick={() => onPageChange(page - 1)}>Prev</button>
        </li>
        {Array.from({ length: totalPages }).map((_, i) => (
          <li key={i} className={`page-item ${page === i + 1 ? 'active' : ''}`}>
            <button className="page-link" onClick={() => onPageChange(i + 1)}>{i + 1}</button>
          </li>
        ))}
        <li className={`page-item ${page === totalPages ? 'disabled' : ''}`}>
          <button className="page-link" onClick={() => onPageChange(page + 1)}>Next</button>
        </li>
      </ul>
    </nav>
  );
};

export default Pagination;
