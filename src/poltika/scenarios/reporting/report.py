"""Pass 1 capability 17: the economist-style report.

`build_report()` assembles an `EconomistReport` from a `PopulationRun`, the
population it ran, and optional withdrawal paths, example households and
parameter sets. The report is a structured model first. `to_json()`,
`to_markdown()` and `to_html()` render the same model, so they cannot
disagree about content.

**No LLM, no free numbers.** The narrative is templated sentences. Every
number in a sentence is read from a table cell (`CellRef`), formatted by the
table's own cell formatter. Facts (ids, hashes, versions) are listed apart
from the narrative.

**Missing inputs are said, not skipped.** A section whose inputs are absent
stays in the report with "Not available in this run: ..." lines.

**Maturity.** Pass 1 components are IMPLEMENTED: they exist, run and have
tests. The banner says so at the top of every rendering, and the report
never describes a figure as a published or official estimate.

**Determinism.** Nothing time- or environment-dependent is included, and
the JSON is sorted and indented, so the same inputs give identical bytes.
"""

from __future__ import annotations

import hashlib
import html
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from poltika.policy.loader import PolicyParameterSet
from poltika.scenarios.reporting import tables as t
from poltika.scenarios.reporting.adapter import (
    UNITS,
    PopulationRun,
    WithdrawalPath,
    WorkedExample,
    analyse,
)
from poltika.scenarios.reporting.charts import (
    ChartSpec,
    chart_from_table,
    render_svg,
    vega_lite,
)
from poltika.scenarios.reporting.tables import Table
from poltika.semantics.population import PopulationDataset

REPORT_FORMAT = "poltika-economist-report/0.1"
MATURITY_BANNER = (
    "MATURITY: IMPLEMENTED (Pass 1). The components behind this report exist, run and have "
    "tests. Correctness checks, external benchmarking and independent review have not been "
    "done. Treat every figure as a working figure for development, not as a published or "
    "official result and not as a finding about New Zealand."
)
UNAVAILABLE = "Not available in this run"


@dataclass(frozen=True)
class CellRef:
    table_id: str
    row: int
    column: str


@dataclass(frozen=True)
class Sentence:
    text: str
    refs: tuple[CellRef, ...] = ()


@dataclass(frozen=True)
class Section:
    section_id: str
    title: str
    facts: tuple[tuple[str, str], ...] = ()
    narrative: tuple[Sentence, ...] = ()
    tables: tuple[Table, ...] = ()
    charts: tuple[ChartSpec, ...] = ()
    unavailable: tuple[str, ...] = ()

    @property
    def status(self) -> str:
        if not (self.facts or self.narrative or self.tables):
            return "not_available"
        return "partial" if self.unavailable else "complete"


@dataclass(frozen=True)
class EconomistReport:
    report_id: str
    title: str
    maturity: str
    maturity_banner: str
    sections: tuple[Section, ...]

    def section(self, section_id: str) -> Section:
        for s in self.sections:
            if s.section_id == section_id:
                return s
        raise KeyError(section_id)

    def tables(self) -> dict[str, Table]:
        found: dict[str, Table] = {}
        for s in self.sections:
            for table in s.tables:
                found[table.table_id] = table
        return found


# ---------------------------------------------------------------- sentences

Fig = tuple[Table, int, str] | str


def _sentence(template: str, *figs: Fig) -> Sentence:
    """Fill `{0}`, `{1}`... from table cells (or plain strings, such as a
    backtick-quoted id). Only cell figures carry a reference."""
    shown: list[str] = []
    refs: list[CellRef] = []
    for fig in figs:
        if isinstance(fig, str):
            shown.append(fig)
        else:
            table, row, column = fig
            shown.append(table.display(row, column))
            refs.append(CellRef(table.table_id, row, column))
    return Sentence(template.format(*shown), tuple(refs))


def _decimal(table: Table, row: int, column: str) -> Decimal | None:
    value = table.cell(row, column)
    return value if isinstance(value, Decimal) else None


def _tick(name: str) -> str:
    return f"`{name}`"


