"""Pass 1 capability 16: standard analytical tables.

A `Table` is a neutral, immutable description of rows and columns that says
what it covers, what it left out, which results it came from and how mature
the model behind it is. Builders take structured results only (the types
re-exported by `adapter.py`) and never calculate a policy amount. They do
only presentation arithmetic: a share of a weight, or a total divided by
the weight it covers. A household whose result was `needs_review` or
`unsupported` is never turned into a zero: its weight sits in its own row
or column.

A table's identity is `sha256`, over its whole content. Charts and the
report carry it, so every picture and every sentence can be traced to the
cells it came from.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Sequence
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal, localcontext
from typing import Any, Literal

from poltika.policy.loader import PolicyParameterSet
from poltika.scenarios.microsim.reform import Reform
from poltika.scenarios.reporting.adapter import (
    ChangeClass,
    ComponentFiscal,
    GroupedTable,
    OverriddenParameter,
    RecordStatus,
    WithdrawalPath,
    WorkedExample,
)

MATURITY = "IMPLEMENTED"
SCENARIO_ASSUMPTION = "scenario_assumption"
NOT_AVAILABLE = "not available"
RATE_UNIT = "fraction (NZD withdrawn per NZD of income)"

Cell = str | Decimal | None
ColumnKind = Literal["text", "number"]


@dataclass(frozen=True)
class Column:
    column_id: str
    label: str
    unit: str | None = None
    kind: ColumnKind = "number"
    display_mode: Literal["exact", "population_3sf"] = "exact"


@dataclass(frozen=True)
class Table:
    table_id: str
    title: str
    columns: tuple[Column, ...]
    rows: tuple[tuple[Cell, ...], ...]
    notes: tuple[str, ...]
    coverage: tuple[str, ...]  # what the figures cover; contains no figures
    exclusions: tuple[tuple[str, Decimal], ...]  # reason, weight left out
    source_result_ids: tuple[str, ...]
    maturity: str = MATURITY
    population_label: str = ""

    def __post_init__(self) -> None:
        ids = [c.column_id for c in self.columns]
        if len(set(ids)) != len(ids):
            raise ValueError(f"table {self.table_id}: duplicate column ids")
        for row in self.rows:
            if len(row) != len(self.columns):
                raise ValueError(f"table {self.table_id}: a row has the wrong number of cells")
            if any(isinstance(v, Decimal) and not v.is_finite() for v in row):
                raise ValueError(f"table {self.table_id}: numeric cells must be finite")
            if any(
                c.kind == "number" and v is not None and not isinstance(v, Decimal)
                for c, v in zip(self.columns, row, strict=True)
            ):
                raise ValueError(
                    f"table {self.table_id}: numeric cells must be Decimals or missing"
                )
        if any(not weight.is_finite() for _, weight in self.exclusions):
            raise ValueError(f"table {self.table_id}: exclusion weights must be finite")

    def column_index(self, column_id: str) -> int:
        for i, c in enumerate(self.columns):
            if c.column_id == column_id:
                return i
        raise KeyError(f"table {self.table_id}: no column {column_id!r}")

    def column(self, column_id: str) -> Column:
        return self.columns[self.column_index(column_id)]

    def row_index(self, key: str) -> int:
        """The first row whose first cell is `key`."""
        for i, row in enumerate(self.rows):
            if row[0] == key:
                return i
        raise KeyError(f"table {self.table_id}: no row {key!r}")

    def cell(self, row: int, column_id: str) -> Cell:
        return self.rows[row][self.column_index(column_id)]

    def display(self, row: int, column_id: str) -> str:
        return format_cell(self.column(column_id), self.cell(row, column_id))

    def displayed_numbers(self) -> set[str]:
        """Every number as the table shows it (for checking narrative text)."""
        shown = set()
        for r in range(len(self.rows)):
            for c in self.columns:
                if c.kind == "number" and isinstance(self.cell(r, c.column_id), Decimal):
                    shown.add(self.display(r, c.column_id))
        shown.update(format_decimal(w, population=True) for _, w in self.exclusions)
        return shown

    def plain(self) -> dict[str, Any]:
        """Deterministic JSON-ready form, without the hash."""
        return {
            "table_id": self.table_id,
            "title": self.title,
            "columns": [
                {
                    "id": c.column_id,
                    "label": c.label,
                    "unit": c.unit,
                    "kind": c.kind,
                    "display_mode": c.display_mode,
                }
                for c in self.columns
            ],
            "rows": [[_plain_cell(v) for v in row] for row in self.rows],
            "notes": list(self.notes),
            "coverage": list(self.coverage),
            "exclusions": [[reason, format(w, "f")] for reason, w in self.exclusions],
            "source_result_ids": list(self.source_result_ids),
            "maturity": self.maturity,
            "population_label": self.population_label,
        }

    @property
    def sha256(self) -> str:
        text = json.dumps(self.plain(), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _plain_cell(value: Cell) -> str | None:
    if isinstance(value, Decimal):
        return format(value, "f")
    return value


def format_decimal(value: Decimal, *, population: bool = False) -> str:
    """Round population presentation only; household/rule amounts stay exact."""
    if not value.is_finite():
        raise ValueError("displayed numbers must be finite")
    if population and value:
        with localcontext() as context:
            context.prec = max(context.prec, len(value.as_tuple().digits) + 1)
            value = value.quantize(Decimal(1).scaleb(value.adjusted() - 2), ROUND_HALF_UP)
    return format(value, ",f")


def format_cell(column: Column, value: Cell) -> str:
    if value is None:
        return NOT_AVAILABLE
    if isinstance(value, Decimal):
        return format_decimal(value, population=column.display_mode == "population_3sf")
    return value


def slug(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_").lower()


_CALCULATED = "Households whose change was calculated in both runs."
_NEVER_ZERO = (
    "Households needing review or outside the modelled scope are shown separately and never "
    "counted as zero."
)
_PRECISION = (
    "Population figures are displayed to three significant figures; stored Decimals are retained. "
    "Uncertainty ranges are unavailable: this retained run supplies no uncertainty method or bounds."
)


def _grouped_table(
    grouped: GroupedTable,
    *,
    table_id: str,
    title: str,
    group_label: str,
    source_result_ids: Sequence[str],
) -> Table:
    unit = grouped.unit
    columns = (
        Column("group", group_label, kind="text"),
        Column("households", "Households (count)", "households"),
        Column("weight", "Weight", "weighted households", display_mode="population_3sf"),
        Column(
            "calculated_weight",
            "Weight calculated",
            "weighted households",
            display_mode="population_3sf",
        ),
        Column(
            "total_change", "Total change", f"{unit}, weighted total", display_mode="population_3sf"
        ),
        Column(
            "average_change",
            "Average change per calculated household",
            unit,
            display_mode="population_3sf",
        ),
        Column(
            "gain_weight", "Weight gaining", "weighted households", display_mode="population_3sf"
        ),
        Column(
            "loss_weight", "Weight losing", "weighted households", display_mode="population_3sf"
        ),
        Column(
            "needs_review_weight",
            "Weight needing review",
            "weighted households",
            display_mode="population_3sf",
        ),
        Column(
            "unsupported_weight",
            "Weight outside scope",
            "weighted households",
            display_mode="population_3sf",
        ),
    )
    rows: list[tuple[Cell, ...]] = []
    for name, s in grouped.groups.items():
        average = s.total_change / s.calculated_weight if s.calculated_weight else None
        rows.append(
            (
                name,
                Decimal(s.households),
                s.weight,
                s.calculated_weight,
                s.total_change,
                average,
                s.by_class[ChangeClass.GAIN],
                s.by_class[ChangeClass.LOSS],
                s.by_class[ChangeClass.NEEDS_REVIEW],
                s.by_class[ChangeClass.UNSUPPORTED],
            )
        )
    notes = [
        f"Component set: {' + '.join(grouped.component_set)} ({unit}).",
        "A household with no calculated change contributes no amount, not a zero.",
        _PRECISION,
    ]
    if not rows:
        notes.append("No household fell into this table.")
    return Table(
        table_id=table_id,
        title=title,
        columns=columns,
        rows=tuple(rows),
        notes=tuple(notes),
        coverage=(_CALCULATED, _NEVER_ZERO),
        exclusions=tuple(
            (reason, weight) for reason, weight in sorted(grouped.left_out.items()) if reason
        ),
        source_result_ids=tuple(source_result_ids),
    )


def distribution_by_income_group(
    grouped: GroupedTable, *, source_result_ids: Sequence[str]
) -> Table:
    """The change by gross household income decile (01 is the lowest)."""
    return _grouped_table(
        grouped,
        table_id="distribution_by_income_group",
        title="Distribution by gross household income decile",
        group_label="Income decile (01 lowest)",
        source_result_ids=source_result_ids,
    )


def household_types(grouped: GroupedTable, *, source_result_ids: Sequence[str]) -> Table:
    return _grouped_table(
        grouped,
        table_id="household_types",
        title="Change by household type",
        group_label="Household type",
        source_result_ids=source_result_ids,
    )


_CLASS_LABELS = {
    ChangeClass.GAIN: "gain",
    ChangeClass.LOSS: "loss",
    ChangeClass.NO_CHANGE: "no change",
    ChangeClass.NEEDS_REVIEW: "needs review",
    ChangeClass.UNSUPPORTED: "outside modelled scope",
}


def winners_losers(grouped: GroupedTable, *, source_result_ids: Sequence[str]) -> Table:
    """Winners and losers over the `all` group of an overall table."""
    summary = grouped.groups["all"]
    unit = grouped.unit
    means = {ChangeClass.GAIN: summary.mean_gain, ChangeClass.LOSS: summary.mean_loss}
    largest = {ChangeClass.GAIN: summary.largest_gain, ChangeClass.LOSS: summary.largest_loss}
    rows: list[tuple[Cell, ...]] = []
    for cls in ChangeClass:
        weight = summary.by_class[cls]
        share = weight * 100 / summary.weight if summary.weight else None
        rows.append((_CLASS_LABELS[cls], weight, share, means.get(cls), largest.get(cls)))
    return Table(
        table_id="winners_losers",
        title="Winners and losers",
        columns=(
            Column("outcome", "Outcome", kind="text"),
            Column("weight", "Weight", "weighted households", display_mode="population_3sf"),
            Column(
                "share",
                "Share of weight",
                "per cent of weighted households",
                display_mode="population_3sf",
            ),
            Column("mean_change", "Mean change", unit, display_mode="population_3sf"),
            Column("largest_change", "Largest change", unit, display_mode="population_3sf"),
        ),
        rows=tuple(rows),
        notes=(
            f"Component set: {' + '.join(grouped.component_set)} ({unit}).",
            "Mean and largest change are shown for gainers and losers only.",
            _PRECISION,
        ),
        coverage=(
            "All households that ran, weighted.",
            _NEVER_ZERO,
        ),
        exclusions=tuple((r, w) for r, w in sorted(grouped.left_out.items()) if r),
        source_result_ids=tuple(source_result_ids),
    )


def fiscal_components(
    fiscal: dict[str, ComponentFiscal], *, source_result_ids: Sequence[str]
) -> Table:
    """Static entitlement by component. Each row keeps its own period, and
    components are never added across periods."""
    ordered = sorted(fiscal.values(), key=lambda f: (-abs(f.delta_total), f.component))
    money = "NZD, weighted total, period per Unit column"
    rows = tuple(
        (
            f.component,
            f.unit,
            f.baseline_total,
            f.reform_total,
            f.delta_total,
            f.coverage["calculated"],
            f.coverage["needs_review"],
            f.coverage["unsupported"],
        )
        for f in ordered
    )
    return Table(
        table_id="fiscal_components",
        title="Direct fiscal result by component (static entitlement)",
        columns=(
            Column("component", "Component", kind="text"),
            Column("unit", "Unit", kind="text"),
            Column("baseline_total", "Baseline total", money, display_mode="population_3sf"),
            Column("reform_total", "Reform total", money, display_mode="population_3sf"),
            Column("change", "Change", money, display_mode="population_3sf"),
            Column(
                "calculated_weight",
                "Weight calculated",
                "weighted households",
                display_mode="population_3sf",
            ),
            Column(
                "needs_review_weight",
                "Weight needing review",
                "weighted households",
                display_mode="population_3sf",
            ),
            Column(
                "unsupported_weight",
                "Weight outside scope",
                "weighted households",
                display_mode="population_3sf",
            ),
        ),
        rows=rows,
        notes=(
            "Static entitlement at full take-up, with no behavioural response.",
            "Components in different periods (tax year, week) are not added together.",
            _PRECISION,
        ),
        coverage=(
            "Totals cover households whose component was calculated in both runs.",
            _NEVER_ZERO,
        ),
        exclusions=(),
        source_result_ids=tuple(source_result_ids),
    )


def baseline_totals(table: Table) -> Table:
    """Baseline entitlement by component, read from the fiscal table."""
    keep = ("component", "unit", "baseline_total", "calculated_weight")
    idx = [table.column_index(k) for k in keep]
    return Table(
        table_id="baseline_totals",
        title="Baseline static entitlement by component",
        columns=tuple(table.columns[i] for i in idx),
        rows=tuple(tuple(row[i] for i in idx) for row in table.rows),
        notes=("Baseline totals are read from the retained population results.", _PRECISION),
        coverage=table.coverage,
        exclusions=table.exclusions,
        source_result_ids=table.source_result_ids,
        population_label=table.population_label,
    )


def reform_overrides(
    reform: Reform,
    overridden: Sequence[OverriddenParameter],
    *,
    source_result_ids: Sequence[str],
) -> Table:
    """The reform's overrides, each marked as a scenario assumption."""
    by_key = {(o.policy_id, o.parameter_id): o for o in overridden}
    rows: list[tuple[Cell, ...]] = []
    for ov in reform.overrides:
        found = by_key.get((ov.policy_id, ov.parameter_id))
        rows.append(
            (
                f"{ov.policy_id}.{ov.parameter_id}",
                ov.operation.value,
                ov.value,
                found.baseline_value if found else None,
                found.reform_value if found else None,
                found.unit if found else None,
                SCENARIO_ASSUMPTION,
            )
        )
    return Table(
        table_id="reform_overrides",
        title="Reform overrides",
        columns=(
            Column("parameter", "Parameter", kind="text"),
            Column("operation", "Operation", kind="text"),
            Column("operand", "Operand"),
            Column("baseline_value", "Baseline value"),
            Column("reform_value", "Reform value"),
            Column("unit", "Unit", kind="text"),
            Column("status", "Status", kind="text"),
        ),
        rows=tuple(rows),
        notes=(
            "Every reform value is a scenario assumption, not a sourced statutory value.",
            (
                "A baseline or reform value shown as not available did not resolve or did not "
                "change in this run."
            ),
        ),
        coverage=("Every override in the reform.",),
        exclusions=(),
        source_result_ids=tuple(source_result_ids),
    )


