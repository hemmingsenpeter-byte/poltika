"use client";

import Link from "next/link";

import { ApiError } from "@/api/errors";
import { getDataset, listDatasets } from "@/api/services/dataService";
import { ErrorState, Loading, Unavailable } from "@/components/states";
import { Section } from "@/components/ui/Card";
import { CopyButton } from "@/components/ui/CopyButton";
import { DataTable } from "@/components/ui/DataTable";
import { PageHeader } from "@/components/ui/PageHeader";
import type { DatasetDetail } from "@/domain";
import { periodWords } from "@/lib/labels";
import { useAsync } from "@/lib/useAsync";
import { useRouteIds } from "@/lib/useRouteIds";

/** The same field the catalogue page reads: `preserved_sources` (ADR-0022). */
function SourceArchive() {
  const state = useAsync(listDatasets, "datasets");
  if (state.status === "loading") return <Loading label="Loading Source Archive state" />;
  if (state.status === "error") return <ErrorState error={state.error} onRetry={state.reload} />;
  const { exposed, note } = state.data.preserved_sources;
  return exposed ? <p className="text-sm">{note}</p> : <Unavailable title="Not yet exposed" reason={note} />;
}

function Detail({ detail }: { detail: DatasetDetail }) {
  const first = detail.snapshots[0];
  return (
    <div>
      <PageHeader
        title={first ? first.dataset_series : detail.dataset_id}
        description={first ? first.source_organisation : undefined}
      />
      <p className="mb-2 font-mono text-xs text-muted">{detail.dataset_id}</p>

      <Section title="Snapshots" id="snapshots">
        <DataTable
          caption="Dataset snapshots"
          rows={detail.snapshots}
          rowKey={(s) => `${s.raw_snapshot_version}`}
          columns={[
            { key: "version", header: "Version", numeric: true, render: (s) => s.raw_snapshot_version },
            { key: "vintage", header: "Vintage", render: (s) => s.vintage },
            { key: "retrieved", header: "Retrieved", render: (s) => <span className="num whitespace-nowrap">{s.retrieval_date}</span> },
            {
              key: "coverage",
              header: "Coverage",
              render: (s) => (
                <span className="num">{periodWords(s.observation_reference_period)}</span>
              ),
            },
            { key: "method", header: "Method", render: (s) => s.retrieval_method },
            {
              key: "sha",
              header: "SHA-256",
              render: (s) => (
                <span className="flex items-center gap-1">
                  <span className="font-mono text-xs" title={s.sha256}>
                    {s.sha256.slice(0, 12)}…
                  </span>
                  <CopyButton text={s.sha256} label={`Copy full SHA-256 of snapshot ${s.raw_snapshot_version}`} />
                </span>
              ),
            },
            {
              key: "transformation",
              header: "Transformation",
              render: (s) => (
                <span className="font-mono text-xs">
                  {s.transformation_id} v{s.transformation_version}
                </span>
              ),
            },
          ]}
        />
      </Section>

      <Section title="Source and scope" id="source">
        <DataTable
          caption="Source, units and population by snapshot"
          rows={detail.snapshots}
          rowKey={(s) => `${s.raw_snapshot_version}`}
          columns={[
            { key: "version", header: "Version", numeric: true, render: (s) => s.raw_snapshot_version },
            { key: "publisher", header: "Publisher", render: (s) => s.source_organisation },
            { key: "source", header: "Source", render: (s) => <span className="break-all">{s.source_url_or_identifier}</span> },
            { key: "units", header: "Units", render: (s) => s.units },
            { key: "population", header: "Geography and population", render: (s) => s.geography_population },
          ]}
        />
      </Section>

      <Section title="Used by" id="used-by">
        <Unavailable
          title="Not recorded"
          reason="No model or scenario declares which datasets it reads, so Poltika cannot list what uses this dataset."
        />
      </Section>

      <Section title="Variables" id="variables">
        {detail.variables.length === 0 ? (
          <p className="text-sm text-muted">No variables are mapped.</p>
        ) : (
          <DataTable
            caption="Canonical variables"
            rows={detail.variables}
            rowKey={(v) => v.id}
            columns={[
              { key: "id", header: "Variable", render: (v) => <span className="font-mono text-xs">{v.id}</span> },
              { key: "meaning", header: "Meaning", render: (v) => v.meaning },
              { key: "unit", header: "Unit", render: (v) => v.unit },
              { key: "frequency", header: "Frequency", render: (v) => v.frequency },
              { key: "basis", header: "Price basis", render: (v) => (v.price_base ? `${v.price_basis} (${v.price_base})` : v.price_basis) },
              { key: "valid", header: "Valid", render: (v) => <span className="num whitespace-nowrap">{v.valid_from} to {v.valid_to ?? "open"}</span> },
            ]}
          />
        )}
      </Section>

      {detail.undefined_variables.length > 0 ? (
        <Section title="Undefined variables" id="undefined">
          <p className="mb-2 text-sm text-muted">The manifest maps these ids, but the variable dictionary does not define them.</p>
          <ul className="list-disc pl-5 font-mono text-xs">
            {detail.undefined_variables.map((v) => (
              <li key={v}>{v}</li>
            ))}
          </ul>
        </Section>
      ) : null}

      <Section title="Raw bytes" id="raw-bytes">
        <p className="text-sm">{detail.raw_bytes_note}</p>
      </Section>

      <Section title="Source Archive snapshots" id="source-archive">
        <SourceArchive />
      </Section>
    </div>
  );
}

export function DatasetDetailPage() {
  const { datasetId } = useRouteIds();
  const state = useAsync(
    (signal) => (datasetId ? getDataset(datasetId, signal) : Promise.reject(new ApiError("not_found", "No dataset id in the address."))),
    `dataset:${datasetId ?? ""}`,
  );
  return (
    <div>
      <p className="mb-3 text-sm">
        <Link href="/data" className="text-accent underline underline-offset-2">
          Data
        </Link>
      </p>
      {state.status === "loading" ? <Loading label="Loading dataset" /> : null}
      {state.status === "error" ? <ErrorState error={state.error} onRetry={state.reload} /> : null}
      {state.status === "ready" ? <Detail detail={state.data} /> : null}
    </div>
  );
}
