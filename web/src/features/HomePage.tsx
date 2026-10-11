"use client";

import { ArrowRight, Search } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

import { getRegistry } from "@/api/services/metaService";
import { useMeta } from "@/components/layout/MetaProvider";
import { Button, buttonClasses } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Empty, ErrorState, Loading } from "@/components/states";
import { searchAnalyses } from "@/lib/searchAnalyses";
import { useAsync } from "@/lib/useAsync";

const MAX_RESULTS = 12;

const ACTIONS = [
  { label: "Analyse a policy change", href: "/scenarios/new?template=policy_change" },
  { label: "Compare two settings", href: "/scenarios/new?template=compare" },
  { label: "Explore a household", href: "/scenarios/new?template=household" },
] as const;

function SupportedSearch() {
  const [query, setQuery] = useState("");
  const registry = useAsync(getRegistry, "registry");
  const { capabilities } = useMeta();
  const searching = query.trim().length > 0;

  return (
    <div>
      <label htmlFor="analysis-search" className="sr-only">
        Search the analyses Poltika supports
      </label>
      <div className="relative">
        <Search aria-hidden="true" className="pointer-events-none absolute top-1/2 left-4 size-5 -translate-y-1/2 text-muted" />
        <input
          id="analysis-search"
          type="search"
          autoComplete="off"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="What happens if the Family Tax Credit rate changes?"
          aria-describedby="analysis-search-note"
          className="h-14 w-full rounded-lg border border-border-strong bg-surface pr-4 pl-12 text-lg shadow-card placeholder:text-muted"
        />
      </div>
      <p id="analysis-search-note" className="mt-2 text-sm text-muted">
        {capabilities.natural_language_scenarios
          ? "Type a policy setting to find it."
          : "This searches the policy settings Poltika supports by name. It does not interpret questions in plain language yet."}
      </p>

      {searching ? (
        <div className="mt-4" aria-live="polite">
          {registry.status === "loading" ? <Loading label="Loading supported analyses" /> : null}
          {registry.status === "error" ? <ErrorState error={registry.error} onRetry={registry.reload} /> : null}
          {registry.status === "ready" ? <Results matches={searchAnalyses(registry.data, query)} /> : null}
        </div>
      ) : null}
    </div>
  );
}

function Results({ matches }: { matches: ReturnType<typeof searchAnalyses> }) {
  if (matches.length === 0) {
    return (
      <Empty title="No supported analysis matches">
        Try a policy setting such as “family tax credit” or “accommodation supplement”.
      </Empty>
    );
  }
  return (
    <Card className="p-0">
      <ul className="divide-y divide-border">
        {matches.slice(0, MAX_RESULTS).map((m) => (
          <li key={m.key}>
            <Link
              href={`/scenarios/new?template=policy_change&instrument=${encodeURIComponent(m.instrumentId)}&parameter=${encodeURIComponent(m.parameterId)}`}
              className="flex items-center justify-between gap-4 px-4 py-3 no-underline hover:bg-surface-muted"
            >
              <span className="min-w-0">
                <span className="block font-medium">{m.label}</span>
                <span className="block text-sm text-muted">
                  {m.instrument} · {m.unit}
                </span>
              </span>
              <ArrowRight aria-hidden="true" className="size-4 shrink-0 text-muted" />
            </Link>
          </li>
        ))}
      </ul>
      {matches.length > MAX_RESULTS ? (
        <p className="border-t border-border px-4 py-2 text-sm text-muted">
          Showing {MAX_RESULTS} of {matches.length}. Narrow the search to see the rest.
        </p>
      ) : null}
    </Card>
  );
}

export function HomePage() {
  return (
    <div className="mx-auto max-w-3xl pt-6 md:pt-12">
      <h1 className="mb-6 text-3xl font-semibold tracking-tight">What do you want to understand?</h1>
      <SupportedSearch />

      <div className="mt-6 flex flex-wrap gap-2" aria-label="Start an analysis" role="group">
        {ACTIONS.map((a) => (
          <Link key={a.href} href={a.href} className={buttonClasses({ variant: "secondary" }, "no-underline")}>
            {a.label}
          </Link>
        ))}
        <Button disabled aria-describedby="recreate-note">
          Recreate an existing policy
        </Button>
        <span id="recreate-note" className="self-center text-sm text-muted">
          Not yet available
        </span>
      </div>

      <section aria-labelledby="about" className="mt-12 border-t border-border pt-6">
        <h2 id="about" className="text-base font-semibold">
          What Poltika does
        </h2>
        <ul className="mt-2 space-y-1 text-sm">
          <li>Poltika makes deterministic New Zealand policy calculations from cited sources.</li>
          <li>It covers Working for Families (2026-27 tax year) and the Accommodation Supplement.</li>
          <li>Population results use a synthetic population: they are not estimates for New Zealand.</li>
        </ul>
        <p className="mt-4 text-sm">
          Prefer the original single-household form?{" "}
          <a href="/analyst" className="text-accent underline underline-offset-2">
            Open the classic household calculator
          </a>
          .
        </p>
      </section>
    </div>
  );
}
