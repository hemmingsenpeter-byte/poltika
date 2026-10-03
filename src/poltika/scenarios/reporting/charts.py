"""Pass 1 capability 16: charts derived mechanically from a `Table`.

A `ChartSpec` names a table (by id and SHA-256), the column on the x axis
and the numeric columns on the y axis. It holds no data of its own. Two
renderings read the table's cells:

- `vega_lite()`: a Vega-Lite v5 specification, for a browser.
- `render_svg()`: a dependency-free static SVG (bar and line), so a report
  can embed its charts offline.

Both refuse a table whose hash differs from the one the spec was made for,
so a chart cannot drift from its data. Cells that are not numbers (a value
not calculated) are gaps, never zeros. The Vega-Lite `values` are floats
for display only; the table's exact decimals stay in the table.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Literal
from xml.sax.saxutils import escape, quoteattr

from poltika.scenarios.reporting.tables import Table, format_cell

VEGA_LITE_SCHEMA = "https://vega.github.io/schema/vega-lite/v5.json"
ChartKind = Literal["bar", "line"]

_PALETTE = ("#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9")
_W, _H = 720, 400
_LEFT, _RIGHT, _TOP, _BOTTOM = 88, 24, 48, 96


@dataclass(frozen=True)
class ChartSpec:
    chart_id: str
    kind: ChartKind
    title: str
    table_id: str
    table_sha256: str
    x: str
    y: tuple[str, ...]
    maturity: str


def chart_from_table(
    table: Table, kind: ChartKind, x: str, y: tuple[str, ...], title: str | None = None
) -> ChartSpec:
    """A chart over a table's columns. `y` columns must be numeric; for a
    line chart `x` must be numeric too."""
    table.column_index(x)
    if not y:
        raise ValueError("a chart needs at least one y column")
    for column_id in y:
        if table.column(column_id).kind != "number":
            raise ValueError(f"column {column_id!r} is not numeric")
    if kind == "line" and table.column(x).kind != "number":
        raise ValueError("a line chart needs a numeric x column")
    digest = hashlib.sha256(
        json.dumps([table.sha256, kind, x, list(y)], separators=(",", ":")).encode()
    ).hexdigest()
    return ChartSpec(
        chart_id=f"{table.table_id}.{kind}.{digest[:12]}",
        kind=kind,
        title=title or table.title,
        table_id=table.table_id,
        table_sha256=table.sha256,
        x=x,
        y=y,
        maturity=table.maturity,
    )


def _check(spec: ChartSpec, table: Table) -> None:
    if table.table_id != spec.table_id or table.sha256 != spec.table_sha256:
        raise ValueError(f"chart {spec.chart_id} was not made from this table")


def _axis_title(table: Table, column_id: str) -> str:
    c = table.column(column_id)
    return f"{c.label} ({c.unit})" if c.unit else c.label


def _y_title(spec: ChartSpec, table: Table) -> str:
    units = {table.column(c).unit for c in spec.y}
    if len(spec.y) == 1 or len(units) == 1:
        unit = next(iter(units))
        label = table.column(spec.y[0]).label if len(spec.y) == 1 else "Value"
        return f"{label} ({unit})" if unit else label
    return "Value (units differ by series)"


def _number(value: Any) -> float | None:
    return float(value) if isinstance(value, Decimal) else None


def vega_lite(spec: ChartSpec, table: Table) -> dict[str, Any]:
    """A Vega-Lite v5 specification for the chart."""
    _check(spec, table)
    columns = [spec.x, *spec.y]
    values = [
        {
            c: (_number(table.cell(r, c)) if table.column(c).kind == "number" else table.cell(r, c))
            for c in columns
        }
        for r in range(len(table.rows))
    ]
    labels = {c: table.column(c).label for c in spec.y}
    x_numeric = table.column(spec.x).kind == "number"
    x_type = "quantitative" if spec.kind == "line" and x_numeric else "ordinal"
    result: dict[str, Any] = {
        "$schema": VEGA_LITE_SCHEMA,
        "title": spec.title,
        "description": (
            f"{spec.title}. Derived from table {spec.table_id} (sha256 {spec.table_sha256}). "
            f"Maturity: {spec.maturity}."
        ),
        "usermeta": {
            "chart_id": spec.chart_id,
            "table_id": spec.table_id,
            "table_sha256": spec.table_sha256,
            "maturity": spec.maturity,
        },
        "data": {"values": values},
        "transform": [
            {"fold": list(spec.y), "as": ["series", "value"]},
            {
                "calculate": json.dumps(labels, sort_keys=True) + "[datum.series]",
                "as": "series_label",
            },
            {"filter": "isValid(datum.value)"},
        ],
        "mark": {"type": "bar"} if spec.kind == "bar" else {"type": "line", "point": True},
        "encoding": {
            "x": {"field": spec.x, "type": x_type, "title": _axis_title(table, spec.x)},
            "y": {"field": "value", "type": "quantitative", "title": _y_title(spec, table)},
            "color": {"field": "series_label", "type": "nominal", "title": "Series"},
        },
    }
    if spec.kind == "bar" and len(spec.y) > 1:
        result["encoding"]["xOffset"] = {"field": "series_label"}
    return result


def _nice_step(span: float, target: int = 5) -> float:
    raw = span / target
    magnitude = 10.0 ** _floor_log10(raw)
    for m in (1, 2, 2.5, 5, 10):
        if raw <= m * magnitude:
            return m * magnitude
    return 10 * magnitude


def _floor_log10(x: float) -> int:
    n = 0
    while x >= 10:
        x /= 10
        n += 1
    while x < 1:
        x *= 10
        n -= 1
    return n


def _ticks(lo: float, hi: float) -> list[float]:
    if hi == lo:
        hi = lo + 1
    step = _nice_step(hi - lo)
    first = _floor_div(lo, step)
    ticks = []
    k = 0
    while True:
        t = (first + k) * step
        ticks.append(round(t, 10))
        if t >= hi or k > 50:
            break
        k += 1
    return ticks


def _floor_div(a: float, b: float) -> int:
    q = int(a // b)
    return q


def _tick_label(value: float, step_hint: float) -> str:
    return f"{value:,.0f}" if step_hint >= 1 else f"{value:,.2f}"


def _f(x: float) -> str:
    return f"{x:.1f}"


def _truncate(text: str, n: int = 18) -> str:
    return text if len(text) <= n else text[: n - 1] + "…"


def render_svg(spec: ChartSpec, table: Table) -> str:
    """A static SVG of the chart, read from the table's cells."""
    _check(spec, table)
    series = [
        (table.column(c).label, [table.cell(r, c) for r in range(len(table.rows))]) for c in spec.y
    ]
    nums = [float(v) for _, vals in series for v in vals if isinstance(v, Decimal)]
    plot_w, plot_h = _W - _LEFT - _RIGHT, _H - _TOP - _BOTTOM
    height = _H + 16 * ((len(series) - 1) // 2)
    parts: list[str] = []

    if spec.kind == "bar":
        lo, hi = min([0.0, *nums]), max([0.0, *nums])
    else:
        lo, hi = min(nums, default=0.0), max(nums, default=1.0)
        lo = min(lo, 0.0)
    ticks = _ticks(lo, hi)
    lo, hi = min(lo, ticks[0]), max(hi, ticks[-1])
    step_hint = (ticks[1] - ticks[0]) if len(ticks) > 1 else 1.0

    def ypx(v: float) -> float:
        return _TOP + plot_h * (1 - (v - lo) / (hi - lo))

    for t in ticks:
        y = _f(ypx(t))
        parts.append(
            f'<line x1="{_LEFT}" x2="{_W - _RIGHT}" y1="{y}" y2="{y}" stroke="#d0d0d0" '
            f'stroke-width="1"/>'
            f'<text x="{_LEFT - 8}" y="{_f(ypx(t) + 4)}" text-anchor="end" font-size="11" '
            f'fill="#333333">{escape(_tick_label(t, step_hint))}</text>'
        )
    zero = _f(ypx(0.0))
    parts.append(
        f'<line x1="{_LEFT}" x2="{_W - _RIGHT}" y1="{zero}" y2="{zero}" stroke="#333333" '
        f'stroke-width="1"/>'
        f'<line x1="{_LEFT}" x2="{_LEFT}" y1="{_TOP}" y2="{_TOP + plot_h}" stroke="#333333" '
        f'stroke-width="1"/>'
    )

    n_rows = len(table.rows)
    if spec.kind == "bar":
        band = plot_w / max(n_rows, 1)
        group_w = band * 0.7
        bar_w = group_w / len(series)
        longest = max(
            (len(format_cell(table.column(spec.x), table.cell(r, spec.x))) for r in range(n_rows)),
            default=0,
        )
        rotate = longest * 6.5 > band
        for r in range(n_rows):
            cx = _LEFT + band * (r + 0.5)
            label = _truncate(format_cell(table.column(spec.x), table.cell(r, spec.x)))
            ly = _TOP + plot_h + 16
            if rotate:
                parts.append(
                    f'<text x="{_f(cx)}" y="{_f(ly)}" font-size="11" text-anchor="end" '
                    f'fill="#333333" transform="rotate(-30 {_f(cx)} {_f(ly)})">'
                    f"{escape(label)}</text>"
                )
            else:
                parts.append(
                    f'<text x="{_f(cx)}" y="{_f(ly)}" font-size="11" text-anchor="middle" '
                    f'fill="#333333">{escape(label)}</text>'
                )
            for s, (_, vals) in enumerate(series):
                v = vals[r]
                if not isinstance(v, Decimal):
                    continue  # a gap: not calculated, never a zero bar
                x0 = cx - group_w / 2 + bar_w * s
                top, bottom = sorted((ypx(float(v)), ypx(0.0)))
                parts.append(
                    f'<rect x="{_f(x0)}" y="{_f(top)}" width="{_f(bar_w * 0.92)}" '
                    f'height="{_f(bottom - top)}" fill="{_PALETTE[s % len(_PALETTE)]}"/>'
                )
    else:
        xs = [
            float(c)
            for c in (table.cell(r, spec.x) for r in range(n_rows))
            if isinstance(c, Decimal)
        ]
        xlo, xhi = min(xs, default=0.0), max(xs, default=1.0)
        if xhi == xlo:
            xhi = xlo + 1

        def xpx(v: float) -> float:
            return _LEFT + plot_w * (v - xlo) / (xhi - xlo)

        for t in _ticks(xlo, xhi):
            if t < xlo or t > xhi:
                continue
            parts.append(
                f'<text x="{_f(xpx(t))}" y="{_TOP + plot_h + 16}" font-size="11" '
                f'text-anchor="middle" fill="#333333">{escape(f"{t:,.0f}")}</text>'
            )
        for s, (_, vals) in enumerate(series):
            colour = _PALETTE[s % len(_PALETTE)]
            run: list[str] = []

            def flush(run: list[str] = run, colour: str = colour) -> None:
                if len(run) > 1:
                    parts.append(
                        f'<polyline points="{" ".join(run)}" fill="none" stroke="{colour}" '
                        f'stroke-width="2"/>'
                    )
                run.clear()

            for r in range(n_rows):
                xv, yv = table.cell(r, spec.x), vals[r]
                if isinstance(xv, Decimal) and isinstance(yv, Decimal):
                    px, py = xpx(float(xv)), ypx(float(yv))
                    run.append(f"{_f(px)},{_f(py)}")
                    parts.append(f'<circle cx="{_f(px)}" cy="{_f(py)}" r="3" fill="{colour}"/>')
                else:
                    flush()  # a gap breaks the line
            flush()

    if n_rows == 0:
        parts.append(
            f'<text x="{_LEFT + plot_w / 2}" y="{_TOP + plot_h / 2}" text-anchor="middle" '
            f'font-size="13" fill="#555555">No rows in this table</text>'
        )

    for s, (label, _) in enumerate(series):
        lx = _LEFT + (s % 2) * 300
        legend_y = _H - 20 + 16 * (s // 2)
        parts.append(
            f'<rect x="{lx}" y="{legend_y - 9}" width="10" height="10" '
            f'fill="{_PALETTE[s % len(_PALETTE)]}"/>'
            f'<text x="{lx + 14}" y="{legend_y}" font-size="11" fill="#333333">'
            f"{escape(_truncate(label, 46))}</text>"
        )
    parts.append(
        f'<text x="{_LEFT + plot_w / 2}" y="{_H - 40}" font-size="11" text-anchor="middle" '
        f'fill="#333333">{escape(_axis_title(table, spec.x))}</text>'
        f'<text x="16" y="{_TOP + plot_h / 2}" font-size="11" text-anchor="middle" '
        f'fill="#333333" transform="rotate(-90 16 {_TOP + plot_h / 2})">'
        f"{escape(_truncate(_y_title(spec, table), 60))}</text>"
    )

    desc = (
        f"Derived from table {spec.table_id} (sha256 {spec.table_sha256}). "
        f"Maturity: {spec.maturity}."
    )
    header = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {_W} {height}" width="{_W}" '
        f'height="{height}" role="img" font-family="sans-serif" '
        f"data-chart-id={quoteattr(spec.chart_id)} "
        f"data-table-id={quoteattr(spec.table_id)} "
        f'data-table-sha256="{spec.table_sha256}">'
        f'<rect width="{_W}" height="{height}" fill="#ffffff"/>'
        f"<title>{escape(spec.title)}</title><desc>{escape(desc)}</desc>"
        f'<text x="{_LEFT}" y="24" font-size="14" font-weight="bold" fill="#111111">'
        f"{escape(_truncate(spec.title, 90))}</text>"
    )
    return header + "".join(parts) + "</svg>"
