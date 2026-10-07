"use client";

import { useState } from "react";

import { listHouseholdExamples } from "@/api/services/registryService";
import { createHouseholdScenario } from "@/api/services/scenarioService";
import { Empty, ErrorState, Loading } from "@/components/states";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { useAsync } from "@/lib/useAsync";

export function HouseholdBuilder({ navigate }: { navigate: (href: string) => void }) {
  const examples = useAsync(listHouseholdExamples, "household-examples");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<unknown>(null);

  if (examples.status === "loading") return <Loading label="Loading examples" />;
  if (examples.status === "error") return <ErrorState error={examples.error} onRetry={examples.reload} />;
  const list = examples.data;
  const selected = list.find((e) => e.id === selectedId) ?? null;

  async function save() {
    if (!selected) return;
    setRunning(true);
    setError(null);
    try {
      const created = await createHouseholdScenario(selected.request);
      navigate(`/scenarios/${created.scenario_id}/runs/${created.result_id}`);
    } catch (e) {
      setError(e);
      setRunning(false);
    }
  }

  return (
    <div className="space-y-6">
      <p className="text-sm text-muted">
        Start from an example household. For a household of your own, use the{" "}
        <a href="/analyst" className="underline underline-offset-2">
          classic calculator
        </a>
        .
      </p>
      {list.length === 0 ? (
        <Empty title="No examples are available" />
      ) : (
        <fieldset>
          <legend className="mb-2 text-sm font-medium">Choose an example household</legend>
          <ul className="space-y-2">
            {list.map((e) => (
              <li key={e.id}>
                <label className="flex cursor-pointer items-start gap-3 rounded-md border border-border bg-surface p-3 text-sm has-[:checked]:border-accent">
                  <input
                    type="radio"
                    name="example"
                    value={e.id}
                    checked={e.id === selectedId}
                    onChange={() => {
                      setSelectedId(e.id);
                      setError(null);
                    }}
                    className="mt-1"
                  />
                  <span>{e.description || e.id}</span>
                </label>
              </li>
            ))}
          </ul>
        </fieldset>
      )}

      {selected ? (
        <Card role="region" aria-labelledby="household-confirm" className="space-y-3">
          <h2 id="household-confirm" className="text-base font-semibold">
            Check before running
          </h2>
          <p className="text-sm">{selected.description || selected.id}</p>
          <p className="text-sm text-muted">
            The facts in this example are caller-asserted: Poltika uses them as stated and has not verified them. The result is a
            conditional calculation, not a determination of entitlement.
          </p>
          <Button variant="primary" onClick={save} disabled={running}>
            {running ? "Calculating…" : "Save & calculate"}
          </Button>
        </Card>
      ) : null}
      {error ? <ErrorState error={error} onRetry={save} /> : null}
    </div>
  );
}
