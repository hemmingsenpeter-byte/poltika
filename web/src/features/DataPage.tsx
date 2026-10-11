"use client";

import Link from "next/link";

import { listDatasets } from "@/api/services/dataService";
import { Empty, ErrorState, Loading, Unavailable } from "@/components/states";
import { Card, Section } from "@/components/ui/Card";
import { Definition } from "@/components/ui/DataTable";
import { PageHeader } from "@/components/ui/PageHeader";
import { Pill } from "@/components/ui/Pill";
import { periodWords } from "@/lib/labels";
import { useAsync } from "@/lib/useAsync";

export function DataPage() {
  const state = useAsync(listDatasets, "datasets");

  return (
    <div>
      <PageHeader
        title="Data"
        description="Published statistics Poltika uses, and the synthetic population built from them."
      />
      {state.status === "loading" ? <Loading label="Loading datasets" /> : null}
      {state.status === "error" ? <ErrorState error={state.error} onRetry={state.reload} /> : null}
      {state.status === "ready" ? (
        <>
          <Section title="Datasets" id="datasets">
            {state.data.datasets.length === 0 ? (
              <Empty title="No datasets are registered">The catalogue on this server is empty.</Empty>
            ) : (
              <ul className="grid gap-3 md:grid-cols-2">
                {state.data.datasets.map((d) => (
                  <li key={d.dataset_id}>
                    <Link href={`/data/${d.dataset_id}`} className="block h-full no-underline">
                      <Card className="h-full hover:border-border-strong">
                        <h3 className="font-medium">{d.dataset_series}</h3>
                        <p className="text-sm text-muted">{d.source_organisation}</p>
                        <dl className="mt-2">
                          <Definition term="Latest vintage">{d.latest_vintage}</Definition>
                          <Definition term="Retrieved">
                            <span className="num">{d.latest_retrieval_date}</span>
                          </Definition>
                          <Definition term="Coverage">
                            <span className="num">{periodWords(d.observation_reference_period)}</span>
                          </Definition>
                          <Definition term="Snapshots">
                            <span className="num">{d.snapshots}</span>
                          </Definition>
                          <Definition term="Variables">
                            <span className="num">{d.variables}</span>
                          </Definition>
                        </dl>
                      </Card>
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </Section>

          <Section title="Synthetic population" id="populations">
            {state.data.populations.length === 0 ? (
              <Empty title="No population specification is registered">The catalogue on this server lists none.</Empty>
            ) : (
              <ul className="space-y-3">
                {state.data.populations.map((p) => (
                  <li key={`${p.population_id}-${p.version}`}>
                    <Card>
                      <div className="flex flex-wrap items-center gap-2">
                        <h3 className="font-medium">{p.population_id}</h3>
                        <Pill tone="warn">Synthetic: not an estimate for New Zealand</Pill>
                      </div>
                      <p className="num mt-1 text-sm text-muted">
                        version {p.version} · {p.households} households
                      </p>
                      <details className="mt-2 text-sm">
                        <summary className="cursor-pointer text-accent">
                          Sources and assumptions (<span className="num">{p.sources.length}</span>)
                        </summary>
                        <ul className="mt-2 list-disc space-y-1 pl-5">
                          {p.sources.map((s) => (
                            <li key={s} className="break-words">
                              {s}
                            </li>
                          ))}
                        </ul>
                      </details>
                    </Card>
                  </li>
                ))}
              </ul>
            )}
          </Section>

          <Section title="Preserved sources" id="preserved">
            <Unavailable reason={state.data.preserved_sources.note} />
          </Section>
        </>
      ) : null}
    </div>
  );
}
