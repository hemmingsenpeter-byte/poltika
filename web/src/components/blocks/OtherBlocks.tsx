import { AlertTriangle, Info, Clock } from "lucide-react";
import Link from "next/link";
import type { ReactNode } from "react";

import { CopyButton } from "@/components/ui/CopyButton";
import { Pill } from "@/components/ui/Pill";
import { cn } from "@/lib/cn";
import type { BlockOf } from "@/domain";

import { ValidationPill } from "./ValidationPill";

export function HorizonStrip({ block }: { block: BlockOf<"horizon"> }) {
  return (
    // A scrollable region must be keyboard-focusable (axe: scrollable-region-focusable).
    // eslint-disable-next-line jsx-a11y/no-noninteractive-tabindex
    <div tabIndex={0} role="region" aria-label={`${block.title ?? "Years modelled"} (scrollable)`} className="overflow-x-auto pb-1">
    <ol className="flex gap-2">
      {block.years.map((y) => (
        <li
          key={y.label}
          className={cn(
            "min-w-36 shrink-0 rounded-md border p-2 text-xs",
            y.modelled ? "border-accent bg-accent-soft" : "border-dashed border-border-strong bg-surface-muted",
          )}
        >
          <p className="font-medium">{y.label}</p>
          <p className="mt-0.5">{y.modelled ? "Modelled" : "Not modelled"}</p>
          <p className="mt-1 text-muted">{y.note}</p>
        </li>
      ))}
    </ol>
    </div>
  );
}

export function ListBlockView({ block }: { block: BlockOf<"list"> }) {
  return (
    <ul className="list-disc space-y-1 pl-5 text-sm">
      {block.items.map((item, i) => (
        <li key={i}>{item}</li>
      ))}
    </ul>
  );
}

const TONES = {
  info: { icon: Info, label: "Note", classes: "border-border bg-surface" },
  caution: { icon: AlertTriangle, label: "Caution", classes: "border-warn-fg bg-warn-bg text-warn-fg" },
  unavailable: { icon: Clock, label: "Not yet available", classes: "border-dashed border-border-strong bg-surface-muted" },
} as const;

export function NoticeBlock({ block }: { block: BlockOf<"notice"> }) {
  const tone = TONES[block.tone];
  const Icon = tone.icon;
  return (
    <div className={cn("flex items-start gap-3 rounded-md border p-3 text-sm", tone.classes)}>
      <Icon aria-hidden="true" className="mt-0.5 size-4 shrink-0" />
      <div className="min-w-0">
        <p className="font-medium">
          {block.title ? `${block.title}` : tone.label}
          {block.title ? <span className="sr-only"> ({tone.label})</span> : null}
        </p>
        <p>{block.text}</p>
      </div>
    </div>
  );
}

export function SourcesList({ block }: { block: BlockOf<"sources"> }) {
  return (
    <div>
      <p className="mb-2 text-xs text-muted">
        Policy <span className="font-mono">{block.policy_id}</span>
        {block.policy_version ? <> version {block.policy_version}</> : null}
      </p>
      <ul className="space-y-3">
        {block.sources.map((s) => (
          <li key={s.id} className="rounded-md border border-border bg-surface p-3 text-sm">
            <p className="font-medium">
              {s.url && isWebUrl(s.url) ? (
                <a href={s.url} rel="noreferrer" target="_blank" className="inline-flex min-h-[24px] items-center underline underline-offset-2">
                  {s.title ?? s.id}
                </a>
              ) : (
                (s.title ?? s.id)
              )}
            </p>
            <p className="mt-1 flex flex-wrap items-center gap-2 text-xs text-muted">
              <span className="font-mono">{s.id}</span>
              {s.kind ? <Pill tone="neutral">{s.kind}</Pill> : null}
              {s.source_type ? <Pill tone="neutral">{s.source_type}</Pill> : null}
              {s.authority_rank !== null ? <span>Authority rank {s.authority_rank}</span> : null}
            </p>
            {s.checked_on.length > 0 ? (
              <ul className="mt-2 text-xs text-muted">
                {s.checked_on.map((c, i) => (
                  <li key={i}>
                    Checked {c.field}: <span className="num">{c.date}</span>
                  </li>
                ))}
              </ul>
            ) : null}
            {s.check_evidence.length > 0 ? (
              <details className="mt-2 text-xs">
                <summary className="cursor-pointer">Check evidence</summary>
                <ul className="mt-1 list-disc space-y-1 pl-5 text-muted">
                  {s.check_evidence.map((e, i) => (
                    <li key={i}>{e}</li>
                  ))}
                </ul>
              </details>
            ) : null}
          </li>
        ))}
      </ul>
    </div>
  );
}

