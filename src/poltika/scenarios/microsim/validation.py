"""v0.2 Task 4.1: population record checks, before anything runs.

Each household gets one status, the worst of its findings:

- `invalid`: it can't run. Its facts don't form a scenario record, or it
  doesn't have exactly one claimant and at most one partner. It is left out
  of every run and counted.
- `needs_review`: it runs, but its record contradicts itself about a fact
  the engines use: `persons` lists a partner while the WFF facts say single,
  or the reverse. Its results are reported as `needs_review` whatever the
  engines return.
- `warning`: it runs normally, but something affects analysis only. A
  grouping characteristic is unknown, so it is left out of that grouping,
  or its dependent-child counts differ between `persons` and the policy
  facts. That can be legitimate, because WFF and the Accommodation
  Supplement define a dependent child differently, so it is reported rather
  than acted on.
- `valid`: no findings.

These are record-consistency checks, not policy rules. Whether a household
qualifies for anything is decided only by the engines.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

from poltika.engines.simulator.wff import PartnerStatus
from poltika.scenarios.population import InvalidHouseholdFacts, dependent_children, scenario_record
from poltika.scenarios.record import ScenarioRecord
from poltika.semantics.population import PersonRole, PopulationDataset, PopulationHousehold


class RecordStatus(str, Enum):
    VALID = "valid"
    WARNING = "warning"
    NEEDS_REVIEW = "needs_review"
    INVALID = "invalid"


_SEVERITY = [
    RecordStatus.VALID,
    RecordStatus.WARNING,
    RecordStatus.NEEDS_REVIEW,
    RecordStatus.INVALID,
]


@dataclass(frozen=True)
class HouseholdValidation:
    household_id: str
    status: RecordStatus
    findings: tuple[tuple[RecordStatus, str], ...]
    record: ScenarioRecord | None  # None iff invalid


@dataclass(frozen=True)
class PopulationValidation:
    households: tuple[HouseholdValidation, ...]
    weights: dict[str, Decimal]

    def by_status(self) -> dict[RecordStatus, tuple[int, Decimal]]:
        """Households and total weight per status, every status present."""
        summary = {s: (0, Decimal(0)) for s in _SEVERITY}
        for h in self.households:
            n, w = summary[h.status]
            summary[h.status] = (n + 1, w + self.weights[h.household_id])
        return summary


def validate_household(household: PopulationHousehold) -> HouseholdValidation:
    findings: list[tuple[RecordStatus, str]] = []
    roles = [p.role for p in household.persons]
    claimants, partners = roles.count(PersonRole.CLAIMANT), roles.count(PersonRole.PARTNER)
    if claimants != 1:
        findings.append((RecordStatus.INVALID, f"{claimants} claimants; exactly one is required"))
    if partners > 1:
        findings.append((RecordStatus.INVALID, f"{partners} partners; at most one is allowed"))

    record: ScenarioRecord | None
    try:
        record = scenario_record(household)
    except InvalidHouseholdFacts as exc:
        record = None
        findings.append((RecordStatus.INVALID, str(exc)))

    if record is not None:
        wff = record.household.wff
        if partners and wff.partner_status is PartnerStatus.SINGLE:
            findings.append(
                (RecordStatus.NEEDS_REVIEW, "persons list a partner; WFF facts say single")
            )
        if not partners and wff.partner_status is PartnerStatus.PARTNERED:
            findings.append(
                (RecordStatus.NEEDS_REVIEW, "WFF facts say partnered; persons list no partner")
            )
        children = dependent_children(household)
        if len(wff.children) != children:
            findings.append(
                (
                    RecordStatus.WARNING,
                    f"persons list {children} dependent children; WFF facts list {len(wff.children)}",
                )
            )
        as_count = record.household.accommodation_supplement.dependent_children_count
        if as_count is not None and as_count != children:
            findings.append(
                (
                    RecordStatus.WARNING,
                    f"persons list {children} dependent children; AS facts count {as_count}",
                )
            )

    characteristics = household.characteristics
    if characteristics.region is None:
        findings.append((RecordStatus.WARNING, "region unknown; left out of regional tables"))
    if characteristics.gross_household_income is None:
        findings.append(
            (RecordStatus.WARNING, "gross household income unknown; left out of deciles")
        )

    status = max((s for s, _ in findings), key=_SEVERITY.index, default=RecordStatus.VALID)
    if status is RecordStatus.INVALID:
        record = None
    return HouseholdValidation(household.household_id, status, tuple(findings), record)


def validate_population(population: PopulationDataset) -> PopulationValidation:
    return PopulationValidation(
        households=tuple(validate_household(h) for h in population.households),
        weights={h.household_id: h.weight for h in population.households},
    )
