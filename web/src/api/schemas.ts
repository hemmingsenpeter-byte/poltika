import { z } from "zod";

import type { components } from "./schema.gen";
import type { Workspace } from "@/domain";

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

const TabId = z.enum(["overview", "fiscal", "distribution", "evidence", "assumptions", "technical", "audit"]);
const BlockFields = { id: z.string(), title: z.string().nullable().optional() };
const Cell = z.string().nullable();
const Precision = z.enum(["household_rule", "population_estimate"]);

const KnownBlockSchema = z.discriminatedUnion("type", [
  z.object({
    ...BlockFields,
    type: z.literal("table"),
    columns: z.array(z.object({
      id: z.string(), label: z.string(), kind: z.enum(["text", "money", "count", "share"]),
      group: z.string().nullable().optional(),
      precision: Precision.default("household_rule"),
    })),
    rows: z.array(z.array(Cell)),
    notes: z.array(z.string()),
  }),
  z.object({
    ...BlockFields, type: z.literal("horizon"),
    years: z.array(z.object({ label: z.string(), modelled: z.boolean(), note: z.string() })),
  }),
  z.object({ ...BlockFields, type: z.literal("list"), items: z.array(z.string()) }),
  z.object({
    ...BlockFields,
    type: z.literal("metric"),
    label: z.string(),
    unit: z.object({
      label: z.string(), currency: z.literal("NZD").nullable(),
      period: z.enum(["tax_year", "week"]).nullable(), basis: z.literal("nominal").nullable(),
      per: z.enum(["household", "population"]).nullable(),
    }),
    values: z.array(z.object({
      option: z.string(), value: Cell,
      outcome: z.enum(["calculated", "needs_review", "unsupported", "not_calculated"]),
    })),
    precision: Precision,
    evidence_class: EvidenceClass,
    context: z.string(),
    provenance: z.array(z.object({ tab: TabId, block_id: z.string() })),
  }),
  z.object({
    ...BlockFields, type: z.literal("notice"),
    tone: z.enum(["info", "caution", "unavailable"]), text: z.string(),
  }),
  z.object({
    ...BlockFields, type: z.literal("sources"), policy_id: z.string(), policy_version: Cell,
    sources: z.array(z.object({
      id: z.string(), title: Cell, url: Cell, kind: Cell, source_type: Cell,
      authority_rank: z.number().nullable(),
      checked_on: z.array(z.object({ field: z.string(), date: z.string() })),
      check_evidence: z.array(z.string()),
    })),
  }),
  z.object({
    ...BlockFields, type: z.literal("audit_record"),
    fields: z.array(z.object({ label: z.string(), value: Cell, note: Cell.optional() })),
  }),
  z.object({
    ...BlockFields, type: z.literal("calculation_chain"),
    steps: z.array(z.object({
      component_id: z.string(), step_id: z.string(), rule_id: Cell,
      description: z.string(), inputs: z.record(z.string(), Cell).default({}), result: Cell,
    })),
  }),
  z.object({
    ...BlockFields, type: z.literal("model_ref"),
    models: z.array(z.object({ id: z.string(), name: z.string(), version: z.string(), label: z.string() })),
  }),
]) satisfies z.ZodType<S["Tab"]["blocks"][number]>;

const knownBlockTypes = new Set<string>(KnownBlockSchema.options.map((schema) => schema.shape.type.value));
const UnknownBlockSchema = z.looseObject({ ...BlockFields, type: z.string() })
  .refine((block) => !knownBlockTypes.has(block.type), "Known block bodies must match their schema");

/** Validate every body we render. Future block types may pass through to the
 * unsupported marker, but a malformed known block cannot take that path. */
const TabSchema = z.object({
  id: TabId,
  title: z.string(),
  status: z.enum(["available", "empty", "unavailable", "deferred"]),
  note: z.string().nullish(),
  blocks: z.array(z.union([KnownBlockSchema, UnknownBlockSchema])),
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
}) satisfies z.ZodType<Workspace>;

