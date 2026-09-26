# Poltika orientation

Read this first: what Poltika does **now**, on one page. It is a summary, not
an authority. If the specifications or `policy.yaml` files disagree with it,
they win, and this page needs fixing.

## What it is

A deterministic simulator for two New Zealand support policies, with every
rate and threshold taken from a cited primary source:

- **Working for Families (WFF)** for the 2026-27 tax year: family tax credit
  (FTC), in-work tax credit (IWTC), minimum family tax credit (MFTC) and
  Best Start. Annual amounts.
- **Accommodation Supplement (AS)**: one weekly amount.
- **Both together for one household**, each in its own period.

v0.1.0 is released. v0.1.5 (`BUILD_PLAN_v0_1_5.md`) adds evidence and
explanations on top without changing any amount: calculation steps with
intermediate values, reason codes, deterministic explanations, and an
analyst web page.

Not modelled: income tax, instalments or square-up, other benefits, any
policy not listed above. Results are conditional simulations built from
facts the caller asserts. They are not entitlement determinations.

Section citations are to the Income Tax Act 2007 (parts M and C, for WFF),
the Tax Administration Act 1994 (s 80KW), and the Social Security Act 2018
and Social Security Regulations 2018 (s, Schedule and r references, for AS).

## Outcomes

Every component returns one of three outcomes:

| Outcome | Meaning | Value |
| --- | --- | --- |
| `calculated` | Inside the modelled domain, with every needed fact verified | An exact decimal (a string in the API) |
| `unsupported` | A verified fact puts the case outside what is modelled | None |
| `needs_review` | A needed fact, parameter or rate is unverified | None |

- `unsupported` outranks `needs_review`. A missing fact never becomes zero.
  A `calculated` zero is an evidenced zero, such as a child verified as too
  old for Best Start.
- WFF amounts are exact and never rounded (`7472.500`): the complete-dollar
  rule applies to income over a threshold, not to the credit. AS is rounded
  up to a whole dollar once, at the end (r 19).
- Each result also carries `reason` (text), `code` (a stable reason code),
  `category` for `unsupported` (`evidenced_exclusion` or `not_modelled`),
  `missing_facts` for `needs_review`, and in the engine a `trace` with the
  parameters, facts and calculation steps used. The WFF and household API
  routes add `explanations`, rendered only from that recorded calculation.

## Facts that always hold

- **No WFF total, ever.** The 2026-27 IWTC base (`in_work_base`) is held at
  `review_status: needs_review` in `policy.yaml`: the temporary rate can be
  reversed early by Order in Council, so it can't be confirmed for the whole
  year until the year ends. IWTC is therefore never `calculated`, and
  `WffResult.total_annual_entitlement()` returns nothing.
- **Inputs are asserted facts, not raw data.** Status facts are `verified`,
  `excluded` or `unknown`. Amounts and choices are unverified when `None`
  (omitted in the API). Anything left out counts as unverified. Only
  `household_eligibility` (both policies), `extra_instalment_status` and the
  child list (WFF) have no default. There is no date of birth, age, child
  ID, hours worked, address or rent breakdown: the caller classifies those.
  An unverified fact makes only the components that need it `needs_review`:
  `cash_assets=None`, for example, makes AS `needs_review` and leaves WFF
  unchanged.
  The API rejects any unknown field with a 422.
- **WFF covers whole years only.** Every child must be under 18 and in the
  claimant's care for the whole tax year (the MC 9 extension for some
  18-year-olds is unsupported). A part-year child, a relationship change or
  shared care makes every WFF component `unsupported`; mark a part-year child
  `qualifies_whole_year=excluded`. `excluded` can't tell
  part of the year from none of it: a child who qualifies for no part of the
  year isn't a qualifying child, so don't list them.
- **Best Start calculates one group only:** a single child born 1 April 2024
  to 31 March 2025. Children verified as too old give a calculated $0. Other
  birth groups, in-year births or third birthdays, and more than one
  eligible child are `unsupported`.
- **MFTC needs an attested after-tax (ME 3) income.** There is no income tax
  module to derive one.
- **AS is weekly.** Each assessment week `[start, end)` (end exclusive, 7
  days) takes one area (1-4), one weekly cost and one weekly income, with no
  rule for a change mid-week. It uses MSD's published entry thresholds.
