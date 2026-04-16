import { env } from "@/shared/config/env";

type HttpMethod = "GET" | "POST" | "PATCH" | "DELETE";

type RequestOptions = {
  method?: HttpMethod;
  token?: string;
  body?: unknown;
  form?: Record<string, string>;
};

export async function httpRequest<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const headers: Record<string, string> = {};
  let body: string | undefined;

  if (options.token) {
    headers.Authorization = `Bearer ${options.token}`;
  }

  if (options.form) {
    headers["Content-Type"] = "application/x-www-form-urlencoded";
    body = new URLSearchParams(options.form).toString();
  } else if (options.body !== undefined) {
    headers["Content-Type"] = "application/json";
    body = JSON.stringify(options.body);
  }

  const response = await fetch(`${env.apiBaseUrl}${path}`, {
    method: options.method ?? "GET",
    headers,
    body,
  });

  const responseText = await response.text();
  const payload = responseText ? (JSON.parse(responseText) as unknown) : {};

  if (!response.ok) {
    const detail =
      payload && typeof payload === "object" && "detail" in payload
        ? (payload as { detail: unknown }).detail
        : payload;
    throw new Error(
      `${response.status} ${response.statusText}${detail ? `: ${JSON.stringify(detail)}` : ""}`,
    );
  }

  return payload as T;
}
