"use client";

import type { ReactNode } from "react";

import { useMeta } from "@/components/layout/MetaProvider";
import { ErrorState, Loading } from "@/components/states";
import { Card, Section } from "@/components/ui/Card";
import { PageHeader } from "@/components/ui/PageHeader";
import { Pill } from "@/components/ui/Pill";
import type { Meta } from "@/domain";
import { humanise } from "@/lib/labels";

function Row({ term, children }: { term: string; children: ReactNode }) {
  return (
    <div className="grid gap-x-6 gap-y-0.5 px-5 py-3 sm:grid-cols-[14rem_minmax(0,1fr)]">
      <dt className="text-muted">{term}</dt>
      <dd className="min-w-0">{children}</dd>
    </div>
  );
}

function Details({ meta }: { meta: Meta }) {
  const { policies, population, build } = meta;
  return (
    <>
      <Section title="Policy versions" id="policy-versions">
        <Card className="p-0">
          {policies.length === 0 ? (
            <p className="px-5 py-3 text-muted">No policy is loaded.</p>
          ) : (
            <dl className="divide-y divide-border">
              {policies.map((p) => (
                <Row key={p.policy_id} term={humanise(p.policy_id)}>
                  <span className="flex flex-wrap items-center gap-3">
                    <span className="num font-semibold">{p.policy_version ?? "Unversioned"}</span>
                    <Pill tone={p.status === "approved" ? "ok" : "neutral"}>{humanise(p.status)}</Pill>
                  </span>
                </Row>
              ))}
            </dl>
          )}
        </Card>
      </Section>

      <Section title="Population" id="population">
        <Card className="p-0">
          {population === null ? (
            <p className="px-5 py-3 text-muted">No population is configured here.</p>
          ) : (
            <dl className="divide-y divide-border">
              <Row term="Population">
                <span className="flex flex-wrap items-center gap-2">
                  {population.label}
                  {population.synthetic ? <Pill tone="warn">Synthetic</Pill> : null}
                </span>
              </Row>
              <Row term="Identifier">
                <span className="font-mono text-sm break-all">{population.population_id}</span>, version{" "}
                <span className="num">{population.version}</span>
              </Row>
            </dl>
          )}
        </Card>
      </Section>

      <Section title="This deployment" id="deployment">
        <Card className="p-0">
          <dl className="divide-y divide-border">
            <Row term="Poltika version">
              <span className="num font-semibold">{meta.package_version}</span>
            </Row>
            <Row term="API version">{meta.api_version}</Row>
            <Row term="Build">
              {build.commit ? (
                <span className="font-mono text-sm break-all">{build.commit}</span>
              ) : (
                "Not reported by the host"
              )}
              <p className="mt-1 text-sm text-muted">{build.note}</p>
            </Row>
          </dl>
        </Card>
      </Section>
    </>
  );
}

/** The versions and data behind this deployment, kept out of the header. */
export function SettingsPage() {
  const { meta } = useMeta();
  return (
    <div className="mx-auto max-w-4xl">
      <PageHeader title="Settings" description="The policy versions, population and build this deployment of Poltika uses." />
      {meta.status === "loading" ? <Loading label="Loading settings" /> : null}
      {meta.status === "error" ? <ErrorState error={meta.error} /> : null}
      {meta.status === "ready" ? <Details meta={meta.data} /> : null}
    </div>
  );
}
