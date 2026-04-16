import { createContext, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";

import { authApi } from "@/entities/auth/api/authApi";
import type { CurrentUser } from "@/entities/user/model/types";

const TOKEN_KEY = "clinic_access_token";

type AuthContextValue = {
  token: string;
  user: CurrentUser | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string>(() => localStorage.getItem(TOKEN_KEY) ?? "");
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!token) {
      setUser(null);
      return;
    }
    void refreshUser();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  async function refreshUser() {
    if (!token) {
      setUser(null);
      return;
    }
    setLoading(true);
    try {
      const currentUser = await authApi.me(token);
      setUser(currentUser);
    } finally {
      setLoading(false);
    }
  }

  async function login(username: string, password: string) {
    setLoading(true);
    try {
      const response = await authApi.login(username, password);
      localStorage.setItem(TOKEN_KEY, response.access_token);
      setToken(response.access_token);
      const currentUser = await authApi.me(response.access_token);
      setUser(currentUser);
    } finally {
      setLoading(false);
    }
  }

  function logout() {
    localStorage.removeItem(TOKEN_KEY);
    setToken("");
    setUser(null);
  }

  const value = useMemo<AuthContextValue>(
    () => ({
      token,
      user,
      isAuthenticated: token.trim().length > 0,
      loading,
      login,
      logout,
      refreshUser,
    }),
    [token, user, loading],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
