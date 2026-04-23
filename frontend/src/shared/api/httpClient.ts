import { env } from "@/shared/config/env";

type HttpMethod = "GET" | "POST" | "PATCH" | "DELETE";

type RequestOptions = {
  method?: HttpMethod;
  token?: string;
  body?: unknown;
  form?: Record<string, string>;
};

type RequestErrorContext = {
  stage: "network" | "http";
  method: HttpMethod;
  requestUrl: string;
  path: string;
  status?: number;
  statusText?: string;
  requestId?: string;
  detail?: unknown;
};

function stringifySafe(value: unknown): string {
  if (typeof value === "string") {
    return value;
  }
  if (value === undefined || value === null) {
    return "";
  }
  try {
    return JSON.stringify(value);
  } catch {
    return String(value);
  }
}

function logRequestError(context: RequestErrorContext, error: unknown): void {
  // Единая точка логирования: по этому объекту видно где и почему запрос упал.
  console.error("[httpRequest] request failed", {
    ...context,
    error:
      error instanceof Error
        ? {
            name: error.name,
            message: error.message,
            stack: error.stack,
          }
        : String(error),
  });
}

export async function httpRequest<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const headers: Record<string, string> = {};
  const method = options.method ?? "GET";
  const requestUrl = `${env.apiBaseUrl}${path}`;
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

  let response: Response;
  try {
    response = await fetch(requestUrl, {
      method,
      headers,
      body,
    });
  } catch (error) {
    logRequestError(
      {
        stage: "network",
        method,
        requestUrl,
        path,
      },
      error,
    );
    throw new Error(
      `Сетевой сбой при обращении к API. method=${method}, url=${requestUrl}. ` +
        "Проверьте, что backend запущен, доступен по сети и не блокируется CORS/фаерволом.",
    );
  }

  const responseText = await response.text();
  const contentType = response.headers.get("content-type") ?? "";
  let payload: unknown = {};
  if (responseText) {
    if (contentType.includes("application/json")) {
      try {
        payload = JSON.parse(responseText) as unknown;
      } catch {
        payload = responseText;
      }
    } else {
      payload = responseText;
    }
  }

  if (!response.ok) {
    const requestId = response.headers.get("X-Request-ID") ?? undefined;
    const detail =
      payload && typeof payload === "object" && "detail" in payload
        ? (payload as { detail: unknown }).detail
        : payload;
    const detailText = stringifySafe(detail);
    logRequestError(
      {
        stage: "http",
        method,
        requestUrl,
        path,
        status: response.status,
        statusText: response.statusText,
        requestId,
        detail,
      },
      new Error(detailText || `${response.status} ${response.statusText}`),
    );
    throw new Error(
      `${response.status} ${response.statusText}; method=${method}; path=${path}` +
        `${requestId ? `; request_id=${requestId}` : ""}` +
        `${detailText ? `; detail=${detailText}` : ""}`,
    );
  }

  return payload as T;
}
