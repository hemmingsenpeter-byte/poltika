# What Poltika v0.3 income tax does not do

v0.3 Phase 2.5 (new-policy PR 5, preparation). Nothing is released and no
release tag is implied. This page is the income-tax lane's limitations record,
alongside `V0_1_LIMITATIONS.md` and `V0_2_LIMITATIONS.md`, whose limits still
apply to the other policies. It states what exists today, so the README's
coverage row is never overstated.

## What exists

- **A draft engine** (`basic_annual_income_tax`, PR #224) and the **shared
  household mapping** (`to_income_tax`, `run_household_income_tax`, PR #232)
  for one natural person and the 2026-27 tax year.
- **Draft values.** `policy_specs/income_tax/policy.yaml` is
  `draft_pending_review` with `policy_version` null, and every parameter is
  `needs_review`. The values are candidates, not approved statutory fixtures.
- **Every result is `needs_review` or `unsupported`, with no amount.** A
  household in the slice stops at `IT_POLICY_NOT_APPROVED`. Nothing is ever
  `calculated`, and a missing fact is never zero.
- **Non-numeric tests only.** The conformance matrix
  (`reviews/2026-10-29-income-tax-conformance-matrix.md`), its tests and the
  golden households (`policy_specs/income_tax/golden_households.yaml`) assert
  outcome, reason code, category, missing facts and policy identity. None holds
  an amount.

## What it does not do

- **No income-tax amount.** Final annual tax precision is open (DEC-004). No
  dated official period-matched result is retained as a benchmark
  (`benchmarks.yaml`, `missing_source`), and no protected numeric expected
  value is approved.
- **The bracket-boundary goldens are not written.** They are listed in
  `golden_households.yaml` as waiting on the protected-value process
  (`doctrine/test-doctrine.md`), together with known zero income, a calculated
  result per earner and rounding.
- **The 2026-27 annual-authority gate stays `needs_review`** (Q16, D36,
  DEC-001). Proposed legislation is context only.
- **Outside the slice** (`unsupported`, `not_modelled`; the specification's
  "Explicit exclusions"): main benefits, self-employment and business income,
  rent, investment and foreign income, non-residents, changing-residence and
  special-residence cases, non-standard and other tax years, deductions, losses,
  special basic rates, schedular and PIE regimes, unusual employment items,
  negative income and income that is not a whole-dollar amount (Q17). PAYE,
  ACC, student loans, KiwiSaver, other tax credits, refunds and terminal tax
  are separate outputs and are not zero.
- **Taxable income is supplied, never derived.** It is one `it_annual_taxable`
  spell that covers exactly the tax year (IT-02, IT-03). Earnings, benefits and
  other spells are never converted to it. A part-year gap leaves it unknown,
  several spells are refused rather than summed, and a spell running past the
  year is refused rather than apportioned (Q10).
- **Each person is assessed alone** (IT-01). A couple gets one result per
  person. Nothing is added across the household.
- **It feeds nothing.** No graph edge connects income tax to WFF, the
  Accommodation Supplement or disposable income. Minimum family tax credit
  still needs a caller-attested after-tax income. Which benefits are taxable
  income is the interaction step (new-policy PR 4), not built.
- **The API returns no amount.** `POST /income-tax/calculate` exposes the
  engine with a strict request model; every response is `needs_review` or
  `unsupported` with a null value. It is not in `/api/v1/meta`, the Workbench
  or a household run, and `/api/v1/evidence` lists it with `policy_version: null`.

## Release gate

`tests/acceptance/test_v0_3_release_gate.py` carries six named income-tax
rows, all skipped while their reason holds: draft values, protected-value
approval, DEC-004 output precision, the annual-authority gate, the official
benchmark and the independent review row. A row whose reason stops holding
fails until it is replaced by a real check, so the gate is not met by skips
that outlive their cause. The v0.3 gate with skips is unmet.

## Maintenance

The 2027-28 annual update is due before 1 April 2027: every rate Poltika uses
stops on that date (`BUILD_PLAN_v0_1_6.md`). Income tax needs its 2027-28
parameters sourced and reviewed through the `new-policy` annual-update steps,
and the annual-authority gate (DEC-001) re-checked, or household results for
the new year resolve to no value for the date.
