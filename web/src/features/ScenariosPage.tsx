"use client";

import Link from "next/link";
import { useState } from "react";

import { isApiError } from "@/api/errors";
import { listScenarios } from "@/api/services/scenarioService";
import { Empty, ErrorState, Loading, Unavailable } from "@/components/states";
import { buttonClasses } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { PageHeader } from "@/components/ui/PageHeader";
import { Pill } from "@/components/ui/Pill";
import type { ScenarioKind } from "@/domain";
import { formatWhen } from "@/lib/formatWhen";
import { useAsync } from "@/lib/useAsync";

const KINDS: { value: ScenarioKind | ""; label: string }[] = [
  { value: "", label: "All" },
  { value: "reform", label: "Policy change" },
  { value: "household", label: "Household" },
];

export function ScenariosPage() {
  const [kind, setKind] = useState<ScenarioKind | "">("");
  const state = useAsync((signal) => listScenarios(kind || undefined, signal), `scenarios:${kind}`);

  return (
    <div>
      <PageHeader
        title="Scenarios"
        description="Saved analyses. Each keeps the settings it was run with."
        actions={
          <Link href="/scenarios/new" className={buttonClasses({ variant: "primary" }, "no-underline")}>
            New scenario
          </Link>
        }
      />

      <div className="mb-4 flex items-center gap-2 text-sm">
        <label htmlFor="kind-filter" className="text-muted">
          Kind
        </label>
        <select
          id="kind-filter"
          value={kind}
          onChange={(e) => setKind(e.target.value as ScenarioKind | "")}
          className="h-9 rounded-md border border-border-strong bg-surface px-2"
        >
          {KINDS.map((k) => (
            <option key={k.value} value={k.value}>
              {k.label}
            </option>
          ))}
        </select>
      </div>

      {state.status === "loading" ? <Loading label="Loading scenarios" /> : null}
      {state.status === "error" ? (
        isApiError(state.error) && state.error.code === "scenario_storage_unavailable" ? (
          <Unavailable title="Scenarios are not available here" reason={state.error.message} />
        ) : (
          <ErrorState error={state.error} onRetry={state.reload} />
        )
      ) : null}
      {state.status === "ready" && state.data.items.length === 0 ? (
        <Empty title="No scenarios yet">Start one from Home or with New scenario.</Empty>
      ) : null}
      {state.status === "ready" && state.data.items.length > 0 ? (
        <Card className="p-0">
          <ul className="divide-y divide-border">
            {state.data.items.map((s) => (
              <li key={s.scenario_id}>
                <Link href={s.latest_run_id ? `/scenarios/${s.scenario_id}/runs/${s.latest_run_id}` : `/scenarios/${s.scenario_id}`} className="block px-4 py-3 no-underline hover:bg-surface-muted">
                  <span className="flex flex-wrap items-center gap-2">
                    <span className="font-medium">{s.title}</span>
                    <Pill tone="neutral">{s.kind === "reform" ? "Policy change" : "Household"}</Pill>
                  </span>
                  {s.description ? <span className="mt-0.5 block text-sm text-muted">{s.description}</span> : null}
                  <span className="mt-1 block text-xs text-muted">
                    <span className="num">{s.runs}</span> {s.runs === 1 ? "run" : "runs"} · created {formatWhen(s.created_at)} ·{" "}
                    <span className="font-mono">{s.scenario_id.slice(0, 12)}</span>
                  </span>
                </Link>
              </li>
            ))}
          </ul>
          <p className="border-t border-border px-4 py-2 text-xs text-muted">
            <span className="num">{state.data.items.length}</span> of <span className="num">{state.data.total}</span> shown
          </p>
        </Card>
      ) : null}
    </div>
  );
}
