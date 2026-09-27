# v0.2 Task 2.3: population-to-engine mapping (author check)

- **Date:** 27 September 2026
- **By:** Claude Code. **Author check, not the independent review.**
  `BUILD_PLAN_v0_2.md` assigns 2.3 to GPT/Codex; this records what the
  author found so that review can start from it.
- **Code checked:** `scenarios/microsim/synthetic.py` (`_record`, how a
  synthetic household becomes a `ScenarioRecord`) and
  `scenarios/population.py` (`scenario_record`, the adapter every
  population household goes through).
- **Against:** the input definitions in
  `policy_specs/working_for_families/policy.yaml` and
  `policy_specs/accommodation_supplement/policy.yaml`.

## Mapping

| Concept | WFF input | AS input | Synthetic mapping | Assessment |
| --- | --- | --- | --- | --- |
| Family | family scheme (claimant, partner, dependent children) | claimant, partner | one family per household | Matches the v0.2 schema decision (one family per household). Other household kinds are not represented (methodology D1) |
| Partner | `partner_status` partnered/single | `partner_status` ordinary_couple/single | couple types → partnered and ordinary couple | Consistent, so the combined runner's partner check never fires. Joint tenancy and community spouse are never generated |
| Dependent child | `children` (whole-year qualification, Best Start cohort) | `dependent_children_count` | the same count for both | The policies define a dependent child differently; the generator makes every child both. Validation already treats a mismatch as a warning, not an error |
| Family scheme income | `family_scheme_income` per person, verified | not used | gross household income, split by `partner_income_share` | A synthetic mapping, stated as a generator rule. Real family scheme income (subpart MB) differs from gross income; the combined amount is exactly the gross |
| Chargeable income | not used | `weekly_income` (claimant and partner, before asset imputation) | gross / 52 (A8) | A synthetic mapping between two income definitions (D9). It excludes WFF credits, consistent with DEC-003 |
| Housing costs | not used | `weekly_accommodation_costs` (plain case, cl 7) | a draw from the housing band distribution | Right concept for renters. Homeowners also draw a cost (A10), unused because homeowner tenure is unsupported |
| Assets | not used | `cash_assets`, exempt-asset check | a draw from the cash-asset bands; exemption `verified` | As stated (D4) |

## Findings (proposed classifications)

1. **Eldest dependent child under 16 was asserted without being named
   (proposed SPEC_ERROR, low; fixed in this PR).** `eldest_dependent_child_under_16`
   is `verified` for every household, though children's ages are not
   generated beyond the Best Start cohort. It selects AS's parent rate rows.
   It is now assumption **A12** in the spec's `sources` and the methodology
   page. No result changes.
2. **One count for two definitions of dependent child (observation).** Fine
   for a synthetic population with no orphan's or unsupported child's
   benefit, but a real-data adapter (D2) must map the two separately.
3. **Two calculable Best Start children in one household (observation).**
   Cohorts are drawn per child, so a household can get two children in the
   calculable cohort. Best Start is then `unsupported` (the v0.1 single-child
   branch), and the coverage report counts it so.

Nothing here changes a calculated amount.
