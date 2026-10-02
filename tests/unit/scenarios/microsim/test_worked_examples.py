"""Worked examples: named households run under a reform."""

from __future__ import annotations

from decimal import Decimal

import pytest

from poltika.api.accommodation_supplement import AS_POLICY_DIR
from poltika.api.analyst import examples
from poltika.api.household import HouseholdCalculationRequest, record_from_request
from poltika.api.wff import WFF_POLICY_DIR
from poltika.scenarios.microsim.reform import (
    Operation,
    Override,
    Reform,
    UnsupportedReformError,
)
from poltika.scenarios.microsim.worked_examples import run_examples


def _records() -> list[tuple[str, object]]:
    return [
        (e["id"], record_from_request(HouseholdCalculationRequest.model_validate(e["request"])))
        for e in examples()
    ]


def _reform(policy_id: str = "working_for_families") -> Reform:
    return Reform(
        reform_id="threshold",
        overrides=(
            Override(
                policy_id=policy_id,
                parameter_id="family_tax_credit_abatement_threshold",
                operation=Operation.SET,
                value=Decimal(60000),
            ),
        ),
    )


def test_a_higher_threshold_raises_abated_family_tax_credit_and_nothing_else() -> None:
    results = run_examples(_records(), _reform(), WFF_POLICY_DIR, AS_POLICY_DIR)  # type: ignore[arg-type]
    assert len(results) == len(examples())
    abated = next(r for r in results if r.example_id.startswith("g2_"))
    ftc = abated.components["family_tax_credit"]
    assert ftc.outcome == "calculated" and ftc.delta is not None and ftc.delta > 0
    # The Accommodation Supplement is a different policy: untouched.
    assert abated.components["accommodation_supplement"].delta == 0


def test_a_component_that_is_not_calculated_has_no_delta() -> None:
    results = run_examples(_records(), _reform(), WFF_POLICY_DIR, AS_POLICY_DIR)  # type: ignore[arg-type]
    for r in results:
        iwtc = r.components["in_work_tax_credit"]
        assert iwtc.outcome != "calculated" and iwtc.delta is None


def test_a_policy_that_is_not_modelled_is_refused() -> None:
    with pytest.raises(UnsupportedReformError):
        run_examples(_records(), _reform("income_tax"), WFF_POLICY_DIR, AS_POLICY_DIR)  # type: ignore[arg-type]
