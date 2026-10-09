import { AlertCircle, Clock, Inbox, Loader2, Lock } from "lucide-react";
import type { ReactNode } from "react";

import { type ApiError, isApiError } from "@/api/errors";
import { Card } from "@/components/ui/Card";

/** Shared states (ADR-0023). Each says what is wrong in plain words and never
 *  stands in for a value. */

export function Loading({ label = "Loading" }: { label?: string }) {
  return (
    <div role="status" aria-live="polite" className="flex items-center gap-2 py-8 text-sm text-muted">
      <Loader2 aria-hidden="true" className="size-4 animate-spin motion-reduce:animate-none" />
      {label}…
    </div>
  );
}

function Panel({ icon, title, children, role }: { icon: ReactNode; title: string; children?: ReactNode; role?: "alert" }) {
  return (
    <Card role={role} className="flex items-start gap-3">
      <span className="mt-0.5 text-muted">{icon}</span>
      <div className="min-w-0">
        <p className="font-medium">{title}</p>
        {children ? <div className="mt-1 text-sm text-muted">{children}</div> : null}
      </div>
    </Card>
  );
}

export function Empty({ title, children }: { title: string; children?: ReactNode }) {
  return (
    <Panel icon={<Inbox aria-hidden="true" className="size-5" />} title={title}>
      {children}
    </Panel>
  );
}

export function Unavailable({ reason, title = "Not yet available" }: { reason: ReactNode; title?: string }) {
  return (
    <Panel icon={<Clock aria-hidden="true" className="size-5" />} title={title}>
      {reason}
    </Panel>
  );
}

const TITLES: Record<ApiError["kind"], string> = {
  busy: "Another analysis is running…",
  unavailable: "Not available here",
  not_found: "Not found",
  invalid: "The request was not accepted",
  network: "Poltika could not be reached",
  server: "Something went wrong",
  invalid_response: "Unexpected response",
};

/** Keyed to the API error kind; the server's own message is shown as given. */
export function ErrorState({ error, onRetry }: { error: unknown; onRetry?: () => void }) {
  const apiError = isApiError(error) ? error : null;
  const kind = apiError?.kind ?? "server";
  const message = apiError?.message ?? "Poltika hit an unexpected problem.";
  const icon =
    apiError?.status === 401 ? (
      <Lock aria-hidden="true" className="size-5" />
    ) : (
      <AlertCircle aria-hidden="true" className="size-5" />
    );
  return (
    <Panel icon={icon} title={TITLES[kind]} role="alert">
      <p>{kind === "busy" ? "Try again shortly." : message}</p>
      {kind === "busy" ? <p>{message}</p> : null}
      {apiError?.code ? <p className="mt-1 font-mono text-xs">{apiError.code}</p> : null}
      {onRetry && kind !== "not_found" ? (
        <button type="button" onClick={onRetry} className="mt-2 underline underline-offset-2">
          Try again
        </button>
      ) : null}
    </Panel>
  );
}
