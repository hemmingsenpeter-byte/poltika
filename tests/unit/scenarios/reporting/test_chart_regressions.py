"""Regression coverage for standalone chart warnings, gaps and numeric bounds.

The numeric probes use arbitrary toy values, not statutory expectations. Each
probe runs in a subprocess because the original SVG renderer could loop forever
on an overflowing or subnormal floating-point axis.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from decimal import Decimal as D
from pathlib import Path
from typing import Literal

import pytest

from poltika.scenarios.reporting.charts import chart_from_table, render_svg, vega_lite
from poltika.scenarios.reporting.report import build_report
from poltika.scenarios.reporting.tables import Column, Table
from tests.unit.scenarios.reporting.conftest import FTC, Case


@pytest.mark.parametrize("renderer", ("svg", "vega"))
def test_standalone_population_charts_show_the_synthetic_warning(
    case: Case, renderer: Literal["svg", "vega"]
) -> None:
    report = build_report(case.population, case.run, FTC)
    tables = report.tables()
    charts = [chart for section in report.sections for chart in section.charts]
    assert charts
    for chart in charts:
        table = tables[chart.table_id]
        if renderer == "svg":
            root = ET.fromstring(render_svg(chart, table))
            # A <desc> or data attribute alone does not label the visible chart.
            visible = " ".join(
                "".join(node.itertext())
                for node in root.iter()
                if node.tag.rsplit("}", 1)[-1] == "text"
            )
            assert case.run.label in visible, chart.chart_id
        else:
            spec = vega_lite(chart, table)
            # Vega permits a title string or an object with a subtitle.
            assert case.run.label in json.dumps(spec["title"]), chart.chart_id
            assert case.run.label in spec["description"], chart.chart_id


def test_vega_line_keeps_a_missing_middle_value_as_a_gap() -> None:
    table = Table(
        table_id="gap_probe",
        title="Toy values with a missing middle point",
        columns=(Column("x", "Toy income"), Column("y", "Toy entitlement")),
        rows=((D(1), D(10)), (D(2), None), (D(3), D(30))),
        notes=("Arbitrary regression values.",),
        coverage=("Three toy observations; the middle outcome is unknown.",),
        exclusions=(),
        source_result_ids=("toy",),
    )
    chart = chart_from_table(table, "line", "x", ("y",))
    spec = vega_lite(chart, table)
    assert spec["data"]["values"][1] == {"x": 2.0, "y": None}
    assert all("filter" not in transform for transform in spec["transform"])
    # Vega-Lite's default breaks paths. Explicit "show"/null would turn
    # unknowns into zero/minimum positions, and "filter" would join endpoints.
    assert spec["mark"].get("invalid", "default") not in ("filter", "show", None)
    svg = ET.fromstring(render_svg(chart, table))
    tags = [node.tag.rsplit("}", 1)[-1] for node in svg.iter()]
    assert tags.count("circle") == 2 and "polyline" not in tags


_NUMERIC_PROBE = r"""
import json
import sys
from decimal import Decimal

from poltika.scenarios.reporting.charts import chart_from_table, render_svg, vega_lite
from poltika.scenarios.reporting.tables import Column, Table

kind, axis, value, renderer = sys.argv[1:]
try:
    bad = Decimal(value)
    if axis == "span":
        columns = (Column("x", "X"), Column("y", "Y"))
        rows = ((Decimal(0), -bad), (Decimal(1), bad))
    elif kind == "bar":
        columns = (Column("x", "X", kind="text"), Column("y", "Y"))
        rows = (("probe", bad), ("ordinary", Decimal(2)))
    elif axis == "x":
        columns = (Column("x", "X"), Column("y", "Y"))
        rows = ((bad, Decimal(1)), (Decimal(1), Decimal(2)))
    else:
        columns = (Column("x", "X"), Column("y", "Y"))
        rows = ((Decimal(0), bad), (Decimal(1), Decimal(2)))
    table = Table("numeric_probe", "Toy numeric probe", columns, rows,
                  ("Arbitrary regression values.",), ("Toy rows.",), (), ("toy",))
    chart = chart_from_table(table, kind, "x", ("y",))
    output = render_svg(chart, table) if renderer == "svg" else vega_lite(chart, table)
except Exception as exc:
    print(json.dumps({"accepted": False, "error": type(exc).__name__, "message": str(exc)}))
else:
    print(json.dumps({"accepted": True, "output_type": type(output).__name__}))
"""


def _assert_numeric_probe_rejected(kind: str, axis: str, value: str, renderer: str) -> None:
    repo = Path(__file__).resolve().parents[4]
    env = dict(os.environ)
    env["PYTHONPATH"] = str(repo / "src") + os.pathsep + env.get("PYTHONPATH", "")
    try:
        result = subprocess.run(
            [sys.executable, "-c", _NUMERIC_PROBE, kind, axis, value, renderer],
            cwd=repo,
            env=env,
            text=True,
            capture_output=True,
            check=False,
            timeout=3,
        )
    except subprocess.TimeoutExpired:
        pytest.fail(f"{renderer} {kind} {axis}={value}: chart rendering exceeded three seconds")
    assert result.returncode == 0, result.stderr
    observed = json.loads(result.stdout)
    assert observed.get("error") == "ValueError", observed
    message = observed["message"].lower()
    assert message and any(
        word in message
        for word in ("finite", "range", "represent", "float", "safe", "decimal", "numeric", "chart")
    ), observed


@pytest.mark.parametrize("renderer", ("svg", "vega"))
@pytest.mark.parametrize("kind,axis", (("bar", "y"), ("line", "y"), ("line", "x")))
@pytest.mark.parametrize(
    "value",
    ("1E+400", "1E-400", "5E-324", "NaN", "sNaN", "Infinity", "-Infinity"),
    ids=("overflow", "underflow", "subnormal", "nan", "signalling-nan", "infinity", "minus-inf"),
)
def test_unsafe_decimal_chart_inputs_fail_clearly(
    renderer: str, kind: str, axis: str, value: str
) -> None:
    _assert_numeric_probe_rejected(kind, axis, value, renderer)


def test_svg_rejects_a_finite_axis_whose_span_overflows() -> None:
    _assert_numeric_probe_rejected("line", "span", "1E+308", "svg")
