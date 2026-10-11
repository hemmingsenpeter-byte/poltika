"use client";

import { useEffect, useRef, useState } from "react";

import { getRegistry, listHouseholdExamples } from "@/api/services/registryService";
import { createHouseholdScenario } from "@/api/services/scenarioService";
import { Empty, ErrorState, Loading } from "@/components/states";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { periodLabel } from "@/format";
import { humanise } from "@/lib/labels";
import { useAsync } from "@/lib/useAsync";

export function HouseholdBuilder({ navigate, initial }: { navigate: (href: string) => void; initial?: Record<string, unknown> }) {
  const examples = useAsync((signal) => initial ? Promise.resolve([]) : listHouseholdExamples(signal), "household-examples");
  const registry = useAsync(getRegistry, "registry");
  const [draft, setDraft] = useState(initial ? JSON.stringify(initial, null, 2) : "");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const request = useRef<AbortController | null>(null);
  useEffect(() => () => request.current?.abort(), []);

  if (examples.status === "loading" || registry.status === "loading") return <Loading label="Loading examples" />;
  if (examples.status === "error") return <ErrorState error={examples.error} onRetry={examples.reload} />;
  if (registry.status === "error") return <ErrorState error={registry.error} onRetry={registry.reload} />;
  const list = examples.data;
  let selected = list.find((e) => e.id === selectedId) ?? null;
  let parsingError: string | null = null;
  if (initial) {
    try {
      const parsed: unknown = JSON.parse(draft);
      if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed) || !("wff" in parsed) || !("accommodation_supplement" in parsed)) {
        throw new Error("Enter a JSON object containing wff and accommodation_supplement facts.");
      }
      selected = { id: "copied", description: "Copied household facts", request: parsed as Record<string, unknown> };
    } catch {
      parsingError = "Enter valid JSON containing wff and accommodation_supplement facts.";
    }
  }

  async function save() {
    if (!selected || request.current) return;
    const controller = new AbortController();
    request.current = controller;
    setRunning(true);
    setError(null);
    try {
      const created = await createHouseholdScenario(selected.request, controller.signal);
      if (controller.signal.aborted) return;
      navigate(`/scenarios/${created.scenario_id}/runs/${created.result_id}`);
    } catch (e) {
      if (!controller.signal.aborted) setError(e);
    } finally {
      if (request.current === controller) {
        request.current = null;
        if (!controller.signal.aborted) setRunning(false);
      }
    }
  }

  return (
    <div className="space-y-6">
      {!initial ? <p className="text-sm text-muted">
        Start from an example household. For a household of your own, use the{" "}
        <a href="/analyst" className="underline underline-offset-2">
          classic calculator
        </a>
        .
      </p> : null}
      {initial ? <div className="space-y-2">
        <label htmlFor="copied-household-facts" className="block text-sm font-medium">Copied household facts</label>
        <p className="text-sm text-muted">Edit the JSON below, then check the facts and requested periods before calculating. The copied versions and dates are kept as stated.</p>
        <textarea id="copied-household-facts" className="min-h-64 w-full rounded-md border border-border-strong bg-surface p-3 font-mono text-xs" value={draft} disabled={running} aria-invalid={parsingError ? true : undefined} onChange={(e) => {
          if (request.current) return;
          setDraft(e.target.value);
          setError(null);
        }} />
        {parsingError ? <><p className="text-sm text-bad-fg" role="alert">{parsingError}</p><Button disabled>Save & calculate</Button></> : null}
      </div> : list.length === 0 ? (
        <Empty title="No examples are available">There are no example households to start from on this server.</Empty>
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
                    disabled={running}
                    onChange={() => {
                      if (request.current) return;
                      setSelectedId(e.id);
                      setError(null);
                    }}
                    className="size-[24px] shrink-0"
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
          <p className="text-sm">Calculation using the requested policy versions; no parameter changes. One household; no population is used.</p>
          <dl className="space-y-1 text-sm">
            {[
              { key: "wff", policyId: "working_for_families" },
              { key: "accommodation_supplement", policyId: "accommodation_supplement" },
            ].map(({ key, policyId }) => {
              const facts = selected.request[key];
              if (typeof facts !== "object" || facts === null || Array.isArray(facts)) return null;
              const values = facts as Record<string, unknown>;
              const policy = registry.data.instruments.find((i) => i.valid && i.id === policyId);
              const period = key === "wff"
                ? `${periodLabel("tax_year")}; policy lookup date ${values.modelled_date ?? "not recorded"}`
                : `${periodLabel("week")}; assessment week ${values.assessment_week_start ?? "not recorded"} to ${values.assessment_week_end ?? "not recorded"} (end exclusive); policy lookup date ${values.modelled_date ?? "not recorded"}`;
              return <div key={key}><dt className="font-medium">{policy?.valid ? policy.title : humanise(policyId)}</dt><dd>Version {String(values.requested_policy_version ?? "not recorded")} · {period}</dd></div>;
            })}
          </dl>
          <p className="text-sm text-muted">
            The facts in this example are caller-asserted: Poltika uses them as stated and has not verified them. The result is a
            conditional calculation, not a determination of entitlement.
          </p>
          <details className="text-sm">
            <summary className="cursor-pointer">Household facts</summary>
            <div className="mt-2 space-y-3">
              {Object.entries(selected.request).map(([group, value]) => <div key={group}>
                <p className="font-medium">{humanise(group)}</p>
                {typeof value === "object" && value !== null && !Array.isArray(value) ? <dl>
                  {Object.entries(value).map(([name, fact]) => <div key={name} className="flex flex-wrap gap-x-3"><dt className="text-muted">{humanise(name)}</dt><dd>{typeof fact === "object" ? JSON.stringify(fact) : String(fact)}</dd></div>)}
                </dl> : <p>{String(value)}</p>}
              </div>)}
            </div>
          </details>
          <details className="text-sm">
            <summary className="cursor-pointer">Current parameter sources and locators</summary>
            <p className="mt-2 text-muted">These sources describe the currently deployed policies. The request keeps its stated versions and dates, which may differ.</p>
            <ul className="mt-2 space-y-1">
              {registry.data.instruments.flatMap((i) => i.valid && i.runnable ? i.parameters.map((p) => <li key={`${i.id}:${p.id}`}>
                {i.title} · {humanise(p.id)}: {i.sources.find((s) => s.id === p.current.source_id)?.title ?? p.current.source_id ?? "No source recorded"}{p.current.locator ? ` · ${p.current.locator}` : ""}
              </li>) : [])}
            </ul>
          </details>
          {registry.data.limitations.length > 0 ? <div className="text-sm"><p className="font-medium">Limitations</p><ul className="list-disc pl-5 text-muted">{registry.data.limitations.map((l, i) => <li key={i}>{l}</li>)}</ul></div> : null}
          <Button variant="primary" onClick={save} disabled={running}>
            {running ? "Calculating…" : "Save & calculate"}
          </Button>
        </Card>
      ) : null}
      {error ? <ErrorState error={error} onRetry={save} /> : null}
    </div>
  );
}
