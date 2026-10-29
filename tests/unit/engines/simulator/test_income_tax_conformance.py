"""Phase C Task 12: conformance tests for the income-tax slice.

Each test cites the specification rule (`policy_specs/income_tax/specification.md`,
IT-01 to IT-08 and the calculation sequence) and the matrix row in
`reviews/2026-10-29-income-tax-conformance-matrix.md`. They assert outcome
states, reason codes, missing-fact names, refusal ordering, the absence of
any amount and trace fields while every income-tax value is draft
`needs_review`. None asserts a statutory dollar figure, none runs the
statutory candidate values, and none changes a protected expected value
(`doctrine/test-doctrine.md`). The few incomes used with approved parameters
run against the synthetic set in `test_income_tax.py`, not the statute.
Income tax is not exposed on the API, so these are engine-level tests.
"""

from __future__ import annotations

import re
from dataclasses import fields, replace
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

from poltika.common.errors import PolicyNotApprovedError, PolicyVersionMismatchError
from poltika.engines.simulator import income_tax
from poltika.engines.simulator.income_tax import (
    POLICY_DIR,
    REQUIRED_PARAMETER_IDS,
    IncomeComposition,
    IncomeTaxScenario,
    ResidenceScope,
    TaxYearBasis,
    calculate_income_tax,
    run_income_tax_module,
)
from poltika.engines.simulator.outcome import FactStatus
from poltika.policy.loader import load_policy_parameters, load_policy_spec
from poltika.scenarios.household_mappings import INCOME_TAX_YEAR_2026_27, run_household_income_tax
from poltika.semantics import household as hh
from tests.unit.engines.simulator.test_income_tax import ORDINARY, synthetic
from tests.unit.engines.simulator.test_income_tax_spec_cases import _CASES, scenario_from_yaml
from tests.unit.scenarios.test_household_income_tax import _IN_SLICE, _couple, _spell

U = FactStatus.UNKNOWN
X = FactStatus.EXCLUDED
# Every fact unknown: a known exclusion set on this must still be reported as
# itself, so each exclusion is checked against the weakest possible context.
ALL_UNKNOWN = IncomeTaxScenario(
    individual_status=U,
    residence_scope=None,
    tax_year_basis=None,
    income_composition=None,
    no_deductions_status=U,
    no_available_losses_status=U,
    general_basic_rate_status=U,
    taxable_income_basis_attestation=None,
    annual_taxable_income=None,
)

# Every refusal and reason code the engine emits (IT_*) and the household
# mapping emits (HOUSEHOLD_*), with the outcome that carries it.
ENGINE_CODES = {
    "IT_NOT_NATURAL_PERSON": "unsupported",
    "IT_RESIDENCE_NOT_MODELLED": "unsupported",
    "IT_TAX_YEAR_NOT_MODELLED": "unsupported",
    "IT_INCOME_COMPOSITION_NOT_MODELLED": "unsupported",
    "IT_DEDUCTIONS_NOT_MODELLED": "unsupported",
    "IT_LOSSES_NOT_MODELLED": "unsupported",
    "IT_SPECIAL_BASIC_RATE_NOT_MODELLED": "unsupported",
    "IT_NEGATIVE_INCOME_NOT_MODELLED": "unsupported",
    "IT_FRACTIONAL_INCOME_NOT_MODELLED": "unsupported",
    "IT_PARAMETER_UNDECLARED": "unsupported",
    "IT_PARAMETER_NO_INTERVAL": "unsupported",
    "IT_DATE_OUTSIDE_REFERENCE_PERIOD": "unsupported",
    "IT_FACTS_UNVERIFIED": "needs_review",
    "IT_TAXABLE_INCOME_NOT_ATTESTED": "needs_review",
    "IT_PARAMETER_NOT_APPROVED": "needs_review",
    "IT_OUTPUT_PRECISION_UNRESOLVED": "needs_review",
    "IT_POLICY_NOT_APPROVED": "needs_review",
}

