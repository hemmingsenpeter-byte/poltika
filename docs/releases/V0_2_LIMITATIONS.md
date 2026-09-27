# What Poltika v0.2 does not do

v0.2 Task 10.3. v0.2 adds static population microsimulation on top of
v0.1's two policies. Everything in `V0_1_LIMITATIONS.md` still applies to
each household. This page lists what the population layer adds, and what
it doesn't do.

**Every v0.2 population result is for the synthetic development
population, not an estimate for New Zealand.** The label is on every
API response, page tab and explanation.

## The population

The population is `data/metadata/populations/nz_synthetic_development.v1.yaml`.
`V0_2_POPULATION_METHODOLOGY.md` states every rule (D1-D7) and assumption
(A1-A11) behind it. Its main limits:

- **Independent marginals.** Household type, income, tenure, housing cost,
  region and area are drawn independently, so the population has none of
  the real correlations (for example between income and housing cost).
- **Income is coarse.** Gross household income is two uniform bands that
  reproduce HES 2025's all-household median and mean (D4). The same bands
  apply to every household type (A11). Family tax credit cost depends on
  where families sit relative to the abatement threshold, so it is
  sensitive to this.
- **Everyone is an in-work non-beneficiary** (A6). No beneficiary
  household, and no main-benefit interaction, is exercised.
- **Accommodation Supplement areas are assumed** equal quarters (A5).
  Area results say nothing about New Zealand's geography.
- **Four household types only.** Other kinds (multi-family, other
  one-family, one parent with only non-dependent children) are not
  represented. The population represents 1.45 million households, not
  HES's 2.03 million.
- **Rent is 2018's shape.** The 2018 Census rent bands are moved to 2025
  by one ratio (D6).
- **All asserted facts are `verified`.** Every one of the 16 eligibility
  and exclusion facts is set to its supported value, so the population
  contains no `needs_review` household from a missing fact.

## Results

- **Static, full take-up entitlement.** No behavioural response, no
  take-up rate, no timing. A cost figure is the change in entitlement if
  every eligible household received it.
- **The 2026-27 in-work tax credit is `needs_review`** for every in-scope
  household (its rate-status contract), and so is minimum family tax
  credit (no net family scheme income is generated). Neither is ever
  counted as zero, and there is no total WFF figure.
- **No annual Accommodation Supplement figure.** WFF results are per tax
  year and AS results per week, and they are never added (D8).
- **Withdrawal rates are per policy** (WFF on family scheme income, AS on
  weekly income). There is no combined effective marginal tax rate (D9);
  that is v0.3 Phase 5.
- **Deciles rank by gross household income** from the population record
  (D3), not an equivalised income.
- **Runs are kept in memory** by the API process. There is no durable run
  storage.

## Not yet independently checked

- The Stats NZ snapshots and canonical variables (#111), and the
  population derivation (#113), await GPT/Codex review. They are open rows
  in `review_packets/review_queue.md`, so the v0.2 release gate's review
  row skips.
- Task 2.3 (the population adapter's mapping), Task 9.3 (hand-calculated
  population cases) and Task 9.4 (cross-validation against published
  programme figures) are GPT/Codex's and still open.
