import { ScenarioWorkspacePage } from "@/features/ScenarioWorkspacePage";

// The parent segment's placeholder is repeated here: both ids are read from
// the URL on the client (useRouteIds).
export const dynamicParams = false;

export function generateStaticParams() {
  return [{ scenarioId: "_", runId: "_" }];
}

export default function Page() {
  return <ScenarioWorkspacePage />;
}