# (scenario override, code): one known fact outside the slice (IT-01 to IT-05, Q17).
EXCLUSIONS: list[tuple[dict[str, Any], str]] = [
    ({"individual_status": X}, "IT_NOT_NATURAL_PERSON"),
    ({"residence_scope": ResidenceScope.NON_RESIDENT}, "IT_RESIDENCE_NOT_MODELLED"),
    ({"residence_scope": ResidenceScope.CHANGING_RESIDENCE}, "IT_RESIDENCE_NOT_MODELLED"),
    ({"residence_scope": ResidenceScope.SPECIAL_RESIDENCE_REGIME}, "IT_RESIDENCE_NOT_MODELLED"),
    ({"tax_year_basis": TaxYearBasis.NON_STANDARD_YEAR}, "IT_TAX_YEAR_NOT_MODELLED"),
    ({"tax_year_basis": TaxYearBasis.OTHER_STANDARD_YEAR}, "IT_TAX_YEAR_NOT_MODELLED"),
    *[
        ({"income_composition": member}, "IT_INCOME_COMPOSITION_NOT_MODELLED")
        for member in IncomeComposition
        if member is not IncomeComposition.ORDINARY_SALARY_WAGES_ONLY
    ],
    ({"no_deductions_status": X}, "IT_DEDUCTIONS_NOT_MODELLED"),
    ({"no_available_losses_status": X}, "IT_LOSSES_NOT_MODELLED"),
    ({"general_basic_rate_status": X}, "IT_SPECIAL_BASIC_RATE_NOT_MODELLED"),
    ({"annual_taxable_income": Decimal(-1)}, "IT_NEGATIVE_INCOME_NOT_MODELLED"),
    ({"annual_taxable_income": Decimal("0.5")}, "IT_FRACTIONAL_INCOME_NOT_MODELLED"),
]
_IDS = [f"{code}-{n}" for n, (_, code) in enumerate(EXCLUSIONS)]


def _assert_refused_without_amount(result: Any, outcome: str, code: str) -> None:
    assert (result.outcome, result.code, result.value) == (outcome, code, None)
    assert result.trace is not None and result.trace.steps == ()


# ---------------------------------------------------------------- IT-01 to IT-05, Q17


@pytest.mark.parametrize(("override", "code"), EXCLUSIONS, ids=_IDS)
def test_it01_05_each_known_exclusion_is_unsupported_with_its_own_code(
    override: dict[str, Any], code: str
) -> None:
    # Matrix IT-01 to IT-05, outcome codes. The spec cases pin outcome and category only.
    result = run_income_tax_module(replace(ORDINARY, **override))
    _assert_refused_without_amount(result, "unsupported", code)
    assert (result.category, result.missing_facts) == ("not_modelled", ())


@pytest.mark.parametrize(("override", "code"), EXCLUSIONS, ids=_IDS)
def test_precedence_each_exclusion_outranks_every_missing_fact(
    override: dict[str, Any], code: str
) -> None:
    # Spec "Input and outcome contract": `unsupported` outranks `needs_review`.
    result = run_income_tax_module(replace(ALL_UNKNOWN, **override))
    _assert_refused_without_amount(result, "unsupported", code)
    assert result.missing_facts == ()


def test_the_exclusion_table_covers_every_out_of_slice_enum_member() -> None:
    # A new enum member must be classified here, not fall through to a gate.
    for enum_type, field_name, slice_member in (
        (ResidenceScope, "residence_scope", ResidenceScope.WHOLE_YEAR_ORDINARY_NZ_RESIDENT),
        (TaxYearBasis, "tax_year_basis", TaxYearBasis.STANDARD_2026_27),
        (IncomeComposition, "income_composition", IncomeComposition.ORDINARY_SALARY_WAGES_ONLY),
    ):
        for member in enum_type:
            result = run_income_tax_module(replace(ORDINARY, **{field_name: member}))
            if member is slice_member:
                assert (result.outcome, result.code) == ("needs_review", "IT_POLICY_NOT_APPROVED")
            else:
                assert result.outcome == "unsupported", member
                assert any(override == {field_name: member} for override, _ in EXCLUSIONS), member


