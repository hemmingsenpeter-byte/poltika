"""v0.1.5 Phases 3 and 5: deterministic explanations, verified against the
calculation they explain."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal
from typing import Any

import pytest
import yaml

from poltika.engines.assurance.explanation import STEP_TEMPLATES, explain, render_text, verify
from poltika.engines.simulator.outcome import ComponentResult
from poltika.engines.simulator.wff import VerifiedIncome
from poltika.scenarios.record import CodeIdentity, ScenarioRecord, run_scenario
from tests.conftest import AS_POLICY_DIR, WFF_POLICY_DIR
from tests.unit.scenarios.test_scenario_record import GOLDEN_PATH, record_from_yaml

CODE = CodeIdentity("0.1.0", None, None, None)
HOUSEHOLDS = yaml.safe_load(GOLDEN_PATH.read_text())["households"]


def _run(record: ScenarioRecord) -> dict[str, ComponentResult]:
    result = run_scenario(record, WFF_POLICY_DIR, AS_POLICY_DIR, code=CODE).result
    w = result.wff
    return {
        "family_tax_credit": w.family_tax_credit,
        "in_work_tax_credit": w.in_work_tax_credit,
        "minimum_family_tax_credit": w.minimum_family_tax_credit,
        "best_start": w.best_start,
        "accommodation_supplement": result.accommodation_supplement,
    }


def _record(household_id: str) -> ScenarioRecord:
    return record_from_yaml(next(h for h in HOUSEHOLDS if h["id"] == household_id))


@pytest.mark.parametrize("household", HOUSEHOLDS, ids=[h["id"] for h in HOUSEHOLDS])
def test_every_explanation_agrees_with_its_calculation(household: dict[str, Any]) -> None:
    """Task 5.1/5.2: value, outcome and every surfaced number match."""
    for component_id, result in _run(record_from_yaml(household)).items():
        explanation = explain(component_id, result)
        assert verify(explanation, result) == [], (household["id"], component_id)
        assert render_text(explanation).startswith(explanation.summary)


def test_every_step_id_has_a_template() -> None:
    import re
    from pathlib import Path

    source = "".join(
        (Path(__file__).resolve().parents[4] / "src/poltika/engines/simulator" / name).read_text()
        for name in ("wff.py", "accommodation_supplement.py")
    )
    step_ids = set(re.findall(r'"((?:WFF|AS)_[A-Z0-9_]+)", "(?:WFF|AS)-\d+"', source))
    assert step_ids and step_ids <= set(STEP_TEMPLATES)


def test_g2_family_tax_credit_explanation_reads_from_the_trace() -> None:
    ftc = _run(_record("g2_couple_two_children_income_abated_both"))["family_tax_credit"]
    explanation = explain("family_tax_credit", ftc)
    assert explanation.summary == "Family tax credit is $7472.500 a year."
    assert [s.step_id for s in explanation.steps][:2] == ["WFF_FTC_GROSS", "WFF_FTC_INCOME_EXCESS"]
    assert any("family_scheme_income" in a for a in explanation.assumptions)
    assert all("not verified by Poltika" in a for a in explanation.assumptions)
    assert "household_eligibility = verified (" in "\n".join(explanation.assumptions)


def test_a_needs_review_explanation_says_what_is_missing() -> None:
    ftc = _run(_record("g9_partner_income_unverified"))["family_tax_credit"]
    explanation = explain("family_tax_credit", ftc)
    assert explanation.outcome == "needs_review" and explanation.steps == ()
    assert "no amount is produced" in explanation.summary
    assert "Waiting for:" in explanation.summary


def test_evidence_applies_to_the_modelled_period() -> None:
    """Task 5.4: every resolved rate cited was in force on the lookup date."""
    lookup = date(2026, 6, 1)
    for result in _run(_record("g2_couple_two_children_income_abated_both")).values():
        for e in explain("x", result).evidence:
            if e.effective_from is None:
                continue
            assert date.fromisoformat(e.effective_from) <= lookup
            assert e.effective_to is None or lookup < date.fromisoformat(e.effective_to)


def test_a_tampered_step_is_caught() -> None:
    """Task 7.5: an explanation that disagrees with the engine fails."""
    ftc = _run(_record("g2_couple_two_children_income_abated_both"))["family_tax_credit"]
    explanation = explain("family_tax_credit", ftc)
    first = explanation.steps[0]
    tampered = replace(explanation, steps=(replace(first, text=first.text + " Adjusted: $999999."),) + explanation.steps[1:])
    assert verify(tampered, ftc)
    wrong_value = replace(explanation, value="7473.500")
    assert verify(wrong_value, ftc)


def test_changing_income_changes_result_trace_and_explanation_consistently() -> None:
    """Task 5.5: $1,000 more claimant income abates family tax credit by
    exactly the abatement rate, and the explanation follows."""
    record = _record("g2_couple_two_children_income_abated_both")
    wff = record.household.wff
    assert wff.family_scheme_income is not None
    richer_income = VerifiedIncome(
        wff.family_scheme_income.claimant_amount + Decimal(1000), wff.family_scheme_income.partner_amount
    )
    richer = replace(record, household=replace(record.household, wff=replace(wff, family_scheme_income=richer_income)))
    before = _run(record)["family_tax_credit"]
    after = _run(richer)["family_tax_credit"]
    assert before.value is not None and after.value is not None
    rate = next(p.value for p in before.trace.parameters if p.parameter_id == "family_tax_credit_abatement_rate")  # type: ignore[union-attr]
    assert rate is not None
    assert before.value - after.value == rate * 1000
    explained_before, explained_after = explain("family_tax_credit", before), explain("family_tax_credit", after)
    assert explained_before.steps[1].text != explained_after.steps[1].text
    assert verify(explained_after, after) == []


def test_changing_the_area_changes_the_accommodation_supplement_explanation() -> None:
    record = _record("g4_single_jobseeker_cap_binds")
    as_scenario = record.household.accommodation_supplement
    from poltika.engines.simulator.accommodation_supplement import Area

    other = next(a for a in Area if a != as_scenario.statistical_area_unit)
    moved = replace(
        record,
        household=replace(record.household, accommodation_supplement=replace(as_scenario, statistical_area_unit=other)),
    )
    before, after = _run(record)["accommodation_supplement"], _run(moved)["accommodation_supplement"]
    cap_text = [s.text for s in explain("accommodation_supplement", before).steps if s.step_id == "AS_AREA_CAP"]
    cap_text_after = [s.text for s in explain("accommodation_supplement", after).steps if s.step_id == "AS_AREA_CAP"]
    assert cap_text != cap_text_after
    assert verify(explain("accommodation_supplement", after), after) == []


def _spec_case_explanations() -> list[tuple[str, str, ComponentResult]]:
    """Task 7.1: every WFF and AS spec case, one explanation per component
    -- ordinary, boundary, zero, capped, missing-fact and unsupported cases
    alike -- well over 100 explanations."""
    from poltika.engines.simulator.accommodation_supplement import (
        calculate_accommodation_supplement,
    )
    from poltika.engines.simulator.wff import calculate_wff
    from poltika.policy.loader import load_policy_parameters
    from tests.conftest import as_parameters_for_case, as_scenario_from_yaml, load_as_cases
    from tests.unit.engines.simulator.test_wff_spec_cases import (
        _load_spec_cases,
        _scenario_from_yaml,
    )

    cases: list[tuple[str, str, ComponentResult]] = []
    for case in _load_spec_cases():
        lookup = case["modelled_date"]
        lookup = date.fromisoformat(lookup) if isinstance(lookup, str) else lookup
        parameters = load_policy_parameters(WFF_POLICY_DIR, lookup, requested_policy_version=case["policy_version"])
        result = calculate_wff(_scenario_from_yaml(case["scenario"]), parameters)
        for name in ("family_tax_credit", "in_work_tax_credit", "minimum_family_tax_credit", "best_start"):
            cases.append((case["id"], name, getattr(result, name)))
    for case in load_as_cases(AS_POLICY_DIR / "spec_cases.yaml", "spec_cases"):
        result = calculate_accommodation_supplement(as_scenario_from_yaml(case["scenario"]), as_parameters_for_case(case))
        cases.append((case["id"], "accommodation_supplement", result))
    return cases


_SPEC_EXPLANATIONS = _spec_case_explanations()


def test_there_are_over_a_hundred_explanation_fixtures() -> None:
    assert len(_SPEC_EXPLANATIONS) > 100
    outcomes = {result.outcome for _, _, result in _SPEC_EXPLANATIONS}
    assert outcomes == {"calculated", "needs_review", "unsupported"}


@pytest.mark.parametrize(
    ("case_id", "component_id", "result"),
    _SPEC_EXPLANATIONS,
    ids=[f"{c}/{k}" for c, k, _ in _SPEC_EXPLANATIONS],
)
def test_spec_case_explanation_verifies(case_id: str, component_id: str, result: ComponentResult) -> None:
    explanation = explain(component_id, result)
    assert verify(explanation, result) == []
    if result.outcome == "needs_review":
        assert "no amount is produced" in explanation.summary
    if result.outcome == "unsupported":
        assert "is not calculated" in explanation.summary
