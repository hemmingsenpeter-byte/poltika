# Poltika v0.1 orientation

Read this first: what v0.1 does **now**, on one page. It is a summary, not an
authority. If the specifications or `policy.yaml` files disagree with it,
they win, and this page needs fixing.

## What v0.1 is

A deterministic simulator for two New Zealand support policies, with every
rate and threshold taken from a cited primary source:

- **Working for Families (WFF)** for the 2026-27 tax year: family tax credit
  (FTC), in-work tax credit (IWTC), minimum family tax credit (MFTC) and
  Best Start. Annual amounts.
- **Accommodation Supplement (AS)**: one weekly amount.
- **Both together for one household**, each in its own period.

Not modelled: income tax, instalments or square-up, other benefits, any
policy not listed above. Results are conditional simulations built from
facts the caller asserts. They are not entitlement determinations.

## Outcomes

Every component returns one of three outcomes:

| Outcome | Meaning | Value |
| --- | --- | --- |
| `calculated` | The case is inside the modelled domain and every needed fact is verified | A decimal amount (a string in the API) |
| `unsupported` | A verified fact puts the case outside what v0.1 models | None |
| `needs_review` | A needed fact, parameter or rate is unverified | None |

`unsupported` outranks `needs_review`. A missing fact never becomes zero. A
`calculated` zero means an evidenced zero, such as a child verified as too
old for Best Start.

## Facts that always hold in v0.1

- **No WFF total, ever.** The 2026-27 IWTC base rate (`in_work_base`) is
  gated `needs_review`, so IWTC is never `calculated`, and
  `WffResult.total_annual_entitlement()` returns nothing unless all four
  components are.
- **Inputs are asserted statuses, not raw facts.** Most facts are
  `verified`, `excluded` or `unknown`, and anything left out counts as
  unverified. There is no
  date of birth, age, child ID, hours worked, address or rent breakdown: the
  caller classifies those. The API rejects any unknown field with a 422.
- **WFF covers whole years only.** A child who qualifies for only part of
  the year, a relationship change or shared care makes every WFF component
  `unsupported` for the household. `excluded` can't tell part of the year
  from none of it: a child who qualifies for no part of the year isn't a
  qualifying child, so don't list them.
- **Best Start calculates one group only:** a single child born 1 April 2024
  to 31 March 2025. Children verified as too old give a calculated $0. Other
  birth groups, in-year births or third birthdays, and more than one
  eligible child are `unsupported`.
- **MFTC needs an attested after-tax (ME 3) income.** Poltika has no income
  tax module, so it can't derive one.
- **AS is weekly.** One area (1-4), one weekly cost, one weekly income per
  assessment week, and no rule for a change in the middle of a week. It uses
  MSD's published entry thresholds and rounds up once, at the end (r 19).
- **Combined runs never add WFF and AS together.** They stay in their own
  periods. If shared facts disagree (partner status, child count, a main
  benefit against in-work facts), every component becomes `needs_review`,
  except one that is already `unsupported`.
- **Run settings.** WFF: policy version `0.1.0`, lookup date from
  2026-04-01 up to (not including) 2027-04-01. AS: policy version `0.1.1`,
  an explicit 7-day week starting on or after 2026-04-01 and ending by
  2027-04-01, with the lookup date inside it.

## How each amount is worked out

The formulas' shape is below. The rates and thresholds are parameters in
each `policy.yaml`; look them up there rather than copying them.

- **FTC:** an eldest-child amount plus an amount for each other child, less
  the abatement rate times the complete dollars of family scheme income over
  the threshold. Any abatement left after FTC reaches zero passes to IWTC
  (MD 2(2)(c)).
- **IWTC:** a base amount plus an amount per child beyond three, less the
  abatement left over from FTC. Always `needs_review` in v0.1, as above.
- **MFTC:** the prescribed amount less the attested after-tax income, never
  below zero.
- **Best Start:** the annual amount less its own abatement rate times the
  complete dollars over its own threshold.
- **AS:** the subsidy rate times the weekly cost over the entry threshold,
  capped by household type and area. For a claimant not on a benefit, a
  reduction for weekly income over the income threshold is then applied,
  with income imputed from cash assets over a lower threshold. The result is
  rounded up to a whole dollar. Cash assets that fail the r 15 ceiling, or
  verified $0 accommodation costs (s 65AAA), make AS `unsupported`.

## The inputs

The scenario dataclasses are the contract: `WffScenario` in
`src/poltika/engines/simulator/wff.py` and `AsScenario` in
`accommodation_supplement.py`. The API request models mirror them field for
field.

- **WFF:** household eligibility; the extra-instalment check; the children
  (whole-year qualification, Best Start group, Best Start disqualifying
  payment); partner status; family scheme income per person; attested
  after-tax income; in-work eligibility; the MC 6(a) and MC 6(b) payment
  checks; the MD 14/15 and MG 4 protected-credit checks; full-time-earner
  weeks; shared care.
