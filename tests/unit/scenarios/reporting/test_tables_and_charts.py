"""Pass 1 capability 16: tables and charts. Expected figures are read back
from the same structured results, never restated."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from decimal import Decimal as D

import pytest

from poltika.scenarios.reporting import tables as t
from poltika.scenarios.reporting.adapter import analyse
from poltika.scenarios.reporting.charts import chart_from_table, render_svg, vega_lite
from tests.unit.scenarios.reporting.conftest import FTC, Case


def _all_tables(case: Case) -> list[t.Table]:
    r = analyse(case.population, case.run, FTC)
    ids = (case.run.run_id,)
    label_path = case.paths[0]
    out = [
        t.distribution_by_income_group(r.deciles, source_result_ids=ids),
        t.winners_losers(r.overall, source_result_ids=ids),
        t.household_types(r.household_types, source_result_ids=ids),
        t.fiscal_components(r.fiscal, source_result_ids=ids),
    ]
    for label, path in case.paths:
        out.append(t.withdrawal_rates(path, label=label, source_result_ids=ids))
        out.append(t.payment_profile(path, label=label, source_result_ids=ids))
    assert label_path
    return out


def test_every_table_is_well_formed_and_hashes_stably(case: Case) -> None:
    for table in _all_tables(case):
        assert table.maturity == "IMPLEMENTED" and table.source_result_ids == (case.run.run_id,)
        assert table.coverage and table.notes
        assert table.sha256 == table.sha256 and len(table.sha256) == 64
        assert all(len(row) == len(table.columns) for row in table.rows)


def test_winners_losers_weights_equal_the_population_weight(case: Case) -> None:
    r = analyse(case.population, case.run, FTC)
    table = t.winners_losers(r.overall, source_result_ids=(case.run.run_id,))
    total = sum((row[1] for row in table.rows if isinstance(row[1], D)), D(0))
    assert total == r.overall.groups["all"].weight


def test_fiscal_table_matches_the_run(case: Case) -> None:
    r = analyse(case.population, case.run, FTC)
    table = t.fiscal_components(r.fiscal, source_result_ids=(case.run.run_id,))
    for i, row in enumerate(table.rows):
        f = r.fiscal[str(row[0])]
        assert table.cell(i, "change") == f.delta_total
        assert table.cell(i, "unit") == f.unit
    assert len(table.rows) == len(r.fiscal)


def test_not_calculated_is_a_gap_never_a_zero(case: Case) -> None:
    # The minimum family tax credit is not calculated along a WFF path.
    _, path = case.paths[0]
    table = t.payment_profile(path, label="wff path", source_result_ids=("x",))
    column = "entitlement_minimum_family_tax_credit"
    assert all(table.cell(i, column) is None for i in range(len(table.rows)))
    assert table.display(0, column) == "not available"


def test_chart_is_linked_to_its_table_and_svg_is_well_formed(case: Case) -> None:
    for table in _all_tables(case):
        numeric = tuple(c.column_id for c in table.columns if c.kind == "number")
        x, ys = numeric[0], numeric[1:]
        kind = "line" if table.table_id.startswith(("withdrawal", "payment")) else "bar"
        if kind == "bar":
            x, ys = table.columns[0].column_id, (numeric[1],)
        spec = chart_from_table(table, kind, x, ys)  # type: ignore[arg-type]
        assert spec.table_sha256 == table.sha256 and spec.table_id == table.table_id
        svg = render_svg(spec, table)
        root = ET.fromstring(svg)
        assert root.tag.endswith("svg")
        assert root.get("data-table-sha256") == table.sha256
        assert root.get("data-chart-id") == spec.chart_id
        vega = vega_lite(spec, table)
        assert vega["$schema"].endswith("/v5.json")
        assert vega["usermeta"]["table_sha256"] == table.sha256
        assert len(vega["data"]["values"]) == len(table.rows)
        assert render_svg(spec, table) == svg  # deterministic


def test_chart_refuses_a_different_table(case: Case) -> None:
    tables = _all_tables(case)
    spec = chart_from_table(tables[1], "bar", "outcome", ("weight",))
    with pytest.raises(ValueError, match="not made from this table"):
        render_svg(spec, tables[0])
    with pytest.raises(ValueError, match="not numeric"):
        chart_from_table(tables[1], "bar", "outcome", ("outcome",))
    with pytest.raises(ValueError, match="numeric x"):
        chart_from_table(tables[1], "line", "outcome", ("weight",))


def test_svg_escapes_text_and_survives_gaps_and_no_rows() -> None:
    table = t.Table(
        table_id="t",
        title="A <b> & title",
        columns=(t.Column("g", "G <x>", kind="text"), t.Column("v", "V")),
        rows=(("a&b", D("1.5")), ("c", None), ("d", D(-2))),
        notes=("n",),
        coverage=("c",),
        exclusions=(),
        source_result_ids=("r",),
    )
    ET.fromstring(render_svg(chart_from_table(table, "bar", "g", ("v",)), table))
    empty = t.Table("e", "E", table.columns, (), ("n",), ("c",), (), ("r",))
    ET.fromstring(render_svg(chart_from_table(empty, "bar", "g", ("v",)), empty))
    line = t.Table(
        "l",
        "L",
        (t.Column("x", "X"), t.Column("y", "Y")),
        ((D(1), D(2)), (D(2), None), (D(3), D(4)), (D(4), D(5))),
        ("n",),
        ("c",),
        (),
        ("r",),
    )
    svg = render_svg(chart_from_table(line, "line", "x", ("y",)), line)
    ET.fromstring(svg)
    assert svg.count("<polyline") == 1  # the gap breaks the line
