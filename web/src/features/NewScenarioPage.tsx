"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense } from "react";

import { getHouseholdDefinition, getScenarioDefinition } from "@/api/services/scenarioService";
import { ErrorState, Loading } from "@/components/states";
import { Card } from "@/components/ui/Card";
import { PageHeader } from "@/components/ui/PageHeader";
import { useAsync } from "@/lib/useAsync";

import { HouseholdBuilder } from "./newScenario/HouseholdBuilder";
import { ReformBuilder } from "./newScenario/ReformBuilder";

type Template = "policy_change" | "compare" | "household";

const TEMPLATES: { id: Template; title: string; text: string }[] = [
  { id: "policy_change", title: "Analyse a policy change", text: "Change one policy setting and see its effect on the synthetic population." },
  { id: "compare", title: "Compare two settings", text: "Run two options side by side against the current law." },
  { id: "household", title: "Explore a household", text: "Calculate one example household's entitlements." },
];

function templateFrom(search: string): Template | null {
  const value = new URLSearchParams(search).get("template");
  return TEMPLATES.find((t) => t.id === value)?.id ?? null;
}

export function NewScenarioPage() {
  return <Suspense fallback={<Loading label="Loading the scenario form" />}><NewScenarioContent /></Suspense>;
}

function CloneBuilder({ scenarioId, navigate }: { scenarioId: string; navigate: (href: string) => void }) {
  const definition = useAsync((signal) => getScenarioDefinition(scenarioId, signal), `definition:${scenarioId}`);
  if (definition.status === "loading") return <Loading label="Loading the saved settings" />;
  if (definition.status === "error") return <ErrorState error={definition.error} onRetry={definition.reload} />;
  return <ReformBuilder compare={definition.data.options.length === 2} initial={definition.data} navigate={navigate} />;
}

function HouseholdCloneBuilder({ scenarioId, runId, navigate }: { scenarioId: string; runId: string; navigate: (href: string) => void }) {
  const definition = useAsync((signal) => getHouseholdDefinition(scenarioId, runId, signal), `household-definition:${scenarioId}:${runId}`);
  if (definition.status === "loading") return <Loading label="Loading the saved household facts" />;
  if (definition.status === "error") return <ErrorState error={definition.error} onRetry={definition.reload} />;
  return <HouseholdBuilder initial={definition.data} navigate={navigate} />;
}

function NewScenarioContent() {
  const router = useRouter();
  const query = useSearchParams();
  const template = templateFrom(query.toString());
  const fromScenario = query.get("fromScenario");
  const fromHousehold = query.get("fromHousehold");
  const fromRun = query.get("fromRun");
  const navigate = (href: string) => router.push(href);
  const current = TEMPLATES.find((t) => t.id === template);

  return (
    <div>
      <PageHeader title={fromScenario || fromHousehold ? "Edit as new scenario" : current?.title ?? "New scenario"} description={current?.text} />
      {fromHousehold && fromRun ? <HouseholdCloneBuilder key={`${fromHousehold}:${fromRun}`} scenarioId={fromHousehold} runId={fromRun} navigate={navigate} /> : fromScenario ? <CloneBuilder key={fromScenario} scenarioId={fromScenario} navigate={navigate} /> : current === undefined ? (
        <ul className="grid gap-3 sm:grid-cols-3">
          {TEMPLATES.map((t) => (
            <li key={t.id}>
              <Link href={`/scenarios/new?template=${t.id}`} className="block no-underline">
                <Card className="h-full hover:bg-surface-muted">
                  <p className="font-medium">{t.title}</p>
                  <p className="mt-1 text-sm text-muted">{t.text}</p>
                </Card>
              </Link>
            </li>
          ))}
        </ul>
      ) : template === "household" ? (
        <HouseholdBuilder navigate={navigate} />
      ) : (
        <ReformBuilder key={template} compare={template === "compare"} navigate={navigate} />
      )}
    </div>
  );
}
