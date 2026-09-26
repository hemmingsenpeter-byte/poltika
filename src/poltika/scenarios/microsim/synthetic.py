"""v0.2 Tasks 3.3-3.4: the seeded synthetic development population.

`generate()` builds a `PopulationDataset` from a `SyntheticSpec`. Every
number that describes New Zealand is an input with no default: the shares,
the bands, the household total represented, and every fact asserted about
a synthetic household. The spec's values come from the published tables
Task 3.1 names, acquired as manifested snapshots (3.2), and `sources` lists
them. Nothing here is a claim about New Zealand, and the output always
carries `SYNTHETIC_LABEL`.

**Generator rules.** These are stated methodology, reported with every
population:

- Each household draws its type, then (if it has children) a child count,
  then each child's Best Start cohort, gross income band, tenure, housing
  cost band, AS area, region, claimant category and cash-asset band,
  independently from the spec's marginal shares. Within a band, the amount
  is uniform in whole dollars on `[from, to)`. There is no joint
  calibration or raking (not in v0.2).
- For a couple, `partner_income_share` of the gross income is the
  partner's and the rest the claimant's. WFF family scheme income is the
  gross income. Net family scheme income is not generated, so minimum
  family tax credit reads `needs_review`.
- AS weekly income is gross income / `weekly_income_divisor`, to the cent.
  That is a synthetic mapping between two income definitions (D9), not law.
- Every household has equal weight, `represents / households`.

The same spec (including `seed`) gives a byte-identical population
(`content_sha256`).
"""

from __future__ import annotations

import json
import random
import sys
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from poltika.engines.simulator.accommodation_supplement import (
    Area,
    AsScenario,
    AssessmentWeek,
    ClaimantCategory,
    PartnerType,
    TenureType,
)
from poltika.engines.simulator.outcome import FactStatus
from poltika.engines.simulator.trace import plain
from poltika.engines.simulator.wff import (
    BestStartCohort,
    ChildFacts,
    PartnerStatus,
    VerifiedIncome,
    WffScenario,
)
from poltika.scenarios.combined import CombinedHouseholdScenario
from poltika.scenarios.population import HouseholdType
from poltika.scenarios.record import ScenarioRecord
from poltika.semantics.population import (
    SYNTHETIC_LABEL,
    HouseholdCharacteristics,
    PersonRecord,
    PersonRole,
    PopulationDataset,
    PopulationHousehold,
)

_WITH_CHILDREN = {HouseholdType.SOLE_PARENT.value, HouseholdType.COUPLE_WITH_CHILDREN.value}
_COUPLES = {HouseholdType.COUPLE_WITH_CHILDREN.value, HouseholdType.COUPLE_WITHOUT_CHILDREN.value}


def _check_shares(
    shares: dict[str, Decimal], allowed: set[str] | None, name: str
) -> dict[str, Decimal]:
    if not shares:
        raise ValueError(f"{name}: no shares")
    if allowed is not None and (unknown := sorted(set(shares) - allowed)):
        raise ValueError(f"{name}: unknown keys {unknown}")
    if any(v <= 0 for v in shares.values()):
        raise ValueError(f"{name}: shares must be positive")
    if sum(shares.values()) != 1:
        raise ValueError(f"{name}: shares sum to {sum(shares.values())}, not 1")
    return shares


