"use client";

import { Unavailable } from "@/components/states";
import { PageHeader } from "@/components/ui/PageHeader";
import { useMounted } from "@/lib/useMounted";
import { useRouteIds } from "@/lib/useRouteIds";

/** The workspace itself is B0.1.4. This page shows which scenario and run the
 *  URL names, so deep links can be checked. */
export function ScenarioWorkspacePage() {
  const mounted = useMounted();
  const ids = useRouteIds();
  const scenarioId = mounted ? ids.scenarioId : undefined;
  const runId = mounted ? ids.runId : undefined;
  return (
    <div>
      <PageHeader title={runId ? "Run" : "Scenario"} />
      <dl className="mb-4 space-y-1 text-sm">
        <div className="flex gap-3">
          <dt className="w-24 text-muted">Scenario</dt>
          <dd className="font-mono break-all">{scenarioId ?? "—"}</dd>
        </div>
        {runId ? (
          <div className="flex gap-3">
            <dt className="w-24 text-muted">Run</dt>
            <dd className="font-mono break-all">{runId}</dd>
          </div>
        ) : null}
      </dl>
      <Unavailable reason="Workspace coming in B0.1.4." />
    </div>
  );
}
