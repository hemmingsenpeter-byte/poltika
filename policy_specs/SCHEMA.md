# POLICY_SPECS v0.1 schema draft

**Schema version:** `0.1` (draft). **Status:** Task 4 design draft with Task 6
versioning; not itself an approved implementation schema or policy calculation.
**Basis:** the Task 2 WFF and Accommodation Supplement source maps,
the frozen doctrines in `BUILD_PLAN.md`, and the bounded Task 3 structural
handoff. Claude Code's Task 7 repo-feasibility review is recorded below;
WFF policy content was separately approved at Task 10, while Accommodation
Supplement remains unapproved pending Task 22.

*Update (Task 27.2, 24 September 2026):* the header above is historical.
Both policies are now approved (Tasks 10 and 22), and the schema is
implemented and stays at `"0.1"`. See "Schema as implemented" below for
what the code accepts today.

## Boundary

`policy.yaml` will describe one policy's supported input domain, assessment
roles, effective-dated parameters, source links, and outputs. Its companion
`specification.md` remains the human-readable rule and calculation authority;
this schema is not a formula language. `sources.yaml` is the policy-source
catalogue. Statistical raw-snapshot manifests live in `data/metadata/` when
Tasks 10a/22a need them, not inside `policy.yaml`. Task 5 establishes those
files. The Task 5 scaffolds contain no accepted statutory value.

No field may silently default a missing fact, source, date, or geographic area
to a value that would yield entitlement. The eventual calculator must
distinguish an in-scope zero from `unsupported`/`needs_review`.

## Minimal policy record

| Field | Shape and purpose | Grounding |
| --- | --- | --- |
| `schema_version` | Required top-level string identifying this contract; both policy scaffolds use `"0.1"`. It is independent of policy revision and law. | `BUILD_PLAN.md` Task 6. |
| `policy_id`, `policy_version` | Stable policy identity (`working_for_families` or `accommodation_supplement`) and revision of its reviewed specification. Neither is a legal effective date. | `BUILD_PLAN.md` Tasks 4-6. |
| `status`, `reference_period` | Review state and dated policy period to which the record applies. A Task 2 map is not `approved`. | Both `specification.md` headers. |
| `source_catalog` | Relative path to the corresponding `sources.yaml`; rule and parameter references use its stable source IDs. | Both source maps. |
| `assessment` | Policy-specific person roles, assessment-unit membership, and membership periods; see below. | WFF-01/02/07 and AS-01/09. |
| `inputs` | Named facts with owner, type, unit, period/granularity, source-rule IDs, and missing/unsupported conditions. These specify the input contract, not case values. | WFF-02/07/09 and AS-02/05/06/07. |
| `parameters` | Named policy constants with unit and one or more non-overlapping, source-linked effective intervals. Values remain unapproved until the relevant policy review. | WFF-03/04/06 and AS-04/06/07; dated maps. |
| `components` | Stable rule IDs and output IDs linking to `specification.md`; no executable expressions or copied external formulas. | WFF-03 through WFF-09; AS-03 through AS-10. |
| `outputs` | Names, units, and period of the calculator's result components, plus explicit unsupported/needs-review outcome. Rounding belongs in the reviewed spec. | WFF-09 and AS-07; Task 10/22 gates. |

Source links on an input, component, or parameter must resolve to a source ID
in that policy's `sources.yaml` and to a pinpoint provision, table, or example
where the claim depends on it. A design-only field can instead be marked as
an inference pending review; that mark is not policy authority. Existing
catalogue entries carry `id`, `kind`, `title`, `url`, and `covers`; date and
locator details may need strengthening during Tasks 10/22 before a value or
rule is accepted.

## Version axes

- `schema_version` identifies the shape of `policy.yaml`. The current design
  is `"0.1"` and remains a draft after Task 7's feasibility review. A change
  to that shape requires a new schema version and migration of both policy
  files; Tasks 25/26 are the planned AS stress test and v0.2 revision. A
  policy rule or rate change alone
  does not change `schema_version`.