def withdrawal_rates(
    path: WithdrawalPath, *, label: str, source_result_ids: Sequence[str]
) -> Table:
    """Withdrawal rates between successive points of an income path."""
    components = tuple(path.steps[0].rates) if path.steps else ()
    columns = (
        Column("income_from", "Income from", path.unit),
        Column("income_to", "Income to", path.unit),
        *(Column(f"rate_{c}", f"{c} withdrawal rate", RATE_UNIT) for c in components),
    )
    rows = tuple(
        (
            step.income_from,
            step.income_to,
            *(step.rates[c] for c in components),
        )
        for step in path.steps
    )
    return Table(
        table_id=f"withdrawal_rates_{slug(label)}",
        title=f"Withdrawal rates along an income path: {label}",
        columns=columns,
        rows=rows,
        notes=(
            f"Income fact stepped: {path.income_fact}.",
            (
                "These are withdrawal rates of the modelled benefits, not effective marginal tax "
                "rates: income tax and other benefits are not modelled here."
            ),
            "A rate shown as not available was not calculated at both ends of the step.",
            "The path is a labelled hypothetical, not a claim about any real household.",
        ),
        coverage=("Only the modelled components along this one path.",),
        exclusions=(),
        source_result_ids=tuple(source_result_ids),
    )


def payment_profile(path: WithdrawalPath, *, label: str, source_result_ids: Sequence[str]) -> Table:
    """Entitlement against income along a path."""
    components = tuple(path.points[0].values) if path.points else ()
    columns = (
        Column("income", "Income", path.unit),
        *(Column(f"entitlement_{c}", f"{c} entitlement", path.unit) for c in components),
    )
    rows = tuple((p.income, *(p.values[c] for c in components)) for p in path.points)
    return Table(
        table_id=f"payment_profile_{slug(label)}",
        title=f"Payment profile along an income path: {label}",
        columns=columns,
        rows=rows,
        notes=(
            f"Income fact stepped: {path.income_fact}.",
            "An entitlement shown as not available was not calculated at that income.",
            "The path is a labelled hypothetical, not a claim about any real household.",
        ),
        coverage=("Only the modelled components along this one path.",),
        exclusions=(),
        source_result_ids=tuple(source_result_ids),
    )


