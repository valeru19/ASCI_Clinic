import { Navigate, Outlet, useLocation } from "react-router-dom";

import { hasRole } from "@/entities/user/model/permissions";
import type { UserRole } from "@/entities/user/model/types";

import { useAuth } from "./AuthProvider";

type ProtectedRouteProps = {
  roles?: UserRole[];
};

export function ProtectedRoute({ roles }: ProtectedRouteProps) {
  const { isAuthenticated, user } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  if (roles && !hasRole(user, roles)) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
}
