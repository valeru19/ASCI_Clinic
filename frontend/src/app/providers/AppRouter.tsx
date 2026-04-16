import { Navigate, Route, Routes } from "react-router-dom";

import { DashboardPage } from "@/pages/dashboard/ui/DashboardPage";
import { LoginPage } from "@/pages/login/ui/LoginPage";
import { PatientsPage } from "@/pages/patients/ui/PatientsPage";
import { AppointmentsPage } from "@/pages/appointments/ui/AppointmentsPage";
import { DoctorsPage } from "@/pages/doctors/ui/DoctorsPage";
import { VisitsPage } from "@/pages/visits/ui/VisitsPage";
import { ReportsPage } from "@/pages/reports/ui/ReportsPage";

import { ProtectedRoute } from "./ProtectedRoute";

export function AppRouter() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<ProtectedRoute />}>
        <Route path="/dashboard" element={<DashboardPage />} />
      </Route>
      <Route element={<ProtectedRoute roles={["admin", "registrar"]} />}>
        <Route path="/patients" element={<PatientsPage />} />
        <Route path="/appointments" element={<AppointmentsPage />} />
        <Route path="/doctors" element={<DoctorsPage />} />
      </Route>
      <Route element={<ProtectedRoute roles={["admin", "doctor"]} />}>
        <Route path="/visits" element={<VisitsPage />} />
      </Route>
      <Route element={<ProtectedRoute roles={["admin", "registrar", "doctor"]} />}>
        <Route path="/reports" element={<ReportsPage />} />
      </Route>
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
