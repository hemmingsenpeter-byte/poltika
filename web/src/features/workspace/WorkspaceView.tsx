"use client";

import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";

import { isApiError } from "@/api/errors";
import { rerunHouseholdScenario, runScenario } from "@/api/services/scenarioService";
import { BlockRenderer } from "@/components/blocks/BlockRenderer";
import { ErrorState, Empty, Loading, Unavailable } from "@/components/states";
import { buttonClasses, Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { IdChip } from "@/components/ui/IdChip";
import { PageHeader } from "@/components/ui/PageHeader";
import { Pill } from "@/components/ui/Pill";
import { Tabs } from "@/components/ui/Tabs";
import type { TabId, Workspace } from "@/domain";
import { formatWhen } from "@/lib/formatWhen";

const TAB_IDS: readonly TabId[] = ["overview", "fiscal", "distribution", "evidence", "assumptions", "technical", "audit"];

function isTabId(value: string | null): value is TabId {
  return value !== null && (TAB_IDS as readonly string[]).includes(value);
}

function Context({ context }: { context: NonNullable<Workspace["context"]> }) {
  const versions = Object.entries(context.policy_versions);
  return (
    <dl className="mt-3 grid gap-x-6 gap-y-1 text-sm sm:grid-cols-2">
      <div>
        <dt className="text-muted">Law baseline</dt>
        <dd>{context.law_baseline}</dd>
      </div>
      <div>
        <dt className="text-muted">Reference period</dt>
        <dd>{context.reference_period}</dd>
      </div>
      <div>
        <dt className="text-muted">Policy versions</dt>
        <dd>
          {versions.length === 0 ? (
            "—"
          ) : (
            <ul>
              {versions.map(([id, version]) => (
                <li key={id}>
                  {id} <span className="num font-semibold">{version}</span>
                </li>
              ))}
            </ul>
          )}
        </dd>
      </div>
      <div>
        <dt className="text-muted">Population</dt>
        <dd className="flex flex-wrap items-center gap-2">
          {context.population_label ?? "No population used"}
          {context.synthetic ? <Pill tone="warn">Synthetic</Pill> : null}
        </dd>
      </div>
    </dl>
  );
}

/** The workspace for a scenario and, when it has been run, one run. Navigation
 *  is passed in so the view needs no router to be tested. */
export function WorkspaceView({ workspace, navigate }: { workspace: Workspace; navigate: (href: string) => void }) {
  const { scenario, run, runs, context, tabs } = workspace;
  const [selected, setSelected] = useState<TabId>("overview");
  const [pendingBlock, setPendingBlock] = useState<string | null>(null);
  const [running, setRunning] = useState(false);
  const [runError, setRunError] = useState<unknown>(null);
  const pendingRun = useRef<AbortController | null>(null);
  useEffect(() => () => pendingRun.current?.abort(), []);

  // The URL is read after mount so the exported HTML and hydration agree.
  useEffect(() => {
    const requested = new URLSearchParams(window.location.search).get("tab");
    if (isTabId(requested)) setSelected(requested);
  }, []);

  const select = useCallback((id: string) => {
    if (!isTabId(id)) return;
    setSelected(id);
    const url = new URL(window.location.href);
    url.searchParams.set("tab", id);
    window.history.replaceState(window.history.state, "", url);
  }, []);

  const openBlock = useCallback(
    (tab: string, blockId: string) => {
      select(tab);
      setPendingBlock(blockId);
    },
    [select],
  );

  useEffect(() => {
    if (pendingBlock === null) return;
    document.getElementById(`block-${pendingBlock}`)?.scrollIntoView?.({ block: "start" });
    setPendingBlock(null);
  }, [pendingBlock, selected]);

  async function runAgain() {
    if (pendingRun.current || (scenario.kind === "household" && !run)) return;
    const controller = new AbortController();
    pendingRun.current = controller;
    setRunning(true);
    setRunError(null);
    try {
      const nextRunId = scenario.kind === "reform"
        ? (await runScenario(scenario.scenario_id, controller.signal)).run_id
        : (await rerunHouseholdScenario(run!.run_id, controller.signal)).new_result_id;
      if (!controller.signal.aborted) navigate(`/scenarios/${scenario.scenario_id}/runs/${nextRunId}`);
    } catch (error) {
      if (!controller.signal.aborted) setRunError(error);
    } finally {
      if (pendingRun.current === controller) {
        pendingRun.current = null;
        if (!controller.signal.aborted) setRunning(false);
      }
    }
  }

  const tab = tabs.find((t) => t.id === selected) ?? tabs[0];
  const status = run ? (run.reproducible === false ? "Run stored (not tied to a source commit)" : "Run stored") : "Not yet run";

  return (
    <div>
      <PageHeader
        title={scenario.title}
        description={scenario.description || undefined}
        actions={
          <div className="flex flex-wrap gap-2">
            {scenario.kind === "reform" || run ? (
              <Button variant="primary" onClick={runAgain} disabled={running}>
                {running ? "Running…" : run ? "Run again" : "Run analysis"}
              </Button>
            ) : null}
            {scenario.kind === "reform" || run ? <Link
              href={scenario.kind === "reform" ? `/scenarios/new?fromScenario=${encodeURIComponent(scenario.scenario_id)}` : `/scenarios/new?fromHousehold=${encodeURIComponent(scenario.scenario_id)}&fromRun=${encodeURIComponent(run!.run_id)}`}
              className={buttonClasses({ variant: "secondary" }, "no-underline")}
            >
              Edit as new scenario
            </Link> : null}
          </div>
        }
      />

      {running ? (
        <div className="mb-4">
          <Loading label={scenario.kind === "household" ? "Calculating the household using its requested policy versions" : "Running on the synthetic population — about 30–60 seconds"} />
        </div>
      ) : null}
      {runError ? (
        <div className="mb-4">
          <ErrorState error={runError} onRetry={isApiError(runError) && runError.kind === "busy" ? runAgain : undefined} />
        </div>
      ) : null}

      <Card className="mb-6">
        <div className="flex flex-wrap items-center gap-x-6 gap-y-2 text-sm">
          <Pill tone="neutral">{scenario.kind === "reform" ? "Policy change" : "Household"}</Pill>
          <span>{status}</span>
          <span className="text-muted">Created {formatWhen(scenario.created_at)}</span>
          <span className="flex items-center gap-1">
            <span className="text-muted">Scenario</span>
            <IdChip id={scenario.scenario_id} label="scenario ID" />
          </span>
          {run ? (
            <span className="flex items-center gap-1">
              <span className="text-muted">Run</span>
              <IdChip id={run.run_id} label="run ID" />
            </span>
          ) : null}
          {run ? <span className="text-muted">Run stored {formatWhen(run.created_at)}</span> : null}
        </div>
        {runs.length > 1 ? (
          <div className="mt-3 flex items-center gap-2 text-sm">
            <label htmlFor="run-select" className="text-muted">
              Run
            </label>
            <select
              id="run-select"
              value={run?.run_id ?? ""}
              onChange={(e) => navigate(`/scenarios/${scenario.scenario_id}/runs/${e.target.value}`)}
              className="h-10 max-w-full rounded-md border md:h-9 border-border-strong bg-surface px-2 font-mono text-xs"
            >
              {runs.map((r) => (
                <option key={r.run_id} value={r.run_id}>
                  {r.run_id.slice(0, 12)} · {formatWhen(r.created_at)}
                </option>
              ))}
            </select>
          </div>
        ) : null}
        {context ? <Context context={context} /> : null}
        {run && scenario.kind === "reform" ? <div className="mt-3 flex flex-wrap gap-2">
          <a className={buttonClasses({ variant: "secondary" }, "no-underline")} href={`/api/v1/scenarios/${encodeURIComponent(scenario.scenario_id)}/runs/${encodeURIComponent(run.run_id)}/export.xlsx`} download>Export Excel</a>
          <a className={buttonClasses({ variant: "secondary" }, "no-underline")} href={`/api/v1/scenarios/${encodeURIComponent(scenario.scenario_id)}/runs/${encodeURIComponent(run.run_id)}/export/headline.csv`} download>Export headline CSV</a>
        </div> : null}
      </Card>

      <Tabs
        label="Scenario results"
        selected={tab?.id ?? "overview"}
        onSelect={select}
        tabs={tabs.map((t) => ({ id: t.id, label: t.title }))}
      >
        {tab === undefined ? (
          <Empty title="Nothing to show" />
        ) : tab.status === "available" ? (
          tab.blocks.length === 0 ? (
            <Empty title="Nothing to show">{tab.note}</Empty>
          ) : (
            <div>
              <h2 className="sr-only">{tab.title}</h2>
              {tab.note ? <p className="mb-4 text-sm text-muted">{tab.note}</p> : null}
              {tab.blocks.map((block) => (
                <BlockRenderer key={block.id} block={block} onOpen={openBlock} />
              ))}
            </div>
          )
        ) : (
          <Unavailable
            title={tab.status === "empty" ? "Nothing to show" : "Not yet available"}
            reason={tab.note ?? "This tab has no content for this scenario."}
          />
        )}
      </Tabs>
    </div>
  );
}