def test_every_engine_reason_code_is_listed_with_its_outcome() -> None:
    source = Path(income_tax.__file__).read_text()
    emitted = set(re.findall(r'"(IT_[A-Z0-9_]+)"', source))
    # IT_BAND_n and IT_BASIC_TAX_SUM are calculation step ids, not result codes.
    emitted = {c for c in emitted if not c.startswith(("IT_BAND_", "IT_BASIC_TAX_SUM"))}
    assert emitted == set(ENGINE_CODES)


# ---------------------------------------------------------------- never-zero, missing facts


@pytest.mark.parametrize(
    ("field_name", "unknown"),
    [
        ("individual_status", U),
        ("residence_scope", None),
        ("tax_year_basis", None),
        ("income_composition", None),
        ("no_deductions_status", U),
        ("no_available_losses_status", U),
        ("general_basic_rate_status", U),
        ("taxable_income_basis_attestation", None),
        ("annual_taxable_income", None),
    ],
)
def test_it01_08_each_unknown_fact_is_named_and_no_other_is(
    field_name: str, unknown: object
) -> None:
    result = run_income_tax_module(replace(ORDINARY, **{field_name: unknown}))
    _assert_refused_without_amount(result, "needs_review", "IT_FACTS_UNVERIFIED")
    assert result.missing_facts == (field_name,)
    assert result.category is None
    use = next(u for u in result.trace.inputs if u.name == field_name)  # type: ignore[union-attr]
    assert use.value is None or use.value is U  # recorded as unknown, never as zero or a default


def test_it02_an_unknown_amount_is_not_a_known_zero_in_the_trace() -> None:
    unknown = run_income_tax_module(replace(ORDINARY, annual_taxable_income=None))
    zero = run_income_tax_module(replace(ORDINARY, annual_taxable_income=Decimal(0)))
    assert (unknown.code, zero.code) == ("IT_FACTS_UNVERIFIED", "IT_POLICY_NOT_APPROVED")
    assert unknown.value is None and zero.value is None
    assert (
        unknown.trace and zero.trace and unknown.trace.scenario_sha256 != zero.trace.scenario_sha256
    )


def test_all_facts_unknown_names_every_fact_in_scenario_order() -> None:
    result = run_income_tax_module(ALL_UNKNOWN)
    assert result.missing_facts == (
        "individual_status",
        "residence_scope",
        "tax_year_basis",
        "income_composition",
        "no_deductions_status",
        "no_available_losses_status",
        "general_basic_rate_status",
        "taxable_income_basis_attestation",
        "annual_taxable_income",
    )


@pytest.mark.parametrize("bad", [15600, "15600", True])
def test_request_validation_rejects_non_decimal_income(bad: object) -> None:
    # Spec handoff: malformed numeric transport is rejected, never coerced.
    with pytest.raises(ValueError, match="finite Decimal"):
        replace(ORDINARY, annual_taxable_income=bad)  # type: ignore[arg-type]


# ---------------------------------------------------------------- gates while values are draft


def test_calculation_step3_every_spec_case_is_gated_with_no_amount_and_no_candidate_value() -> None:
    # Spec sequence step 3: the pending gates stop a numeric result. Neither a
    # step nor a parameter value reaches any of the 47 draft spec cases.
    for case in _CASES:
        result = run_income_tax_module(scenario_from_yaml(case["scenario"]))
        assert result.outcome in ("needs_review", "unsupported"), case["id"]
        assert result.value is None, case["id"]
        trace = result.trace
        assert trace is not None, case["id"]
        assert trace.steps == () and trace.calculation_rules == (), case["id"]
        assert [p.parameter_id for p in trace.parameters] == list(REQUIRED_PARAMETER_IDS), case[
            "id"
        ]
        assert all(p.value is None for p in trace.parameters), case["id"]


