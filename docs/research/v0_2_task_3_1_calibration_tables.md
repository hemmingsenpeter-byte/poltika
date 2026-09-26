# v0.2 Tasks 3.1-3.2: calibration tables for the synthetic population

- **Date:** 27 September 2026
- **By:** Claude Code, at Pete's request, from a local machine that can reach
  Stats NZ (the cloud session could not). `BUILD_PLAN_v0_2.md` assigns 3.1 to
  GPT/Codex and 3.2 to Pete or GPT/Codex, so this is an **author record
  awaiting independent review**.
- **What landed:** five raw snapshots with manifests, the four transformations
  that read them (`src/poltika/data/transforms/`), 54 canonical variables in
  `data/metadata/variables/dictionary.yaml`, and
  `tests/unit/data/test_real_snapshots.py`, which checks published figures
  through `DataContext`.
- **Not here:** the population spec derived from these variables (Task 3.3's
  next step).

## Snapshots (all Stats NZ, retrieved 27 September 2026, exactly as published)

| Dataset id | Publication | Vintage | Transformation |
| --- | --- | --- | --- |
| `stats_nz_household_income_housing_costs` v1 | *Household income and housing-cost statistics*, CSV zip (Tables 1-13, `inc-csv-codes.xlsx`) | Year ended June 2025, corrected | `stats_nz_hes_tables` |
| `stats_nz_census_2018_totals_by_topic_national` v1 | *2018 Census totals by topic: national highlights*, CSV zip | Census night 6 March 2018 | `stats_nz_census_2018_national` |
| `stats_nz_household_net_worth` v1 | *Household net worth statistics*, CSV | Year ended June 2024 | `stats_nz_household_net_worth` |
| `stats_nz_births_and_deaths_release` v1, v2 | *Births and deaths* release pages (key facts); the counts are published only in the text | Years ended March 2025 and 2026 | `stats_nz_births_release` |

Only the rows the population needs are transformed: Table 5 composition and
regions, Table 10 total households, Table 3 gross income, Table 9 rent; the
2018 weekly rent bands and tenure; net worth currency and deposits; live
births registered.

## Findings

1. **HES Table 5 counts people, not households.** Its total (H001A) is
   5,205.2 thousand, the population, while Table 10 gives 2,025.4 thousand
   households. Household shares by composition therefore need household
   sizes: exact for one-person (1), couple-only (2) and couples with one or
   two dependent children (3, 4), but not for "three or more" children or
   one-parent households.
2. **Table 3's CSV codes differ from the workbook** (`M0001`/`1001A` in the
   CSV, `M001`/`I001A` in `inc-csv-codes.xlsx`). The transformation follows
   the CSV.
3. **Births are registrations**, not births by date of birth, and are
   published only in the release text.
4. **MSD's Accommodation Supplement Definitions of areas** (already the
   `as-msd-areas` policy source) classifies Statistical Area Units 2017 but
   carries no counts, so it was not taken as a dataset.
5. **Aotearoa Data Explorer needs a registered API key**, so 2023 Census
   tables (household composition counts, households by area) were not
   acquired.

## Task 3.1: which variable feeds which `SyntheticSpec` input

| Spec input | Variables | Coverage |
| --- | --- | --- |
| `households` / `represents` | `household.count.total`, `household.people.*` | Sourced, with the household-size derivation in finding 1 |
| `household_type` | `household.people.{one_person_household, couple_only, couple_*_dependent_child*, one_parent_dependent_children}` | Sourced, with finding 1's size assumptions for two groups |
| `children_count` | `household.people.couple_*_dependent_child*` | Couples only; one-parent households assumed to share the couples' distribution |
| `best_start_cohort` | `population.live_births_registered` (years ended March 2024-2026) | Sourced, as registrations relative to the derived dependent-child count |
| `gross_income` | `household.gross_income.{median,mean}` | Median and mean only; no band distribution was found |
| `tenure` | `household.tenure_2018.*` | Sourced (2018 household counts) |
| `weekly_housing_cost` | `household.renting.weekly_rent_band.*`, `household.rent.weekly_mean_paying_households` | 2018 rent bands, which can be moved to 2025 by the HES mean-rent ratio; the top band is open |
| `region` | `household.people.region.*` | People, not households |
| `cash_assets` | `household.currency_and_deposits.{median,mean}` | Median and mean only |
| `as_area` | None | **Gap**: no household counts by Accommodation Supplement area |
| `claimant_category` | None | **Gap**; the population's asserted facts assume in-work, non-beneficiary households |

## For review

- The derivation choices above (household sizes, one-parent child counts,
  bands built from a median and mean, the rent adjustment, the open top rent
  band, and people-based region shares) belong to the population spec and
  must be stated there as methodology.
- The AS area and claimant category gaps: either name a publication, or keep
  them as stated assumptions in the spec.