class Band(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    from_: int = Field(alias="from", ge=0)
    to: int
    share: Decimal = Field(gt=0)

    @model_validator(mode="after")
    def _ordered(self) -> Band:
        if self.to <= self.from_:
            raise ValueError(f"band [{self.from_}, {self.to}) is empty")
        return self


def _check_bands(bands: list[Band], name: str) -> list[Band]:
    if not bands:
        raise ValueError(f"{name}: no bands")
    if sum(b.share for b in bands) != 1:
        raise ValueError(f"{name}: shares sum to {sum(b.share for b in bands)}, not 1")
    return bands


class AssumedFacts(BaseModel):
    """Facts asserted for every synthetic household. Each is an explicit
    assumption, stated in the spec and reported with the population."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    wff_household_eligibility: FactStatus
    extra_instalment_status: FactStatus
    in_work_eligibility: FactStatus
    ftc_iwtc_protected_or_direct_abatement: FactStatus
    mc6a_veterans_payment: FactStatus
    mc6b_disqualifying_payment: FactStatus
    minimum_family_full_time_earner_weeks: FactStatus
    best_start_no_shared_care: FactStatus
    best_start_protected_credit: FactStatus
    child_qualifies_whole_year: FactStatus
    child_best_start_no_disqualifying_payment: FactStatus
    as_household_eligibility: FactStatus
    exempt_cash_asset_status: FactStatus
    ordinary_rate_status: FactStatus
    eldest_dependent_child_under_16: FactStatus
    as_claimant_is_wff_claimant_or_partner: FactStatus


class SyntheticSpec(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    population_id: str
    version: int = Field(ge=1)
    seed: int
    households: int = Field(ge=1)
    represents: Decimal = Field(gt=0)
    sources: tuple[str, ...] = Field(min_length=1)

    household_type: dict[str, Decimal]
    children_count: dict[str, Decimal]
    best_start_cohort: dict[str, Decimal]
    gross_income: list[Band]
    partner_income_share: Decimal = Field(ge=0, le=1)
    weekly_income_divisor: Decimal = Field(gt=0)
    tenure: dict[str, Decimal]
    weekly_housing_cost: list[Band]
    as_area: dict[str, Decimal]
    region: dict[str, Decimal]
    claimant_category: dict[str, Decimal]
    cash_assets: list[Band]
    assumed: AssumedFacts

    wff_lookup_date: date
    as_lookup_date: date
    assessment_week_start: date
    assessment_week_end: date
    requested_wff_policy_version: str
    requested_as_policy_version: str

    @field_validator("household_type")
    @classmethod
    def _types(cls, v: dict[str, Decimal]) -> dict[str, Decimal]:
        return _check_shares(
            v,
            {t.value for t in HouseholdType if t is not HouseholdType.UNCLASSIFIED},
            "household_type",
        )

    @field_validator("children_count")
    @classmethod
    def _children(cls, v: dict[str, Decimal]) -> dict[str, Decimal]:
        if any(not k.isdigit() or int(k) < 1 for k in v):
            raise ValueError("children_count keys must be whole numbers of at least 1")
        return _check_shares(v, None, "children_count")

    @field_validator("best_start_cohort")
    @classmethod
    def _cohort(cls, v: dict[str, Decimal]) -> dict[str, Decimal]:
        return _check_shares(v, {c.value for c in BestStartCohort}, "best_start_cohort")

    @field_validator("tenure")
    @classmethod
    def _tenure(cls, v: dict[str, Decimal]) -> dict[str, Decimal]:
        return _check_shares(v, {t.value for t in TenureType}, "tenure")

    @field_validator("as_area")
    @classmethod
    def _area(cls, v: dict[str, Decimal]) -> dict[str, Decimal]:
        return _check_shares(v, {a.value for a in Area}, "as_area")

    @field_validator("region")
    @classmethod
    def _region(cls, v: dict[str, Decimal]) -> dict[str, Decimal]:
        return _check_shares(v, None, "region")

    @field_validator("claimant_category")
    @classmethod
    def _category(cls, v: dict[str, Decimal]) -> dict[str, Decimal]:
        return _check_shares(v, {c.value for c in ClaimantCategory}, "claimant_category")

    @field_validator("gross_income", "weekly_housing_cost", "cash_assets")
    @classmethod
    def _bands(cls, v: list[Band]) -> list[Band]:
        return _check_bands(v, "bands")


@dataclass(frozen=True)
class CalibrationRow:
    dimension: str
    key: str
    target: Decimal
    generated: Decimal  # weighted share in the generated population


def generate(spec: SyntheticSpec) -> tuple[PopulationDataset, list[CalibrationRow]]:
    rng = random.Random(spec.seed)
    weight = spec.represents / spec.households
    households = []
    drawn: dict[str, dict[str, int]] = {}

    def pick(dimension: str, shares: dict[str, Decimal]) -> str:
        roll = Decimal(repr(rng.random()))
        cumulative = Decimal(0)
        keys = sorted(shares)
        choice = keys[-1]
        for key in keys:
            cumulative += shares[key]
            if roll < cumulative:
                choice = key
                break
        drawn.setdefault(dimension, {}).setdefault(choice, 0)
        drawn[dimension][choice] += 1
        return choice

    def band(dimension: str, bands: list[Band]) -> int:
        index = int(pick(dimension, {str(i): b.share for i, b in enumerate(bands)}))
        b = bands[index]
        return rng.randrange(b.from_, b.to)

    for n in range(spec.households):
        htype = pick("household_type", spec.household_type)
        children = (
            int(pick("children_count", spec.children_count)) if htype in _WITH_CHILDREN else 0
        )
        cohorts = [pick("best_start_cohort", spec.best_start_cohort) for _ in range(children)]
        gross = Decimal(band("gross_income", spec.gross_income))
        tenure = pick("tenure", spec.tenure)
        housing = Decimal(band("weekly_housing_cost", spec.weekly_housing_cost))
        area = pick("as_area", spec.as_area)
        region = pick("region", spec.region)
        category = pick("claimant_category", spec.claimant_category)
        assets = Decimal(band("cash_assets", spec.cash_assets))
        couple = htype in _COUPLES
        record = _record(spec, couple, cohorts, gross, tenure, housing, area, category, assets)
        roles = (
            [PersonRole.CLAIMANT]
            + ([PersonRole.PARTNER] if couple else [])
            + [PersonRole.DEPENDENT_CHILD] * children
        )
        households.append(
            PopulationHousehold(
                household_id=f"s{n:07d}",
                weight=weight,
                persons=tuple(
                    PersonRecord(person_id=f"s{n:07d}p{i}", role=r) for i, r in enumerate(roles)
                ),
                characteristics=HouseholdCharacteristics(
                    region=region, gross_household_income=gross
                ),
                facts=json.loads(json.dumps(plain(record))),
            )
        )

    population = PopulationDataset(
        population_id=spec.population_id,
        version=spec.version,
        synthetic=True,
        label=SYNTHETIC_LABEL,
        households=tuple(households),
    )
    return population, _calibration(spec, drawn)


def _record(
    spec: SyntheticSpec,
    couple: bool,
    cohorts: list[str],
    gross: Decimal,
    tenure: str,
    housing: Decimal,
    area: str,
    category: str,
    assets: Decimal,
) -> ScenarioRecord:
    a = spec.assumed
    partner = (
        (gross * spec.partner_income_share).quantize(Decimal(1), ROUND_HALF_UP) if couple else None
    )
    claimant = gross - (partner or Decimal(0))
    wff = WffScenario(
        household_eligibility=a.wff_household_eligibility,
        extra_instalment_status=a.extra_instalment_status,
        children=[
            ChildFacts(
                qualifies_whole_year=a.child_qualifies_whole_year,
                best_start_cohort=BestStartCohort(c),
                best_start_no_disqualifying_payment=a.child_best_start_no_disqualifying_payment,
            )
            for c in cohorts
        ],
        partner_status=PartnerStatus.PARTNERED if couple else PartnerStatus.SINGLE,
        family_scheme_income=VerifiedIncome(claimant, partner),
        in_work_eligibility=a.in_work_eligibility,
        ftc_iwtc_protected_or_direct_abatement=a.ftc_iwtc_protected_or_direct_abatement,
        mc6a_veterans_payment=a.mc6a_veterans_payment,
        mc6b_disqualifying_payment=a.mc6b_disqualifying_payment,
        minimum_family_full_time_earner_weeks=a.minimum_family_full_time_earner_weeks,
        best_start_no_shared_care=a.best_start_no_shared_care,
        best_start_protected_credit=a.best_start_protected_credit,
    )
    as_ = AsScenario(
        household_eligibility=a.as_household_eligibility,
        claimant_category=ClaimantCategory(category),
        tenure_type=TenureType(tenure),
        partner_status=PartnerType.ORDINARY_COUPLE if couple else PartnerType.SINGLE,
        statistical_area_unit=Area(area),
        weekly_accommodation_costs=housing,
        dependent_children_count=len(cohorts),
        cash_assets=assets,
        exempt_cash_asset_status=a.exempt_cash_asset_status,
        weekly_income=(gross / spec.weekly_income_divisor).quantize(Decimal("0.01"), ROUND_HALF_UP),
        ordinary_rate_status=a.ordinary_rate_status,
        eldest_dependent_child_under_16=a.eldest_dependent_child_under_16,
    )
    return ScenarioRecord(
        household=CombinedHouseholdScenario(
            wff=wff,
            accommodation_supplement=as_,
            as_claimant_is_wff_claimant_or_partner=a.as_claimant_is_wff_claimant_or_partner,
        ),
        wff_lookup_date=spec.wff_lookup_date,
        as_lookup_date=spec.as_lookup_date,
        assessment_week=AssessmentWeek(spec.assessment_week_start, spec.assessment_week_end),
        requested_wff_policy_version=spec.requested_wff_policy_version,
        requested_as_policy_version=spec.requested_as_policy_version,
    )


def _calibration(spec: SyntheticSpec, drawn: dict[str, dict[str, int]]) -> list[CalibrationRow]:
    targets: dict[str, dict[str, Decimal]] = {
        "household_type": spec.household_type,
        "children_count": spec.children_count,
        "best_start_cohort": spec.best_start_cohort,
        "tenure": spec.tenure,
        "as_area": spec.as_area,
        "region": spec.region,
        "claimant_category": spec.claimant_category,
        "gross_income": {str(i): b.share for i, b in enumerate(spec.gross_income)},
        "weekly_housing_cost": {str(i): b.share for i, b in enumerate(spec.weekly_housing_cost)},
        "cash_assets": {str(i): b.share for i, b in enumerate(spec.cash_assets)},
    }
    rows = []
    for dimension, shares in targets.items():
        counts = drawn.get(dimension, {})
        total = sum(counts.values())
        for key in sorted(shares):
            generated = Decimal(counts.get(key, 0)) / total if total else Decimal(0)
            rows.append(CalibrationRow(dimension, key, shares[key], generated))
    return rows


def main(argv: list[str]) -> int:
    """`python -m poltika.scenarios.microsim.synthetic <spec.yaml> <out.json>`
    writes the population and prints its calibration report."""
    if len(argv) != 2:
        sys.stderr.write("usage: synthetic <spec.yaml> <population.json>\n")
        return 2
    spec = SyntheticSpec.model_validate(yaml.safe_load(Path(argv[0]).read_text()))
    population, calibration = generate(spec)
    Path(argv[1]).write_text(population.model_dump_json(indent=None) + "\n")
    sys.stdout.write(
        f"{population.population_id} v{population.version}: {len(population.households)} households\n"
    )
    sys.stdout.write(f"sha256 {population.content_sha256()}\n{SYNTHETIC_LABEL}\n")
    for row in calibration:
        sys.stdout.write(
            f"{row.dimension:20} {row.key:32} target {row.target:<8} generated {row.generated:.4f}\n"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
