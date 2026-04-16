import { type FormEvent, useState } from "react";

import { Button, Input } from "@/shared/ui";

type LoginFormProps = {
  loading: boolean;
  onSubmit: (username: string, password: string) => Promise<void>;
  defaultUsername?: string;
  defaultPassword?: string;
};

export function LoginForm({
  loading,
  onSubmit,
  defaultUsername = "admin",
  defaultPassword = "admin12345",
}: LoginFormProps) {
  const [username, setUsername] = useState(defaultUsername);
  const [password, setPassword] = useState(defaultPassword);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await onSubmit(username, password);
  }

  return (
    <form className="ui-form-grid" onSubmit={handleSubmit}>
      <Input
        label="Логин"
        name="username"
        value={username}
        onChange={(event) => setUsername(event.target.value)}
      />
      <Input
        label="Пароль"
        name="password"
        type="password"
        value={password}
        onChange={(event) => setPassword(event.target.value)}
      />
      <Button type="submit" disabled={loading}>
        Войти
      </Button>
    </form>
  );
}
