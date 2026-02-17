import React from 'react';
import { Navigate } from 'react-router-dom';
import { isAuthed } from '../utils/constants';

const RequireAuth = ({ children }) => {
  if (!isAuthed()) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

export default RequireAuth;
