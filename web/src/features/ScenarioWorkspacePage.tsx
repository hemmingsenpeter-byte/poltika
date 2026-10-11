"use client";

import { useRouter } from "next/navigation";

import { isApiError } from "@/api/errors";
import { getWorkspace } from "@/api/services/scenarioService";
import { ErrorState, Loading, Unavailable } from "@/components/states";
import { useAsync } from "@/lib/useAsync";
import { useMounted } from "@/lib/useMounted";
import { useRouteIds } from "@/lib/useRouteIds";

import { WorkspaceView } from "./workspace/WorkspaceView";

/** /scenarios/:id and /scenarios/:id/runs/:runId. The ids come from the URL
 *  after mount (the export holds a placeholder). */
export function ScenarioWorkspacePage() {
  const mounted = useMounted();
  const router = useRouter();
  const { scenarioId, runId } = useRouteIds();
  const key = `workspace:${scenarioId ?? ""}:${runId ?? ""}`;
  const state = useAsync(
    (signal) => (scenarioId ? getWorkspace(scenarioId, runId, signal) : Promise.reject(new Error("no scenario id"))),
    key,
  );

  if (!mounted || state.status === "loading") return <Loading label="Loading the scenario" />;
  if (state.status === "error") {
    if (isApiError(state.error) && state.error.kind === "unavailable") {
      return <Unavailable title="Scenarios are not available here" reason={state.error.message} />;
    }
    return <ErrorState error={state.error} onRetry={state.reload} />;
  }
  return <WorkspaceView key={key} workspace={state.data} navigate={(href) => router.push(href)} />;
}
