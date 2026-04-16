import type { ReactNode } from "react";
import { NavLink } from "react-router-dom";
import { useLocation } from "react-router-dom";

import { useAuth } from "@/app/providers/AuthProvider";
import {
  canManageAppointments,
  canManageDiagnoses,
  canManageDoctors,
  canManagePatients,
  canViewDiagnosesReport,
} from "@/entities/user/model/permissions";
import { Badge, Button } from "@/shared/ui";

type AppLayoutProps = {
  title: string;
  subtitle?: string;
  breadcrumbs?: string[];
  headerActions?: ReactNode;
  children: ReactNode;
};

export function AppLayout({
  title,
  subtitle,
  breadcrumbs = [],
  headerActions,
  children,
}: AppLayoutProps) {
  const location = useLocation();
  const { user, logout } = useAuth();
  const canPatients = canManagePatients(user);
  const canAppointments = canManageAppointments(user);
  const canDiagnoses = canManageDiagnoses(user);
  const canDoctors = canManageDoctors(user);
  const canReports = canViewDiagnosesReport(user);

  const getNavClass = ({ isActive }: { isActive: boolean }) =>
    ["app-nav__item", isActive ? "active" : ""].join(" ").trim();

  return (
    <div className="app-shell">
      <aside className="app-sidebar">
        <h1 className="app-logo">AIS Clinic</h1>
        <p className="app-logo-subtitle">Медицинская ИС</p>
        <nav className="app-nav">
          <NavLink to="/dashboard" className={getNavClass}>
            Главная
          </NavLink>
          {canPatients && (
            <NavLink to="/patients" className={getNavClass}>
              Пациенты
            </NavLink>
          )}
          {canAppointments && (
            <NavLink to="/appointments" className={getNavClass}>
              Записи
            </NavLink>
          )}
          {canDoctors && (
            <NavLink to="/doctors" className={getNavClass}>
              Врачи
            </NavLink>
          )}
          {canDiagnoses && (
            <NavLink to="/visits" className={getNavClass}>
              Диагнозы
            </NavLink>
          )}
          {canReports && (
            <NavLink to="/reports" className={getNavClass}>
              Отчеты
            </NavLink>
          )}
        </nav>
      </aside>

      <main className="app-main">
        <header className="app-header">
          <div>
            {breadcrumbs.length > 0 && (
              <p className="app-breadcrumbs">{breadcrumbs.join(" / ")}</p>
            )}
            <h2>{title}</h2>
            {subtitle && <p className="ui-muted">{subtitle}</p>}
          </div>
          <div className="ui-row">
            {headerActions}
            {user && <Badge>{`${user.username} (${user.role})`}</Badge>}
            <Button variant="secondary" onClick={logout}>
              Выйти
            </Button>
          </div>
        </header>
        <div key={location.pathname} className="app-content app-content--animated">
          {children}
        </div>
      </main>
    </div>
  );
}