def test_the_draft_policy_state_gates_every_value() -> None:
    # Gates: protected values, annual authority, DEC-004. When Pete approves
    # a value this test must be revisited deliberately, not edited around.
    spec = load_policy_spec(POLICY_DIR / "policy.yaml")
    assert spec.status.value == "draft_pending_review" and spec.policy_version is None
    declared = {p.id: p for p in spec.parameters}
    assert set(REQUIRED_PARAMETER_IDS) <= set(declared)
    for parameter_id in REQUIRED_PARAMETER_IDS:
        for value in declared[parameter_id].values:
            assert value.review_status.value == "needs_review", parameter_id
            assert (value.effective_from, value.effective_to) == (
                spec.reference_period.from_,
                spec.reference_period.to,
            )
    assert income_tax.FINAL_OUTPUT_METHOD_APPROVED is False
    benchmarks = yaml.safe_load((POLICY_DIR / "benchmarks.yaml").read_text())
    assert benchmarks["benchmarks"] == [] and benchmarks["benchmark_status"] == "missing_source"
    assert benchmarks["policy_version"] is None


def test_the_loader_refuses_the_draft_policy_as_executable() -> None:
    with pytest.raises(PolicyNotApprovedError):
        load_policy_parameters(POLICY_DIR, date(2026, 4, 1))


@pytest.mark.parametrize("income", ["0", "1", "25", "41", "10000000"])
def test_it08_fully_approved_synthetic_parameters_still_give_no_amount(income: str) -> None:
    # DEC-004: with every band parameter approved, only the output-precision
    # gate remains, and it holds for every supported income.
    result = calculate_income_tax(
        replace(ORDINARY, annual_taxable_income=Decimal(income)), synthetic()
    )
    _assert_refused_without_amount(result, "needs_review", "IT_OUTPUT_PRECISION_UNRESOLVED")
    assert result.missing_facts == ()
    assert "DEC-004" in (result.reason or "")


def test_it06_the_policy_gate_names_the_annual_authority_questions() -> None:
    result = run_income_tax_module(ORDINARY)
    _assert_refused_without_amount(result, "needs_review", "IT_POLICY_NOT_APPROVED")
    assert "Q16" in (result.reason or "") and "DEC-001" in (result.reason or "")
    assert result.missing_facts == ()  # a server gate, not a fact the caller can supply


def test_it06_no_caller_assertion_clears_the_server_gates() -> None:
    # Every assertion at its most favourable still stops at the policy gate.
    result = run_income_tax_module(ORDINARY)
    assert (result.outcome, result.value) == ("needs_review", None)
    assert {f.name for f in fields(IncomeTaxScenario)}.isdisjoint(
        {
            "annual_authority",
            "policy_approved",
            "output_precision",
            "authority_status",
            "precision_status",
        }
    )


# ---------------------------------------------------------------- refusal ordering


@pytest.mark.parametrize(
    "scenario",
    [ORDINARY, replace(ORDINARY, residence_scope=ResidenceScope.NON_RESIDENT), ALL_UNKNOWN],
    ids=["supported", "unsupported", "missing_facts"],
)
@pytest.mark.parametrize("requested", ["0.1.0", "1", ""])
def test_a_version_mismatch_is_raised_before_any_refusal_result(
    scenario: IncomeTaxScenario, requested: str
) -> None:
    # The draft policy holds no version, so no requested version matches it.
    with pytest.raises(PolicyVersionMismatchError):
        run_income_tax_module(scenario, requested_policy_version=requested)


def test_it02_a_date_outside_the_period_is_traced_and_carries_no_missing_facts() -> None:
    result = run_income_tax_module(ALL_UNKNOWN, modelled_date=date(2027, 4, 1))
    _assert_refused_without_amount(result, "unsupported", "IT_DATE_OUTSIDE_REFERENCE_PERIOD")
    assert (result.category, result.missing_facts) == ("not_modelled", ())
    assert result.trace is not None
    assert result.trace.modelled_date == date(2027, 4, 1)
    assert result.trace.assessment_period == (date(2026, 4, 1), date(2027, 4, 1))