def example_households(
    examples: Sequence[WorkedExample],
    units: dict[str, str],
    *,
    source_result_ids: Sequence[str],
) -> Table:
    """Named example households, one row per household and component."""
    rows: list[tuple[Cell, ...]] = []
    for ex in examples:
        for component, d in ex.components.items():
            calculated = d.outcome == "calculated"
            rows.append(
                (
                    ex.example_id,
                    component,
                    units[component],
                    d.baseline.value if calculated else None,
                    d.reform.value if calculated else None,
                    d.delta,
                    d.outcome,
                )
            )
    return Table(
        table_id="example_households",
        title="Example household impacts",
        columns=(
            Column("household", "Example household", kind="text"),
            Column("component", "Component", kind="text"),
            Column("unit", "Unit", kind="text"),
            Column("baseline", "Baseline", "NZD, period per Unit column"),
            Column("reform", "Reform", "NZD, period per Unit column"),
            Column("change", "Change", "NZD, period per Unit column"),
            Column("outcome", "Outcome", kind="text"),
        ),
        rows=tuple(rows),
        notes=(
            (
                "Illustrative named households run once under the reform, not a sample of any "
                "population."
            ),
            "A value shown as not available was not calculated.",
        ),
        coverage=("Each named example household, for every modelled component.",),
        exclusions=(),
        source_result_ids=tuple(source_result_ids),
    )


