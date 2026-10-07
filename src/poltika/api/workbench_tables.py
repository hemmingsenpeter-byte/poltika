"""Workbench results as generic, renderable blocks.

`build_results` turns stored population runs into the payload the workbench
shows: a headline strip and one entry per tab, each a list of *blocks*
(tables, a horizon strip, a list of statements). The page renders blocks and
knows nothing about any instrument, and the Excel and CSV exports are written
from the same blocks, so what is on screen is what is exported.

Every amount is an engine result, aggregated only by the weighted sums and
counts of `scenarios/microsim/analysis.py`. This module adds nothing to a
household's entitlement and never converts between units: WFF is per tax
year, the Accommodation Supplement per week, and they are never added.

**Not calculated is not zero.** A cell whose component was not calculated
holds the outcome word (`needs_review`, `unsupported`) or "not calculated",
never `0`.

**Rounding.** Aggregate amounts are rounded once, to whole cents, and
weighted household counts to whole households, here. The page and the
exports show these same strings, so their totals match. Worked-example
amounts are the engine's exact decimals.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from poltika.api import workbench_config as config
from poltika.engines.simulator.trace import plain
from poltika.scenarios.microsim import analysis
from poltika.scenarios.microsim.runner import COMPONENTS, UNITS, PopulationRun
from poltika.scenarios.microsim.validation import RecordStatus
from poltika.scenarios.microsim.weighting import weighted_mean
from poltika.scenarios.microsim.worked_examples import WorkedExample
from poltika.scenarios.population import household_type
from poltika.semantics.population import PopulationDataset

NOT_CALCULATED = "not calculated"
_CENT = Decimal("0.01")
_ONE = Decimal(1)


@dataclass(frozen=True)
class OptionResult:
    label: str
    dataset: PopulationDataset
    run: PopulationRun
    examples: list[WorkedExample]


@dataclass(frozen=True)
class FamilyType:
    family_id: str
    description: str


def _money(value: Decimal | None) -> str | None:
    return None if value is None else str(value.quantize(_CENT, ROUND_HALF_UP))


def _count(value: Decimal) -> str:
    return str(value.quantize(_ONE, ROUND_HALF_UP))


def _col(column_id: str, label: str, kind: str = "text", group: str | None = None) -> dict[str, Any]:
    return {"id": column_id, "label": label, "kind": kind, "group": group}


def _table(
    table_id: str,
    title: str,
    columns: list[dict[str, Any]],
    rows: list[list[Any]],
    notes: Sequence[str] = (),
) -> dict[str, Any]:
    return {
        "type": "table",
        "id": table_id,
        "title": title,
        "columns": columns,
        "rows": rows,
        "notes": list(notes),
    }


# --- classification with a threshold ---------------------------------------


def _classify(change: analysis.HouseholdChange, threshold: Decimal) -> str:
    if change.change is None:
        return change.change_class.value  # needs_review or unsupported
    if change.change >= threshold:
        return "better_off"
    if change.change <= -threshold:
        return "worse_off"
    return "no_material_change"


_CLASSES = ("better_off", "worse_off", "no_material_change", "needs_review", "unsupported", "invalid")


def _summary(
    changes: list[tuple[analysis.HouseholdChange, str]],
) -> dict[str, Any]:
    weights = {c: Decimal(0) for c in _CLASSES}
    calculated = []
    for change, cls in changes:
        weights[cls] += change.weight
        if change.change is not None:
            calculated.append((change.change, change.weight))
    total = sum((v * w for v, w in calculated), Decimal(0))
    return {
        "weights": weights,
        "total_change": total if calculated else None,
        "mean_change": weighted_mean(calculated),
    }


def _measure_changes(
    option: OptionResult, components: Sequence[str], threshold: Decimal
) -> list[tuple[str, analysis.HouseholdChange, str]]:
    by_id = {h.household_id: h for h in option.dataset.households}
    out = []
    for result in option.run.households:
        change = analysis.household_change(result, components)
        out.append(
            (household_type(by_id[result.household_id]).value, change, _classify(change, threshold))
        )
    for checked in option.run.validation.households:
        if checked.status is RecordStatus.INVALID:
            change = analysis.HouseholdChange(
                checked.household_id,
                option.run.validation.weights[checked.household_id],
                analysis.ChangeClass.UNSUPPORTED,
                None,
            )
            out.append((household_type(by_id[checked.household_id]).value, change, "invalid"))
    return out


def _threshold(unit: str) -> Decimal:
    return config.WINNER_LOSER_THRESHOLDS[unit]


# --- headline ---------------------------------------------------------------


def headline(options: Sequence[OptionResult]) -> list[dict[str, Any]]:
    items = []
    for measure in config.MEASURES:
        unit = analysis.component_set_unit(measure.components)
        threshold = _threshold(unit)
        for option in options:
            rows = _measure_changes(option, measure.components, threshold)
            s = _summary([(c, cls) for _, c, cls in rows])
            items.append(
                {
                    "measure_id": measure.measure_id,
                    "measure": measure.label,
                    "unit": unit,
                    "option": option.label,
                    "change_total": (
                        _money(s["total_change"])
                        if s["total_change"] is not None
                        else NOT_CALCULATED
                    ),
                    "mean_change": _money(s["mean_change"]),
                    "better_off": _count(s["weights"]["better_off"]),
                    "worse_off": _count(s["weights"]["worse_off"]),
                    "no_material_change": _count(s["weights"]["no_material_change"]),
                    "not_calculated": _count(
                        s["weights"]["needs_review"]
                        + s["weights"]["unsupported"]
                        + s["weights"]["invalid"]
                    ),
                    "threshold": str(threshold),
                }
            )
    return items


# --- fiscal tab ---------------------------------------------------------------


def _fiscal_tab(options: Sequence[OptionResult]) -> dict[str, Any]:
    fiscals = [analysis.fiscal(o.run) for o in options]
    for fiscal in fiscals[1:]:
        # One status quo column: every option must share the same baseline.
        if any(fiscal[c].baseline_total != fiscals[0][c].baseline_total for c in COMPONENTS):
            raise ValueError("options were run against different baselines")
    columns = [
        _col("component", "Component"),
        _col("unit", "Unit"),
        _col("status_quo", "Status quo", "money", group="Total"),
    ]
    for i, option in enumerate(options):
        columns.append(_col(f"opt{i}_value", option.label, "money", group="Total"))
        columns.append(_col(f"opt{i}_change", f"{option.label}: change", "money", group="Total"))
    rows: list[list[Any]] = []
    coverage_rows: list[list[Any]] = []
    for component in COMPONENTS:
        first = fiscals[0][component]
        calculated = first.coverage["calculated"] > 0
        row: list[Any] = [
            component,
            UNITS[component],
            _money(first.baseline_total) if calculated else NOT_CALCULATED,
        ]
        for option, fiscal in zip(options, fiscals, strict=True):
            f = fiscal[component]
            ok = f.coverage["calculated"] > 0
            row.append(_money(f.reform_total) if ok else NOT_CALCULATED)
            row.append(_money(f.delta_total) if ok else NOT_CALCULATED)
            invalid = option.run.validation.by_status()[RecordStatus.INVALID][1]
            total = sum(f.coverage.values(), Decimal(0)) + invalid
            share = (
                (f.coverage["calculated"] * 100 / total).quantize(Decimal("0.1"), ROUND_HALF_UP)
                if total
                else Decimal(0)
            )
            coverage_rows.append(
                [
                    component,
                    option.label,
                    _count(f.coverage["calculated"]),
                    _count(f.coverage["needs_review"]),
                    _count(f.coverage["unsupported"]),
                    _count(invalid),
                    str(share),
                ]
            )
        rows.append(row)
    population_label = options[0].run.label
    return {
        "id": "fiscal",
        "title": "Fiscal",
        "status": "active",
        "blocks": [
            {
                "type": "horizon",
                "id": "horizon",
                "title": "Fiscal years",
                "years": [
                    {"label": y.label, "modelled": y.modelled, "note": y.note}
                    for y in config.FISCAL_YEARS
                ],
            },
            _table(
                "fiscal_components",
                "Entitlement by component, 2026-27",
                columns,
                rows,
                notes=[
                    (
                        "Totals are the weighted entitlement of households whose component was "
                        "calculated both before and after the change. Components are never "
                        "added: WFF is per tax year, the Accommodation Supplement per week, and "
                        "the in-work tax credit is not calculated in 2026-27, so there is no "
                        "total row."
                    ),
                    config.INTERACTION_NOTE,
                    population_label,
                    "Full take-up (static entitlement), not expenditure.",
                ],
            ),
            _table(
                "fiscal_coverage",
                "Households behind each total (weighted)",
                [
                    _col("component", "Component"),
                    _col("option", "Option"),
                    _col("calculated", "Calculated", "count"),
                    _col("needs_review", "Needs review", "count"),
                    _col("unsupported", "Unsupported", "count"),
                    _col("invalid", "Invalid (excluded)", "count"),
                    _col("share", "Calculated, % of households", "share"),
                ],
                coverage_rows,
                notes=["A component that was not calculated is left out of its total, not counted as zero."],
            ),
        ],
    }


# --- households tab -------------------------------------------------------------


def _winners_losers_tables(options: Sequence[OptionResult]) -> list[dict[str, Any]]:
    tables = []
    for measure in config.MEASURES:
        unit = analysis.component_set_unit(measure.components)
        threshold = _threshold(unit)
        rows: list[list[Any]] = []
        for option in options:
            grouped: dict[str, list[tuple[analysis.HouseholdChange, str]]] = {}
            for group, change, cls in _measure_changes(option, measure.components, threshold):
                grouped.setdefault(group, []).append((change, cls))
            for group in sorted(grouped):
                s = _summary(grouped[group])
                w = s["weights"]
                rows.append(
                    [
                        option.label,
                        group,
                        _count(w["better_off"]),
                        _count(w["worse_off"]),
                        _count(w["no_material_change"]),
                        _count(w["needs_review"]),
                        _count(w["unsupported"]),
                        _count(w["invalid"]),
                        _money(s["mean_change"]) if s["mean_change"] is not None else NOT_CALCULATED,
                    ]
                )
        tables.append(
            _table(
                f"winners_losers_{measure.measure_id}",
                f"{measure.label}: better and worse off by household type ({unit})",
                [
                    _col("option", "Option"),
                    _col("household_type", "Household type"),
                    _col("better_off", "Better off", "count"),
                    _col("worse_off", "Worse off", "count"),
                    _col("no_material_change", "No material change", "count"),
                    _col("needs_review", "Needs review", "count"),
                    _col("unsupported", "Unsupported", "count"),
                    _col("invalid", "Invalid (excluded)", "count"),
                    _col("mean_change", f"Mean change of those calculated ({unit})", "money"),
                ],
                rows,
                notes=[
                    (
                        f"Better or worse off means a change of at least {threshold} ({unit}). "
                        "Weighted households."
                    )
                ],
            )
        )
    return tables


def _cell(outcome: str, value: Decimal | None) -> str:
    return str(value) if outcome == "calculated" and value is not None else outcome


def _examples_table(options: Sequence[OptionResult], families: Sequence[FamilyType]) -> dict[str, Any]:
    columns = [
        _col("family", "Family type"),
        _col("component", "Component"),
        _col("unit", "Unit"),
        _col("status_quo", "Status quo", "money", group="Amount"),
    ]
    for i, option in enumerate(options):
        columns.append(_col(f"opt{i}_value", option.label, "money", group="Amount"))
        columns.append(_col(f"opt{i}_change", f"{option.label}: change", "money", group="Amount"))
    by_option = [{e.example_id: e for e in o.examples} for o in options]
    rows: list[list[Any]] = []
    for family in families:
        for component in COMPONENTS:
            first = by_option[0][family.family_id].components[component]
            row: list[Any] = [
                family.description or family.family_id,
                component,
                UNITS[component],
                _cell(first.baseline.outcome, first.baseline.value),
            ]
            for examples in by_option:
                d = examples[family.family_id].components[component]
                row.append(_cell(d.reform.outcome, d.reform.value))
                row.append(_cell(d.outcome, d.delta))
            rows.append(row)
    return _table(
        "worked_examples",
        "Worked examples: standard family types",
        columns,
        rows,
        notes=[
            (
                "Each family type is one household with stated facts, not an average. Amounts "
                "are in each component's own unit. A component that is not calculated shows "
                "its outcome, never zero."
            ),
        ],
    )


def _households_tab(options: Sequence[OptionResult], families: Sequence[FamilyType]) -> dict[str, Any]:
    return {
        "id": "households",
        "title": "Households",
        "status": "active",
        "blocks": [*_winners_losers_tables(options), _examples_table(options, families)],
    }


# --- assumptions and provenance -------------------------------------------------------


def _assumptions_tab(
    options: Sequence[OptionResult], instruments: Sequence[dict[str, Any]]
) -> dict[str, Any]:
    first = options[0].run
    runnable = [i for i in instruments if i.get("valid") and i.get("runnable")]

    identity_rows: list[list[Any]] = [
        ["Law baseline", config.BASELINE_LABEL],
        ["Population", f"{first.population_id} v{first.population_version}"],
        ["Population SHA-256", first.population_sha256],
        ["Population label", first.label],
        ["Engine package version", first.code.package_version],
        ["Source commit", first.code.source_commit or "unknown"],
        ["Source tree clean", str(first.code.source_tree_clean)],
        ["Reproducible from the commit", "yes" if first.code.reproducible else "no"],
        ["Dependency lock SHA-256", first.code.dependency_lock_sha256 or "unknown"],
    ]
    for instrument in runnable:
        identity_rows.append([f"Policy: {instrument['title']}", f"version {instrument['version']}"])
    for option in options:
        identity_rows.append([f"Run ID: {option.label}", option.run.run_id])
        identity_rows.append([f"Results SHA-256: {option.label}", option.run.results_sha256])
        identity_rows.append([f"Reform SHA-256: {option.label}", option.run.reform.reform_sha256()])

    changed_rows: list[list[Any]] = []
    for option in options:
        for o in option.run.overridden:
            changed_rows.append(
                [
                    option.label,
                    o.policy_id,
                    o.parameter_id,
                    o.modelled_date,
                    o.unit or "",
                    None if o.baseline_value is None else str(o.baseline_value),
                    str(o.reform_value),
                    "scenario assumption, not sourced",
                ]
            )

    used_rows: list[list[Any]] = []
    for instrument in runnable:
        sources = {s["id"]: s for s in instrument["sources"]}
        for p in instrument["parameters"]:
            cur = p["current"]
            source = sources.get(cur.get("source_id") or "", {})
            used_rows.append(
                [
                    instrument["title"],
                    instrument["version"],
                    p["id"],
                    cur["value"] if cur["outcome"] == "resolved" else cur["outcome"],
                    p["unit_label"],
                    cur.get("effective_from"),
                    cur.get("effective_to"),
                    cur.get("review_status"),
                    source.get("title"),
                    cur.get("locator"),
                    source.get("url"),
                ]
            )

    decision_rows = [
        [instrument["title"], d["id"], d["title"]]
        for instrument in runnable
        for d in instrument["decisions"]
    ]
    artifact_rows = [[name, sha] for name, sha in first.policy_artifacts]

    return {
        "id": "assumptions",
        "title": "Assumptions & provenance",
        "status": "active",
        "blocks": [
            _table(
                "run_identity",
                "Run identity",
                [_col("item", "Item"), _col("value", "Value")],
                identity_rows,
                notes=["Rerunning the same inputs on the same commit reproduces these run IDs."],
            ),
            _table(
                "parameters_changed",
                "Parameters changed by the options",
                [
                    _col("option", "Option"),
                    _col("policy", "Policy"),
                    _col("parameter", "Parameter"),
                    _col("modelled_date", "Modelled date"),
                    _col("unit", "Unit"),
                    _col("baseline", "Current value", "money"),
                    _col("new", "New value", "money"),
                    _col("basis", "Basis"),
                ],
                changed_rows,
            ),
            _table(
                "parameters_used",
                "Every parameter used",
                [
                    _col("policy", "Policy"),
                    _col("version", "Spec version"),
                    _col("parameter", "Parameter"),
                    _col("value", "Value", "money"),
                    _col("unit", "Unit"),
                    _col("effective_from", "Effective from"),
                    _col("effective_to", "Effective to (exclusive)"),
                    _col("review_status", "Review status"),
                    _col("source", "Source"),
                    _col("locator", "Locator"),
                    _col("url", "Link"),
                ],
                used_rows,
            ),
            _table(
                "policy_artifacts",
                "Policy files the parameters were read from",
                [_col("file", "File"), _col("sha256", "SHA-256")],
                artifact_rows,
            ),
            _table(
                "decisions",
                "Interpretation decisions",
                [_col("policy", "Policy"), _col("decision", "Decision"), _col("title", "Title")],
                decision_rows,
            ),
            {
                "type": "list",
                "id": "limitations",
                "title": "Limitations",
                "items": list(config.LIMITATIONS),
            },
        ],
    }


# --- the payload -------------------------------------------------------------------------


def build_results(
    scenario: dict[str, Any],
    options: Sequence[OptionResult],
    instruments: Sequence[dict[str, Any]],
    families: Sequence[FamilyType],
) -> dict[str, Any]:
    first = options[0].run
    for option in options[1:]:
        if (
            option.run.population_sha256 != first.population_sha256
            or option.run.code != first.code
            or option.run.policy_artifacts != first.policy_artifacts
        ):
            raise ValueError("options must share the same population, code and policy baseline")
    active = {
        "fiscal": _fiscal_tab(options),
        "households": _households_tab(options, families),
        "assumptions": _assumptions_tab(options, instruments),
    }
    tabs = [
        active[t.tab_id]
        if t.status == "active" and t.tab_id in active
        else {"id": t.tab_id, "title": t.title, "status": "deferred", "note": t.note, "blocks": []}
        for t in config.TABS
    ]
    return {
        "scenario": scenario,
        "law_baseline": config.BASELINE_LABEL,
        "synthetic": first.synthetic,
        "population_label": first.label,
        "runs": [
            {
                "label": o.label,
                "run_id": o.run.run_id,
                "results_sha256": o.run.results_sha256,
                "reproducible": o.run.code.reproducible,
                "reform": plain(o.run.reform.model_dump(mode="json")),
            }
            for o in options
        ],
        "headline": headline(options),
        "tabs": tabs,
    }


# --- distribution (Task B0.1.2) ----------------------------------------------------------

_DIMENSIONS = (
    ("decile", analysis.by_decile),
    ("household_type", analysis.by_household_type),
    ("children", analysis.by_children),
    ("region", analysis.by_region),
)


NONE_IN_GROUP = "none"


def _mean_or(value: Decimal | None, calculated_weight: Decimal) -> str:
    """A group mean, or why there is none: no household in the group was
    calculated ("not calculated"), or none had that kind of change ("none")."""
    if value is not None:
        return str(_money(value))
    return NONE_IN_GROUP if calculated_weight else NOT_CALCULATED


def distribution_tables(options: Sequence[OptionResult]) -> list[dict[str, Any]]:
    """Gains and losses of any size by income decile, household type,
    children and region, from `analysis`'s grouped summaries. Built once,
    when the run is made, and stored with it. Unlike the winners and losers
    tables there is no threshold: every calculated change counts."""
    tables = []
    for measure in config.MEASURES:
        unit = analysis.component_set_unit(measure.components)
        for dimension_id, group in _DIMENSIONS:
            rows: list[list[Any]] = []
            notes: list[str] = []
            dimension = ""
            for option in options:
                table = group(option.dataset, option.run, list(measure.components))
                dimension = table.dimension
                for key in sorted(table.groups):
                    s = table.groups[key]
                    c = s.by_class
                    rows.append(
                        [
                            option.label,
                            key,
                            _count(s.weight),
                            _count(c[analysis.ChangeClass.GAIN]),
                            _count(c[analysis.ChangeClass.LOSS]),
                            _count(c[analysis.ChangeClass.NO_CHANGE]),
                            _count(
                                c[analysis.ChangeClass.NEEDS_REVIEW]
                                + c[analysis.ChangeClass.UNSUPPORTED]
                            ),
                            _mean_or(s.mean_gain, s.calculated_weight),
                            _mean_or(s.mean_loss, s.calculated_weight),
                            _money(s.total_change) if s.calculated_weight else NOT_CALCULATED,
                        ]
                    )
                notes += [
                    f"{option.label}: {_count(w)} weighted households left out ({reason})."
                    for reason, w in sorted(table.left_out.items())
                ]
            tables.append(
                _table(
                    f"distribution_{measure.measure_id}_{dimension_id}",
                    f"{measure.label} by {dimension} ({unit})",
                    [
                        _col("option", "Option"),
                        _col("group", dimension.capitalize()),
                        _col("households", "Households", "count"),
                        _col("gain", "Gain", "count"),
                        _col("loss", "Loss", "count"),
                        _col("no_change", "No change", "count"),
                        _col("not_calculated", "Not calculated", "count"),
                        _col("mean_gain", f"Mean gain ({unit})", "money"),
                        _col("mean_loss", f"Mean loss ({unit})", "money"),
                        _col("total_change", f"Total change, calculated ({unit})", "money"),
                    ],
                    rows,
                    notes=[
                        (
                            "Any change counts here, with no threshold. Weighted households. "
                            "A household whose component was not calculated is counted as not "
                            "calculated, never as no change. A mean shows \"none\" when no "
                            "calculated household in the group had that kind of change."
                        ),
                        *notes,
                    ],
                )
            )
    return tables