def _na(*items: str) -> tuple[str, ...]:
    return tuple(f"{UNAVAILABLE}: {i}" for i in items)


# ----------------------------------------------------------------- sections


def _scenario(
    run: PopulationRun,
    reference_period: str | None,
    policy_versions: Mapping[str, str] | None,
) -> Section:
    missing: list[str] = []
    if reference_period is None:
        missing.append("reference period (the run does not record one)")
    if not policy_versions:
        missing.append("policy versions (the run records file hashes, not version labels)")
    code = run.code
    facts = (
        ("run_id", run.run_id),
        ("results_sha256", run.results_sha256),
        ("reform_id", run.reform.reform_id),
        ("reform_sha256", run.reform.reform_sha256()),
        ("reform_description", run.reform.description or f"{UNAVAILABLE}: none was given"),
        ("reference_period", reference_period or f"{UNAVAILABLE}"),
        (
            "policy_versions",
            "; ".join(f"{k}={v}" for k, v in sorted(policy_versions.items()))
            if policy_versions
            else UNAVAILABLE,
        ),
        (
            "data_version",
            (
                f"{run.population_id} version {run.population_version} "
                f"(sha256 {run.population_sha256})"
            ),
        ),
        (
            "model_code_version",
            (
                f"poltika {code.package_version}; source commit {code.source_commit or UNAVAILABLE}; "
                f"source tree clean: {_yn(code.source_tree_clean)}; dependency lock sha256 "
                f"{code.dependency_lock_sha256 or UNAVAILABLE}; reproducible: "
                f"{'yes' if code.reproducible else 'no'}"
            ),
        ),
    )
    return Section("scenario", "Scenario", facts=facts, unavailable=_na(*missing))


def _yn(value: bool | None) -> str:
    return UNAVAILABLE.lower() if value is None else ("yes" if value else "no")


def _baseline(fiscal_table: Table) -> Section:
    table = t.baseline_totals(fiscal_table)
    narrative = [
        Sentence(
            "The baseline applies the approved policy parameters unchanged. Totals are static "
            "entitlements at full take-up over the households whose component was calculated."
        )
    ]
    for r, row in enumerate(table.rows):
        narrative.append(
            _sentence(
                "Baseline {0}: {1} ({2}) over weight {3}.",
                _tick(str(row[0])),
                (table, r, "baseline_total"),
                (table, r, "unit"),
                (table, r, "calculated_weight"),
            )
        )
    return Section("baseline", "Baseline", narrative=tuple(narrative), tables=(table,))


def _reform(run: PopulationRun, ids: Sequence[str]) -> tuple[Section, Section]:
    table = t.reform_overrides(run.reform, run.overridden, source_result_ids=ids)
    narrative: list[Sentence] = []
    for r, row in enumerate(table.rows):
        name = _tick(str(row[0]))
        if _decimal(table, r, "reform_value") is not None:
            baseline = (
                _sentence("The baseline value is {0}.", (table, r, "baseline_value"))
                if _decimal(table, r, "baseline_value") is not None
                else Sentence("The baseline value did not resolve or did not change.")
            )
            first = _sentence(
                "The reform applies {0} to {1}, giving {2} ({3}), as a scenario assumption.",
                str(row[1]),
                name,
                (table, r, "reform_value"),
                (table, r, "unit"),
            )
            narrative += [first, baseline]
        else:
            narrative.append(
                Sentence(
                    f"The reform applies {row[1]} to {name} as a scenario assumption. The "
                    "reform value did not differ from the baseline in this run."
                )
            )
    reform = Section("reform", "Reform", narrative=tuple(narrative), tables=(table,))
    facts = (
        ("scenario_assumption", "every reform override above is a scenario assumption"),
        ("take_up", "full take-up of every entitlement"),
        ("behaviour", "no behavioural response; incomes and household composition are held fixed"),
        ("period", "amounts keep their own period (tax year or week) and are not added across"),
        (
            "income_definitions",
            (
                "income measures follow each policy's own definition; any mapping between them is "
                "stated by the population, not assumed by the report"
            ),
        ),
    )
    return reform, Section("assumptions", "Assumptions", facts=facts)


