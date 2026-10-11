"use client";

import Link from "next/link";

import { listModels } from "@/api/services/modelService";
import { Empty, ErrorState, Loading } from "@/components/states";
import { Card } from "@/components/ui/Card";
import { PageHeader } from "@/components/ui/PageHeader";
import { ValidationPill } from "@/components/blocks/ValidationPill";
import type { ModelSummary } from "@/domain";
import { humanise } from "@/lib/labels";
import { useAsync } from "@/lib/useAsync";

function groupByKind(models: readonly ModelSummary[]): [string, ModelSummary[]][] {
  const groups = new Map<string, ModelSummary[]>();
  for (const model of models) groups.set(model.kind, [...(groups.get(model.kind) ?? []), model]);
  return [...groups.entries()];
}

export function ModelsPage() {
  const state = useAsync(listModels, "models");

  return (
    <div>
      <PageHeader
        title="Models"
        description="The calculation models Poltika runs, with how far each has been validated."
      />
      {state.status === "loading" ? <Loading label="Loading models" /> : null}
      {state.status === "error" ? <ErrorState error={state.error} onRetry={state.reload} /> : null}
      {state.status === "ready" && state.data.models.length === 0 ? <Empty title="No models are registered" /> : null}
      {state.status === "ready"
        ? groupByKind(state.data.models).map(([kind, models]) => (
            <section key={kind} aria-labelledby={`kind-${kind}`} className="mb-8">
              <h2 id={`kind-${kind}`} className="mb-3 text-sm font-semibold tracking-wide text-muted uppercase">
                {humanise(kind)}s
              </h2>
              <ul className="grid gap-3 md:grid-cols-2">
                {models.map((m) => (
                  <li key={m.id}>
                    <Link href={`/models/${m.id}`} className="block h-full no-underline">
                      <Card className="h-full hover:border-border-strong">
                        <div className="flex items-start justify-between gap-3">
                          <h3 className="font-medium">{m.name}</h3>
                          <ValidationPill label={m.label} levels={state.data.validation_levels} />
                        </div>
                        <p className="num mt-0.5 font-mono text-xs text-muted">version {m.version}</p>
                        <p className="mt-2 text-sm">{m.purpose}</p>
                      </Card>
                    </Link>
                  </li>
                ))}
              </ul>
            </section>
          ))
        : null}
    </div>
  );
}