def test_calculation_step5_every_refusal_trace_names_the_policy_state_and_caller_assertions() -> (
    None
):
    for scenario in (ORDINARY, ALL_UNKNOWN, replace(ORDINARY, individual_status=X)):
        trace = run_income_tax_module(scenario).trace
        assert trace is not None
        assert (trace.component_id, trace.policy_id) == ("basic_annual_income_tax", "income_tax")
        assert trace.policy_version == "none (draft_pending_review)"
        assert {i.name for i in trace.inputs} == {f.name for f in fields(IncomeTaxScenario)}
        assert {i.asserted_by for i in trace.inputs} == {"caller"}
        assert trace.scenario_sha256 and trace.artifact_sha256


def test_the_trace_identity_follows_the_scenario() -> None:
    first = run_income_tax_module(ORDINARY).trace
    again = run_income_tax_module(ORDINARY).trace
    other = run_income_tax_module(replace(ORDINARY, annual_taxable_income=Decimal(26))).trace
    assert first and again and other
    assert first.scenario_sha256 == again.scenario_sha256 != other.scenario_sha256


# ---------------------------------------------------------------- household mapping


def test_household_several_spells_is_a_traced_needs_review_with_no_amount() -> None:
    mid = date(2026, 10, 1)
    year = INCOME_TAX_YEAR_2026_27
    household = _couple(_spell("a", year.start, mid, "1"), _spell("a", mid, year.end, "1"))
    result = run_household_income_tax(household, "a", tax_year=year)
    _assert_refused_without_amount(result, "needs_review", "HOUSEHOLD_MAPPING_INVALID_FACTS")
    income_use = next(u for u in result.trace.inputs if u.name == "annual_taxable_income")  # type: ignore[union-attr]
    assert income_use.value is None  # no part is summed and none becomes zero
    assert result.trace.assessment_period == (year.start, year.end)  # type: ignore[union-attr]


@pytest.mark.parametrize(("override", "code"), EXCLUSIONS[:6], ids=_IDS[:6])
def test_household_a_known_exclusion_keeps_its_engine_code(
    override: dict[str, Any], code: str
) -> None:
    # The household path reports the engine's own code for a held exclusion.
    facts_override: dict[str, Any] = {}
    if "individual_status" in override:
        facts_override["individual_status"] = hh.Assertion.EXCLUDED
    if "residence_scope" in override:
        facts_override["residence_scope"] = hh.TaxResidenceScope(override["residence_scope"].value)
    if "tax_year_basis" in override:
        facts_override["tax_year_basis"] = hh.TaxYearBasis(override["tax_year_basis"].value)
    year = INCOME_TAX_YEAR_2026_27
    facts = _IN_SLICE.model_copy(update=facts_override)
    household = _couple(_spell("a", year.start, year.end, "1"), claimant=facts)
    result = run_household_income_tax(household, "a", tax_year=year)
    _assert_refused_without_amount(result, "unsupported", code)


# ---------------------------------------------------------------- IT-07 component scope


def test_it07_the_component_is_declared_basic_tax_only_with_its_exclusions() -> None:
    # Spec "Explicit exclusions" and "Supported scope": the output is basic
    # annual tax for one taxpayer, not credits, PAYE, ACC, terminal tax,
    # refunds or net wages. The declaration is read, never inferred.
    raw = yaml.safe_load((POLICY_DIR / "policy.yaml").read_text())
    output = raw["outputs"]["basic_annual_income_tax"]
    assert (output["unit"], output["owner"], output["class"]) == (
        "NZD_per_tax_year",
        "taxpayer",
        "Model output",
    )
    assert set(output["excludes"]) == {
        "credits",
        "PAYE",
        "ACC",
        "terminal_tax",
        "refunds",
        "net_wages",
    }
    assert raw["outputs"]["outcome_precedence"] == ["unsupported", "needs_review", "calculated"]
    assert [c["id"] for c in raw["components"]] == [income_tax.COMPONENT_ID]