def _fiscal(fiscal_table: Table) -> Section:
    narrative: list[Sentence] = []
    for r, row in enumerate(fiscal_table.rows):
        narrative.append(
            _sentence(
                "{0}: static entitlement change of {1} ({2}) at full take-up, over households "
                "calculated in both runs (weight {3}). Not counted: weight {4} needs review and "
                "{5} is outside the modelled scope.",
                _tick(str(row[0])),
                (fiscal_table, r, "change"),
                (fiscal_table, r, "unit"),
                (fiscal_table, r, "calculated_weight"),
                (fiscal_table, r, "needs_review_weight"),
                (fiscal_table, r, "unsupported_weight"),
            )
        )
    return Section(
        "direct_fiscal", "Direct fiscal result", narrative=tuple(narrative), tables=(fiscal_table,)
    )


def _chart(table: Table, kind: Any, x: str, y: tuple[str, ...]) -> tuple[ChartSpec, ...]:
    return (chart_from_table(table, kind, x, y),) if table.rows else ()


def _distributional(winners: Table, deciles: Table, types: Table, unit: str) -> Section:
    narrative: list[Sentence] = []
    cls = {str(r[0]): i for i, r in enumerate(winners.rows)}
    narrative.append(
        _sentence(
            "Weight {0} gains, {1} loses, {2} is unchanged, {3} needs review and {4} is outside "
            "the modelled scope.",
            (winners, cls["gain"], "weight"),
            (winners, cls["loss"], "weight"),
            (winners, cls["no change"], "weight"),
            (winners, cls["needs review"], "weight"),
            (winners, cls["outside modelled scope"], "weight"),
        )
    )
    for name in ("gain", "loss"):
        i = cls[name]
        if _decimal(winners, i, "mean_change") is not None:
            narrative.append(
                _sentence(
                    "The weighted mean " + name + " among " + name + "ers is {0} ({1}); the "
                    "largest single " + name + " is {2}.",
                    (winners, i, "mean_change"),
                    unit,
                    (winners, i, "largest_change"),
                )
            )
    if deciles.rows:
        best = max(range(len(deciles.rows)), key=lambda i: abs(deciles.cell(i, "total_change")))  # type: ignore[arg-type]
        narrative.append(
            _sentence(
                "The largest weighted total change is in income decile {0}: {1} ({2}).",
                _tick(str(deciles.rows[best][0])),
                (deciles, best, "total_change"),
                unit,
            )
        )
    gaining = [i for i in range(len(types.rows)) if (_decimal(types, i, "gain_weight") or 0) > 0]
    if gaining:
        top = max(gaining, key=lambda i: types.cell(i, "gain_weight"))  # type: ignore[arg-type,return-value]
        narrative.append(
            _sentence(
                "The household type with the most gaining weight is {0} ({1}).",
                _tick(str(types.rows[top][0])),
                (types, top, "gain_weight"),
            )
        )
    charts = (
        *_chart(winners, "bar", "outcome", ("weight",)),
        *_chart(deciles, "bar", "group", ("total_change",)),
        *_chart(types, "bar", "group", ("total_change",)),
    )
    unavailable: list[str] = []
    if not deciles.rows:
        unavailable += _na("income decile table (no household had a known income)")
    if not types.rows:
        unavailable += _na("household type table (no household ran)")
    return Section(
        "distributional",
        "Distributional result",
        narrative=tuple(narrative),
        tables=(winners, deciles, types),
        charts=charts,
        unavailable=tuple(unavailable),
    )