- **AS:** household eligibility; claimant category (Jobseeker Support, Sole
  Parent Support, Supported Living Payment or not on a benefit); tenure
  (rent or board only); partner type; area; weekly costs; number of
  dependent children; cash assets and the exempt-asset check; weekly income;
  the ordinary-rate check; whether the eldest child is under 16.
  `exempt_cash_asset_status` must be `verified`, or AS is `unsupported`.
- **Combined:** both scenarios, plus whether the AS claimant is the WFF
  claimant or their partner (`as_claimant_is_wff_claimant_or_partner`).

`docs/demo/v0_1/request.json` is a complete, valid household request.

## Where things live

| What | Where |
| --- | --- |
| Sources, specification, parameters, test cases, decisions | `policy_specs/<policy>/` (`sources.yaml`, `specification.md`, `policy.yaml`, `spec_cases.yaml`, `benchmarks.yaml`, `decisions/`) |
| Cross-policy cases and golden households | `policy_specs/wff_as_interaction/` |
| Parameter loader | `src/poltika/policy/loader.py` |
| Calculators and module entry points | `src/poltika/engines/simulator/wff.py`, `accommodation_supplement.py` |
| Per-component trace; provenance report | `engines/simulator/trace.py`; `engines/assurance/provenance.py` |
| Combined household runner | `src/poltika/scenarios/combined.py` |
| Scenario records and the PostgreSQL store | `scenarios/record.py`, `scenarios/store.py` |
| HTTP API | `src/poltika/api/` |
| Tests | `tests/unit`, `tests/regression`, `tests/acceptance`, `tests/fixtures` |
| Rules of work | `CLAUDE.md`, `doctrine/`, `adr/` |
| A worked household, with provenance | `docs/demo/v0_1/` |
| Earlier question sets and their answers | `review_packets/v0_1_question_set/` |

## Running it

From the repository root:

```sh
uv sync --extra dev
uv run --extra dev pytest -q                       # the fast suite
uv run --extra dev uvicorn poltika.api.main:app    # the API; routes at /docs
```

API routes: `POST /wff/calculate`, `POST /accommodation-supplement/calculate`,
`POST /household/calculate`, and `/scenarios` (stored runs, replay and
re-run; these need `POLTIKA_DATABASE_URL`, and return 503 without it).

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
child = ChildFacts(V, BestStartCohort.OUTSIDE_BEST_START_ENTITLEMENT, V)
wff = WffScenario(
    household_eligibility=V, extra_instalment_status=V, children=[child, child],
    partner_status=PartnerStatus.PARTNERED,
    family_scheme_income=VerifiedIncome(D("50000"), D("20000")),
    mc6a_veterans_payment=V, ftc_iwtc_protected_or_direct_abatement=V,
    best_start_no_shared_care=V, best_start_protected_credit=V,
)  # facts left out default to unknown, so MFTC and IWTC come back needs_review
accommodation = AsScenario(
    household_eligibility=V, claimant_category=ClaimantCategory.NON_BENEFICIARY,
    tenure_type=TenureType.RENT_CONTRIBUTIONS_OR_BOARD, partner_status=PartnerType.ORDINARY_COUPLE,
    statistical_area_unit=Area.AREA_1, weekly_accommodation_costs=D("600"),
    dependent_children_count=2, cash_assets=D("2000"), exempt_cash_asset_status=V,
    weekly_income=D("1346"), ordinary_rate_status=V, eldest_dependent_child_under_16=V,
)
week = AssessmentWeek(date(2026, 6, 1), date(2026, 6, 8))
specs = Path("policy_specs")
result = run_combined_household(
    specs / "working_for_families", specs / "accommodation_supplement",
    CombinedHouseholdScenario(wff, accommodation, as_claimant_is_wff_claimant_or_partner=V),
    wff_lookup_date=date(2026, 6, 1), as_lookup_date=week.start, assessment_week=week,
    requested_wff_policy_version="0.1.0", requested_as_policy_version="0.1.1",
)
for name in ("family_tax_credit", "in_work_tax_credit", "minimum_family_tax_credit", "best_start"):
    r = getattr(result.wff, name)
    print(f"{name}: {r.outcome} {r.value} {r.reason or ''}")
print("accommodation_supplement:", result.accommodation_supplement.outcome, result.accommodation_supplement.value)
```

To run one policy on its own, call `run_wff_module(policy_dir, lookup_date,
scenario, requested_policy_version=...)` or `run_as_module(policy_dir,
lookup_date, scenario, requested_policy_version=..., assessment_week=...)`.

## What to read next

| Task | Read |
| --- | --- |
| Running scenarios or answering questions about v0.1 | This page and `docs/demo/v0_1/` |
| Checking or explaining a result | Also the calculation sequence in the policy's `specification.md`, and its `decisions/` |
| Changing policy logic or statutory values | CLAUDE.md's full list: `BUILD_PLAN.md`, `ARCHITECTURE.md`, `REPOSITORY_STRUCTURE.md`, `doctrine/` and the policy's specification. Protected expected values follow `doctrine/test-doctrine.md` |
| Opening or reviewing a PR | `.claude/skills/pr-review-preflight/SKILL.md` and `doctrine/review-doctrine.md` |

## Keeping this page current

If a change makes any statement on this page untrue, update this page in the
same PR.
