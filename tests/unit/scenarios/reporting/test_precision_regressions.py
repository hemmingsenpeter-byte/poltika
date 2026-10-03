"""Presentation precision regressions on purely synthetic arithmetic."""

from __future__ import annotations

from decimal import Decimal

import pytest

from poltika.scenarios.microsim.runner import ComponentOutcomeValue
from poltika.scenarios.reporting import tables as t
from poltika.scenarios.reporting.adapter import (
    ChangeClass,
    ChangeSummary,
    ComponentDelta,
    GroupedTable,
    WorkedExample,
)


def _population_average(total: Decimal, weight: Decimal) -> t.Table:
    classes = {change: Decimal(0) for change in ChangeClass}
    classes[ChangeClass.GAIN if total > 0 else ChangeClass.LOSS] = weight
    mean = total / weight
    gain = mean if total > 0 else None
    loss = mean if total < 0 else None
    summary = ChangeSummary(
        3, weight, classes, gain, gain, loss, loss, gain, loss, total, weight
    )
    grouped = GroupedTable(
        ("family_tax_credit",), "NZD per tax year", "income", {"01": summary}
    )
    return t.distribution_by_income_group(grouped, source_result_ids=("synthetic-arithmetic",))


def test_derived_population_average_retains_full_decimal_precision() -> None:
    table = _population_average(Decimal(1), Decimal(3))
    expected = Decimal(1) / Decimal(3)
    assert table.cell(0, "average_change") == expected
    column = table.column_index("average_change")
    assert table.plain()["rows"][0][column] == format(expected, "f")


@pytest.mark.parametrize("amount", ["123456789.123", "0.00000123456789", "-9876543.21"])
def test_population_display_uses_at_most_three_significant_figures(amount: str) -> None:
    table = _population_average(Decimal(amount), Decimal(1))
    displayed = Decimal(table.display(0, "average_change").replace(",", ""))
    assert displayed != 0
    assert len(displayed.normalize().as_tuple().digits) <= 3
    assert abs((displayed - Decimal(amount)) / Decimal(amount)) <= Decimal("0.005")
    assert table.cell(0, "average_change") == Decimal(amount)


def test_household_example_preserves_half_cent_without_presentation_rounding() -> None:
    # This is an invented exact Rule-shaped result, not a statutory expected value.
    baseline = ComponentOutcomeValue("calculated", Decimal("1000.005"), None)
    reform = ComponentOutcomeValue("calculated", Decimal("1000.010"), None)
    delta = ComponentDelta("calculated", baseline, reform, Decimal("0.005"))
    example = WorkedExample("invented-half-cent", {"family_tax_credit": delta})
    table = t.example_households(
        [example], {"family_tax_credit": "NZD per tax year"}, source_result_ids=("supplied-example",)
    )
    assert Decimal(table.display(0, "baseline").replace(",", "")) == Decimal("1000.005")
    assert Decimal(table.display(0, "change").replace(",", "")) == Decimal("0.005")
