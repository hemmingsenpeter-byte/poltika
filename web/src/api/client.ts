import { z } from "zod";

import { ApiError, type ApiErrorKind } from "./errors";

/** The one place that calls `fetch`. Same origin, JSON only (ADR-0023). */

function kindForStatus(status: number): ApiErrorKind {
  if (status === 404) return "not_found";
  if (status === 429) return "busy";
  if (status === 503) return "unavailable";
  if (status >= 500) return "server";
  return "invalid";
}

const DEFAULT_MESSAGES: Record<ApiErrorKind, string> = {
  unavailable: "This part of Poltika is not available here.",
  not_found: "That was not found.",
  busy: "Another analysis is running. Try again shortly.",
  invalid: "The request was not accepted.",
  network: "Poltika could not be reached. Check the connection and try again.",
  server: "Poltika hit an unexpected problem.",
  invalid_response: "Poltika returned a response this page does not understand.",
};

/** The backend answers `{"detail": {"code", "message"}}`; legacy routes answer
 *  `{"detail": "text"}`; request validation answers `{"detail": [...]}`. */
export function parseErrorBody(status: number, body: unknown): ApiError {
  const kind = kindForStatus(status);
  const detail = typeof body === "object" && body !== null ? (body as { detail?: unknown }).detail : undefined;
  if (typeof detail === "string" && detail.length > 0) {
    return new ApiError(kind, detail, { status });
  }
  if (typeof detail === "object" && detail !== null && !Array.isArray(detail)) {
    const { code, message } = detail as { code?: unknown; message?: unknown };
    return new ApiError(kind, typeof message === "string" && message ? message : DEFAULT_MESSAGES[kind], {
      status,
      ...(typeof code === "string" ? { code } : {}),
    });
  }
  return new ApiError(kind, DEFAULT_MESSAGES[kind], { status });
}

async function send<T>(
  method: "GET" | "POST",
  path: string,
  schema: z.ZodType<T>,
  body?: unknown,
  signal?: AbortSignal,
): Promise<T> {
  let response: Response;
  try {
    response = await fetch(path, {
      method,
      credentials: "same-origin",
      headers: body === undefined ? { Accept: "application/json" } : { Accept: "application/json", "Content-Type": "application/json" },
      ...(body === undefined ? {} : { body: JSON.stringify(body) }),
      ...(signal ? { signal } : {}),
    });
  } catch (cause) {
    if (cause instanceof DOMException && cause.name === "AbortError") throw cause;
    throw new ApiError("network", DEFAULT_MESSAGES.network);
  }

  let json: unknown;
  try {
    json = await response.json();
  } catch {
    json = undefined;
  }

  if (!response.ok) throw parseErrorBody(response.status, json);

  const parsed = schema.safeParse(json);
  if (!parsed.success) {
    throw new ApiError("invalid_response", DEFAULT_MESSAGES.invalid_response, { status: response.status });
  }
  return parsed.data;
}

export function getJson<T>(path: string, schema: z.ZodType<T>, signal?: AbortSignal): Promise<T> {
  return send("GET", path, schema, undefined, signal);
}

export function postJson<T>(path: string, body: unknown, schema: z.ZodType<T>, signal?: AbortSignal): Promise<T> {
  return send("POST", path, schema, body, signal);
}
