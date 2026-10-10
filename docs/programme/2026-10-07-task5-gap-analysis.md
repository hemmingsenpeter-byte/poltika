# Phase B Task 5 gap analysis (7 October 2026)

Task 5 is complete when "units, periods, people/families, income facts,
identifiers and required geography support current policies without hidden
conversions" (`BUILD_PLAN_PROGRAMME.md`). The current policies are WFF 2026-27
(policy 0.1.0) and the Accommodation Supplement (policy 0.1.1). This record
assesses `main` after #181. It assesses evidence and claims no gate.

| Requirement | Existing implementation | Evidence | Actual gap | Blocks Task 6? | Classification |
| --- | --- | --- | --- | --- | --- |
| Units | `semantics/units.py` (#161, #169): 15 units with dimension, scale, nominal price basis and NZD currency. Exact rescaling only; `convert` refuses every price-basis change. Policy specs separately declare `ParameterUnit` and input units in `semantics/schemas/policy_spec.py`, such as `NZD_per_week` and `NZD_per_tax_year`. | `tests/unit/semantics/test_units.py`; the policy-spec schema checks each unit against its value type | The two vocabularies are not linked. No test shows that every unit a policy declares decomposes into a registered unit, period and per-entity qualifier. `semantics.units` is used only by its own tests and `variables.py`. | No, but Tasks 6–8 add units, so the link should exist first | Genuinely missing (small) |
| Periods | `semantics/periods.py` (#166): `Period` with half-open dates; an assessment week is exactly 7 days. Only the containment relation between the AS week and the WFF year is registered. `convert_amount` refuses every annual or weekly value conversion (v0.2 D8). | `tests/unit/semantics/test_periods.py`; the engines keep WFF annual and AS weekly results separate | Policy units encode the period inside a string such as `NZD_per_week`, not as a `PeriodType`. The patch for the units row closes this too. | No | Sufficient, once the units patch lands |
| People and families | Per-policy facts: `WffScenario` (`children`, `partner_status`) and `AsScenario` (`partner_status`, `dependent_children_count`, `claimant_category`). `semantics/entities.py` (#171) has the vocabulary (person, family, household and others). `PopulationDataset` has persons with a role and an age. | Engine spec, benchmark and golden tests; `test_entities.py` | No shared person or family structure. That structure is the Task 6 deliverable (ADR-0017), not a Task 5 prerequisite. | n/a (Task 6) | Sufficient for Phase B |
| Income facts | WFF `family_scheme_income` (`VerifiedIncome`, annual, with the partnered-income verification boundary); `net_family_scheme_income` (after tax, attested); AS `weekly_income`. An unknown value is `needs_review`, never zero. | Spec and golden tests; CLAUDE.md "a missing fact is never zero" | No shared income-fact type or dated spells. ADR-0017 D6 puts spells in Task 6. A single income path across policies is Q10 (D8/D9), held for Pete. | n/a (Task 6 / Q10) | Sufficient for Phase B; spells deferred to Task 6 |
| Identifiers | Household scheme validated, with a trailing newline refused since #181 (`\Z` under `re.match`). `crown` and `new_zealand` are fixed. Person, family, firm and sector schemes are registered as unassigned with a reason and refuse to validate. | `test_entities.py`, including the #181 trailing-newline cases | Person and family ids are unassigned because no repository rule defines them. Task 6 defines them (ADR-0017 holds families "by person id"). The current policies take no person or child id. | No; Task 6 registers them | Deferred, non-blocking |
| Required geography | AS `Area` enum (area1–area4): a verified Statistical Area Unit resolved to an area. It is never inferred from a place name, and the enum has no default member. WFF needs no geography. Population `region` is a plain string used only for grouping. | AS spec and golden tests; `accommodation_supplement.py` `Area` docstring | No geography type (old Task 2.5). No current policy needs more than the AS area. | No | Deferred, non-blocking |

## Recommendation

Task 5 can close with one bounded patch that changes no calculated amount.
The patch maps each `ParameterUnit` and policy input unit to a registered
`semantics.units` unit, a `PeriodType` (or none) and a per-entity qualifier,
for example `NZD_per_child_per_tax_year` to `nzd`, `tax_year`, per child. A test
then loads every `policy_specs/*/policy.yaml` and fails on any unit without a
mapping. The patch adds no conversion, no new unit without a source, and no
geography or quantity type. Once it merges, Task 5 is Done and Task 6 starts.
