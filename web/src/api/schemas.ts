import { z } from "zod";

import type { components } from "./schema.gen";

/** Response schemas, each checked against the generated OpenAPI types. A
 *  response that does not parse is an `ApiError{kind:"invalid_response"}`. */
type S = components["schemas"];

const Period = z.object({ from: z.string(), to: z.string() }) satisfies z.ZodType<S["Period"]>;

export const MetaSchema = z.object({
  service: z.literal("poltika"),
  api_version: z.literal("v1"),
  package_version: z.string(),
  build: z.object({ commit: z.string().nullable(), note: z.string() }),
  policies: z.array(
    z.object({
      policy_id: z.string(),
      policy_version: z.string().nullable(),
      status: z.string(),
      reference_period: Period,
    }),
  ),
  population: z
    .object({ population_id: z.string(), version: z.number(), synthetic: z.boolean(), label: z.string() })
    .nullable(),
  access: z.object({ password_required: z.boolean() }),
  capabilities: z.record(z.string(), z.boolean()),
}) satisfies z.ZodType<S["Meta"]>;

const Statement = z.object({ text: z.string(), source: z.string() }) satisfies z.ZodType<S["Statement"]>;

const EvidenceClass = z.enum([
  "Fact",
  "Rule",
  "Estimate",
  "Transferred estimate",
  "Assumption",
  "Scenario",
  "Model output",
  "AI hypothesis",
]);

const ModelSchema = z.object({
  id: z.string(),
  name: z.string(),
  kind: z.enum(["engine", "runner"]),
  version: z.string(),
  version_basis: z.string(),
  policy_versions: z.record(z.string(), z.string()),
  owner: z.string(),
  purpose: z.string(),
  entry_points: z.array(z.object({ module: z.string(), function: z.string() })),
  depends_on: z.array(z.string()),
  validation: z.object({
    level: z.string(),
    basis: z.string(),
    cases: z.array(
      z.object({ kind: z.string(), path: z.string(), count: z.union([z.number(), z.literal("unknown")]) }),
    ),
    tests: z.array(z.string()),
    reviews: z.array(z.string()),
    open_items: z.array(z.string()),
  }),
  evidence_classes_consumed: z.array(EvidenceClass),
  evidence_note: z.string(),
  limitations: z.array(Statement),
  model_risks: z.array(Statement),
  change_log: z.array(
    z.object({
      date: z.string(),
      change: z.string(),
      why: z.string(),
      evidence: z.string(),
      validation_rerun: z.string(),
      approval: z.string(),
    }),
  ),
}) satisfies z.ZodType<S["Model"]>;

export const ModelCatalogueSchema = z.object({
  validation_levels: z.array(z.string()),
  models: z.array(
    z.object({
      id: z.string(),
      name: z.string(),
      kind: z.string(),
      version: z.string(),
      purpose: z.string(),
      policy_versions: z.record(z.string(), z.string()),
      depends_on: z.array(z.string()),
      validation_level: z.string(),
      label: z.string(),
    }),
  ),
}) satisfies z.ZodType<S["ModelCatalogue"]>;

export const ModelDetailSchema = z.object({
  model: ModelSchema,
  label: z.string(),
  used_by: z.array(z.string()),
  validation_levels: z.array(z.string()),
}) satisfies z.ZodType<S["ModelDetail"]>;

export const DatasetCatalogueSchema = z.object({
  datasets: z.array(
    z.object({
      dataset_id: z.string(),
      source_organisation: z.string(),
      dataset_series: z.string(),
      latest_snapshot_version: z.number(),
      latest_vintage: z.string(),
      latest_retrieval_date: z.string(),
      observation_reference_period: Period,
      snapshots: z.number(),
      variables: z.number(),
    }),
  ),
  populations: z.array(
    z.object({
      population_id: z.string(),
      version: z.number(),
      households: z.number(),
      synthetic: z.literal(true),
      sources: z.array(z.string()),
    }),
  ),
  preserved_sources: z.object({ exposed: z.literal(false), note: z.string() }),
}) satisfies z.ZodType<S["DatasetCatalogue"]>;

export const DatasetDetailSchema = z.object({
  dataset_id: z.string(),
  snapshots: z.array(
    z.object({
      raw_snapshot_version: z.number(),
      vintage: z.string(),
      sha256: z.string(),
      raw_file: z.string(),
      transformation_id: z.string(),
      transformation_version: z.number(),
      source_organisation: z.string(),
      dataset_series: z.string(),
      source_url_or_identifier: z.string(),
      retrieval_date: z.string(),
      retrieval_method: z.string(),
      observation_reference_period: Period,
      units: z.string(),
      geography_population: z.string(),
      canonical_variable_mapping: z.array(z.string()),
    }),
  ),
  variables: z.array(
    z.object({
      id: z.string(),
      meaning: z.string(),
      unit: z.string(),
      frequency: z.string(),
      price_basis: z.string(),
      price_base: z.string().nullable(),
      measure: z.string(),
      geography_population: z.string(),
      valid_from: z.string(),
      valid_to: z.string().nullable(),
    }),
  ),
  undefined_variables: z.array(z.string()),
  raw_bytes_note: z.string(),
}) satisfies z.ZodType<S["DatasetDetail"]>;

