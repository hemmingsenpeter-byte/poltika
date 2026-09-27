"""v0.2 Task 9.4: cross-validation against published programme figures.

Compares what the synthetic population's baseline run models (weighted
recipients and entitlement at full take-up) with what Inland Revenue and
MSD publish. Nothing is tuned to close a gap: each row reports both
figures, their ratio and coverage, and the reasons the two are expected to
differ. Published figures are read through a `CanonicalContext`, so this
module never touches a file.

The comparison is deliberately loose. The population is synthetic, the
modelled year (2026-27 rates) is not the published year, and the model
covers only in-work, non-beneficiary households of four types. A ratio far
from one is a finding to explain, not an error to fix.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from poltika.scenarios.microsim.runner import AS_COMPONENT, PopulationRun
from poltika.scenarios.population import scenario_record
from poltika.semantics.population import PopulationDataset
from poltika.semantics.variables import CanonicalContext

_WFF_YEAR = date(2025, 1, 1)  # inside the 2025 tax year (to 31 March 2025)
_AS_QUARTER = date(2026, 5, 1)  # inside the June 2026 quarter

_COMMON = (
    "synthetic development population, not an estimate for New Zealand",
    "modelled at full take-up with 2026-27 rates; the published figure is a different period",
)
_WFF_SCOPE = (
    (
        "the model covers only in-work, non-beneficiary households (assumption A6); "
        "beneficiary families also receive family tax credit"
    ),
    "only four household types are represented, and 'three or more' children count as three (A1)",
    "income, household type and children are drawn independently, so their real correlation is lost",
)
_BEST_START = (
    (
        "only one calculable Best Start child is modelled; other cohorts and several eligible "
        "children are unsupported, not zero"
    ),
    (
        "the published figure includes every cohort, among them children in their first year, "
        "which is exempt from abatement for children born before 1 April 2026 (specification "
        "WFF-06); the model calculates only children born 1 April 2024 to 31 March 2025"
    ),
)
_AS_SCOPE = (
    (
        "the published count covers all ages and every recipient, beneficiaries included, "
        "while the model has only in-work non-beneficiaries (A6)"
    ),
    "homeowners are unsupported in the model (rent or board only)",
    "AS area shares are assumed equal (A5), so caps and entry points are not New Zealand's mix",
)


@dataclass(frozen=True)
class Comparison:
    measure: str
    unit: str
    modelled: Decimal
    published: Decimal
    published_source: str
    covered_weight: Decimal  # weight whose outcome was calculated
    uncovered_weight: Decimal  # weight needs_review or unsupported
    reasons: tuple[str, ...]

    @property
    def ratio(self) -> Decimal:
        return (self.modelled / self.published).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _component(
    run: PopulationRun, component: str
) -> tuple[Decimal, Decimal, Decimal, Decimal, set[str]]:
    """(recipient weight, weighted amount, covered weight, uncovered weight, recipient ids)."""
    recipients = amount = covered = uncovered = Decimal(0)
    ids: set[str] = set()
    for h in run.households:
        base = h.components[component].baseline
        if base.outcome == "calculated" and base.value is not None:
            covered += h.weight
            if base.value > 0:
                recipients += h.weight
                amount += h.weight * base.value
                ids.add(h.household_id)
        else:
            uncovered += h.weight
    return recipients, amount, covered, uncovered, ids


def compare(
    population: PopulationDataset, run: PopulationRun, ctx: CanonicalContext
) -> list[Comparison]:
    def published(variable: str, on: date) -> tuple[Decimal, str]:
        obs = ctx.get(variable, on)
        source = f"{obs.lineage.publication}, {obs.lineage.vintage} ({variable})"
        return obs.value, source

    rows: list[Comparison] = []
    thousand, million = Decimal(1000), Decimal(1_000_000)

    ftc_n, ftc_amount, ftc_cov, ftc_unc, ftc_ids = _component(run, "family_tax_credit")
    value, source = published("wff.families_entitled.family_tax_credit", _WFF_YEAR)
    rows.append(
        Comparison(
            "families with family tax credit",
            "families",
            ftc_n,
            value * thousand,
            source,
            ftc_cov,
            ftc_unc,
            _COMMON + _WFF_SCOPE,
        )
    )
    value, source = published("wff.entitlement.family_tax_credit", _WFF_YEAR)
    rows.append(
        Comparison(
            "family tax credit entitlement",
            "NZD million per year",
            ftc_amount / million,
            value,
            source,
            ftc_cov,
            ftc_unc,
            _COMMON + _WFF_SCOPE,
        )
    )

    children = Decimal(0)
    by_id = {h.household_id: h for h in population.households}
    for h in run.households:
        if h.household_id in ftc_ids:
            children += h.weight * len(
                scenario_record(by_id[h.household_id]).household.wff.children
            )
    value, source = published("wff.children_supported", _WFF_YEAR)
    rows.append(
        Comparison(
            "children in families with family tax credit",
            "children",
            children,
            value * thousand,
            source,
            ftc_cov,
            ftc_unc,
            _COMMON + _WFF_SCOPE,
        )
    )

    bs_n, bs_amount, bs_cov, bs_unc, _ = _component(run, "best_start")
    value, source = published("wff.families_entitled.best_start", _WFF_YEAR)
    rows.append(
        Comparison(
            "families with Best Start",
            "families",
            bs_n,
            value * thousand,
            source,
            bs_cov,
            bs_unc,
            _COMMON + _WFF_SCOPE + _BEST_START,
        )
    )
    value, source = published("wff.entitlement.best_start", _WFF_YEAR)
    rows.append(
        Comparison(
            "Best Start entitlement",
            "NZD million per year",
            bs_amount / million,
            value,
            source,
            bs_cov,
            bs_unc,
            _COMMON + _WFF_SCOPE + _BEST_START,
        )
    )

    as_n, _, as_cov, as_unc, _ = _component(run, AS_COMPONENT)
    value, source = published("accommodation_supplement.recipients", _AS_QUARTER)
    rows.append(
        Comparison(
            "Accommodation Supplement recipients",
            "recipients (households modelled)",
            as_n,
            value,
            source,
            as_cov,
            as_unc,
            _COMMON + _AS_SCOPE,
        )
    )
    return rows


def _fmt(value: Decimal) -> str:
    return f"{value.quantize(Decimal(1), rounding=ROUND_HALF_UP):,}"


def render_markdown(rows: Sequence[Comparison], run: PopulationRun) -> str:
    lines = [
        "# v0.2 cross-validation against published programme figures",
        "",
        f"**{run.label}**",
        "",
        (
            "Generated by `scenarios/microsim/crossval_cli.py` (v0.2 Task 9.4) from the baseline "
            f"run of `{run.population_id}` v{run.population_version} (population "
            f"`{run.population_sha256[:16]}`, results `{run.results_sha256[:16]}`). Nothing here "
            "is tuned: each gap is reported with the reasons it is expected."
        ),
        "",
        "| Measure | Modelled | Published | Modelled / published | Calculated (weight) | Needs review or outside scope (weight) |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        lines.append(
            f"| {r.measure} ({r.unit}) | {_fmt(r.modelled)} | {_fmt(r.published)} | {r.ratio} | "
            f"{_fmt(r.covered_weight)} | {_fmt(r.uncovered_weight)} |"
        )
    lines += ["", "## Sources and reasons", ""]
    for r in rows:
        lines += [f"**{r.measure}.** Published: {r.published_source}.", ""]
        lines += [f"- {reason}" for reason in r.reasons]
        lines.append("")
    return "\n".join(lines)