- **Combined runs never add WFF and AS together.** They stay in their own
  periods. The runner checks, in order: the AS claimant is the WFF claimant
  or their partner; the AS week is inside the WFF year; partner status; a
  main benefit against WFF in-work eligibility, MC 6(b), MD 14/15 and MG 4;
  and the dependent-child count (`SHARED_FACT_CHECKS` in
  `scenarios/combined.py`). Any disagreement makes every component
  `needs_review`, except one already `unsupported`.
- **Run settings.** WFF: policy version `0.1.0`, lookup date from 2026-04-01
  up to (not including) 2027-04-01. AS: policy version `0.1.1`, a week
  starting on or after 2026-04-01 and ending by 2027-04-01, with the lookup
  date inside it. Every rate ends on 1 April 2027.

## How each amount is worked out

The rates and thresholds are parameters in each `policy.yaml`; look them up
there rather than copying them.

- **FTC:** an eldest-child amount plus an amount for each other child, less
  the abatement rate times the complete dollars of family scheme income over
  the threshold. Abatement left after FTC reaches zero passes to IWTC
  (MD 2(2)(c)).
- **IWTC:** a base plus an amount per child beyond three, less the abatement
  left from FTC. Always `needs_review`, as above.
- **MFTC:** the prescribed amount less the attested after-tax income, never
  below zero.
- **Best Start:** the annual amount less its own rate times the complete
  dollars over its own threshold.
- **AS:** the subsidy rate times the weekly cost over the entry threshold,
  capped by household type and area. For a claimant not on a benefit, a
  reduction for weekly income over the income threshold follows, with income
  imputed from cash assets over a lower threshold. Cash assets over the
  r 15 ceiling, or verified $0 costs (s 65AAA), make AS `unsupported`.

## The inputs

The scenario dataclasses are the contract: `WffScenario` in
`src/poltika/engines/simulator/wff.py` and `AsScenario` in
`accommodation_supplement.py`. The API request models mirror them field for
field; `docs/demo/v0_1/request.json` is a complete household request.

- **WFF:** household eligibility; the extra-instalment check; the children
  (whole-year qualification, Best Start group, Best Start disqualifying
  payment); partner status; family scheme income per person; attested
  after-tax income; in-work eligibility; the MC 6(a) and MC 6(b) payment
  checks; the MD 14/15 and MG 4 protected-credit checks; full-time-earner
  weeks; shared care.
- **AS:** household eligibility; claimant category (Jobseeker Support, Sole
  Parent Support, Supported Living Payment or not on a benefit); tenure
  (rent or board only); partner type; area; weekly costs; number of
  dependent children; cash assets and the exempt-asset check (which must be
  `verified`, or AS is `unsupported`); weekly income; the ordinary-rate
  check; whether the eldest child is under 16.
- **Combined:** both, plus `as_claimant_is_wff_claimant_or_partner`.

## Where things live

| What | Where |
| --- | --- |
| Sources, specification, parameters, cases, decisions | `policy_specs/<policy>/` |
| Cross-policy cases and golden households | `policy_specs/wff_as_interaction/` |
| Parameter loader; source catalogue model | `src/poltika/policy/loader.py`; `semantics/schemas/source_catalog.py` |
| Calculators; shared outcome types; trace and steps | `src/poltika/engines/simulator/wff.py`, `src/poltika/engines/simulator/accommodation_supplement.py`; `src/poltika/engines/simulator/outcome.py`; `src/poltika/engines/simulator/trace.py` |
| Provenance, evidence and explanations | `engines/assurance/provenance.py`, `evidence.py`, `explanation.py` |
| Combined runner; scenario records and store | `src/poltika/scenarios/combined.py`; `record.py`, `store.py` |
| HTTP API and analyst page | `src/poltika/api/` |
| Tests | `tests/unit`, `tests/regression`, `tests/acceptance`, `tests/fixtures` |
| Rules of work | `CLAUDE.md`, `doctrine/`, `adr/` |
| Worked household; limitations, baseline, release gate; pilot | `docs/demo/v0_1/`; `docs/releases/`; `docs/pilot/` |

## Running it

From the repository root:

```sh
uv sync --extra dev
uv run --extra dev pytest -q                       # the fast suite
uv run --extra dev uvicorn poltika.api.main:app    # routes at /docs; analyst page at /analyst
```

Routes: `POST /wff/calculate`, `POST /accommodation-supplement/calculate`,
`POST /household/calculate`, `/analyst` (page, examples, pilot cases,
evidence), and `/scenarios` (stored runs; these need `POLTIKA_DATABASE_URL`
and return 503 without it). `docs/pilot/GUIDE.md` runs it in Docker.

