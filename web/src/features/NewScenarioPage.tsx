"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { Card } from "@/components/ui/Card";
import { PageHeader } from "@/components/ui/PageHeader";

import { HouseholdBuilder } from "./newScenario/HouseholdBuilder";
import { ReformBuilder } from "./newScenario/ReformBuilder";

type Template = "policy_change" | "compare" | "household";

const TEMPLATES: { id: Template; title: string; text: string }[] = [
  { id: "policy_change", title: "Analyse a policy change", text: "Change one policy setting and see its effect on the synthetic population." },
  { id: "compare", title: "Compare two settings", text: "Run two options side by side against the current law." },
  { id: "household", title: "Explore a household", text: "Calculate one example household's entitlements." },
];

function templateFrom(search: string): Template | null {
  const value = new URLSearchParams(search).get("template");
  return TEMPLATES.find((t) => t.id === value)?.id ?? null;
}

export function NewScenarioPage() {
  const router = useRouter();
  // The query is read after mount: the exported page is the same for every URL.
  const [template, setTemplate] = useState<Template | null | undefined>(undefined);
  useEffect(() => setTemplate(templateFrom(window.location.search)), []);
  const navigate = (href: string) => router.push(href);
  const current = TEMPLATES.find((t) => t.id === template);

  return (
    <div>
      <PageHeader title={current?.title ?? "New scenario"} description={current?.text} />
      {template === undefined ? null : current === undefined ? (
        <ul className="grid gap-3 sm:grid-cols-3">
          {TEMPLATES.map((t) => (
            <li key={t.id}>
              <Link href={`/scenarios/new?template=${t.id}`} className="block no-underline" onClick={() => setTemplate(t.id)}>
                <Card className="h-full hover:bg-surface-muted">
                  <p className="font-medium">{t.title}</p>
                  <p className="mt-1 text-sm text-muted">{t.text}</p>
                </Card>
              </Link>
            </li>
          ))}
        </ul>
      ) : template === "household" ? (
        <HouseholdBuilder navigate={navigate} />
      ) : (
        <ReformBuilder key={template} compare={template === "compare"} navigate={navigate} />
      )}
    </div>
  );
}
