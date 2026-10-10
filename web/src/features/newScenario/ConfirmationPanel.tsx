import { OutcomeMarker } from "@/components/blocks/Outcome";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Pill } from "@/components/ui/Pill";
import type { CheckResult, RegistryParameter, ValidInstrument } from "@/domain";
import { formatExact } from "@/format";
import { humanise } from "@/lib/labels";

export const POPULATION_NOTICE = "Synthetic population — not an estimate for New Zealand";

/** One option, as the registry and the check describe it. */
export type ConfirmationItem = {
  /** Option label; null for a single policy change. */
  label: string | null;
  /** What the person typed, in words. */
  asked: string;
  instrument: ValidInstrument;
  parameter: RegistryParameter;
  check: CheckResult;
};

function Value({ value }: { value: string | null }) {
  return value === null ? <OutcomeMarker outcome="not_calculated" /> : <span className="num">{formatExact(value)}</span>;
}

function Row({ term, children }: { term: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-0.5 py-1.5 sm:flex-row sm:gap-4">
      <dt className="w-44 shrink-0 text-sm text-muted">{term}</dt>
      <dd className="min-w-0 text-sm break-words">{children}</dd>
    </div>
  );
}

function Interpreted({ item, sourceTitles }: { item: ConfirmationItem; sourceTitles: ReadonlyMap<string, string | null> }) {
  const { instrument, parameter, check } = item;
  const change = check.changes[0];
  const current = parameter.current;
  const sourceId = current.source_id ?? null;
  const sourceTitle = sourceId ? (sourceTitles.get(sourceId) ?? null) : null;
  return (
    <dl className="divide-y divide-border">
      <Row term="Policy">
        {instrument.title}
        {instrument.version ? <span className="text-muted"> · version {instrument.version}</span> : null}
      </Row>
      <Row term="Parameter">{humanise(parameter.id)}</Row>
      <Row term="Baseline → scenario">
        {change ? (
          <span className="flex flex-wrap items-center gap-2">
            <Value value={change.baseline} />
            <span aria-label="becomes">→</span>
            <Value value={change.resulting} />
            <span className="text-muted">
              {change.unit === parameter.unit ? parameter.unit_label : humanise(change.unit)}
            </span>
          </span>
        ) : (
          <OutcomeMarker outcome="not_calculated" />
        )}
      </Row>
      <Row term="Source">
        {sourceId ? (
          <>
            {sourceTitle ?? sourceId}
            {current.locator ? <span className="text-muted"> · {current.locator}</span> : null}
          </>
        ) : (
          "No source recorded"
        )}
      </Row>
      <Row term="Reference period">
        <span className="num">
          {instrument.reference_period.from} to {instrument.reference_period.to}
        </span>
      </Row>
    </dl>
  );
}

/** Built only from the registry and the check response. Run stays disabled
 *  unless every option checked clean. */
export function ConfirmationPanel({
  items,
  limitations,
  reformJson,
  onRun,
  running,
  runLabel = "Run analysis",
}: {
  items: readonly ConfirmationItem[];
  limitations: readonly string[];
  reformJson: unknown;
  onRun: () => void;
  running: boolean;
  runLabel?: string;
}) {
  const ok = items.length > 0 && items.every((i) => i.check.ok);
  return (
    <Card aria-labelledby="confirm-heading" role="region" className="space-y-4">
      <h2 id="confirm-heading" className="text-base font-semibold">
        Check before running
      </h2>
      {items.map((item, index) => {
        const titles = new Map(item.instrument.sources.map((s) => [s.id, s.title] as const));
        return (
          <section key={index} aria-label={item.label ?? "Policy change"} className="space-y-2">
            {item.label ? <h3 className="text-sm font-semibold">{item.label}</h3> : null}
            <p className="text-sm">
              <span className="font-medium">You asked: </span>
              {item.asked}
            </p>
            <p className="text-sm font-medium">Poltika has interpreted this as:</p>
            {item.check.ok ? <Interpreted item={item} sourceTitles={titles} /> : null}
            {item.check.problems.length > 0 ? (
              <ul role="alert" className="space-y-1 text-sm text-bad-fg">
                {item.check.problems.map((p, i) => (
                  <li key={i}>
                    <Pill tone="bad">Problem</Pill> {humanise(p.parameter_id)}: {p.message}
                  </li>
                ))}
              </ul>
            ) : null}
          </section>
        );
      })}
      <p className="text-sm">
        <Pill tone="warn">Synthetic</Pill> <span className="ml-1">{POPULATION_NOTICE}</span>
      </p>
      {limitations.length > 0 ? (
        <div>
          <h3 className="text-sm font-semibold">Limitations</h3>
          <ul className="mt-1 list-disc space-y-1 pl-5 text-sm text-muted">
            {limitations.map((l, i) => (
              <li key={i}>{l}</li>
            ))}
          </ul>
        </div>
      ) : null}
      <details className="text-sm">
        <summary className="cursor-pointer">Advanced settings</summary>
        <pre className="mt-2 overflow-x-auto rounded-md border border-border bg-surface-muted p-3 font-mono text-xs">
          {JSON.stringify(reformJson, null, 2)}
        </pre>
      </details>
      <div className="flex flex-wrap items-center gap-3">
        <Button variant="primary" onClick={onRun} disabled={!ok || running}>
          {running ? "Running…" : runLabel}
        </Button>
        {!ok ? <span className="text-sm text-muted">Fix the problems above to run this analysis.</span> : null}
      </div>
    </Card>
  );
}
