"use client";

import { Unavailable } from "@/components/states";
import { PageHeader } from "@/components/ui/PageHeader";

export function NewScenarioPage() {
  return (
    <div>
      <PageHeader title="New scenario" />
      <Unavailable reason="Creating a scenario is coming in B0.1.4." />
    </div>
  );
}
