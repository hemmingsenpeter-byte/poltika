# v0.2 Tasks 3.1-3.2: calibration tables for the synthetic population

- **Date:** 27 September 2026
- **By:** Claude Code, at Pete's request, from a local machine that can reach
  Stats NZ and MSD (the cloud session could not). `BUILD_PLAN_v0_2.md`
  assigns 3.1 to GPT/Codex and 3.2 to Pete or GPT/Codex, so this is an
  **author record awaiting independent review**, not a reviewed one.
- **Snapshots added (Task 3.2):** two raw snapshots with manifests under
  `data/`. Both pass `DatasetRegistry`, and their canonical variables are in
  `data/metadata/variables/dictionary.yaml`.
- **Not done here:** the transformations that read these snapshots
  (`stats_nz_hes_tables`, `msd_as_area_definitions`, Task 3.3) and a real
  `SyntheticSpec` under `data/metadata/populations/`. No share or band has
  been computed, and no number enters a test.

## Snapshots

| Dataset id | Publication | File (exactly as published) | Vintage | Retrieved |
| --- | --- | --- | --- | --- |
| `stats_nz_household_income_housing_costs` | Stats NZ, *Household income and housing-cost statistics: Year ended June 2025* | `household-income-and-housing-cost-statistics-year-ended-june-2025-corrected.ZIP`: Tables 1-13 as CSV, plus `inc-csv-codes.xlsx` defining every code | Year ended June 2025, corrected release (archive files dated 26 May 2026) | 27 Sep 2026 |
| `msd_as_area_definitions` | MSD, *Map*, Accommodation Supplement tables: *Definitions of areas* | The HTML page | Areas used from 1 April 2018; the page shows no last-updated date | 27 Sep 2026 |

The Stats NZ release also publishes the same tables as one `.xlsx`. The CSV
archive was taken because it carries the code definitions and is
machine-readable. Both files are labelled "corrected".

## Task 3.1: which table feeds which `SyntheticSpec` input

| Spec input | Source table | Coverage |
| --- | --- | --- |
| `households`, `represents` (total households) | HES Table 10, `D003A` "Total number of households in thousands (000)", 2019-2025 | Covered |
| `household_type` | HES Table 5, `H003A-H003J` household composition | Covered, **with a unit question**: the codes workbook says Table 5's Estimate is "Number of people in thousands". Confirm households or people before use |
| `children_count` | HES Table 5, `H003B-H003D` (couple with one, two, three or more dependent children) and `H003F` (one parent with dependent children) | **Partial**: couples only by number of children; one-parent households are not split by number of children |
| `best_start_cohort` (children's ages) | HES Table 7 has only a 0-14 person age group | **Gap**: no table here gives children under 3 by household. Needs a Census 2023 or births table |
| `gross_income` bands | HES Table 3, mean and median household gross income; Table 5 quintile boundaries are for *equivalised disposable* income | **Gap**: no gross-income band distribution in this release. Needs a HES gross-income-band table (for example from Aotearoa Data Explorer) |
| `tenure` | HES Table 5, `H004A-H006D`; Table 10 owned vs not owned counts | Covered (Table 5 has the same unit question) |
| `weekly_housing_cost` bands | HES Tables 8-9, average weekly expenditure by housing cost type | **Partial**: averages only, no band distribution |
| `region` | HES Table 5, `H007A-H007L` | Covered (unit question; two pairs of regions are combined) |
| `as_area` | MSD Definitions of areas (Statistical Area Unit 2017 to Area 1-4) | **Partial**: gives the classification, not household counts. Shares need household counts by Statistical Area Unit 2017 (Census 2018 area-unit tables) |
| `claimant_category` | None | **Gap**: needs MSD benefit fact sheets (Jobseeker, Sole Parent Support, Supported Living Payment counts) |
| `cash_assets` bands | None | **Gap**: no published household cash-asset distribution was identified |

## Decisions and questions for review

1. **Table 5's unit.** People or households? It decides whether Table 5 can
   give household shares directly.
2. **Gross income bands.** Which HES table, and which vintage, to acquire.
3. **Children's ages, AS area shares, claimant categories and cash assets.**
   Name the publication for each, or record that the synthetic population
   keeps an asserted assumption for it (the generator already requires every
   such input to be stated and labelled).
4. **MSD page vintage.** The page gives no date beyond "from 1 April 2018",
   so the manifest's observation period ends on the retrieval date.
5. **Dictionary frequency for the area classification.** The schema has no
   "not applicable" frequency; `annual` was used and should be reviewed.
