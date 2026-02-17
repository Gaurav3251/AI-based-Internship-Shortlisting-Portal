import React from 'react';
import { Navigate } from 'react-router-dom';
import { getUser } from '../utils/constants';

const RoleGuard = ({ role, children }) => {
  const user = getUser();
  if (!user) return <Navigate to="/login" replace />;
  if (user.role !== role) return <Navigate to="/403" replace />;
  return children;
};

export default RoleGuard;
