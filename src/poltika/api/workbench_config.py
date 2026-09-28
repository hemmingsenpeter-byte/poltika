"""Workbench presentation configuration (the registry-driven UI's config).

This is what the analyst workbench shows and how it groups things, never a
policy value. Statutory parameters, units, dates and sources come from
`policy_specs/` through `GET /workbench/registry`; amounts come from the
engines. Adding an instrument is adding a spec directory, not editing this
file. Adding an output tab is adding an entry to `TABS` and a builder in
`workbench_tables.py`.

Nothing here is calculated. The winner/loser thresholds are presentation
settings: a household counts as better or worse off only when its change is
at least the threshold, in the measure's own unit.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

# The date the parameter panel resolves "current value" at. It is inside the
# WFF 2026-27 tax year and the first Accommodation Supplement assessment week
# the population uses (`scenarios/population.py`).
BASELINE_DATE = date(2026, 6, 1)
BASELINE_LABEL = "Current law as modelled at 1 June 2026 (2026-27 rates)"


@dataclass(frozen=True)
class FiscalYear:
    label: str
    modelled: bool
    note: str


# Only 2026-27 law is sourced. The other years are slots, not estimates: a
# year is filled only when its parameters exist in `policy_specs/`.
FISCAL_YEARS: tuple[FiscalYear, ...] = (
    FiscalYear(
        "2026-27",
        True,
        "WFF amounts are for the 2026-27 tax year (1 April 2026 to 31 March 2027); "
        "Accommodation Supplement amounts are weekly.",
    ),
    FiscalYear("2027-28", False, "Not modelled: no sourced parameters for this year."),
    FiscalYear("2028-29", False, "Not modelled: no sourced parameters for this year."),
    FiscalYear("2029-30", False, "Not modelled: no sourced parameters for this year."),
)


@dataclass(frozen=True)
class Measure:
    """A set of components summed for winners and losers. Every component in
    a set shares one unit (`analysis.component_set_unit`)."""

    measure_id: str
    label: str
    components: tuple[str, ...]


MEASURES: tuple[Measure, ...] = (
    Measure("family_tax_credit", "Family tax credit", ("family_tax_credit",)),
    Measure("best_start", "Best Start", ("best_start",)),
    Measure("accommodation_supplement", "Accommodation Supplement", ("accommodation_supplement",)),
)

# Per unit (`runner.UNITS`), in that unit. $52 a tax year is $1 a week only
# by this explicit setting; nothing converts one unit to the other.
WINNER_LOSER_THRESHOLDS: dict[str, Decimal] = {
    "NZD per tax year": Decimal(52),
    "NZD per week": Decimal(1),
}


@dataclass(frozen=True)
class Tab:
    tab_id: str
    title: str
    status: str  # "active" or "deferred"
    note: str = ""


TABS: tuple[Tab, ...] = (
    Tab("fiscal", "Fiscal", "active"),
    Tab("households", "Households", "active"),
    Tab("work_incentives", "Work incentives", "deferred", "Built with the household mode."),
    Tab("assumptions", "Assumptions & provenance", "active"),
    Tab("sensitivity", "Sensitivity", "deferred", "Deferred: sensitivity and Monte Carlo."),
    Tab("distribution", "Distribution", "deferred", "Deferred: decile distribution."),
    Tab("options_matrix", "Options comparison", "deferred", "Deferred: comparison matrix."),
    Tab("cba", "CBA / NPV", "deferred", "Deferred: cost-benefit analysis."),
)

# Standard family types: golden household ids from
# `policy_specs/wff_as_interaction/golden_households.yaml`. An id missing from
# that file is skipped, not invented.
FAMILY_TYPES: tuple[str, ...] = (
    "g1_sole_parent_two_children_non_beneficiary",
    "g2_couple_two_children_income_abated_both",
    "g3_childless_couple_as_only",
    "g4_single_jobseeker_cap_binds",
    "g5_supported_living_couple_two_children",
    "g6_sole_parent_support_best_start_child",
    "g7_sole_parent_asset_imputation_and_income_reduction",
    "g8_homeowner_wff_only",
    "g9_partner_income_unverified",
)

LIMITATIONS: tuple[str, ...] = (
    "Static costing: households are not assumed to change their behaviour.",
    "Entitlement at full take-up, not expenditure.",
    (
        "Results come from a synthetic population and representative households; "
        "they are not an estimate for New Zealand."
    ),
    "No macroeconomic feedback and no interaction with other taxes or benefits.",
    "Not an official poverty measure.",
    "WFF is annual and the Accommodation Supplement is weekly: they are never added together.",
    "In-work tax credit is not calculated in 2026-27, so there is no Working for Families total.",
)

INTERACTION_NOTE = (
    "No WFF and Accommodation Supplement interaction is modelled: each is run for its own "
    "period, and no WFF amount enters Accommodation Supplement income "
    "(Accommodation Supplement decision DEC-003)."
)