def validation_summary(
    by_status: dict[RecordStatus, tuple[int, Decimal]], *, source_result_ids: Sequence[str]
) -> Table:
    """Population records by validation status."""
    rows = tuple((status.value, Decimal(n), w) for status, (n, w) in by_status.items())
    return Table(
        table_id="population_validation",
        title="Population records by validation status",
        columns=(
            Column("status", "Status", kind="text"),
            Column("households", "Households (count)", "households"),
            Column("weight", "Weight", "weighted households", display_mode="population_3sf"),
        ),
        rows=rows,
        notes=("Invalid households are left out of the run and counted here.", _PRECISION),
        coverage=("Every household in the population.",),
        exclusions=(),
        source_result_ids=tuple(source_result_ids),
    )


def policy_artifacts(
    artifacts: Sequence[tuple[str, str]], *, source_result_ids: Sequence[str]
) -> Table:
    """The policy files the run's parameters were bound to, with hashes."""
    return Table(
        table_id="policy_artifacts",
        title="Policy files bound by the run",
        columns=(
            Column("artifact", "Policy file", kind="text"),
            Column("sha256", "SHA-256", kind="text"),
        ),
        rows=tuple((path, sha) for path, sha in artifacts),
        notes=("Each file's hash was recorded when the parameters were loaded.",),
        coverage=("Every policy file the run bound.",),
        exclusions=(),
        source_result_ids=tuple(source_result_ids),
    )


