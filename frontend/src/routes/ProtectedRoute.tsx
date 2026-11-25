import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import type { UserRole } from '@/types';

export const ProtectedRoute: React.FC<{
  children: React.ReactNode;
  allowedRoles?: UserRole[];
  redirectTo?: string;
}> = ({ children, allowedRoles, redirectTo = '/login' }) => {
  const { user, isLoading } = useAuthStore();

  if (isLoading) {
    return <div className="py-12 text-center text-sm text-muted-fg">Verifying session...</div>;
  }

  if (!user) {
    return <Navigate to={redirectTo} replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

