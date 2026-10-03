"""Pass 1 capability 17: the economist report, on a real run of the toy
synthetic population."""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

import pytest

from poltika.scenarios.reporting.report import (
    MATURITY_BANNER,
    EconomistReport,
    build_report,
    to_html,
    to_json,
    to_markdown,
)
from tests.unit.scenarios.reporting.conftest import FTC, Case

SECTIONS = [
    "scenario",
    "baseline",
    "reform",
    "assumptions",
    "direct_fiscal",
    "distributional",
    "household_impacts",
    "incentive_analysis",
    "data",
    "provenance",
    "limitations",
]
def _full(case: Case) -> EconomistReport:
    return build_report(
        case.population,
        case.run,
        FTC,
        withdrawal_paths=case.paths,
        examples=case.examples,
        parameter_sets=case.parameter_sets,
    )


@pytest.fixture(scope="module")
def report(case: Case) -> EconomistReport:
    return _full(case)


def test_all_sections_present_in_order(report: EconomistReport) -> None:
    assert [s.section_id for s in report.sections] == SECTIONS
    partial = {"scenario", "household_impacts", "incentive_analysis", "provenance"}
    assert {s.section_id for s in report.sections if s.status == "partial"} == partial
    assert all(s.status == "complete" for s in report.sections if s.section_id not in partial)


def test_deterministic_bytes(case: Case, report: EconomistReport) -> None:
    again = _full(case)
    assert to_json(again) == to_json(report)
    assert to_markdown(again) == to_markdown(report)
    assert to_html(again) == to_html(report)
    assert again.report_id == report.report_id
    assert to_json(report).encode() == to_json(again).encode()


_NUMBER = re.compile(r"-?\d[\d,]*(?:\.\d+)?")


def test_every_narrative_number_is_a_table_cell(report: EconomistReport) -> None:
    tables = report.tables()
    shown = set().union(*(tb.displayed_numbers() for tb in tables.values()))
    checked = 0
    for section in report.sections:
        for sentence in section.narrative:
            # Ids are backtick-quoted and may contain digits; they are not figures.
            text = re.sub(r"`[^`]*`", "", sentence.text)
            for token in _NUMBER.findall(text):
                assert token in shown, f"{section.section_id}: {token!r} is not a table cell"
                checked += 1
            for ref in sentence.refs:
                assert tables[ref.table_id].display(ref.row, ref.column) in sentence.text
    assert checked > 20


def test_maturity_banner_is_first_and_never_overclaims(report: EconomistReport) -> None:
    assert "IMPLEMENTED" in MATURITY_BANNER and report.maturity == "IMPLEMENTED"
    markdown, page, data = to_markdown(report), to_html(report), to_json(report)
    assert markdown.index("MATURITY: IMPLEMENTED") < markdown.index("## Scenario")
    assert page.index(MATURITY_BANNER) < page.index("<section")
    assert json.loads(data)["maturity_banner"] == MATURITY_BANNER
    for text in (markdown, page, data):
        assert "validated" not in text.lower()
        assert "official estimate" not in text.lower()


def test_synthetic_population_is_labelled(case: Case, report: EconomistReport) -> None:
    facts = dict(report.section("data").facts)
    assert facts["evidence_class"] == "Scenario"
    assert case.run.label in facts["population_label"]
    text = to_markdown(report)
    assert "population is synthetic" in text.lower() and "not a sample or estimate" in text


def test_reform_overrides_are_marked_scenario_assumptions(report: EconomistReport) -> None:
    table = report.section("reform").tables[0]
    assert table.rows and all(r[-1] == "scenario_assumption" for r in table.rows)
    assert any("scenario assumption" in n.text for n in report.section("reform").narrative)


def test_json_is_valid_and_carries_chart_traceability(report: EconomistReport) -> None:
    data = json.loads(to_json(report))
    tables = {tb["table_id"]: tb["sha256"] for s in data["sections"] for tb in s["tables"]}
    charts = [c for s in data["sections"] for c in s["charts"]]
    assert charts
    for chart in charts:
        assert tables[chart["table_id"]] == chart["table_sha256"]
        assert chart["vega_lite"]["usermeta"]["table_sha256"] == chart["table_sha256"]


class _Strict(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.svgs = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.svgs += tag == "svg"


def test_html_is_self_contained_with_inline_svg(report: EconomistReport) -> None:
    page = to_html(report)
    parser = _Strict()
    parser.feed(page)
    assert parser.svgs == sum(len(s.charts) for s in report.sections) > 0
    assert "<script" not in page and "http://www.w3.org/2000/svg" in page
    assert not re.search(r'(src|href)="https?://', page)
    for svg in re.findall(r"<svg.*?</svg>", page, flags=re.DOTALL):
        ET.fromstring(svg)


def test_markdown_svgs_parse(report: EconomistReport) -> None:
    for svg in re.findall(r"<svg.*?</svg>", to_markdown(report), flags=re.DOTALL):
        ET.fromstring(svg)


def test_missing_inputs_are_said_not_omitted(case: Case) -> None:
    bare = build_report(case.population, case.run, FTC)
    assert [s.section_id for s in bare.sections] == SECTIONS
    for section_id in ("household_impacts", "incentive_analysis"):
        s = bare.section(section_id)
        assert s.status == "not_available"
        assert s.unavailable and s.unavailable[0].startswith("Not available in this run")
    scenario = dict(bare.section("scenario").facts)
    assert scenario["reference_period"] != "Not available in this run"
    assert scenario["policy_versions"] != "Not available in this run"
    assert bare.section("provenance").status == "partial"
    for text in (to_markdown(bare), to_html(bare)):
        assert text.count("Not available in this run") >= 4


def test_report_refuses_the_wrong_population(case: Case) -> None:
    from poltika.semantics.population import PopulationDataset

    other = PopulationDataset.model_validate(
        {**case.population.model_dump(mode="json"), "version": 2}
    )
    with pytest.raises(ValueError, match="not the one this run used"):
        build_report(other, case.run, FTC)


def test_unit_mixing_component_sets_are_refused(case: Case) -> None:
    with pytest.raises(ValueError, match="mix units"):
        build_report(case.population, case.run, ("family_tax_credit", "accommodation_supplement"))