def _examples(examples: Sequence[WorkedExample], ids: Sequence[str]) -> Section:
    if not examples:
        return Section(
            "household_impacts",
            "Household impacts",
            unavailable=_na("example households (none were supplied)"),
        )
    table = t.example_households(examples, dict(UNITS), source_result_ids=ids)
    narrative: list[Sentence] = []
    for r, row in enumerate(table.rows):
        who, component = _tick(str(row[0])), _tick(str(row[1]))
        if row[5] is not None:
            narrative.append(
                _sentence(
                    "For {0}, {1} changes by {2} ({3}), from {4} to {5}.",
                    who,
                    component,
                    (table, r, "change"),
                    (table, r, "unit"),
                    (table, r, "baseline"),
                    (table, r, "reform"),
                )
            )
        else:
            narrative.append(Sentence(f"For {who}, {component} is {row[6]}; no amount is shown."))
    return Section(
        "household_impacts", "Household impacts", narrative=tuple(narrative), tables=(table,)
    )


def _incentives(paths: Sequence[tuple[str, WithdrawalPath]], ids: Sequence[str]) -> Section:
    if not paths:
        return Section(
            "incentive_analysis",
            "Incentive analysis",
            unavailable=_na("withdrawal paths (none were supplied)"),
        )
    tables: list[Table] = []
    charts: list[ChartSpec] = []
    narrative = [
        Sentence(
            "These are withdrawal rates of the modelled benefits along hypothetical income "
            "paths. They are not effective marginal tax rates, because income tax and other "
            "benefits are not modelled."
        )
    ]
    for label, path in paths:
        path_ids = (*ids, f"withdrawal_path:{label}")
        rates = t.withdrawal_rates(path, label=label, source_result_ids=path_ids)
        profile = t.payment_profile(path, label=label, source_result_ids=path_ids)
        tables += [rates, profile]
        rate_cols = tuple(c.column_id for c in rates.columns if c.column_id.startswith("rate_"))
        for column_id in rate_cols:
            calculated = [
                i for i in range(len(rates.rows)) if _decimal(rates, i, column_id) is not None
            ]
            name = _tick(column_id.removeprefix("rate_"))
            if calculated:
                top = max(calculated, key=lambda i: rates.cell(i, column_id))  # type: ignore[arg-type,return-value]
                narrative.append(
                    _sentence(
                        "Along the path {0}, the highest calculated {1} withdrawal rate is {2} "
                        "between income {3} and {4} ({5}).",
                        _tick(label),
                        name,
                        (rates, top, column_id),
                        (rates, top, "income_from"),
                        (rates, top, "income_to"),
                        path.unit,
                    )
                )
            else:
                narrative.append(
                    Sentence(
                        f"Along the path {_tick(label)}, no {name} withdrawal rate was "
                        "calculated at both ends of any step."
                    )
                )
        charts += _chart(rates, "line", "income_from", rate_cols)
        charts += _chart(
            profile,
            "line",
            "income",
            tuple(c.column_id for c in profile.columns if c.column_id.startswith("entitlement_")),
        )
    return Section(
        "incentive_analysis",
        "Incentive analysis",
        narrative=tuple(narrative),
        tables=tuple(tables),
        charts=tuple(charts),
    )


def _data(run: PopulationRun, ids: Sequence[str]) -> Section:
    validation = t.validation_summary(run.validation.by_status(), source_result_ids=ids)
    evidence = (
        "synthetic"
        if run.synthetic
        else f"{UNAVAILABLE}: the population is not marked synthetic and no evidence class is "
        "recorded"
    )
    facts = (
        ("population_id", run.population_id),
        ("population_version", str(run.population_version)),
        ("population_sha256", run.population_sha256),
        ("evidence_class", evidence),
        ("population_label", run.label),
    )
    narrative: list[Sentence] = []
    if run.synthetic:
        narrative.append(
            Sentence(
                "The population is synthetic. It is a development population generated from "
                "stated rules, not a sample or estimate of New Zealand households, so no figure "
                "in this report is an empirical New Zealand estimate."
            )
        )
    narrative.append(
        _sentence(
            "Records are checked before running. Weight {0} was invalid and left out of the run; "
            "weight {1} needs review and ran with its results marked as such.",
            (validation, validation.row_index("invalid"), "weight"),
            (validation, validation.row_index("needs_review"), "weight"),
        )
    )
    return Section("data", "Data", facts=facts, narrative=tuple(narrative), tables=(validation,))