The demo household through the API, with no server needed:

```python
import json

from fastapi.testclient import TestClient

from poltika.api.main import app

request = json.load(open("docs/demo/v0_1/request.json"))
response = TestClient(app).post("/household/calculate", json=request).json()
print(response["wff"]["family_tax_credit"])  # calculated, 7472.500
print(response["accommodation_supplement"])  # calculated, 220
```

The same household through the engines:

```python
from datetime import date
from decimal import Decimal as D
from pathlib import Path

from poltika.engines.simulator.accommodation_supplement import (
    Area, AsScenario, AssessmentWeek, ClaimantCategory, PartnerType, TenureType,
)
from poltika.engines.simulator.wff import (
    BestStartCohort, ChildFacts, FactStatus as F, PartnerStatus, VerifiedIncome, WffScenario,
)
from poltika.scenarios.combined import CombinedHouseholdScenario, run_combined_household

V = F.VERIFIED
child = ChildFacts(
    qualifies_whole_year=V,
    best_start_cohort=BestStartCohort.OUTSIDE_BEST_START_ENTITLEMENT,
    best_start_no_disqualifying_payment=V,
)
wff = WffScenario(
    household_eligibility=V, extra_instalment_status=V, children=[child, child],
    partner_status=PartnerStatus.PARTNERED,
    family_scheme_income=VerifiedIncome(D("50000"), D("20000")),
    in_work_eligibility=V, mc6a_veterans_payment=V, mc6b_disqualifying_payment=V,
    ftc_iwtc_protected_or_direct_abatement=V,
    best_start_no_shared_care=V, best_start_protected_credit=V,
)  # MFTC facts left out, so MFTC is needs_review; IWTC is needs_review (in_work_base)
accommodation = AsScenario(
    household_eligibility=V, claimant_category=ClaimantCategory.NON_BENEFICIARY,
    tenure_type=TenureType.RENT_CONTRIBUTIONS_OR_BOARD, partner_status=PartnerType.ORDINARY_COUPLE,
    statistical_area_unit=Area.AREA_1, weekly_accommodation_costs=D("600"),
    dependent_children_count=2, cash_assets=D("2000"), exempt_cash_asset_status=V,
    weekly_income=D("1346"), ordinary_rate_status=V, eldest_dependent_child_under_16=V,
)
week = AssessmentWeek(date(2026, 6, 1), date(2026, 6, 8))  # [start, end)
specs = Path("policy_specs")
result = run_combined_household(
    specs / "working_for_families", specs / "accommodation_supplement",
    CombinedHouseholdScenario(wff, accommodation, as_claimant_is_wff_claimant_or_partner=V),
    wff_lookup_date=date(2026, 6, 1), as_lookup_date=week.start, assessment_week=week,
    requested_wff_policy_version="0.1.0", requested_as_policy_version="0.1.1",
)
for name in ("family_tax_credit", "in_work_tax_credit", "minimum_family_tax_credit", "best_start"):
    r = getattr(result.wff, name)
    print(f"{name}: {r.outcome} {r.value} {r.code or ''} {r.reason or ''}")
print("accommodation_supplement:", result.accommodation_supplement.outcome, result.accommodation_supplement.value)
```

To run one policy alone, call `run_wff_module(policy_dir, lookup_date,
scenario, requested_policy_version=...)` or `run_as_module(policy_dir,
lookup_date, scenario, requested_policy_version=..., assessment_week=...)`.

## What to read next

| Task | Read |
| --- | --- |
| Running scenarios or answering questions | This page and `docs/demo/v0_1/` |
| Checking or explaining a result | Also the calculation sequence in the policy's `specification.md`, and its `decisions/` |
| Changing policy logic or statutory values | CLAUDE.md's full list: `BUILD_PLAN.md`, `ARCHITECTURE.md`, `REPOSITORY_STRUCTURE.md`, `doctrine/` and the policy's specification. Protected expected values follow `doctrine/test-doctrine.md` |
| Current work | `BUILD_PLAN_v0_1_5.md` |
| Opening or reviewing a PR | `.claude/skills/pr-review-preflight/SKILL.md` and `doctrine/review-doctrine.md` |

## Keeping this page current

If a change makes any statement on this page untrue, update this page, and
CLAUDE.md's "v0.1 at a glance" block, in the same PR. CI runs both examples
above and compares them with the demo summary
(`tests/acceptance/test_orientation_examples.py`). Nothing checks the prose.
