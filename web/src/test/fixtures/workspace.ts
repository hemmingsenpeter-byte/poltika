import type { Block, Workspace } from "@/domain";

/** One block of every type the backend can send, with a metric whose value was
 *  not calculated. Values are strings, as the API sends them. */
export const BLOCKS: Block[] = [
  {
    type: "metric",
    id: "headline_ftc",
    title: null,
    label: "Family Tax Credit: change in total entitlement",
    unit: { label: "NZD per tax year", currency: "NZD", period: "tax_year", basis: "nominal", per: "population" },
    values: [
      { option: "Proposed change", value: "123456789.5", outcome: "calculated" },
      { option: "Second option", value: null, outcome: "not_calculated" },
      { option: "Third option", value: null, outcome: "needs_review" },
    ],
    precision: "population_estimate",
    evidence_class: "Model output",
    context: "Weighted households; full take-up.",
    provenance: [{ tab: "fiscal", block_id: "fiscal_components" }],
  },
  {
    type: "table",
    id: "headline",
    title: "Who is affected",
    columns: [
      { id: "measure", label: "Measure", kind: "text", group: null },
      { id: "better", label: "Better off", kind: "count", group: "Households" },
      { id: "mean", label: "Mean change", kind: "money", group: "Households" },
    ],
    rows: [
      ["Family Tax Credit", "1234567", "1234.50"],
      ["Best Start", "not calculated", "none"],
    ],
    notes: ["Weighted households."],
  },
  {
    type: "horizon",
    id: "years",
    title: "Years",
    years: [
      { label: "2026-27", modelled: true, note: "Modelled." },
      { label: "2027-28", modelled: false, note: "Not modelled." },
    ],
  },
  { type: "list", id: "limits", title: "Limitations", items: ["First limitation.", "Second limitation."] },
  { type: "notice", id: "population", title: null, tone: "caution", text: "Synthetic population." },
  {
    type: "sources",
    id: "sources_wff",
    title: "Sources",
    policy_id: "working_for_families",
    policy_version: "0.1.0",
    sources: [
      {
        id: "ird_ftc",
        title: "IRD Family Tax Credit",
        url: "https://example.org/ftc",
        kind: "primary",
        source_type: "guidance",
        authority_rank: 2,
        checked_on: [{ field: "rates", date: "2026-09-01" }],
        check_evidence: ["Compared with the published table."],
      },
    ],
  },
  {
    type: "audit_record",
    id: "identity",
    title: "Identity",
    fields: [
      { label: "Scenario ID", value: "a".repeat(64) },
      { label: "Run stored at", value: null },
    ],
  },
  {
    type: "calculation_chain",
    id: "chain",
    title: "Calculation",
    steps: [{ component_id: "ftc", step_id: "s1", rule_id: "R1", description: "Apply the rate.", result: "100" }],
  },
  {
    type: "model_ref",
    id: "models",
    title: "Models",
    models: [{ id: "population_runner", name: "Population runner", version: "0.1.0", label: "spec_validated" }],
  },
];

const ID = "a".repeat(64);
const RUN = "b".repeat(64);

export function workspaceFixture(overrides: Partial<Workspace> = {}): Workspace {
  return {
    scenario: { scenario_id: ID, kind: "reform", title: "Raise the FTC rate", description: "A test.", created_at: "2026-10-01T00:00:00Z" },
    run: { run_id: RUN, created_at: "2026-10-01T00:01:00Z", reproducible: true },
    runs: [{ run_id: RUN, created_at: "2026-10-01T00:01:00Z" }],
    context: {
      law_baseline: "Law as at 1 April 2026",
      reference_period: "2026-27: modelled",
      policy_versions: { working_for_families: "0.1.0" },
      population_label: "Synthetic population — not an estimate for New Zealand",
      synthetic: true,
    },
    tabs: [
      { id: "overview", title: "Overview", status: "available", blocks: BLOCKS.slice(0, 5) },
      { id: "fiscal", title: "Fiscal", status: "available", blocks: [{ type: "list", id: "fiscal_components", title: "Components", items: ["One."] }] },
      { id: "distribution", title: "Distribution", status: "empty", note: "No distribution for this run.", blocks: [] },
      { id: "evidence", title: "Evidence", status: "available", blocks: [BLOCKS[5]!] },
      { id: "assumptions", title: "Assumptions", status: "deferred", note: "Coming later.", blocks: [] },
      { id: "technical", title: "Technical", status: "available", blocks: [BLOCKS[8]!] },
      { id: "audit", title: "Audit", status: "available", blocks: [BLOCKS[6]!, BLOCKS[7]!] },
    ],
    ...overrides,
  };
}
