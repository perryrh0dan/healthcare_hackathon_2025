import React from 'react';
import { useAuth } from '../contexts';
import { Navigate } from '@tanstack/react-router';

interface ProtectedRouteProps {
  route?: string;
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ route, children }) => {
  const { isAuthenticated, isLoading, user } = useAuth();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  if (route !== 'setup' && user?.status === 'setup') {
    return <Navigate to='/setup' />;
  }

  // if (route !== 'daily' && user?.needs_daily_questions) {
  //   return <Navigate to='/daily' />;
  // }

  return <>{children}</>;
};

export default ProtectedRoute;
