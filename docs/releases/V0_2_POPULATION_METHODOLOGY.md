# v0.2 synthetic development population: methodology

**Synthetic development population, not an estimate for New Zealand.**

The spec is `data/metadata/populations/nz_synthetic_development.v1.yaml`.
It is derived, never hand-edited: `scenarios/microsim/calibration.py`
computes it from canonical variables, and
`tests/unit/scenarios/microsim/test_calibration.py` fails if the committed
file differs from a fresh derivation. To regenerate:

```sh
uv run --extra dev python -m poltika.scenarios.microsim.calibrate_cli data data/metadata/populations/nz_synthetic_development.v1.yaml
```

## Sources

All Stats NZ, retrieved 27 September 2026, committed exactly as published
under `data/raw/` with manifests (`docs/research/v0_2_task_3_1_calibration_tables.md`):

- Household income and housing-cost statistics, year ended June 2025
  (corrected): Tables 3, 5, 9 and 10;
- 2018 Census totals by topic, national highlights: weekly rent paid and
  tenure of household;
- Household net worth statistics, year ended June 2024: currency and
  deposits;
- Births and deaths, years ended March 2025 and 2026: live births
  registered.

## How each input is set

| Input | Rule | Value (v1) |
| --- | --- | --- |
| Households represented | D1: HES Table 5 people in the four modelled household kinds, divided by household size | 1,452,567 (of HES's 2,025,400 households; other kinds are not represented) |
| Household type | D1, with A1 (three or more children counted as three) and A2 (one-parent households have the couples' mean children) | single 34.6%, couple 35.1%, couple with children 24.2%, sole parent 6.1% |
| Children per family | D2: couples' distribution, also used for one-parent households (A2) | 1: 36.9%, 2: 46.1%, 3: 17.0% |
| Best Start cohort | D3: births registered in the year ended March 2025 (calculable cohort) and in 2024 plus 2026 (other cohorts), as shares of derived dependent children (A3) | 7.4% / 14.3% / 78.3% outside |
| Gross household income | D4: two equal uniform bands reproducing HES 2025's median ($109,556) and mean ($139,111) | [0, 109,556), [109,556, 337,332) |
| Tenure | D5: 2018 households paying rent vs owning | renting 33.1% |
| Weekly housing cost | D6: 2018 rent bands scaled by HES mean rent 2025/2018 ($505.50/$340.50); A9 closes the open top band | 16 bands, $0 to $1,781 |
| Region | D7: HES Table 5 people by regional council (A4: people shares as household shares) | 12 regions |
| Cash assets | D4 on currency and deposits, 2024 (median $16,000, mean $75,000) | [0, 16,000), [16,000, 268,000) |
| AS area | A5: equal quarters. No published household count by area was acquired | 25% each |
| Claimant category | A6: non-beneficiary, as the asserted facts require | 100% |
| Partner income share | A7: 0.5; WFF and AS use combined income, so no result depends on it | 0.5 |
| Weekly income | A8: annual gross / 52 | 52 |

The generator's own rules (independent marginals, equal weights, the
couple income split) are in `scenarios/microsim/synthetic.py`, and every
generated population reports its calibration against each target.

## Known limits

- Independent marginals: income, tenure, housing cost and household type are
  not correlated, unlike the real population.
- AS area shares are assumed (A5), so area results say nothing about New
  Zealand's geography.
- Households are all in-work non-beneficiaries (A6), so beneficiary
  interactions are not exercised.
- Minimum family tax credit is `needs_review` throughout (no net income is
  generated), and the in-work tax credit is `needs_review` for 2026-27.
- The 2018 rent distribution is moved to 2025 by one ratio, so its shape is
  2018's.
