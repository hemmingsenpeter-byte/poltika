"""Programme Task 5: every unit a policy declares binds to the registries."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from poltika.common.errors import UnboundPolicyUnitError, UnknownUnitError
from poltika.semantics.periods import PeriodType, convert_amount
from poltika.semantics.schemas.policy_spec import ParameterUnit
from poltika.semantics.unit_binding import (
    UNIT_BINDINGS,
    PerEntity,
    PeriodStatus,
    bind_input_period,
    bind_unit,
    check_input,
)
from poltika.semantics.units import UNITS, get_unit

SPECS = sorted((Path(__file__).parents[3] / "policy_specs").glob("*/policy.yaml"))


def _load(path: Path) -> dict[str, object]:
    return yaml.safe_load(path.read_text())  # type: ignore[no-any-return]


def test_policies_found() -> None:
    assert len(SPECS) >= 2


def test_every_parameter_unit_member_is_bound_to_a_registered_unit() -> None:
    assert set(UNIT_BINDINGS) == {u.value for u in ParameterUnit}
    for binding in UNIT_BINDINGS.values():
        assert binding.unit_id in UNITS
        assert get_unit(binding.unit_id).id == binding.unit_id
        if binding.period_status is PeriodStatus.BOUND:
            assert binding.period is not None
        else:
            assert binding.period is None


@pytest.mark.parametrize("path", SPECS, ids=lambda p: p.parent.name)
def test_every_declared_unit_and_input_period_is_bound(path: Path) -> None:
    spec = _load(path)
    for param in spec["parameters"]:  # type: ignore[attr-defined]
        bind_unit(param["unit"])
    for item in spec["inputs"]:  # type: ignore[attr-defined]
        if "period" in item:
            bind_input_period(item["period"])
        if "unit" in item:
            check_input(item["unit"], item["period"])
    assert bind_input_period(spec["assessment"]["membership_period"]) is not None  # type: ignore[index]


def test_unregistered_unit_fails() -> None:
    with pytest.raises(UnboundPolicyUnitError):
        bind_unit("NZD_per_fortnight")


def test_unregistered_period_fails() -> None:
    with pytest.raises(UnboundPolicyUnitError):
        bind_input_period("fortnight")


def test_cross_period_use_fails() -> None:
    check_input("NZD_per_tax_year", "full_tax_year")
    check_input("NZD_per_week", "assessment_week")
    with pytest.raises(UnboundPolicyUnitError):
        check_input("NZD_per_week", "full_tax_year")
    with pytest.raises(UnboundPolicyUnitError):
        check_input("NZD_per_tax_year", "assessment_week")


def test_unregistered_registry_unit_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    import poltika.semantics.unit_binding as ub

    def refuse(unit_id: str) -> None:
        raise UnknownUnitError(unit_id)

    monkeypatch.setattr(ub, "get_unit", refuse)
    with pytest.raises(UnknownUnitError):
        check_input("NZD_per_week", "assessment_week")


def test_bindings_pin_qualifiers() -> None:
    child = bind_unit("NZD_per_child_per_tax_year")
    assert (child.unit_id, child.period, child.per) == ("nzd", PeriodType.TAX_YEAR, PerEntity.CHILD)
    assert bind_unit("NZD_per_tax_year_after_tax").qualifier == "after_tax"


def test_asset_stock_period_is_unresolved_not_guessed() -> None:
    nzd = bind_unit("NZD")
    assert nzd.period is None
    assert nzd.period_status is PeriodStatus.UNRESOLVED


def test_no_hidden_conversion() -> None:
    from poltika.common.errors import PeriodConversionRefusedError

    with pytest.raises(PeriodConversionRefusedError):
        convert_amount(1, PeriodType.ASSESSMENT_WEEK, PeriodType.TAX_YEAR)  # type: ignore[arg-type]
