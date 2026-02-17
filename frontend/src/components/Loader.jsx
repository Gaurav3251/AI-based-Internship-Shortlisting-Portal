import React from 'react';

const Loader = ({ text = 'Loading...' }) => (
  <div className="text-center py-4">
    <div className="spinner-border text-primary" role="status"></div>
    <div className="mt-2">{text}</div>
  </div>
);

export default Loader;
