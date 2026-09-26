"""v0.2 Tasks 6.1-6.3: reforms as overrides of loaded parameters, and the
engines' preloaded-parameter path."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from typing import Any

import pytest
import yaml
from pydantic import ValidationError

from poltika.common.errors import PolicyVersionMismatchError
from poltika.policy.loader import PolicyParameterSet, load_policy_parameters
from poltika.scenarios.combined import run_combined_household
from poltika.scenarios.microsim.reform import (
    SCENARIO_ASSUMPTION,
    InvalidReformError,
    Override,
    Reform,
    UnsupportedReformError,
    apply_reform,
)
from poltika.scenarios.record import ScenarioRecord, result_payload
from tests.conftest import AS_POLICY_DIR, WFF_POLICY_DIR
from tests.unit.scenarios.test_scenario_record import GOLDEN_PATH, record_from_yaml

GOLDEN = [record_from_yaml(h) for h in yaml.safe_load(GOLDEN_PATH.read_text())["households"]]


def _params(record: ScenarioRecord) -> tuple[PolicyParameterSet, PolicyParameterSet]:
    return (
        load_policy_parameters(
            WFF_POLICY_DIR,
            record.wff_lookup_date,
            requested_policy_version=record.requested_wff_policy_version,
        ),
        load_policy_parameters(
            AS_POLICY_DIR,
            record.as_lookup_date,
            requested_policy_version=record.requested_as_policy_version,
        ),
    )


def _run(
    record: ScenarioRecord,
    wff: PolicyParameterSet | None = None,
    as_: PolicyParameterSet | None = None,
) -> Any:
    return run_combined_household(
        WFF_POLICY_DIR,
        AS_POLICY_DIR,
        record.household,
        wff_lookup_date=record.wff_lookup_date,
        as_lookup_date=record.as_lookup_date,
        assessment_week=record.assessment_week,
        requested_wff_policy_version=record.requested_wff_policy_version,
        requested_as_policy_version=record.requested_as_policy_version,
        wff_parameters=wff,
        as_parameters=as_,
    )


def _reform(*overrides: tuple[str, str, str, str]) -> Reform:
    return Reform(
        reform_id="test",
        overrides=tuple(
            Override(policy_id=p, parameter_id=k, operation=op, value=Decimal(v))
            for p, k, op, v in overrides
        ),
    )


WFF = "working_for_families"


@pytest.mark.parametrize(("operation", "value"), [("set", "0"), ("multiply", "0"), ("add", "-100")])
def test_zero_asset_imputation_divisor_is_refused(operation: str, value: str) -> None:
    _, parameters = _params(GOLDEN[0])
    reform = _reform(("accommodation_supplement", "asset_imputation_step_size", operation, value))
    with pytest.raises(InvalidReformError, match="positive"):
        apply_reform(parameters, reform)


@pytest.mark.parametrize("record", GOLDEN, ids=lambda r: str(r.wff_lookup_date))
def test_preloaded_parameters_give_identical_results(record: ScenarioRecord) -> None:
    wff, as_ = _params(record)
    assert result_payload(_run(record, wff, as_)) == result_payload(_run(record))


def test_preloaded_parameters_for_another_date_or_version_are_refused() -> None:
    record = GOLDEN[0]
    wff, as_ = _params(record)
    with pytest.raises(ValueError, match="resolved for"):
        _run(record, replace(wff, modelled_date=wff.modelled_date.replace(day=2)), as_)
    with pytest.raises(PolicyVersionMismatchError):
        _run(record, replace(wff, policy_version="other"), as_)


@pytest.mark.parametrize("record", GOLDEN, ids=lambda r: str(r.wff_lookup_date))
def test_identity_reform_changes_nothing(record: ScenarioRecord) -> None:
    wff, as_ = _params(record)
    identity = _reform(
        (WFF, "family_tax_credit_abatement_threshold", "add", "0"),
        (WFF, "family_tax_credit_eldest_child", "multiply", "1"),
    )
    reformed = _run(record, apply_reform(wff, identity), as_)
    assert result_payload(reformed) == result_payload(_run(record))


def test_overridden_value_is_labelled_a_scenario_assumption() -> None:
    wff, _ = _params(GOLDEN[0])
    baseline = wff.get("family_tax_credit_abatement_threshold")
    assert baseline.value is not None
    reformed = apply_reform(
        wff, _reform((WFF, "family_tax_credit_abatement_threshold", "set", "50000"))
    )
    changed = reformed.get("family_tax_credit_abatement_threshold")
    assert changed.value == Decimal(50000)
    assert changed.review_status == SCENARIO_ASSUMPTION
    assert changed.source_id is None
    assert "reform 'test'" in (changed.locator or "")
    assert (changed.effective_from, changed.effective_to) == (
        baseline.effective_from,
        baseline.effective_to,
    )
    assert wff.get("family_tax_credit_abatement_threshold") == baseline  # the original is untouched


def test_set_can_replace_a_needs_review_value_but_add_cannot() -> None:
    wff, _ = _params(GOLDEN[0])
    assert wff.get("in_work_base").outcome == "needs_review"
    with pytest.raises(InvalidReformError, match="use set"):
        apply_reform(wff, _reform((WFF, "in_work_base", "add", "1")))
    assumed = apply_reform(wff, _reform((WFF, "in_work_base", "set", "1")))
    assert assumed.get("in_work_base").outcome == "resolved"


@pytest.mark.parametrize(
    ("override", "match"),
    [
        ((WFF, "no_such_parameter", "set", "1"), "no parameter"),
        ((WFF, "family_tax_credit_eldest_child", "set", "-1"), "negative"),
        ((WFF, "family_tax_credit_abatement_rate", "add", "1"), "rate above 1"),
    ],
)
def test_invalid_overrides(override: tuple[str, str, str, str], match: str) -> None:
    wff, _ = _params(GOLDEN[0])
    with pytest.raises(InvalidReformError, match=match):
        apply_reform(wff, _reform(override))


def test_unmodelled_policy_is_unsupported_not_approximated() -> None:
    wff, _ = _params(GOLDEN[0])
    with pytest.raises(UnsupportedReformError, match="childcare_subsidy"):
        apply_reform(wff, _reform(("childcare_subsidy", "rate", "set", "1")))


def test_duplicate_override_rejected_and_hash_is_stable() -> None:
    with pytest.raises(ValidationError, match="more than once"):
        _reform((WFF, "in_work_base", "set", "1"), (WFF, "in_work_base", "set", "2"))
    a = _reform((WFF, "in_work_base", "set", "1"))
    assert a.reform_sha256() == _reform((WFF, "in_work_base", "set", "1")).reform_sha256()
    assert a.reform_sha256() != _reform((WFF, "in_work_base", "set", "2")).reform_sha256()


def test_other_policys_overrides_are_left_for_its_own_set() -> None:
    _, as_ = _params(GOLDEN[0])
    reform = _reform((WFF, "family_tax_credit_abatement_threshold", "set", "50000"))
    assert apply_reform(as_, reform) == as_
