# What Poltika v0.2 does not do

v0.2 Task 10.3. v0.2 adds static population microsimulation over the v0.1
engines, so everything in `V0_1_LIMITATIONS.md` still applies to every
household. This page lists what v0.2 adds on top.

## The population is synthetic

- **Not an estimate for New Zealand.** `nz_synthetic_development` v1 is
  built from published aggregate tables, not unit records. Every output
  carries that label (`V0_2_POPULATION_METHODOLOGY.md`).
- **Independent marginals.** Household type, income, tenure, housing cost,
  region and area are drawn independently, so the real correlations between
  them (for example between income and number of children) are lost.
- **Coarse distributions.** Gross income and cash assets are two bands each,
  built to reproduce a published median and mean. The rent distribution is
  2018's shape moved to 2025 by one ratio.
- **Assumed inputs.** Accommodation Supplement area shares are equal (A5),
  every household is an in-work non-beneficiary (A6), and one-parent
  households share the couples' distribution of children (A2).
- **Four household types only.** Other household kinds (about 28% of HES
  households) are not represented.

## Results are static entitlement at full take-up

- **Entitlement, not spending.** Costs assume everyone entitled claims. No
  take-up assumption is registered.
- **No behaviour.** Nobody changes work, income or housing in response to a
  reform.
- **Coverage is reported, not filled.** Households whose component is
  `needs_review` or `unsupported` are counted separately and never as zero.
  In 2026-27 the in-work tax credit is `needs_review` for every household,
  and minimum family tax credit too (no net income is generated), so no
  total WFF figure exists.
- **No WFF-to-AS interaction.** None exists in the modelled law (AS DEC-003),
  so a WFF-only reform never changes Accommodation Supplement.

## Cross-validation shows the scope gaps

`V0_2_CROSS_VALIDATION.md` compares the baseline with Inland Revenue and MSD
figures. The model reaches about three-quarters of published family tax
credit, a fifth of Accommodation Supplement recipients and an eighth of
Best Start families. Each gap is explained by scope and none is tuned away.

## Not in v0.2

Poverty and income-adequacy measures, income tax, main benefits, other
policies, behavioural responses, take-up modelling, calibration or raking of
weights, uncertainty ranges, and the historical fiscal baseline
(`BUILD_PLAN_v0_2.md`, "Not in v0.2").