export function AuditRecord({ block }: { block: BlockOf<"audit_record"> }) {
  return (
    <dl className="divide-y divide-border rounded-md border border-border bg-surface">
      {block.fields.map((f) => (
        <div key={f.label} className="flex flex-col gap-1 px-3 py-2 sm:flex-row sm:items-start sm:gap-4">
          <dt className="w-64 shrink-0 text-sm text-muted">{f.label}</dt>
          <dd className="min-w-0 flex-1 text-sm">
            {f.value === null ? (
              <span className="text-muted">Not recorded</span>
            ) : (
              <span className="flex flex-wrap items-center gap-2">
                <span className="font-mono text-xs break-all">{f.value}</span>
                <CopyButton text={f.value} label={`Copy ${f.label}`} />
              </span>
            )}
            {f.note ? <span className="mt-0.5 block text-xs text-muted">{f.note}</span> : null}
          </dd>
        </div>
      ))}
    </dl>
  );
}

export function CalculationChain({ block }: { block: BlockOf<"calculation_chain"> }) {
  return (
    <ol className="space-y-2">
      {block.steps.map((s, i) => (
        <li key={`${s.component_id}/${s.step_id}/${i}`} className="rounded-md border border-border bg-surface p-3 text-sm">
          <p className="font-medium">{s.description}</p>
          <p className="mt-1 text-xs text-muted">
            <span className="font-mono">{s.component_id}</span> · <span className="font-mono">{s.step_id}</span>
            {s.rule_id ? (
              <>
                {" "}
                · rule <span className="font-mono">{s.rule_id}</span>
              </>
            ) : null}
          </p>
          {Object.keys(s.inputs).length > 0 ? (
            <dl className="mt-2 text-xs" aria-label="Recorded inputs">
              {Object.entries(s.inputs).map(([name, value]) => (
                <div key={name} className="flex flex-wrap gap-x-2">
                  <dt className="font-mono text-muted">{name}</dt>
                  <dd>{value === null ? <span className="text-muted">Not recorded</span> : <span className="num">{value}</span>}</dd>
                </div>
              ))}
            </dl>
          ) : null}
          <p className="mt-1">
            Result: {s.result === null ? <span className="text-muted">Not calculated</span> : <span className="num">{s.result}</span>}
          </p>
        </li>
      ))}
    </ol>
  );
}

export function ModelReferences({ block }: { block: BlockOf<"model_ref"> }) {
  const levels: readonly string[] = ["not_validated", "spec_validated"];
  return (
    <ul className="space-y-2">
      {block.models.map((m) => (
        <li key={m.id} className="flex flex-wrap items-center gap-2 rounded-md border border-border bg-surface p-3 text-sm">
          <Link href={`/models/${m.id}`} className="inline-flex min-h-[24px] items-center font-medium underline underline-offset-2">
            {m.name}
          </Link>
          <span className="text-xs text-muted">version {m.version}</span>
          <ValidationPill label={m.label} levels={levels} />
        </li>
      ))}
    </ul>
  );
}

export function UnsupportedBlock({ type }: { type: string }): ReactNode {
  return (
    <div className="flex items-start gap-3 rounded-md border border-dashed border-border-strong bg-surface-muted p-3 text-sm">
      <Clock aria-hidden="true" className="mt-0.5 size-4 shrink-0" />
      <p>
        Unsupported block: this page cannot show a block of type <span className="font-mono">{type}</span>.
      </p>
    </div>
  );
}


/** Only http(s) sources become links; anything else is shown as text. */
function isWebUrl(url: string): boolean {
  try {
    const { protocol } = new URL(url);
    return protocol === "http:" || protocol === "https:";
  } catch {
    return false;
  }
}
