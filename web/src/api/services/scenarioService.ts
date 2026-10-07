import { getJson, postJson } from "../client";
import {
  HouseholdCreatedSchema,
  HouseholdDefinitionSchema,
  RerunResponseSchema,
  RunCreatedSchema,
  ScenarioDefinitionSchema,
  ScenarioListSchema,
  WorkspaceSchema,
} from "../schemas";
import type { RunCreated, ScenarioKind, ScenarioList, Workspace } from "@/domain";

export type Operation = "set" | "add" | "multiply";

export type ReformOverride = {
  policy_id: string;
  parameter_id: string;
  operation: Operation;
  /** A decimal string; the server parses it. No client arithmetic. */
  value: string;
};

export type Reform = { reform_id: string; description: string; overrides: ReformOverride[] };
export type ReformOption = { label: string; reform: Reform };

export type CreateScenarioRequest = { title: string; description: string; options: ReformOption[] };

export function getScenarioDefinition(scenarioId: string, signal?: AbortSignal): Promise<CreateScenarioRequest> {
  return getJson(`/api/v1/scenarios/${encodeURIComponent(scenarioId)}/definition`, ScenarioDefinitionSchema, signal);
}

export function rerunHouseholdScenario(resultId: string, signal?: AbortSignal): Promise<{ new_result_id: string }> {
  return postJson(`/scenarios/${encodeURIComponent(resultId)}/rerun`, undefined, RerunResponseSchema, signal);
}

export function getHouseholdDefinition(scenarioId: string, resultId: string, signal?: AbortSignal): Promise<Record<string, unknown>> {
  return getJson(`/api/v1/scenarios/${encodeURIComponent(scenarioId)}/runs/${encodeURIComponent(resultId)}/definition`, HouseholdDefinitionSchema, signal);
}

export function listScenarios(kind?: ScenarioKind, signal?: AbortSignal): Promise<ScenarioList> {
  const query = kind ? `?kind=${kind}` : "";
  return getJson(`/api/v1/scenarios${query}`, ScenarioListSchema, signal);
}

/** Returns the stored scenario; its id is content-derived. */
export async function createScenario(request: CreateScenarioRequest, signal?: AbortSignal): Promise<string> {
  const created = await postJson("/api/v1/scenarios", request, ScenarioListSchema.shape.items.element, signal);
  return created.scenario_id;
}

export function runScenario(scenarioId: string, signal?: AbortSignal): Promise<RunCreated> {
  return postJson(`/api/v1/scenarios/${encodeURIComponent(scenarioId)}/runs`, undefined, RunCreatedSchema, signal);
}

export function getWorkspace(scenarioId: string, runId?: string, signal?: AbortSignal): Promise<Workspace> {
  const path = runId
    ? `/api/v1/scenarios/${encodeURIComponent(scenarioId)}/runs/${encodeURIComponent(runId)}`
    : `/api/v1/scenarios/${encodeURIComponent(scenarioId)}`;
  return getJson(path, WorkspaceSchema, signal);
}

/** `POST /scenarios` with an example's request body. The household run is
 *  addressed as scenario_id / result_id. */
export function createHouseholdScenario(
  request: Record<string, unknown>,
  signal?: AbortSignal,
): Promise<{ scenario_id: string; result_id: string }> {
  return postJson("/scenarios", request, HouseholdCreatedSchema, signal);
}
