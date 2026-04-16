import { useState } from "react";
import { Navigate } from "react-router-dom";

import { useAuth } from "@/app/providers/AuthProvider";
import { LoginForm } from "@/features/auth/login-form/ui/LoginForm";
import { Alert, Card } from "@/shared/ui";

export function LoginPage() {
  const { login, isAuthenticated, loading } = useAuth();
  const [error, setError] = useState("");

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  async function handleLogin(username: string, password: string) {
    setError("");
    try {
      await login(username, password);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка авторизации");
    }
  }

  return (
    <div className="login-page">
      <Card
        title="Вход в AIS Clinic"
        subtitle="Используйте backend-учетную запись для доступа к role-aware интерфейсу"
      >
        {error && <Alert variant="error">{error}</Alert>}
        <LoginForm loading={loading} onSubmit={handleLogin} />
      </Card>
    </div>
  );
}
