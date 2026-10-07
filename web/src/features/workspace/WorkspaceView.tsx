"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { isApiError } from "@/api/errors";
import { runScenario } from "@/api/services/scenarioService";
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
                  <span className="font-mono text-xs">{id}</span> {version}
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
    setRunning(true);
    setRunError(null);
    try {
      const created = await runScenario(scenario.scenario_id);
      navigate(`/scenarios/${scenario.scenario_id}/runs/${created.run_id}`);
    } catch (error) {
      setRunError(error);
    } finally {
      setRunning(false);
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
            {scenario.kind === "reform" ? (
              <Button variant="primary" onClick={runAgain} disabled={running}>
                {running ? "Running…" : run ? "Run again" : "Run analysis"}
              </Button>
            ) : null}
            <Link
              href={`/scenarios/new?template=${scenario.kind === "reform" ? "policy_change" : "household"}`}
              className={buttonClasses({ variant: "secondary" }, "no-underline")}
            >
              Edit as new scenario
            </Link>
          </div>
        }
      />

      {running ? (
        <div className="mb-4">
          <Loading label="Running on the synthetic population — about 30–60 seconds" />
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
              className="h-9 rounded-md border border-border-strong bg-surface px-2 font-mono text-xs"
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
        <p className="mt-3 text-xs text-muted">
          Export: available from the classic workbench API. A stored run is not kept in the memory those exports read.
        </p>
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
