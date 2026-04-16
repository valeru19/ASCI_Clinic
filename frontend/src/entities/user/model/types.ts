export type UserRole = "admin" | "doctor" | "registrar" | "patient";

export type CurrentUser = {
  id: string;
  username: string;
  email: string;
  role: UserRole;
  is_active: boolean;
};
