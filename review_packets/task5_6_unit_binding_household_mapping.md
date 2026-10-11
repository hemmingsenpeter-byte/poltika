# Review Packet: Task 5 unit binding and Task 6 household mappings — 2026-10-11

## Review inputs

- PR/diff: `origin/main...c807ea2` on `feat/task5-unit-binding-20261011` (base `b19e764`). Author: Claude Code. Cross-model reviewer: GPT/Codex.
- Primary sources and source-map paths: none new. No statutory value is added or changed. Each mapping relies on `policy_specs/working_for_families/` and `policy_specs/accommodation_supplement/` (`specification.md`, `policy.yaml`, `sources.yaml`, `decisions/`).
- Specification paths and clauses: listed per mapping below.
- Test commands: `uv run --extra dev pytest -q tests/unit/semantics tests/unit/scenarios/test_household_roundtrip.py` (190 passed at `c807ea2`); `ruff check src tests`; `mypy --strict src`.
- Effect on amounts: none. Round-trip tests compare scenario, canonical result payload and result id for the golden households, the interaction cases and the WFF and AS spec cases and benchmarks.

## Independent review

Complete this section before reading the author response.

### Independently derived expected behaviour

(reviewer derives from sources and spec)

### Discrepancies found

| Discrepancy | Classification | Notes |
|---|---|---|
| | CODE_ERROR / TEST_ERROR / SPEC_ERROR / SOURCE_CONFLICT / INTERPRETATION_AMBIGUITY / MISSING_SOURCE / ARCHITECTURE_ISSUE / REVIEWER_ERROR | |

## Author response

Written after the author's own preflight. The author wrote the rationale, so it is not independent.

### A. Unit bindings (`src/poltika/semantics/unit_binding.py`)

| policy.yaml unit | Registered unit | PeriodType | Qualifier | Relies on |
|---|---|---|---|---|
| `NZD_per_tax_year` | `nzd` | `tax_year` | none | WFF `policy.yaml` `membership_period: tax_year`; `periods.py` TAX_YEAR |
| `NZD_per_tax_year_after_tax` | `nzd` | `tax_year` | `after_tax` | WFF-05 (ME 3 attested net income) |
| `NZD_per_child_per_tax_year` | `nzd` | `tax_year` | per child (a role) | WFF-03, WFF-06 |
| `NZD_per_complete_NZD_above_threshold` | `ratio` | none | per complete NZD above threshold | WFF abatement parameters; flooring is calculator logic (DEC-001 for AS) |
| `fraction` | `ratio` | none | none | AS r 18(2) rate, DEC-001 |
| `NZD_per_week` | `nzd` | `assessment_week` | none | AS `membership_period: assessment_week`; the explicit 7-day week (policy 0.1.1) |
| `NZD` | `nzd` | UNRESOLVED | none | AS asset ceilings, imputation thresholds and step size (`policy.yaml` 230-258); `cash_assets` input |

Input `period:` values: `full_tax_year` and `tax_year` map to `tax_year`; `assessment_week` maps to `assessment_week`; `day` maps to `point_in_time`.

Enforced by `tests/unit/semantics/test_unit_binding.py`. An unregistered unit, an unregistered period, a parameter or input whose unit period differs from the policy's `membership_period`, or a unit-bearing input with no period all fail. A spec directory with no `policy.yaml` fails unless it is in an explicit not-yet-executable set. No conversion is added: `periods.convert_amount`, `units.convert` and `units.rescale` still refuse.

### B. Household to WFF mapping (`to_wff`, `scenarios/household_mappings.py`)

| WffScenario field | Taken from the household | Relies on |
|---|---|---|
| `children[*]` (`qualifies_whole_year`, `best_start_cohort`, `best_start_no_disqualifying_payment`) | each dependent child's `ChildFacts`; a child with no facts is unknown | WFF-01, WFF-06 (MC 6(c)) |
| `partner_status` | the family's partner status; unknown stays unknown | WFF-01, WFF-02 |
| `family_scheme_income` (`VerifiedIncome`) | claimant and partner spells of basis `wff_family_scheme` tiling the tax year; the partner alone is refused | WFF-02 (subpart MB) |
| `net_family_scheme_income` and `..._me3_attested` | claimant spell of basis `wff_net_family_scheme_me3_attested` or `net_of_tax`; both together is refused | WFF-05 (ME 3) |
| nine asserted gates (`household_eligibility`, `extra_instalment_status`, `in_work_eligibility`, `ftc_iwtc_protected_or_direct_abatement`, `mc6a_veterans_payment`, `mc6b_disqualifying_payment`, `minimum_family_full_time_earner_weeks`, `best_start_no_shared_care`, `best_start_protected_credit`) | household-level asserted facts `wff.<name>`; not derived from spells | WFF-01, 04, 05, 06, 07, 08, 09 |

