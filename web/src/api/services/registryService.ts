import { getJson, postJson } from "../client";
import { CheckSchema, HouseholdExamplesSchema, RegistrySchema } from "../schemas";
import type { CheckResult, HouseholdExample, Registry } from "@/domain";

import type { Reform } from "./scenarioService";

/** The supported instruments and parameters (the Workbench registry). */
export function getRegistry(signal?: AbortSignal): Promise<Registry> {
  return getJson("/workbench/registry", RegistrySchema, signal);
}

/** What a reform would do to each parameter, before any run. */
export function checkReform(reform: Reform, signal?: AbortSignal): Promise<CheckResult> {
  return postJson("/workbench/check", { reform }, CheckSchema, signal);
}

export function listHouseholdExamples(signal?: AbortSignal): Promise<HouseholdExample[]> {
  return getJson("/analyst/examples", HouseholdExamplesSchema, signal);
}
