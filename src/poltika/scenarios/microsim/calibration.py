"""v0.2 Task 3.3: the synthetic development population's spec, from data.

`derive_spec()` turns canonical variables (read through a
`CanonicalContext`, so this module never touches a file) into the
`SyntheticSpec` the generator takes. Every share and band is computed from
published figures by the rules below. Where no published figure exists, the
value is a named assumption. Each rule and assumption is written into the
spec's `sources`, so it travels with the population, and
`docs/releases/V0_2_POPULATION_METHODOLOGY.md` explains them.

Derivation rules (D) and assumptions (A):

- **D1 households by type.** HES Table 5 counts *people* in households of
  each kind. People are divided by household size: one-person 1, couple
  only 2, couple with one dependent child 3, with two 4. **A1:** a couple
  with "three or more" dependent children is counted with exactly three
  (size 5). **A2:** a one-parent household has the couples' mean number of
  dependent children. Other household kinds (other one-family, multi-family,
  one parent with only non-dependent children, and so on) are outside the
  four modelled types and are not represented.
- **D2 children count:** the couples' distribution of one, two and three
  (A1) children, also used for one-parent households (A2).
- **D3 Best Start cohort.** Children in the calculable cohort (born
  1 April 2024 to 31 March 2025) are live births registered in the year
  ended March 2025. Children in another cohort still inside Best Start's
  three years (third birthday during 2026-27, or born from 1 April 2025)
  are births registered in the years ended March 2024 and 2026. Each is a
  share of the dependent children D1 derives. **A3:** registrations stand
  for births in the year, and every such child is in a modelled household.
- **D4 bands from a median and a mean.** Where only a median m and mean
  μ are published (gross household income; currency and deposits), two
  equal-share uniform bands, [0, m) and [m, 4μ - 2m), reproduce both.
- **D5 tenure:** 2018 Census households paying rent against households
  owning (directly or through a family trust). Households neither paying
  rent nor owning, and "not stated", are excluded.
- **D6 weekly housing cost:** the 2018 Census weekly rent bands, every
  edge scaled by HES's 2025 to 2018 mean weekly rent ratio (the same HES
  definition in both years) and rounded to a whole dollar. **A9:** the open
  "$600 and over" band is closed at $1,200 in 2018 dollars. No AS result
  depends on that bound: scaled, the band starts above the weekly cost at
  which every AS area cap binds. (Fitting the bound to HES's 2018 mean rent
  was tried and fails: the Census bands' midpoints already exceed that mean,
  since the two publications measure rent differently.)
- **D7 region:** HES Table 5's people by regional council area. **A4:**
  people shares stand for household shares.
- **A5 AS area:** no published household count by Accommodation Supplement
  area was acquired, so the four areas are given equal shares.
- **A6 claimant category:** every household is a non-beneficiary, as the
  asserted facts (in-work eligibility, no main benefit) already require.
- **A7 partner income share** is 0.5. No v0.1 result depends on it: WFF
  and AS both use the couple's combined income.
- **A8 weekly income divisor** is 52 (annual gross income over 52 weeks, a
  synthetic mapping between the two income definitions, D9).

Shares are rounded to six decimal places, with the rounding remainder on
the largest share, so each set sums to exactly 1.
"""

from __future__ import annotations

from datetime import date
from decimal import ROUND_HALF_EVEN, ROUND_HALF_UP, Decimal
from itertools import pairwise
from typing import Any

from poltika.semantics.variables import CanonicalContext

POPULATION_ID = "nz_synthetic_development"
VERSION = 1
SEED = 20260927
HOUSEHOLDS = 2000

_HES = date(2025, 1, 1)  # inside the year ended June 2025
_CENSUS = date(2018, 3, 6)
_NET_WORTH = date(2024, 1, 1)  # inside the year ended June 2024
_BIRTHS_2025_RELEASE = "Year ended March 2025 (release page dated 15 May 2025)"

# 2018 Census weekly rent bands, [from, to) in 2018 dollars; the last is open.
_RENT_BANDS = (
    ("under_50", 0, 50),
    ("from_50_to_74", 50, 75),
    ("from_75_to_99", 75, 100),
    ("from_100_to_124", 100, 125),
    ("from_125_to_149", 125, 150),
    ("from_150_to_174", 150, 175),
    ("from_175_to_199", 175, 200),
    ("from_200_to_249", 200, 250),
    ("from_250_to_299", 250, 300),
    ("from_300_to_349", 300, 350),
    ("from_350_to_399", 350, 400),
    ("from_400_to_449", 400, 450),
    ("from_450_to_499", 450, 500),
    ("from_500_to_549", 500, 550),
    ("from_550_to_599", 550, 600),
)
_RENT_OPEN = ("from_600", 600)
_RENT_OPEN_UPPER = 1200  # A9
_OWNED = (
    "owned_mortgage_not_further_defined",
    "owned_mortgage_payments_made",
    "owned_mortgage_payments_not_made",
    "family_trust_mortgage_not_further_defined",
    "family_trust_mortgage_payments_made",
    "family_trust_mortgage_payments_not_made",
)
_REGIONS = {
    "northland": "Northland Region",
    "auckland": "Auckland Region",
    "waikato": "Waikato Region",
    "bay_of_plenty": "Bay of Plenty Region",
    "gisborne_hawkes_bay": "Gisborne/Hawke's Bay Region",
    "taranaki": "Taranaki Region",
    "manawatu_whanganui": "Manawatū–Whanganui Region",
    "wellington": "Wellington Region",
    "tasman_nelson_marlborough_west_coast": "Tasman/Nelson/Marlborough/West Coast Region",
    "canterbury": "Canterbury Region",
    "otago": "Otago Region",
    "southland": "Southland Region",
}