### C. Household to AS mapping (`to_as`)

| AsScenario field | Taken from the household | Relies on |
|---|---|---|
| `claimant_category` | the claimant's benefit spell covering the whole assessment week; two different benefits is refused | AS-08 |
| `partner_status` | single from the family; a partnered family needs the recorded arrangement (ordinary, joint tenancy, community partner), else unverified | AS-09; Schedule 4 Part 7 cl 1-3 and 6A |
| `dependent_children_count` | verified only if the child list is complete and each child's `as_dependent_child` is verified or excluded | AS-03 (cl 7 costs formula input); definition source NOT checked by the author |
| `tenure_type`, `weekly_accommodation_costs`, `statistical_area_unit`, `cash_assets` | `Housing`; `None` stays unverified | AS-01 to AS-05 |
| `weekly_income` | claimant spell of basis `as_chargeable_weekly` tiling the week | AS-07 (r 18), DEC-001 |
| four asserted gates | household-level asserted facts `as.<name>` | AS-02, AS-06, AS-07 |

### D. Deliberate refusals

- A spell extending past the policy period gives `HOUSEHOLD_SPELL_PERIOD_MISMATCH` (`needs_review`) naming Q10 and v0.2 D8/D9. No spell is ever scaled, and a gap is unknown, never zero.
- `to_wff` gives `HOUSEHOLD_CHILD_LIST_INCOMPLETE` (`needs_review`, missing fact `wff_children_complete`) unless the family's child list is asserted complete under the WFF definition, because WFF reads its `children` list as the complete list (an empty list is `WFF_NO_DEPENDENT_CHILD`). The adapter from the existing WFF request marks that list complete, which is how the engine already reads it. Completeness is held per definition (`wff_children_complete`, `as_children_complete`), so an AS-only household's AS count never stands in for a WFF list. Added after the `poltika-reviewer` pass (two P2s). Reviewer: confirm this reading of the WFF `children` input.
- Multi-family household: `UnsupportedHousehold` (ADR-0017 D6 answer 2).
- Adapter refusals (`AdapterRefused`): WFF and AS asserting partner status differently; AS count above WFF's child list; a partner income on a non-partnered family; an ME 3 attestation without a net figure. The one named case is `interaction:disagreement_keeps_existing_unsupported_components`; the old pairwise path still handles it.
- Pairwise checks in `scenarios/combined.py` are not retired (Task 1.4 not started; see escalation 4).

### E. Unresolved or escalated

1. The period of an AS stock amount (`NZD`): unresolved, never guessed. Does a stock belong to a point in time or to the assessment week?
2. `ChildFacts` holds both the WFF and AS dependent-child definitions; the AS definition's source is not confirmed by the author.
3. Person and family identifier schemes are still unassigned in `semantics/entities.py`. The household uses synthetic ids (`claimant`, `partner`, `child_N`).
4. Retiring the pairwise checks needs a main-benefit period rule (Q10-linked).
5. `NZD_per_complete_NZD_above_threshold` and `fraction` are bound to `ratio` with no period. That is the author's reading and needs confirming.

### What the reviewer must confirm

1. Each row of A: unit, period and qualifier are supported by the cited spec (not by memory). Binding 5 above in particular.
2. Each row of B and C: the household field really is what the cited rule needs. Check `dependent_children_count`, `partner_status` and the AS category from spells.
3. No path turns an unknown into a number, and no spell is scaled (probe `amount_in_period` edges: exact tiling, gap, straddle, verified zero).
4. The round trip proves bit-identity: scenario, result payload and result id equal for every golden household, interaction case and spec case or benchmark, with exactly one listed refusal.
5. The refusals in D are the right ones and none hides a calculated result.
6. Persons or ids: whether synthetic ids need a scheme before use.

## Resolution

(pending)

## Author preflight (same-model, not independent) at `c807ea2`

- `git diff --check origin/main...HEAD`: clean.
- Probed: a tiling of two half-year spells sums without scaling; a verified zero spell gives 0; a gap gives `None`; a straddling spell gives `None` and a Q10 refusal; basis filter stops WFF-year spells being flagged against the AS week (found and fixed in `c807ea2`).
- Not probed: the sources behind the AS cl 7 dependent-child wording (flagged above); tests/regression and the installed-artifact and code-replay markers (the independent re-check runs regression).
- Findings open: none P1 or P2 known.
