"""v0.1.5 Task 2: calculation steps carry the intermediate values, and they
are the values the calculator used -- the last step of every calculated
component is its reported value, and each step's arithmetic re-computes
from its own inputs."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest
import yaml

from poltika.engines.assurance.provenance import build_provenance_report
from poltika.engines.simulator.outcome import ComponentResult
from poltika.engines.simulator.trace import CalculationStep
from poltika.scenarios.record import CodeIdentity, run_scenario
from tests.conftest import AS_POLICY_DIR, WFF_POLICY_DIR
from tests.unit.scenarios.test_scenario_record import GOLDEN_PATH, record_from_yaml

CODE = CodeIdentity("0.1.0", None, None, None)
HOUSEHOLDS = yaml.safe_load(GOLDEN_PATH.read_text())["households"]


def _components(household: dict[str, Any]) -> list[tuple[str, ComponentResult]]:
    result = run_scenario(record_from_yaml(household), WFF_POLICY_DIR, AS_POLICY_DIR, code=CODE).result
    wff = result.original_wff
    return [
        ("family_tax_credit", wff.family_tax_credit),
        ("in_work_tax_credit", wff.in_work_tax_credit),
        ("minimum_family_tax_credit", wff.minimum_family_tax_credit),
        ("best_start", wff.best_start),
        ("accommodation_supplement", result.original_accommodation_supplement),
    ]


def _inputs(step: CalculationStep) -> dict[str, Any]:
    return dict(step.inputs)


# How each step's result follows from its recorded inputs. A step whose
# rule is a floor/cap/choice is checked by that rule, so a step that
# recorded the wrong operand cannot pass.
def _recompute(step: CalculationStep) -> Decimal | None:
    i = _inputs(step)
    zero = Decimal(0)
    match step.step_id:
        case "WFF_FTC_GROSS":
            return i["eldest_child_amount"] + i["additional_child_amount"] * i["additional_children"]
        case "WFF_FTC_INCOME_EXCESS" | "WFF_BS_INCOME_EXCESS":
            return max(zero, i["family_scheme_income"] - i["abatement_threshold"]).to_integral_value(rounding="ROUND_FLOOR")
        case "WFF_FTC_ABATEMENT" | "WFF_BS_ABATEMENT":
            return i["abatement_rate"] * i["income_excess"]
        case "WFF_FTC_NET":
            return max(zero, i["gross_family_tax_credit"] - i["abatement"])
        case "WFF_FTC_REMAINING_ABATEMENT":
            return max(zero, i["abatement"] - i["gross_family_tax_credit"])
        case "WFF_BS_NET":
            return max(zero, i["annual_amount"] - i["abatement"])
        case "WFF_MFTC_TOPUP":
            return max(zero, i["prescribed_amount"] - i["net_family_scheme_income"])
        case "AS_QUALIFYING_COSTS":
            return i["weekly_accommodation_costs"]
        case "AS_COST_EXCESS":
            return i["weekly_qualifying_costs"] - i["entry_threshold"]
        case "AS_SUBSIDY":
            return i["subsidy_rate"] * i["cost_excess"]
        case "AS_AREA_CAP":
            return min(i["subsidy"], i["area_maximum"])
        case "AS_TOTAL_INCOME":
            return i["weekly_income"] + i["imputed_income"]
        case "AS_REDUCED_AMOUNT":
            return max(zero, i["cost_based_amount"] - i["income_reduction"])
        case "AS_ROUNDING":
            return i["amount_before_rounding"].to_integral_value(rounding="ROUND_CEILING")
    return None


@pytest.mark.parametrize("household", HOUSEHOLDS, ids=[h["id"] for h in HOUSEHOLDS])
def test_steps_recompute_and_end_at_the_reported_value(household: dict[str, Any]) -> None:
    for component_id, result in _components(household):
        assert result.trace is not None
        steps = result.trace.steps
        for step in steps:
            expected = _recompute(step)
            if expected is not None:
                assert step.result == expected, (household["id"], component_id, step.step_id)
        if result.outcome != "calculated" or result.value is None:
            continue
        if not steps:
            # A calculated zero reached without arithmetic (e.g. Best Start
            # with every child outside entitlement) carries no steps.
            assert result.value == 0, (household["id"], component_id)
            continue
        if component_id == "family_tax_credit":
            final = next(s for s in steps if s.step_id == "WFF_FTC_NET")
        elif component_id == "accommodation_supplement" and result.value == 0:
            continue
        else:
            final = steps[-1]
        assert final.result == result.value, (household["id"], component_id)


def test_family_tax_credit_steps_for_golden_g2() -> None:
    """g2: two children, $70,000 combined family scheme income."""
    household = next(h for h in HOUSEHOLDS if h["id"] == "g2_couple_two_children_income_abated_both")
    ftc = dict(_components(household))["family_tax_credit"]
    assert ftc.trace is not None
    ids = [s.step_id for s in ftc.trace.steps]
    assert ids == [
        "WFF_FTC_GROSS",
        "WFF_FTC_INCOME_EXCESS",
        "WFF_FTC_ABATEMENT",
        "WFF_FTC_NET",
        "WFF_FTC_REMAINING_ABATEMENT",
    ]
    assert all(s.rule_id == "WFF-03" for s in ftc.trace.steps)


def test_a_component_that_stopped_early_records_no_arithmetic() -> None:
    household = next(h for h in HOUSEHOLDS if h["id"] == "g9_partner_income_unverified")
    ftc = dict(_components(household))["family_tax_credit"]
    assert ftc.outcome == "needs_review"
    assert ftc.trace is not None and ftc.trace.steps == ()


def test_provenance_report_lists_steps_with_resolved_rules() -> None:
    household = next(h for h in HOUSEHOLDS if h["id"] == "g2_couple_two_children_income_abated_both")
    components = _components(household)
    as_result = dict(components)["accommodation_supplement"]
    report = build_provenance_report(AS_POLICY_DIR, {"accommodation_supplement": as_result})
    steps = report["components"][0]["steps"]
    assert steps and steps[-1]["result"] == report["components"][0]["value"]
    assert all(step["rule_summary"] for step in steps)