SOURCES = (
    (
        "Stats NZ, Household income and housing-cost statistics, year ended June 2025, corrected "
        "(stats_nz_household_income_housing_costs v1): Tables 3, 5, 9 and 10"
    ),
    (
        "Stats NZ, 2018 Census totals by topic, national highlights "
        "(stats_nz_census_2018_totals_by_topic_national v1): weekly rent paid, tenure of household"
    ),
    (
        "Stats NZ, Household net worth statistics, year ended June 2024 (stats_nz_household_net_worth v1): "
        "currency and deposits"
    ),
    (
        "Stats NZ, Births and deaths, years ended March 2025 and 2026 (stats_nz_births_and_deaths_release "
        "v1, v2): live births registered"
    ),
    "D1 households by type: HES Table 5 people divided by household size",
    "D2 children count: couples' distribution, used for one-parent households too",
    "D3 Best Start cohort: births registered per year as shares of derived dependent children",
    "D4 gross income and cash assets: two equal uniform bands reproducing the published median and mean",
    "D5 tenure: 2018 households paying rent against households owning",
    "D6 weekly housing cost: 2018 rent bands scaled by HES 2025/2018 mean weekly rent",
    "D7 region: HES Table 5 people by regional council area",
    "A1 assumption: 'three or more' dependent children counted as three",
    "A2 assumption: one-parent households have the couples' mean number of children",
    "A3 assumption: births registered stand for births, all in modelled households",
    "A4 assumption: people shares by region stand for household shares",
    "A5 assumption: equal shares across AS Areas 1-4 (no published household counts by area)",
    "A6 assumption: every household is a non-beneficiary",
    "A7 assumption: partner income share 0.5 (no v0.1 result depends on it)",
    "A8 assumption: weekly income is annual gross income / 52",
    "A9 assumption: the open $600-and-over 2018 rent band is closed at $1,200 (no AS result depends on it)",
)

_V = "verified"
ASSUMED = {
    "wff_household_eligibility": _V,
    "extra_instalment_status": _V,
    "in_work_eligibility": _V,
    "ftc_iwtc_protected_or_direct_abatement": _V,
    "mc6a_veterans_payment": _V,
    "mc6b_disqualifying_payment": _V,
    "minimum_family_full_time_earner_weeks": _V,
    "best_start_no_shared_care": _V,
    "best_start_protected_credit": _V,
    "child_qualifies_whole_year": _V,
    "child_best_start_no_disqualifying_payment": _V,
    "as_household_eligibility": _V,
    "exempt_cash_asset_status": _V,
    "ordinary_rate_status": _V,
    "eldest_dependent_child_under_16": _V,
    "as_claimant_is_wff_claimant_or_partner": _V,
}

_SIX = Decimal("0.000001")


class CalibrationError(ValueError):
    pass


def _shares(weights: dict[str, Decimal]) -> dict[str, str]:
    """Six-decimal shares summing to exactly 1; the remainder goes on the largest."""
    total = sum(weights.values(), Decimal(0))
    if total <= 0 or any(w <= 0 for w in weights.values()):
        raise CalibrationError(f"weights must be positive: {weights}")
    shares = {k: (w / total).quantize(_SIX, rounding=ROUND_HALF_EVEN) for k, w in weights.items()}
    largest = max(shares, key=lambda k: (shares[k], k))
    shares[largest] += Decimal(1) - sum(shares.values(), Decimal(0))
    return {k: str(v) for k, v in shares.items()}


def _two_bands(median: Decimal, mean: Decimal) -> list[dict[str, Any]]:
    """D4: [0, m) and [m, 4μ - 2m), half each, reproduce the median and mean."""
    upper = 4 * mean - 2 * median
    if not (median > 0 and upper > median):
        raise CalibrationError(f"median {median} and mean {mean} give no valid upper band")
    m, u = int(median), int(upper)
    if Decimal(m) != median or Decimal(u) != upper:
        raise CalibrationError(f"band edges must be whole dollars: {median}, {upper}")
    return [{"from": 0, "to": m, "share": "0.5"}, {"from": m, "to": u, "share": "0.5"}]