def _provenance(
    run: PopulationRun, parameter_sets: Sequence[PolicyParameterSet], ids: Sequence[str]
) -> Section:
    artifacts = t.policy_artifacts(run.policy_artifacts, source_result_ids=ids)
    params = t.parameter_provenance(parameter_sets, run.overridden, source_result_ids=ids)
    missing = (
        _na(
            "review statuses of baseline parameters (supply the loaded parameter sets to list "
            "them; the run records only overridden parameters' sources)"
        )
        if not parameter_sets
        else ()
    )
    return Section(
        "provenance",
        "Provenance",
        narrative=(
            Sentence(
                "Baseline parameters come from the repository's cited policy sources. Each "
                "carries its source, a locator and a review status; reform values are scenario "
                "assumptions with no source."
            ),
        ),
        tables=(params, artifacts),
        unavailable=missing,
    )


def _limitations(run: PopulationRun, has_paths: bool) -> Section:
    items = [
        (
            "Static entitlement only: full take-up, no behavioural response, no change in "
            "household composition or income."
        ),
        (
            "Only the components listed in the direct fiscal table are modelled. Taxes and "
            "benefits outside that list are not included."
        ),
        (
            "Households whose result needs review, or lies outside the modelled scope, are never "
            "counted as zero; their weight is shown separately."
        ),
        "Reform values are scenario assumptions, not sourced law.",
        (
            "The components behind this report are implemented but not checked for correctness, benchmarked "
            "externally or independently reviewed."
        ),
        "The narrative is templated text filled from table cells; it adds no judgement.",
    ]
    if run.synthetic:
        items.append("The population is synthetic; nothing here describes New Zealand.")
    if not run.code.reproducible:
        items.append(
            "The code identity is not a clean committed source tree, so this run may not be "
            "reproducible from the recorded commit."
        )
    if has_paths:
        items.append("Withdrawal paths are hypothetical households, not real ones.")
    return Section("limitations", "Limitations", narrative=tuple(Sentence(i) for i in items))


# -------------------------------------------------------------------- build


def build_report(
    population: PopulationDataset,
    run: PopulationRun,
    components: Sequence[str],
    *,
    withdrawal_paths: Sequence[tuple[str, WithdrawalPath]] = (),
    examples: Sequence[WorkedExample] = (),
    parameter_sets: Sequence[PolicyParameterSet] = (),
    policy_versions: Mapping[str, str] | None = None,
    reference_period: str | None = None,
    title: str | None = None,
) -> EconomistReport:
    """Assemble the report. `components` names the set whose change the
    distribution tables measure (one unit, per `analysis.component_set_unit`)."""
    if population.content_sha256() != run.population_sha256:
        raise ValueError("the population is not the one this run used")
    results = analyse(population, run, components)
    ids = (run.run_id,)
    fiscal_table = t.fiscal_components(results.fiscal, source_result_ids=ids)
    winners = t.winners_losers(results.overall, source_result_ids=ids)
    deciles = t.distribution_by_income_group(results.deciles, source_result_ids=ids)
    types = t.household_types(results.household_types, source_result_ids=ids)
    reform, assumptions = _reform(run, ids)

    sections = (
        _scenario(run, reference_period, policy_versions),
        _baseline(fiscal_table),
        reform,
        assumptions,
        _fiscal(fiscal_table),
        _distributional(winners, deciles, types, results.unit),
        _examples(examples, ids),
        _incentives(withdrawal_paths, ids),
        _data(run, ids),
        _provenance(run, parameter_sets, ids),
        _limitations(run, bool(withdrawal_paths)),
    )
    report_title = title or f"Static policy analysis: {run.reform.reform_id}"
    draft = EconomistReport("", report_title, t.MATURITY, MATURITY_BANNER, sections)
    digest = hashlib.sha256(_dumps(_plain(draft, with_id=False)).encode("utf-8")).hexdigest()
    return EconomistReport(digest, report_title, t.MATURITY, MATURITY_BANNER, sections)


