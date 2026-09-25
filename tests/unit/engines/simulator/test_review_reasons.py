"""v0.1.5 Tasks 4.2, 4.4 and 4.6: every result that is not `calculated`
carries a stable reason code; an `unsupported` result says whether it is an
evidenced exclusion or not modelled; a `needs_review` result names the
scenario facts it is waiting for. The human-readable reasons are unchanged."""

from __future__ import annotations

import re
from dataclasses import fields
from datetime import date
from typing import Any

import pytest
import yaml

from poltika.engines.simulator.accommodation_supplement import (
    AsScenario,
    calculate_accommodation_supplement,
)
from poltika.engines.simulator.outcome import ComponentResult
from poltika.engines.simulator.wff import ChildFacts, WffScenario, calculate_wff
from poltika.policy.loader import load_policy_parameters
from poltika.scenarios.record import CodeIdentity, run_scenario
from tests.conftest import (
    AS_POLICY_DIR,
    WFF_POLICY_DIR,
    as_parameters_for_case,
    as_scenario_from_yaml,
    load_as_cases,
)
from tests.unit.engines.simulator.test_wff_spec_cases import _load_spec_cases, _scenario_from_yaml
from tests.unit.scenarios.test_scenario_record import GOLDEN_PATH, record_from_yaml

_CODE = re.compile(r"^[A-Z][A-Z0-9_]+$")
_WFF_FACTS = {f.name for f in fields(WffScenario)} | {f"children.{f.name}" for f in fields(ChildFacts)} | {
    "family_scheme_income.partner_amount"
}
_AS_FACTS = {f.name for f in fields(AsScenario)}


def _check(result: ComponentResult, known_facts: set[str], where: str) -> None:
    if result.outcome == "calculated":
        assert (result.code, result.category, result.missing_facts) == (None, None, ()), where
        return
    assert result.code is not None and _CODE.match(result.code), where
    assert result.reason, where
    if result.outcome == "unsupported":
        assert result.category in ("evidenced_exclusion", "not_modelled"), where
    else:
        assert result.category is None, where
    assert set(result.missing_facts) <= known_facts, (where, result.missing_facts)


_WFF_CASES = _load_spec_cases()


@pytest.mark.parametrize("case", _WFF_CASES, ids=[c["id"] for c in _WFF_CASES])
def test_wff_spec_case_reasons_are_structured(case: dict[str, Any]) -> None:
    modelled_date = case["modelled_date"]
    if isinstance(modelled_date, str):
        modelled_date = date.fromisoformat(modelled_date)
    parameters = load_policy_parameters(WFF_POLICY_DIR, modelled_date, requested_policy_version=case["policy_version"])
    result = calculate_wff(_scenario_from_yaml(case["scenario"]), parameters)
    for f in fields(result):
        _check(getattr(result, f.name), _WFF_FACTS, f"{case['id']}/{f.name}")


_AS_CASES = load_as_cases(AS_POLICY_DIR / "spec_cases.yaml", "spec_cases")


@pytest.mark.parametrize("case", _AS_CASES, ids=[c["id"] for c in _AS_CASES])
def test_as_spec_case_reasons_are_structured(case: dict[str, Any]) -> None:
    result = calculate_accommodation_supplement(as_scenario_from_yaml(case["scenario"]), as_parameters_for_case(case))
    _check(result, _AS_FACTS, case["id"])


def test_golden_household_reasons_are_structured() -> None:
    for household in yaml.safe_load(GOLDEN_PATH.read_text())["households"]:
        run = run_scenario(record_from_yaml(household), WFF_POLICY_DIR, AS_POLICY_DIR, code=CodeIdentity("0", None, None, None))
        for f in fields(run.result.wff):
            _check(getattr(run.result.wff, f.name), _WFF_FACTS, f"{household['id']}/{f.name}")
        _check(run.result.accommodation_supplement, _AS_FACTS, household["id"])


def _as_case(case_id: str) -> ComponentResult:
    case = next(c for c in _AS_CASES if c["id"] == case_id)
    return calculate_accommodation_supplement(as_scenario_from_yaml(case["scenario"]), as_parameters_for_case(case))


def test_assets_over_the_ceiling_is_an_evidenced_exclusion() -> None:
    result = _as_case("asset_ceiling_exceeded_is_unsupported")
    assert (result.code, result.category) == ("AS_ASSETS_OVER_CEILING", "evidenced_exclusion")


def test_an_unverified_partner_status_names_the_missing_fact() -> None:
    household = next(
        h for h in yaml.safe_load(GOLDEN_PATH.read_text())["households"] if h["id"] == "g9_partner_income_unverified"
    )
    run = run_scenario(record_from_yaml(household), WFF_POLICY_DIR, AS_POLICY_DIR, code=CodeIdentity("0", None, None, None))
    ftc = run.result.original_wff.family_tax_credit
    assert ftc.outcome == "needs_review"
    assert ftc.missing_facts in (("partner_status",), ("family_scheme_income.partner_amount",))