- `policy_version` identifies a reviewed revision of one policy's content.
  It was `null` in the Task 5 scaffolds. WFF received its first version
  (`"0.1.0"`) at Task 10 approval; Accommodation Supplement remains `null`
  until its Task 22 gate. Once assigned, it changes when that policy's
  approved specification changes, even if the schema shape stays the same.
- `reference_period` describes the period the policy record is intended to
  model. Each parameter value has its own `effective_from` and optional
  exclusive `effective_to` date. These dates are legal applicability data,
  not versions. The source catalogue's `as_of` date is an inventory date,
  not a policy or schema version.

A loader must recognise the declared schema version before interpreting
policy content and must not treat a scaffold or `null` policy version as an
approved executable specification. Task 7 recommends Pydantic validation;
this document does not install it.

## People, units, and time

A person has a stable identifier within a scenario. An assessment unit is a
policy-specific set of relationships over a bounded period, not a synonym for
an address or an undifferentiated household. Membership has `person_id`,
`role`, `from`, and `to` (exclusive), allowing relationships and care to change
within a tax year or benefit week. A person may participate in more than one
relevant care arrangement; the schema must not enforce one universal family.
The policy input contract names the roles it accepts, but scenario instances
and derived facts are outside `policy.yaml`.

- **WFF:** claimant, partner during a dated relationship, and dependent child
  with care intervals and component-specific care shares. Annual family-scheme
  income aggregates the appropriate people and adjustments for the relevant
  period; wages alone are not a substitute. Earner, full-time-earner, benefit,
  birth-cohort, and paid-parental-leave facts stay distinct (WFF-01/02/04/05/06/07).
- **AS:** claimant and partner form the benefit assessment unit; joint tenants
  and accommodation-cost shares are separate arrangement facts. Tenure, benefit
  class, cash assets, weekly income, qualifying costs, and verified Area 1-4
  must be represented independently. A suburb string is not an area lookup
  (AS-01/02/05/06/08/09).

Each fact declares whether it belongs to a person, assessment unit, or
accommodation arrangement, and whether its period is a date, week, entitlement
interval, or tax year. Do not combine WFF family-scheme income and AS chargeable
income into a generic `family_income`: their inclusions and payment-channel
exceptions differ (WFF-02; AS-07/10). Cross-policy transfers require an
explicitly sourced mapping, not shared field names.

## Effective-dated parameters

Each parameter declares `id`, `value_type`, `unit`, and `values`. A value entry
has `effective_from`, optional exclusive `effective_to`, `value`, `source_id`,
`locator`, and `review_status`. Currency must state NZD and its annual or
weekly basis; rates must state their dimension (for example, fraction of
income), and area/household tables need explicit keys. Intervals for the same
key cannot overlap. No matching interval means unsupported, not the newest
value and not zero.

Legal commencement, the observed date of an agency table, and the date a
source was retrieved are separate facts. Future law stays in a future
effective interval. In particular, WFF's possible in-work tax credit reversal
requires a dated legal instrument check for each modelled interval, while AS's
2027 homeowner
change must not affect September 2026 cases. The Task 2 maps' listed figures
are observations, not approved parameter values or benchmark expectations.

## Schema as implemented (Task 27.2, 24 September 2026)

This section records what `src/poltika/semantics/schemas/policy_spec.py`
and the two approved `policy.yaml` files actually accept today. The design
text above predates Tasks 11-26. Where they differ, the code and this
section are authoritative, and each change below traces to the task that
made it.

**Schema version stays `"0.1"`.** Task 25 stress-tested this schema against
Accommodation Supplement and found no `PolicySpec`/`ParameterSpec` revision
needed. Pete decided Task 27.1(a) on 24 September 2026: no v0.2 bump and no
migration, and the v0.1 Definition of Done now reads "schema v0.1". The
Task 7 response below still mentions a "Task 26 `v0.2` bump and Task 27 WFF
migration". That was the plan at the time and neither happened. The loader
accepts only `"0.1"` (`SUPPORTED_SCHEMA_VERSIONS`).