# ---------------------------------------------------------------- rendering


def _dumps(content: Any) -> str:
    return json.dumps(content, sort_keys=True, indent=2, ensure_ascii=False)


def _chart_plain(chart: ChartSpec, table: Table) -> dict[str, Any]:
    return {
        "chart_id": chart.chart_id,
        "kind": chart.kind,
        "title": chart.title,
        "table_id": chart.table_id,
        "table_sha256": chart.table_sha256,
        "x": chart.x,
        "y": list(chart.y),
        "maturity": chart.maturity,
        "vega_lite": vega_lite(chart, table),
    }


def _plain(report: EconomistReport, *, with_id: bool = True) -> dict[str, Any]:
    tables = report.tables()
    sections = []
    for s in report.sections:
        sections.append(
            {
                "section_id": s.section_id,
                "title": s.title,
                "status": s.status,
                "facts": [[k, v] for k, v in s.facts],
                "narrative": [
                    {
                        "text": n.text,
                        "refs": [
                            {"table_id": r.table_id, "row": r.row, "column": r.column}
                            for r in n.refs
                        ],
                    }
                    for n in s.narrative
                ],
                "tables": [{**tb.plain(), "sha256": tb.sha256} for tb in s.tables],
                "charts": [_chart_plain(c, tables[c.table_id]) for c in s.charts],
                "unavailable": list(s.unavailable),
            }
        )
    out: dict[str, Any] = {
        "format": REPORT_FORMAT,
        "title": report.title,
        "maturity": report.maturity,
        "maturity_banner": report.maturity_banner,
        "sections": sections,
    }
    if with_id:
        out["report_id"] = report.report_id
    return out


def to_json(report: EconomistReport) -> str:
    return _dumps(_plain(report)) + "\n"


def _md_cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def _md_table(table: Table) -> list[str]:
    heads = [f"{c.label} ({c.unit})" if c.unit else c.label for c in table.columns]
    lines = [
        (
            f"**{table.title}** (table `{table.table_id}`, sha256 `{table.sha256}`, "
            f"maturity {table.maturity})"
        ),
        "",
        "| " + " | ".join(_md_cell(h) for h in heads) + " |",
        "| " + " | ".join("---" for _ in heads) + " |",
    ]
    for r in range(len(table.rows)):
        lines.append(
            "| " + " | ".join(_md_cell(table.display(r, c.column_id)) for c in table.columns) + " |"
        )
    lines.append("")
    lines += [f"- Coverage: {c}" for c in table.coverage]
    lines += [
        f"- Left out: {reason}: weight {t.format_decimal(w)}" for reason, w in table.exclusions
    ]
    lines += [f"- Note: {n}" for n in table.notes]
    lines += [f"- Source result: `{i}`" for i in table.source_result_ids]
    lines.append("")
    return lines


def to_markdown(report: EconomistReport) -> str:
    tables = report.tables()
    lines = [f"# {report.title}", "", f"> **{report.maturity_banner}**", ""]
    lines += [f"Report id: `{report.report_id}`", ""]
    for s in report.sections:
        lines += [f"## {s.title}", ""]
        if s.status == "not_available":
            lines += [f"*{u}*" for u in s.unavailable] or [f"*{UNAVAILABLE}.*"]
            lines.append("")
            continue
        lines += [f"- **{k}**: {v}" for k, v in s.facts]
        if s.facts:
            lines.append("")
        for n in s.narrative:
            lines += [n.text, ""]
        for table in s.tables:
            lines += _md_table(table)
        for chart in s.charts:
            lines += [
                (
                    f"*Chart `{chart.chart_id}`, derived from table `{chart.table_id}` "
                    f"(sha256 `{chart.table_sha256}`).*"
                ),
                "",
                render_svg(chart, tables[chart.table_id]),
                "",
            ]
        lines += [f"*{u}*" for u in s.unavailable]
        if s.unavailable:
            lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


