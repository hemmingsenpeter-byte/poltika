"""Pass 1, BUILD_PLAN_v0_3.md Task 1.3: the byte-identical proof.

Every existing-format input is put into the canonical `Household`, mapped
back to the engines' input types, and run. The mapped scenario must equal the
original (the engines are pure functions of scenario and parameters, so equal
inputs give equal results); for combined households the result is also run
through `run_scenario` and the scenario id, result payload and result id are
compared. Inputs that cannot round-trip are listed below with the reason, so
a new refusal fails the test instead of passing silently.

Sources: the nine golden households and the interaction spec cases (combined),
the WFF spec cases and benchmarks (WFF only) and the AS spec cases and
benchmarks (AS only). Protected files are only read.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import pytest
import yaml

from poltika.engines.simulator.accommodation_supplement import (
    AsScenario,
    AssessmentWeek,
    calculate_accommodation_supplement,
)
from poltika.engines.simulator.outcome import FactStatus
from poltika.engines.simulator.wff import WffScenario, calculate_wff
from poltika.policy.loader import load_policy_parameters
from poltika.scenarios.combined import CombinedHouseholdScenario
from poltika.scenarios.household_mappings import (
    AdapterRefused,
    MappingRefusal,
    household_from_as,
    household_from_combined,
    household_from_record,
    household_from_wff,
    to_as,
    to_combined,
    to_wff,
)
from poltika.scenarios.record import (
    CodeIdentity,
    ScenarioRecord,
    canonical_json,
    result_payload,
    run_scenario,
    scenario_id,
)
from poltika.semantics.household import DatePeriod
from tests.conftest import (
    AS_POLICY_DIR,
    AS_POLICY_VERSION,
    WFF_POLICY_DIR,
    as_parameters_for_case,
    as_scenario_from_yaml,
    load_as_cases,
    wff_scenario_from_yaml,
)

ROOT = Path(__file__).resolve().parents[3]
INTERACTION_DIR = ROOT / "policy_specs" / "wff_as_interaction"
LOOKUP = date(2026, 6, 1)
WEEK = AssessmentWeek(start=date(2026, 6, 1), end=date(2026, 6, 8))
TAX_YEAR = DatePeriod(start=date(2026, 4, 1), end=date(2027, 4, 1))
CODE = CodeIdentity(package_version="test", source_commit=None, source_tree_clean=None, dependency_lock_sha256=None)

# Combined inputs the household cannot hold as one set of facts: the two
# halves assert one fact two ways. case id -> the reason the adapter gives
# (a substring). The old path keeps catching these through the pairwise
# checks, which Task 1.4 does not yet retire (backlog P2-HH-02).
COMBINED_REFUSALS: dict[str, str] = {
    # WFF lists 1 child, AS asserts 2: the second child has no WFF facts, so
    # a household holding both would change the WFF input.
    "interaction:disagreement_keeps_existing_unsupported_components": "more than WFF lists",
}


def _yaml(path: Path, key: str) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = yaml.safe_load(path.read_text())[key]
    return cases


def _combined(case: dict[str, Any]) -> CombinedHouseholdScenario:
    return CombinedHouseholdScenario(
        wff=wff_scenario_from_yaml(case["wff"]),
        accommodation_supplement=as_scenario_from_yaml(case["accommodation_supplement"]),
        as_claimant_is_wff_claimant_or_partner=FactStatus(case["precondition"]),
    )


def _record(combined: CombinedHouseholdScenario) -> ScenarioRecord:
    return ScenarioRecord(
        household=combined,
        wff_lookup_date=LOOKUP,
        as_lookup_date=LOOKUP,
        assessment_week=WEEK,
        requested_wff_policy_version="0.1.0",
        requested_as_policy_version=AS_POLICY_VERSION,
    )


_COMBINED = [
    *((f"golden:{h['id']}", h) for h in _yaml(INTERACTION_DIR / "golden_households.yaml", "households")),
    *((f"interaction:{c['id']}", c) for c in _yaml(INTERACTION_DIR / "spec_cases.yaml", "interaction_cases")),
]


@pytest.mark.parametrize("name,case", _COMBINED, ids=[n for n, _ in _COMBINED])
def test_combined_input_round_trips_with_identical_results(name: str, case: dict[str, Any]) -> None:
    combined = _combined(case)
    if name in COMBINED_REFUSALS:
        with pytest.raises(AdapterRefused, match=COMBINED_REFUSALS[name]):
            household_from_combined(combined, household_id="h1", tax_year=TAX_YEAR, assessment_week=WEEK)
        return
    household = household_from_combined(combined, household_id="h1", tax_year=TAX_YEAR, assessment_week=WEEK)
    mapped = to_combined(household, TAX_YEAR, WEEK)
    assert not isinstance(mapped, MappingRefusal), mapped
    assert mapped == combined

    direct = run_scenario(_record(combined), WFF_POLICY_DIR, AS_POLICY_DIR, code=CODE)
    via_household = run_scenario(_record(mapped), WFF_POLICY_DIR, AS_POLICY_DIR, code=CODE)
    assert via_household.scenario_id == direct.scenario_id == scenario_id(_record(combined))
    assert canonical_json(result_payload(via_household.result)) == canonical_json(result_payload(direct.result))
    assert via_household.result_id == direct.result_id
    # The stored-record adapter reaches the same household.
    assert household_from_record(_record(combined), household_id="h1", tax_year=TAX_YEAR) == household


def test_every_listed_refusal_is_a_real_case() -> None:
    assert set(COMBINED_REFUSALS) <= {n for n, _ in _COMBINED}


_WFF_ONLY = [
    *((f"spec:{c['id']}", c) for c in _yaml(WFF_POLICY_DIR / "spec_cases.yaml", "spec_cases")),
    *((f"benchmark:{c['id']}", c) for c in _yaml(WFF_POLICY_DIR / "benchmarks.yaml", "benchmarks")),
]
# WFF-only inputs that cannot round-trip: name -> reason.
WFF_REFUSALS: dict[str, str] = {}


@pytest.mark.parametrize("name,case", _WFF_ONLY, ids=[n for n, _ in _WFF_ONLY])
def test_wff_only_input_round_trips(name: str, case: dict[str, Any]) -> None:
    original = wff_scenario_from_yaml(case["scenario"])
    if name in WFF_REFUSALS:
        with pytest.raises(AdapterRefused, match=WFF_REFUSALS[name]):
            household_from_wff(original, household_id="h1", tax_year=TAX_YEAR)
        return
    mapped = to_wff(household_from_wff(original, household_id="h1", tax_year=TAX_YEAR), TAX_YEAR)
    assert isinstance(mapped, WffScenario)
    assert mapped == original
    if name.startswith("spec:"):
        modelled = case["modelled_date"]
        modelled = date.fromisoformat(modelled) if isinstance(modelled, str) else modelled
        parameters = load_policy_parameters(
            WFF_POLICY_DIR, modelled, requested_policy_version=case["policy_version"]
        )
        assert calculate_wff(mapped, parameters) == calculate_wff(original, parameters)


_AS_ONLY = [
    *((f"spec:{c['id']}", c) for c in load_as_cases(AS_POLICY_DIR / "spec_cases.yaml", "spec_cases")),
    *((f"benchmark:{c['id']}", c) for c in load_as_cases(AS_POLICY_DIR / "benchmarks.yaml", "benchmarks")),
]
AS_REFUSALS: dict[str, str] = {}


@pytest.mark.parametrize("name,case", _AS_ONLY, ids=[n for n, _ in _AS_ONLY])
def test_as_only_input_round_trips(name: str, case: dict[str, Any]) -> None:
    original = as_scenario_from_yaml(case["scenario"])
    if name in AS_REFUSALS:
        with pytest.raises(AdapterRefused, match=AS_REFUSALS[name]):
            household_from_as(original, household_id="h1", assessment_week=WEEK)
        return
    mapped = to_as(household_from_as(original, household_id="h1", assessment_week=WEEK), WEEK)
    assert isinstance(mapped, AsScenario)
    assert mapped == original
    parameters = as_parameters_for_case(case)
    assert calculate_accommodation_supplement(mapped, parameters) == calculate_accommodation_supplement(
        original, parameters
    )


def test_a_spell_longer_than_the_policy_period_is_refused_not_scaled() -> None:
    from decimal import Decimal

    from poltika.semantics import household as hh

    base = household_from_as(
        as_scenario_from_yaml(_AS_ONLY[0][1]["scenario"]), household_id="h1", assessment_week=WEEK
    )
    long_year = hh.IncomeSpell(
        person_id="claimant",
        income_type=hh.IncomeType.UNSPLIT_TOTAL,
        start=date(2025, 4, 1),
        end=date(2027, 4, 1),
        amount=Decimal(100000),
        basis=hh.IncomeBasis.WFF_FAMILY_SCHEME,
    )
    longer = base.model_copy(update={"income_spells": (long_year,)})
    wff = to_wff(longer, TAX_YEAR)
    assert isinstance(wff, MappingRefusal) and "Q10" in wff.reason
    annual = long_year.model_copy(
        update={"basis": hh.IncomeBasis.AS_CHARGEABLE_WEEKLY, "amount": Decimal(36500)}
    )
    as_ = to_as(base.model_copy(update={"income_spells": (annual,)}), WEEK)
    assert isinstance(as_, MappingRefusal) and "Q10" in as_.reason