**Parameter `value_type` and `unit`** are closed enums, not free text (Task
11, per the Task 7 response). Each `value_type` admits only its own units:

| `value_type` | Allowed `unit` | Added by |
| --- | --- | --- |
| `money` | `NZD_per_tax_year`, `NZD_per_tax_year_after_tax`, `NZD_per_child_per_tax_year` | Task 11 (WFF) |
| `money` | `NZD` (a stock amount, e.g. an asset ceiling), `NZD_per_week` | Task 23 (AS) |
| `fraction` | `NZD_per_complete_NZD_above_threshold` (carries WFF's complete-dollar flooring) | Task 11 (WFF) |
| `fraction` | `fraction` (a plain rate; any rounding is calculator logic, per DEC-001) | Task 23 (AS) |

The Task 23 units were a narrow, additive extension that Pete approved on 23
September 2026. WFF's `policy.yaml` validates unchanged. Adding a unit
means adding an enum member and its row in `_VALID_UNITS_BY_VALUE_TYPE`; the
field is never widened back to `str`.

**Parameter-id convention for keyed tables.** The first draft said area and
household tables "need explicit keys". Tasks 23-26 implemented this with a
compound parameter-id convention, not a new schema field:
`<parameter>_<key>_<key>...`, where each key is a closed enum value the
calculator derives from verified facts. Each combination is its own
parameter with its own effective intervals and `source_id`. A missing
combination resolves to `needs_review`, never a default.

| Pattern | Keys | Task |
| --- | --- | --- |
| `area_cap_<household_category>_<area>` | household category × `area1`-`area4` | 23 |
| `as_base_rate_<claimant_category>_<household_category>` | claimant category × household category | 25/26 |
| `asset_ceiling_{relationship_or_dependent_children,other}`, `asset_imputation_threshold_{...}` | a fixed two-way split, spelled out in the id | 23 |

The AS household categories are `single_no_dependent_children`,
`no_dependent_children_couple_or_sole_parent_one_child`, and
`with_dependent_children` (Schedule 4 Part 7 cl 1-3). The claimant categories
are those of AS's `claimant_category` input. `as_base_rate_*` values are not
yet declared in `policy.yaml`; populating them is Task 26a.

**`assessment.membership_period`** is stored in the schema's untyped
`assessment` mapping. Values in use are `tax_year` (WFF) and
`assessment_week` (AS). Task 25 confirmed the untyped field is sufficient for
two policies. Typing it is a candidate for a later schema version once a
third policy needs it, not before.

## Dataset provenance boundary

The policy-source catalogue and statistical dataset manifest are different
records. If a policy input is supplied by a canonical statistical variable,
the input references that canonical variable ID; it does not point at a raw
file, CSV column, or live API. The raw-snapshot manifest must carry the eleven
Data Acquisition Doctrine fields: source organisation, dataset/series, source
URL or identifier, retrieval date, observation/reference period, units,
geography/population, retrieval method, raw snapshot/version,
transformation/version, and canonical variable mapping. For v0.1 the retrieval
method is `manual_download`.

At acquisition, the snapshot identity and source metadata must be known. If
transformation version or canonical mapping has not yet been established,
record it explicitly as pending; do not invent it. Both must be resolved
before the snapshot is registered as a Task 10b/15 regression fixture or used
by a calculator. Corrections create a new immutable snapshot version. This
keeps the provenance chain required by `BUILD_PLAN.md` without forcing Task
10b transformation work into Task 10a acquisition.

## Task 7 review questions

1. Can the existing repo boundaries represent dated membership and
   accommodation arrangements without duplicating scenario facts in
   `policy.yaml`?
2. Which exact file and validation mechanism should enforce source-ID
   resolution, parameter interval uniqueness, units, and unsupported inputs?
3. Can the loader enforce the distinct schema, policy-revision, and legal-date
   axes above without accepting a scaffold as an executable specification?
4. What is the smallest practical way to link a canonical variable to its
   snapshot manifest while keeping source-specific formats out of the
   calculator?

These are feasibility questions, not permission to change frozen doctrine or
to implement the Task 10/22 policy rules before their review gates.

## Task 7 review response (Claude Code, 2026-09-21)

**Verdict: feasible as drafted. Proceed to Task 5/6.** No ARCHITECTURE_ISSUE,
SPEC_ERROR, or doctrine conflict found. Every field traces to a WFF/AS
provision already in `specification.md`, or is explicitly marked as a design
inference — none silently assert a rule the source maps don't support. The
entity split (person vs. assessment unit), the explicit unsupported/
needs_review requirement, and the dataset-provenance boundary all match
doctrine (Data Acquisition Doctrine's 11 fields; `doctrine/deterministic_core.md`'s
canonical-variable-only rule; the G4/G1 findings in
`docs/research/nz_policy_engines_review.md`).

1. **Dated membership without duplicating scenario facts:** yes. `policy.yaml`
   should hold the input *contract* only (role names, period shape); actual
   scenario instances belong in `scenarios/definitions/` (not yet created).
   One real ordering dependency, not a blocker: `semantics/` doesn't exist yet,
   so nothing yet defines what a "canonical Poltika variable ID" looks like
   structurally. Resolve this when the `canonical-data-model` skill and
   `src/poltika/semantics/` are built (see `.claude/skills/poltika-skill-roadmap`),
   not before Task 5.

2. **Validation mechanism:** Pydantic models under `src/poltika/semantics/schemas/`
   (already the settled stack per `ARCHITECTURE.md`), with custom validators
   for source-ID resolution against `sources.yaml`, non-overlapping parameter
   intervals, unit typing (`Literal`/enum, not free text), and a required
   unsupported/needs_review condition on every input. Run as a pytest suite
   under `tests/unit/`, CI-gated alongside Task 9's statutory-value
   protection — recommend this become explicit scope of Task 9 rather than a
   new task.

3. **Loader enforcement of the three version axes:** yes, feasible with the
   same mechanism as (2), no separate subsystem. Two checks, run in order:
   (a) a version gate — reject any `schema_version` outside an explicitly
   supported set before interpreting anything else; (b) an approval gate —
   require `status == "approved"` (not merely `policy_version` being
   non-null) before treating content as executable. Gating on `status`
   rather than on "is `policy_version` present" matters: it stops a future
   scaffold from accidentally looking approved just because someone fills in
   a version number without going through the Task 10/22 review gate. Task
   26's `v0.2` bump and Task 27's WFF migration should each get a one-line
   ADR, matching the existing ADR pattern — no separate versioning subsystem
   needed (would be the speculative abstraction Architecture Doctrine warns
   against).

4. **Canonical variable ↔ snapshot manifest link:** the smallest mechanism is
   already implied by `REPOSITORY_STRUCTURE.md`'s target tree — no new
   design required. A canonical variable ID (dotted namespace, e.g.
   `demographics.population.total`) is defined once in
   `data/metadata/variables/<canonical_id>.yaml`, which points at the
   specific `data/metadata/datasets/<snapshot_id>.yaml` manifest
   (`.claude/skills/provenance`'s 11-field template) satisfying it. The
   calculator/parameter loader reads only the canonical variable ID; the
   manifest and snapshot never cross the `data/` → `semantics/` boundary.
   Make this explicit when Task 5 establishes file structure.

**Note, not a finding:** `.agents/skills/` (policy-spec-draft,
clean-room-boundary, nz-primary-source-check) appeared alongside this draft —
a separate, GPT-side skill convention, distinct from `.claude/skills/`. No
conflict: their scope matches this project's doctrine and they explicitly
hand off Task 7 to Claude Code (see `policy-spec-draft`, step 5). Flagging
only so it isn't mistaken for an untracked/unexplained directory later.