_CSS = """
:root{--bg:#ffffff;--fg:#1a1a1a;--muted:#555555;--rule:#d0d0d0;--warn-bg:#fff4d6;--warn-fg:#5a3d00}
@media (prefers-color-scheme: dark){:root{--bg:#161616;--fg:#e8e8e8;--muted:#a8a8a8;--rule:#3a3a3a;--warn-bg:#3a2e0a;--warn-fg:#ffe7a0}}
body{background:var(--bg);color:var(--fg);font-family:system-ui,sans-serif;max-width:60rem;margin:0 auto;padding:1rem 16px;line-height:1.5}
.maturity{background:var(--warn-bg);color:var(--warn-fg);border:2px solid var(--warn-fg);padding:.75rem 1rem;font-weight:bold}
table{border-collapse:collapse;width:100%;margin:.5rem 0;font-size:.9rem}
th,td{border:1px solid var(--rule);padding:.25rem .5rem;text-align:left;vertical-align:top}
.wrap{overflow-x:auto}
.meta,.na{color:var(--muted);font-size:.85rem}
svg{max-width:100%;height:auto;display:block;margin:.5rem 0}
code{word-break:break-all}
"""


def _h(text: str) -> str:
    return html.escape(text, quote=True)


def _html_table(table: Table) -> list[str]:
    out = [
        f"<h3>{_h(table.title)}</h3>",
        (
            f'<p class="meta">table <code>{_h(table.table_id)}</code>, sha256 '
            f"<code>{table.sha256}</code>, maturity {_h(table.maturity)}</p>"
        ),
        '<div class="wrap"><table><thead><tr>',
    ]
    for c in table.columns:
        label = f"{c.label} ({c.unit})" if c.unit else c.label
        out.append(f'<th scope="col">{_h(label)}</th>')
    out.append("</tr></thead><tbody>")
    for r in range(len(table.rows)):
        out.append(
            "<tr>"
            + "".join(f"<td>{_h(table.display(r, c.column_id))}</td>" for c in table.columns)
            + "</tr>"
        )
    out.append('</tbody></table></div><ul class="meta">')
    out += [f"<li>Coverage: {_h(c)}</li>" for c in table.coverage]
    out += [
        f"<li>Left out: {_h(reason)}: weight {t.format_decimal(w)}</li>"
        for reason, w in table.exclusions
    ]
    out += [f"<li>Note: {_h(n)}</li>" for n in table.notes]
    out += [f"<li>Source result: <code>{_h(i)}</code></li>" for i in table.source_result_ids]
    out.append("</ul>")
    return out


def to_html(report: EconomistReport) -> str:
    tables = report.tables()
    body = [
        f"<h1>{_h(report.title)}</h1>",
        f'<div class="maturity" role="note">{_h(report.maturity_banner)}</div>',
        f'<p class="meta">Report id <code>{report.report_id}</code></p>',
    ]
    for s in report.sections:
        body.append(f'<section id="{_h(s.section_id)}"><h2>{_h(s.title)}</h2>')
        if s.status == "not_available" and not s.unavailable:
            body.append(f'<p class="na">{UNAVAILABLE}.</p>')
        if s.facts:
            body.append("<dl>")
            body += [f"<dt>{_h(k)}</dt><dd>{_h(v)}</dd>" for k, v in s.facts]
            body.append("</dl>")
        body += [f"<p>{_h(n.text)}</p>" for n in s.narrative]
        for table in s.tables:
            body += _html_table(table)
        for chart in s.charts:
            body.append(
                f'<figure><figcaption class="meta">Chart <code>{_h(chart.chart_id)}</code>, '
                f"derived from table <code>{_h(chart.table_id)}</code> (sha256 "
                f"<code>{chart.table_sha256}</code>)</figcaption>"
                f"{render_svg(chart, tables[chart.table_id])}</figure>"
            )
        body += [f'<p class="na">{_h(u)}</p>' for u in s.unavailable]
        body.append("</section>")
    return (
        '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{_h(report.title)}</title><style>{_CSS}</style></head><body>\n"
        + "\n".join(body)
        + "\n</body></html>\n"
    )
