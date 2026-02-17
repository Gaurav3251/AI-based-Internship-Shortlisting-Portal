import React from 'react';
import RequireAuth from '../auth/RequireAuth.jsx';
import RoleGuard from '../auth/RoleGuard.jsx';

const ProtectedRoute = ({ role, children }) => (
  <RequireAuth>
    <RoleGuard role={role}>{children}</RoleGuard>
  </RequireAuth>
);

export default ProtectedRoute;
