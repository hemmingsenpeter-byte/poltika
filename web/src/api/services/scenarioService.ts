import { getJson } from "../client";
import { ScenarioListSchema } from "../schemas";
import type { ScenarioKind, ScenarioList } from "@/domain";

export function listScenarios(kind?: ScenarioKind, signal?: AbortSignal): Promise<ScenarioList> {
  const query = kind ? `?kind=${kind}` : "";
  return getJson(`/api/v1/scenarios${query}`, ScenarioListSchema, signal);
}
