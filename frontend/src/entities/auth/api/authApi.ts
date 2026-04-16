import { httpRequest } from "@/shared/api/httpClient";

import type { TokenResponse } from "../model/types";
import type { CurrentUser } from "@/entities/user/model/types";

export const authApi = {
  login: (username: string, password: string) =>
    httpRequest<TokenResponse>("/auth/login", {
      method: "POST",
      form: { username, password },
    }),
  me: (token: string) => httpRequest<CurrentUser>("/auth/me", { token }),
};