export type Instrument = z.infer<typeof InstrumentSchema>;
export type ValidInstrument = Extract<Instrument, { valid: true }>;
export type RegistryParameter = z.infer<typeof RegistryParameterSchema>;
export type Registry = z.infer<typeof RegistrySchema>;
export type CheckResult = z.infer<typeof CheckSchema>;
export type HouseholdExample = z.infer<typeof HouseholdExamplesSchema>[number];

export const ScenarioDefinitionSchema = z.object({
  title: z.string(),
  description: z.string(),
  options: z.array(z.object({
    label: z.string(),
    reform: z.object({
      reform_id: z.string(),
      description: z.string(),
      overrides: z.array(z.object({
        policy_id: z.string(), parameter_id: z.string(),
        operation: z.enum(["set", "add", "multiply"]), value: z.string(),
      })),
    }),
  })),
}) satisfies z.ZodType<S["CreateScenario-Output"]>;

export const RerunResponseSchema = z.object({
  original_result_id: z.string(),
  new_result_id: z.string(),
  changed_artifacts: z.array(z.string()),
  result_changed: z.boolean(),
}) satisfies z.ZodType<S["RerunResponse"]>;

const HouseholdFactStatus = z.enum(["verified", "excluded", "unknown"]);
const RequestedPolicy = { modelled_date: z.string(), requested_policy_version: z.string() };
export const HouseholdDefinitionSchema = z.strictObject({
  as_claimant_is_wff_claimant_or_partner: HouseholdFactStatus,
  wff: z.strictObject({
    ...RequestedPolicy,
    household_eligibility: HouseholdFactStatus,
    extra_instalment_status: HouseholdFactStatus,
    children: z.array(z.strictObject({
      qualifies_whole_year: HouseholdFactStatus,
      best_start_cohort: z.enum(["in_supported_cohort", "outside_best_start_entitlement", "other_cohort_unsupported", "unknown"]),
      best_start_no_disqualifying_payment: HouseholdFactStatus,
    })),
    partner_status: z.enum(["single", "partnered", "unknown"]),
    family_scheme_income: z.strictObject({ claimant_amount: z.string(), partner_amount: z.string().nullable().optional() }).nullable().optional(),
    net_family_scheme_income: z.string().nullable().optional(),
    net_family_scheme_income_me3_attested: z.boolean(),
    in_work_eligibility: HouseholdFactStatus,
    ftc_iwtc_protected_or_direct_abatement: HouseholdFactStatus,
    mc6a_veterans_payment: HouseholdFactStatus,
    mc6b_disqualifying_payment: HouseholdFactStatus,
    minimum_family_full_time_earner_weeks: HouseholdFactStatus,
    best_start_no_shared_care: HouseholdFactStatus,
    best_start_protected_credit: HouseholdFactStatus,
  }),
  accommodation_supplement: z.strictObject({
    ...RequestedPolicy,
    assessment_week_start: z.string(), assessment_week_end: z.string(),
    household_eligibility: HouseholdFactStatus,
    claimant_category: z.enum(["jobseeker_support", "sole_parent_support", "supported_living_payment", "non_beneficiary", "pension_or_veterans", "mixed_benefit_couple"]).nullable().optional(),
    tenure_type: z.enum(["rent_contributions_or_board", "homeowner"]).nullable().optional(),
    partner_status: z.enum(["single", "ordinary_couple", "joint_tenancy", "community_spouse_or_partner"]).nullable().optional(),
    statistical_area_unit: z.enum(["area1", "area2", "area3", "area4"]).nullable().optional(),
    weekly_accommodation_costs: z.string().nullable().optional(),
    dependent_children_count: z.number().int().nullable().optional(),
    cash_assets: z.string().nullable().optional(),
    exempt_cash_asset_status: HouseholdFactStatus,
    weekly_income: z.string().nullable().optional(),
    ordinary_rate_status: HouseholdFactStatus,
    eldest_dependent_child_under_16: HouseholdFactStatus,
  }),
}) satisfies z.ZodType<S["HouseholdCalculationRequest-Output"]>;
