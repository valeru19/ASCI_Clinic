import type { CurrentUser, UserRole } from "./types";

export function hasRole(user: CurrentUser | null, roles: UserRole[]): boolean {
  if (!user) {
    return false;
  }
  return roles.includes(user.role);
}

export function canManagePatients(user: CurrentUser | null): boolean {
  return hasRole(user, ["admin", "registrar"]);
}

export function canManageAppointments(user: CurrentUser | null): boolean {
  return hasRole(user, ["admin", "registrar"]);
}

export function canManageDoctors(user: CurrentUser | null): boolean {
  return hasRole(user, ["admin", "registrar"]);
}

export function canManageDiagnoses(user: CurrentUser | null): boolean {
  return hasRole(user, ["admin", "doctor"]);
}

export function canViewDiagnosesReport(user: CurrentUser | null): boolean {
  return hasRole(user, ["admin", "registrar", "doctor"]);
}
