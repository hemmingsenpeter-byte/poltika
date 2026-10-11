export type ApiErrorKind =
  | "unavailable"
  | "not_found"
  | "busy"
  | "invalid"
  | "network"
  | "server"
  | "invalid_response";

/** What every service call raises. Components see this and nothing else. */
export class ApiError extends Error {
  readonly kind: ApiErrorKind;
  readonly code: string | undefined;
  readonly status: number | undefined;

  constructor(kind: ApiErrorKind, message: string, options: { code?: string; status?: number } = {}) {
    super(message);
    this.name = "ApiError";
    this.kind = kind;
    this.code = options.code;
    this.status = options.status;
  }
}

export function isApiError(value: unknown): value is ApiError {
  return value instanceof ApiError;
}