export const ScenarioListSchema = z.object({
  items: z.array(
    z.object({
      scenario_id: z.string(),
      kind: z.enum(["reform", "household"]),
      title: z.string(),
      description: z.string(),
      created_at: z.string(),
      runs: z.number(),
      latest_run_id: z.string().nullable(),
    }),
  ),
  total: z.number(),
}) satisfies z.ZodType<S["ScenarioList"]>;

/** `GET /workbench/registry` has no response model on the backend (ADR-0018),
 *  so this schema is the contract for the fields the web app reads. */
const CurrentValueSchema = z.object({
  outcome: z.string(),
  value: z.string().nullable(),
  source_id: z.string().nullish(),
  locator: z.string().nullish(),
  effective_from: z.string().nullish(),
});

const RegistryParameterSchema = z.object({
  id: z.string(),
  policy_id: z.string(),
  unit: z.string(),
  unit_label: z.string(),
  editable: z.boolean(),
  value_type: z.string(),
  current: CurrentValueSchema,
});

const RegistrySourceSchema = z.object({
  id: z.string(),
  title: z.string().nullable(),
});

const InstrumentSchema = z.discriminatedUnion("valid", [
  z.object({
    valid: z.literal(true),
    id: z.string(),
    title: z.string(),
    version: z.string().nullable(),
    runnable: z.boolean(),
    reference_period: z.object({ from: z.string(), to: z.string() }),
    parameters: z.array(RegistryParameterSchema),
    sources: z.array(RegistrySourceSchema),
  }),
  z.object({ valid: z.literal(false), id: z.string(), error: z.string() }),
]);

export const RegistrySchema = z.object({
  law_baseline: z.string(),
  instruments: z.array(InstrumentSchema),
  limitations: z.array(z.string()),
  max_options: z.number(),
  status_quo_label: z.string(),
});

/** `POST /workbench/check`: each override against the baseline, or why not. */
export const CheckSchema = z.object({
  ok: z.boolean(),
  changes: z.array(
    z.object({
      policy_id: z.string(),
      parameter_id: z.string(),
      operation: z.string(),
      operand: z.string(),
      baseline: z.string().nullable(),
      resulting: z.string().nullable(),
      unit: z.string(),
    }),
  ),
  problems: z.array(z.object({ policy_id: z.string(), parameter_id: z.string(), message: z.string() })),
});

/** `GET /analyst/examples`: example household requests (untyped on the backend). */
export const HouseholdExamplesSchema = z.array(
  z.object({ id: z.string(), description: z.string(), request: z.record(z.string(), z.unknown()) }),
);

/** `POST /scenarios`: only the identifiers the web app navigates with. */
export const HouseholdCreatedSchema = z.object({ scenario_id: z.string(), result_id: z.string() });

export const RunCreatedSchema = z.object({ scenario_id: z.string(), run_id: z.string() }) satisfies z.ZodType<S["RunCreated"]>;

/** The workspace: the top-level shape and each block's discriminator are
 *  checked; block bodies are trusted to the generated types. An unknown block
 *  type passes through so the page can say it is unsupported. */
const TabSchema = z.object({
  id: z.enum(["overview", "fiscal", "distribution", "evidence", "assumptions", "technical", "audit"]),
  title: z.string(),
  status: z.enum(["available", "empty", "unavailable", "deferred"]),
  note: z.string().nullish(),
  blocks: z.array(z.looseObject({ id: z.string(), type: z.string() })),
});

export const WorkspaceSchema = z.object({
  scenario: z.object({
    scenario_id: z.string(),
    kind: z.enum(["reform", "household"]),
    title: z.string(),
    description: z.string(),
    created_at: z.string().nullable(),
  }),
  run: z.object({ run_id: z.string(), created_at: z.string().nullable(), reproducible: z.boolean().nullable() }).nullable(),
  runs: z.array(z.object({ run_id: z.string(), created_at: z.string().nullable() })),
  context: z
    .object({
      law_baseline: z.string(),
      reference_period: z.string(),
      policy_versions: z.record(z.string(), z.string()),
      population_label: z.string().nullable(),
      synthetic: z.boolean(),
    })
    .nullable(),
  tabs: z.array(TabSchema),
});

export type Instrument = z.infer<typeof InstrumentSchema>;
export type ValidInstrument = Extract<Instrument, { valid: true }>;
export type RegistryParameter = z.infer<typeof RegistryParameterSchema>;
export type Registry = z.infer<typeof RegistrySchema>;
export type CheckResult = z.infer<typeof CheckSchema>;
export type HouseholdExample = z.infer<typeof HouseholdExamplesSchema>[number];