def derive_spec(ctx: CanonicalContext) -> dict[str, Any]:
    def val(variable: str, on: date, vintage: str | None = None) -> Decimal:
        return ctx.get(variable, on, vintage).value

    # D1-D2: households by type, from people in thousands.
    people = "household.people."
    single = val(people + "one_person_household", _HES)
    couple_only = val(people + "couple_only", _HES) / 2
    with_1 = val(people + "couple_one_dependent_child", _HES) / 3
    with_2 = val(people + "couple_two_dependent_children", _HES) / 4
    with_3 = val(people + "couple_three_plus_dependent_children", _HES) / 5  # A1
    couples_with = with_1 + with_2 + with_3
    mean_children = (with_1 + 2 * with_2 + 3 * with_3) / couples_with
    sole = val(people + "one_parent_dependent_children", _HES) / (1 + mean_children)  # A2
    households = {
        "single_without_children": single,
        "couple_without_children": couple_only,
        "couple_with_children": couples_with,
        "sole_parent": sole,
    }
    represents = (sum(households.values(), Decimal(0)) * 1000).quantize(
        _SIX, rounding=ROUND_HALF_EVEN
    )

    # D3: Best Start cohorts as shares of dependent children (persons).
    children = (couples_with + sole) * mean_children * 1000
    supported = val("population.live_births_registered", date(2025, 1, 1))
    other = val("population.live_births_registered", date(2024, 1, 1), _BIRTHS_2025_RELEASE) + val(
        "population.live_births_registered", date(2026, 1, 1)
    )
    outside = children - supported - other
    if outside <= 0:
        raise CalibrationError("births exceed the derived dependent children")

    # D5: tenure.
    tenure = "household.tenure_2018."
    renting = val(tenure + "not_owned_rent_payments_made", _CENSUS)
    owning = sum((val(tenure + slug, _CENSUS) for slug in _OWNED), Decimal(0))

    # D6: rent bands scaled to 2025; A9 closes the open band.
    band = "household.renting.weekly_rent_band."
    counts = {slug: val(band + slug, _CENSUS) for slug, _, _ in _RENT_BANDS}
    counts[_RENT_OPEN[0]] = val(band + _RENT_OPEN[0], _CENSUS)
    stated = sum(counts.values(), Decimal(0))
    rent_2018 = val("household.rent.weekly_mean_paying_households", date(2018, 1, 1))
    rent_2025 = val("household.rent.weekly_mean_paying_households", _HES)
    if stated <= 0:
        raise CalibrationError("no stated rent bands")
    scale = rent_2025 / rent_2018
    edges = [Decimal(lo) for _, lo, _ in _RENT_BANDS] + [
        Decimal(_RENT_OPEN[1]),
        Decimal(_RENT_OPEN_UPPER),
    ]
    scaled = [int((e * scale).quantize(Decimal(1), rounding=ROUND_HALF_UP)) for e in edges]
    if any(b <= a for a, b in pairwise(scaled)):
        raise CalibrationError(f"scaled rent band edges are not increasing: {scaled}")
    rent_shares = _shares(counts)
    slugs = [slug for slug, _, _ in _RENT_BANDS] + [_RENT_OPEN[0]]
    housing = [
        {"from": scaled[i], "to": scaled[i + 1], "share": rent_shares[slug]}
        for i, slug in enumerate(slugs)
    ]

    # D7: region.
    region = _shares({name: val(f"{people}region.{slug}", _HES) for slug, name in _REGIONS.items()})

    thousand = Decimal(1000)
    return {
        "population_id": POPULATION_ID,
        "version": VERSION,
        "seed": SEED,
        "households": HOUSEHOLDS,
        "represents": str(represents),
        "sources": list(SOURCES),
        "household_type": _shares(households),
        "children_count": _shares({"1": with_1, "2": with_2, "3": with_3}),
        "best_start_cohort": _shares(
            {
                "in_supported_cohort": supported,
                "other_cohort_unsupported": other,
                "outside_best_start_entitlement": outside,
            }
        ),
        "gross_income": _two_bands(
            val("household.gross_income.median", _HES), val("household.gross_income.mean", _HES)
        ),
        "partner_income_share": "0.5",
        "weekly_income_divisor": "52",
        "tenure": _shares({"rent_contributions_or_board": renting, "homeowner": owning}),
        "weekly_housing_cost": housing,
        "as_area": {"area1": "0.25", "area2": "0.25", "area3": "0.25", "area4": "0.25"},
        "region": region,
        "claimant_category": {"non_beneficiary": "1"},
        "cash_assets": _two_bands(
            val("household.currency_and_deposits.median", _NET_WORTH) * thousand,
            val("household.currency_and_deposits.mean", _NET_WORTH) * thousand,
        ),
        "assumed": dict(ASSUMED),
        "wff_lookup_date": "2026-06-01",
        "as_lookup_date": "2026-06-01",
        "assessment_week_start": "2026-06-01",
        "assessment_week_end": "2026-06-08",
        "requested_wff_policy_version": "0.1.0",
        "requested_as_policy_version": "0.1.1",
    }
