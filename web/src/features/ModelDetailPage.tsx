"use client";

import Link from "next/link";

import { ApiError } from "@/api/errors";
import { getModel } from "@/api/services/modelService";
import { ValidationPill } from "@/components/blocks/ValidationPill";
import { ErrorState, Loading } from "@/components/states";
import { Card, Section } from "@/components/ui/Card";
import { DataTable, Definition } from "@/components/ui/DataTable";
import { PageHeader } from "@/components/ui/PageHeader";
import { Pill } from "@/components/ui/Pill";
import type { ModelDetail } from "@/domain";
import { humanise } from "@/lib/labels";
import { useAsync } from "@/lib/useAsync";
import { useRouteIds } from "@/lib/useRouteIds";

function TextList({ items, empty }: { items: readonly string[]; empty: string }) {
  if (items.length === 0) return <p className="text-sm text-muted">{empty}</p>;
  return (
    <ul className="list-disc space-y-1 pl-5 text-sm">
      {items.map((item) => (
        <li key={item} className="break-words">
          {item}
        </li>
      ))}
    </ul>
  );
}

function ModelLinks({ ids, empty }: { ids: readonly string[]; empty: string }) {
  if (ids.length === 0) return <p className="text-sm text-muted">{empty}</p>;
  return (
    <ul className="flex flex-wrap gap-2">
      {ids.map((id) => (
        <li key={id}>
          <Link href={`/models/${id}`} className="rounded-sm border border-border-strong px-2 py-0.5 font-mono text-xs text-accent no-underline hover:bg-surface-muted">
            {id}
          </Link>
        </li>
      ))}
    </ul>
  );
}

function Statements({ items, empty }: { items: ModelDetail["model"]["limitations"]; empty: string }) {
  if (items.length === 0) return <p className="text-sm text-muted">{empty}</p>;
  return (
    <ul className="space-y-2">
      {items.map((s) => (
        <li key={s.text}>
          <Card className="text-sm">
            <p>{s.text}</p>
            <p className="mt-1 text-xs text-muted">Source: {s.source}</p>
          </Card>
        </li>
      ))}
    </ul>
  );
}

function Detail({ detail }: { detail: ModelDetail }) {
  const { model, label, used_by, validation_levels } = detail;
  return (
    <div>
      <PageHeader
        title={model.name}
        description={model.purpose}
        actions={<ValidationPill label={label} levels={validation_levels} />}
      />
      <dl className="rounded-md border border-border bg-surface px-4 py-2">
        <Definition term="Id">
          <span className="font-mono">{model.id}</span>
        </Definition>
        <Definition term="Kind">{humanise(model.kind)}</Definition>
        <Definition term="Version">
          <span className="num font-mono">{model.version}</span> ({model.version_basis})
        </Definition>
        <Definition term="Owner">{model.owner}</Definition>
        <Definition term="Policy versions">
          {Object.keys(model.policy_versions).length === 0
            ? "None"
            : Object.entries(model.policy_versions)
                .map(([policy, version]) => `${policy} ${version}`)
                .join(", ")}
        </Definition>
      </dl>

      <Section title="Validation" id="validation">
        <Card>
          <p className="text-sm">
            <span className="text-muted">Level: </span>
            <strong>{humanise(model.validation.level)}</strong>
          </p>
          <p className="mt-2 text-sm">{model.validation.basis}</p>
        </Card>
        <h3 className="mt-4 mb-2 text-sm font-medium">Cases</h3>
        {model.validation.cases.length === 0 ? (
          <p className="text-sm text-muted">No validation cases are listed.</p>
        ) : (
          <DataTable
            caption="Validation cases"
            rows={model.validation.cases}
            rowKey={(c) => `${c.kind}:${c.path}`}
            columns={[
              { key: "kind", header: "Kind", render: (c) => c.kind },
              { key: "path", header: "File", render: (c) => <span className="font-mono text-xs break-all">{c.path}</span> },
              { key: "count", header: "Count", numeric: true, render: (c) => (c.count === "unknown" ? "Not recorded" : c.count) },
            ]}
          />
        )}
        <h3 className="mt-4 mb-2 text-sm font-medium">Tests</h3>
        <TextList items={model.validation.tests} empty="No tests are listed." />
        <h3 className="mt-4 mb-2 text-sm font-medium">Reviews</h3>
        <TextList items={model.validation.reviews} empty="No reviews are listed." />
        <h3 className="mt-4 mb-2 text-sm font-medium">Open items</h3>
        <TextList items={model.validation.open_items} empty="No open items are listed." />
      </Section>

      <Section title="Limitations" id="limitations">
        <Statements items={model.limitations} empty="No limitations are listed." />
      </Section>
      <Section title="Model risks" id="risks">
        <Statements items={model.model_risks} empty="No risks are listed." />
      </Section>

      <Section title="Evidence classes consumed" id="evidence">
        <ul className="mb-2 flex flex-wrap gap-2">
          {model.evidence_classes_consumed.map((c) => (
            <li key={c}>
              <Pill tone="neutral">{c}</Pill>
            </li>
          ))}
        </ul>
        <p className="text-sm text-muted">{model.evidence_note}</p>
      </Section>

      <Section title="Depends on" id="depends-on">
        <ModelLinks ids={model.depends_on} empty="This model depends on no other registered model." />
      </Section>
      <Section title="Used by" id="used-by">
        <ModelLinks ids={used_by} empty="No registered model uses this one." />
      </Section>

      <Section title="Change log" id="change-log">
        {model.change_log.length === 0 ? (
          <p className="text-sm text-muted">No changes are recorded.</p>
        ) : (
          <DataTable
            caption="Change log"
            rows={model.change_log}
            rowKey={(c) => `${c.date}:${c.change}`}
            columns={[
              { key: "date", header: "Date", render: (c) => <span className="num whitespace-nowrap">{c.date}</span> },
              { key: "change", header: "Change", render: (c) => c.change },
              { key: "why", header: "Why", render: (c) => c.why },
              { key: "evidence", header: "Evidence", render: (c) => c.evidence },
              { key: "rerun", header: "Validation rerun", render: (c) => c.validation_rerun },
              { key: "approval", header: "Approval", render: (c) => c.approval },
            ]}
          />
        )}
      </Section>
    </div>
  );
}

export function ModelDetailPage() {
  const { modelId } = useRouteIds();
  const state = useAsync(
    (signal) => (modelId ? getModel(modelId, signal) : Promise.reject(new ApiError("not_found", "No model id in the address."))),
    `model:${modelId ?? ""}`,
  );
  return (
    <div>
      <p className="mb-3 text-sm">
        <Link href="/models" className="text-accent underline underline-offset-2">
          Models
        </Link>
      </p>
      {state.status === "loading" ? <Loading label="Loading model" /> : null}
      {state.status === "error" ? <ErrorState error={state.error} onRetry={state.reload} /> : null}
      {state.status === "ready" ? <Detail detail={state.data} /> : null}
    </div>
  );
}