def parameter_provenance(
    parameter_sets: Sequence[PolicyParameterSet],
    overridden: Sequence[OverriddenParameter],
    *,
    source_result_ids: Sequence[str],
) -> Table:
    """Parameter sources and review statuses.

    From the loaded parameter sets when the caller supplies them (every
    parameter, with its source, locator and review status). Otherwise only
    the overridden parameters' baseline evidence, which the run records;
    their review status is not recorded in the run, so it shows as not
    available."""
    rows: list[tuple[Cell, ...]] = []
    if parameter_sets:
        for ps in sorted(parameter_sets, key=lambda p: (p.policy_id, p.modelled_date)):
            for pid in sorted(ps.resolutions):
                r = ps.resolutions[pid]
                rows.append(
                    (
                        f"{ps.policy_id}.{pid}",
                        r.outcome,
                        r.value,
                        r.unit,
                        r.source_id,
                        r.locator,
                        r.review_status,
                    )
                )
        note = "All parameters of the loaded policy versions, as resolved for the modelled date."
    else:
        for o in overridden:
            rows.append(
                (
                    f"{o.policy_id}.{o.parameter_id}",
                    o.baseline_outcome,
                    o.baseline_value,
                    o.unit,
                    o.baseline_source_id,
                    o.baseline_locator,
                    None,
                )
            )
        note = (
            "Only the overridden parameters' baseline evidence is recorded in the run; review "
            "status is not recorded there."
        )
    return Table(
        table_id="parameter_provenance",
        title="Baseline parameter evidence and supplied context",
        columns=(
            Column("parameter", "Parameter", kind="text"),
            Column("outcome", "Outcome", kind="text"),
            Column("value", "Baseline value"),
            Column("unit", "Unit", kind="text"),
            Column("source_id", "Source", kind="text"),
            Column("locator", "Locator", kind="text"),
            Column("review_status", "Review status", kind="text"),
        ),
        rows=tuple(rows),
        notes=(note,),
        coverage=("Baseline parameters only; reform values are scenario assumptions.",),
        exclusions=(),
        source_result_ids=tuple(source_result_ids),
    )
