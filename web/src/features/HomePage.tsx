"use client";

import { ArrowRight, ChevronDown, Columns2, House, Search, SlidersHorizontal } from "lucide-react";
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
  { label: "Analyse a policy change", href: "/scenarios/new?template=policy_change", icon: SlidersHorizontal },
  { label: "Compare two settings", href: "/scenarios/new?template=compare", icon: Columns2 },
  { label: "Explore a household", href: "/scenarios/new?template=household", icon: House },
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
        <Search aria-hidden="true" className="pointer-events-none absolute top-1/2 left-5 size-6 -translate-y-1/2 text-accent" />
        <input
          id="analysis-search"
          type="search"
          autoComplete="off"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          // The note saying what this search does sits under Advanced, so the
          // placeholder itself must not suggest it reads questions.
          placeholder={
            capabilities.natural_language_scenarios
              ? "What happens if the Family Tax Credit rate changes?"
              : "Search a policy setting, such as the Family Tax Credit"
          }
          aria-describedby="analysis-search-note"
          className="h-14 w-full rounded-md border-2 border-accent bg-surface pr-4 pl-14 text-lg placeholder:text-muted md:h-16 md:text-xl"
        />
      </div>
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

/** Everything beyond the search, folded away until asked for. */
function Advanced() {
  const { capabilities } = useMeta();
  return (
    <details className="group mt-6">
      <summary className="mx-auto flex min-h-[24px] w-fit cursor-pointer list-none items-center gap-1.5 rounded-md px-3 py-2 text-sm font-semibold text-accent hover:bg-accent-soft [&::-webkit-details-marker]:hidden">
        Advanced
        <ChevronDown aria-hidden="true" className="size-4 transition-transform group-open:rotate-180" />
      </summary>
      <Card className="mt-3 md:p-6">
        <p id="analysis-search-note" className="text-sm text-muted">
          {capabilities.natural_language_scenarios
            ? "Type a policy setting to find it."
            : "This searches the policy settings Poltika supports by name. It does not interpret questions in plain language yet."}
        </p>
        <div className="mt-5 flex flex-wrap items-center gap-3" aria-label="Start an analysis" role="group">
          {ACTIONS.map((a, i) => (
            <Link
              key={a.href}
              href={a.href}
              className={buttonClasses({ variant: i === 0 ? "primary" : "secondary" }, "no-underline")}
            >
              <a.icon aria-hidden="true" className="size-4" />
              {a.label}
            </Link>
          ))}
          <Button disabled aria-describedby="recreate-note">
            Recreate an existing policy
          </Button>
          <span id="recreate-note" className="text-sm text-muted">
            Not yet available
          </span>
        </div>
        <p className="mt-5 text-sm text-muted">
          Prefer the original single-household form?{" "}
          <a href="/analyst" className="font-semibold text-accent underline underline-offset-2">
            Open the classic household calculator
          </a>
          .
        </p>
      </Card>
    </details>
  );
}

export function HomePage() {
  return (
    <div className="mx-auto max-w-2xl pt-[8vh] md:pt-[14vh]">
      <h1 className="mb-8 text-center text-4xl leading-none font-semibold tracking-[-0.02em] text-accent md:mb-10 md:text-[4.5rem]">
        Poltika
      </h1>
      <SupportedSearch />
      <Advanced />
    </div>
  );
}
