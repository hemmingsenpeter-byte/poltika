"""Bounded synthetic probes for extreme finite Decimal exponents.

Million-exponent storage probes can produce at most about 1 MB on the old
implementation. Billion-exponent chart probes forbid serialization entirely,
so a failing test cannot allocate a billion-character fixed-point string.
"""

from __future__ import annotations

import json
from decimal import Decimal
from typing import Any, Literal

import pytest

from poltika.scenarios.reporting.charts import chart_from_table
from poltika.scenarios.reporting.tables import Column, Table


def _table(
    value: Decimal | None,
    *,
    population: bool = False,
    exclusions: tuple[tuple[str, Decimal], ...] = (),
) -> Table:
    return Table(
        table_id="extreme_toy",
        title="Arbitrary extreme finite values",
        columns=(
            Column("value", "Toy amount", display_mode="population_3sf" if population else "exact"),
        ),
        rows=((value,),),
        notes=("Synthetic arithmetic only; no statutory expected values.",),
        coverage=("Unknown outcomes remain unavailable.",),
        exclusions=exclusions,
        source_result_ids=("separately-supplied-toy",),
    )


@pytest.mark.parametrize(
    "amount",
    (
        "1.23456789E+1000000",
        "1.23456789E-1000000",
        "-1.23456789E+1000000",
        "-1.23456789E-1000000",
    ),
)
def test_extreme_exact_amount_storage_and_display_stay_compact(amount: str) -> None:
    value = Decimal(amount)
    table = _table(value)
    plain = table.plain()
    stored = plain["rows"][0][0]
    displayed = table.display(0, "value")
    assert len(stored) < 80 and len(displayed) < 80
    assert Decimal(stored).as_tuple() == value.as_tuple()
    assert Decimal(displayed).as_tuple() == value.as_tuple()
    assert len(json.dumps(plain)) < 1000
    assert table.sha256 == _table(value).sha256


@pytest.mark.parametrize(
    "amount,expected",
    (
        ("1.23456789E+1000000", "1.23E+1000000"),
        ("1.23456789E-1000000", "1.23E-1000000"),
        ("-1.23456789E+1000000", "-1.23E+1000000"),
        ("-1.23456789E-1000000", "-1.23E-1000000"),
    ),
)
def test_extreme_population_display_has_three_figures_without_losing_storage(
    amount: str, expected: str
) -> None:
    value = Decimal(amount)
    table = _table(value, population=True)
    displayed = table.display(0, "value")
    assert len(displayed) < 80
    shown = Decimal(displayed)
    assert shown == Decimal(expected)
    assert len(shown.as_tuple().digits) <= 3
    stored = table.plain()["rows"][0][0]
    assert len(stored) < 80
    assert Decimal(stored).as_tuple() == value.as_tuple()
    assert table.cell(0, "value") == value


@pytest.mark.parametrize(
    "weight,expected",
    (
        ("1.23456789E+1000000", "1.23E+1000000"),
        ("1.23456789E-1000000", "1.23E-1000000"),
    ),
)
def test_extreme_excluded_weight_is_compact_exact_and_keeps_unknown_outcome(
    weight: str, expected: str
) -> None:
    value = Decimal(weight)
    table = _table(None, population=True, exclusions=(("withheld toy outcome", value),))
    plain = table.plain()
    reason, stored = plain["exclusions"][0]
    assert reason == "withheld toy outcome"
    assert len(stored) < 80
    assert Decimal(stored).as_tuple() == value.as_tuple()
    assert plain["rows"] == [[None]]
    assert {Decimal(number) for number in table.displayed_numbers()} == {Decimal(expected)}
    assert len(json.dumps(plain)) < 1000


@pytest.mark.parametrize("amount", ("1.23456789E+1000000000", "1.23456789E-1000000000"))
@pytest.mark.parametrize("kind,axis", (("bar", "y"), ("line", "y"), ("line", "x")))
def test_unrepresentable_chart_value_is_rejected_before_serialization(
    monkeypatch: pytest.MonkeyPatch, amount: str, kind: Literal["bar", "line"], axis: str
) -> None:
    value = Decimal(amount)
    rows: tuple[tuple[str | Decimal, Decimal], ...]
    if kind == "bar":
        columns = (Column("x", "Toy label", kind="text"), Column("y", "Toy amount"))
        rows = (("toy", value),)
    else:
        columns = (Column("x", "Toy income"), Column("y", "Toy amount"))
        rows = ((value, Decimal(1)),) if axis == "x" else ((Decimal(1), value),)
    table = Table(
        "chart_resource_toy", "Toy chart", columns, rows,
        ("Synthetic arithmetic only.",), ("One toy row.",), (), ("toy",),
    )

    def forbid_serialization(self: Table) -> dict[str, Any]:
        raise AssertionError("Unrepresentable chart value reached table serialization")

    monkeypatch.setattr(Table, "plain", forbid_serialization)
    with pytest.raises(ValueError, match="numeric range"):
        chart_from_table(table, kind, "x", ("y",))
