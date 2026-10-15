"""Task 7: the income-tax engine's gates and arithmetic.

The band arithmetic is checked against a synthetic parameter set (uppers
10/20/30/40, rates .1-.5), not the statutory candidates, so these tests
assert no tax-law value."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from poltika.engines.simulator import income_tax
from poltika.engines.simulator.income_tax import (
    REQUIRED_PARAMETER_IDS,
    IncomeComposition,
    IncomeTaxScenario,
    ResidenceScope,
    TaxYearBasis,
    basic_tax_band_sum,
    calculate_income_tax,
    run_income_tax_module,
)
from poltika.engines.simulator.outcome import FactStatus
from poltika.engines.simulator.trace import CalculationStep
from poltika.policy.loader import ParameterResolution, PolicyParameterSet

V = FactStatus.VERIFIED
ORDINARY = IncomeTaxScenario(
    individual_status=V,
    residence_scope=ResidenceScope.WHOLE_YEAR_ORDINARY_NZ_RESIDENT,
    tax_year_basis=TaxYearBasis.STANDARD_2026_27,
    income_composition=IncomeComposition.ORDINARY_SALARY_WAGES_ONLY,
    no_deductions_status=V,
    no_available_losses_status=V,
    general_basic_rate_status=V,
    taxable_income_basis_attestation=True,
    annual_taxable_income=Decimal(25),
)
SYNTHETIC = {
    "band_1_upper": "10", "band_2_upper": "20", "band_3_upper": "30", "band_4_upper": "40",
    "band_1_rate": "0.1", "band_2_rate": "0.2", "band_3_rate": "0.3", "band_4_rate": "0.4", "band_5_rate": "0.5",
}


def synthetic(**overrides: ParameterResolution | None) -> PolicyParameterSet:
    resolutions = {
        pid: ParameterResolution(parameter_id=pid, outcome="resolved", value=Decimal(v), review_status="approved")
        for pid, v in SYNTHETIC.items()
    }
    for pid, resolution in overrides.items():
        if resolution is None:
            del resolutions[pid]
        else:
            resolutions[pid] = resolution
    return PolicyParameterSet("income_tax", "synthetic", "0.1", date(2026, 4, 1), resolutions)


@pytest.mark.parametrize(
    ("income", "expected"),
    [
        ("0", "0"),
        ("1", "0.1"),
        ("10", "1.0"),  # band 1 boundary
        ("11", "1.2"),  # first dollar of band 2
        ("25", "4.5"),  # 10x.1 + 10x.2 + 5x.3
        ("40", "10.0"),
        ("41", "10.5"),  # first dollar of the open top band
        ("45", "12.5"),
    ],
)
def test_band_sum_on_synthetic_parameters(income: str, expected: str) -> None:
    assert basic_tax_band_sum(Decimal(income), synthetic()) == Decimal(expected)


def test_band_sum_records_each_band_and_the_total() -> None:
    steps: list[CalculationStep] = []
    total = basic_tax_band_sum(Decimal(25), synthetic(), steps)
    assert [s.step_id for s in steps] == ["IT_BAND_1", "IT_BAND_2", "IT_BAND_3", "IT_BASIC_TAX_SUM"]
    assert [s.result for s in steps] == [Decimal("1.0"), Decimal("2.0"), Decimal("1.5"), total]
    assert dict(steps[2].inputs) == {"dollars_in_band": Decimal(5), "band_rate": Decimal("0.3")}
    assert {s.rule_id for s in steps} == {"IT-05"}


@pytest.mark.parametrize("income", ["-1", "0.5", "10.01"])
def test_band_sum_refuses_non_whole_or_negative_income(income: str) -> None:
    with pytest.raises(ValueError, match="whole-dollar"):
        basic_tax_band_sum(Decimal(income), synthetic())


def test_band_sum_refuses_an_unresolved_parameter() -> None:
    gated = ParameterResolution(parameter_id="band_2_rate", outcome="needs_review", reason="candidate")
    with pytest.raises(ValueError, match="band_2_rate"):
        basic_tax_band_sum(Decimal(25), synthetic(band_2_rate=gated))


def test_approved_parameters_still_stop_at_the_output_precision_gate() -> None:
    # Even with every parameter approved, DEC-004 has no reviewed final-output
    # method, so the supported case returns no amount.
    result = calculate_income_tax(ORDINARY, synthetic())
    assert (result.outcome, result.value, result.code) == ("needs_review", None, "IT_OUTPUT_PRECISION_UNRESOLVED")
    assert income_tax.FINAL_OUTPUT_METHOD_APPROVED is False


def test_known_zero_income_is_gated_not_zero() -> None:
    result = calculate_income_tax(replace(ORDINARY, annual_taxable_income=Decimal(0)), synthetic())
    assert result.outcome == "needs_review" and result.value is None


def test_a_needs_review_parameter_gates_the_component() -> None:
    gated = ParameterResolution(parameter_id="band_3_upper", outcome="needs_review", reason="review_status 'needs_review'")
    result = calculate_income_tax(ORDINARY, synthetic(band_3_upper=gated))
    assert (result.outcome, result.code) == ("needs_review", "IT_PARAMETER_NOT_APPROVED")


def test_a_parameter_with_no_interval_is_unsupported() -> None:
    absent = ParameterResolution(parameter_id="band_5_rate", outcome="unsupported", reason="no interval")
    result = calculate_income_tax(ORDINARY, synthetic(band_5_rate=absent))
    assert (result.outcome, result.code) == ("unsupported", "IT_PARAMETER_NO_INTERVAL")


def test_an_undeclared_parameter_is_unsupported_not_a_key_error() -> None:
    result = calculate_income_tax(ORDINARY, synthetic(band_1_rate=None))
    assert (result.outcome, result.code) == ("unsupported", "IT_PARAMETER_UNDECLARED")


def test_unsupported_outranks_missing_facts_and_every_gate() -> None:
    scenario = replace(
        ORDINARY,
        income_composition=IncomeComposition.MAIN_BENEFIT,
        annual_taxable_income=None,
        individual_status=FactStatus.UNKNOWN,
    )
    for result in (calculate_income_tax(scenario, synthetic()), run_income_tax_module(scenario)):
        assert (result.outcome, result.category, result.code) == (
            "unsupported", "not_modelled", "IT_INCOME_COMPOSITION_NOT_MODELLED",
        )


def test_missing_facts_are_named_in_scenario_order() -> None:
    scenario = replace(ORDINARY, residence_scope=None, annual_taxable_income=None, no_deductions_status=FactStatus.UNKNOWN)
    result = calculate_income_tax(scenario, synthetic())
    assert result.missing_facts == ("residence_scope", "no_deductions_status", "annual_taxable_income")


def test_every_result_from_a_parameter_set_is_traced() -> None:
    for scenario in (ORDINARY, replace(ORDINARY, residence_scope=ResidenceScope.NON_RESIDENT)):
        trace = calculate_income_tax(scenario, synthetic()).trace
        assert trace is not None and trace.component_id == "basic_annual_income_tax"
        assert [p.parameter_id for p in trace.parameters] == list(REQUIRED_PARAMETER_IDS)
        assert len(trace.inputs) == 9 and all(i.asserted_by == "caller" for i in trace.inputs)
        assert trace.steps == () and trace.calculation_rules == ()


def test_the_draft_policy_is_never_loaded_as_executable() -> None:
    result = run_income_tax_module(ORDINARY)
    assert (result.outcome, result.value, result.code) == ("needs_review", None, "IT_POLICY_NOT_APPROVED")
    assert "Q16" in (result.reason or "")


@pytest.mark.parametrize("bad", [Decimal("NaN"), Decimal("Infinity"), 15600.0])
def test_non_finite_or_binary_float_income_is_rejected(bad: object) -> None:
    with pytest.raises(ValueError, match="finite Decimal"):
        replace(ORDINARY, annual_taxable_income=bad)  # type: ignore[arg-type]
