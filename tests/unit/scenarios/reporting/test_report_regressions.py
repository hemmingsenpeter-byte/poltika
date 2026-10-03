"""Reporting integrity regressions using retained synthetic results.

The altered values here are invented adversarial inputs. They are neither
statutory expected values nor new policy calculations.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from decimal import Decimal

import pytest

from poltika.scenarios.microsim.runner import PopulationRun, results_sha256
from poltika.scenarios.reporting.report import (
    EconomistReport,
    Section,
    Sentence,
    build_report,
    to_html,
    to_json,
    to_markdown,
)
from tests.unit.scenarios.reporting.conftest import FTC, Case


def _alter_delta(case: Case, *, refresh_digest: bool) -> PopulationRun:
    households = list(case.run.households)
    i = next(
        i for i, h in enumerate(households) if h.components[FTC[0]].outcome == "calculated"
    )
    household = households[i]
    delta = household.components[FTC[0]]
    assert delta.delta is not None
    changed = replace(delta, delta=delta.delta + Decimal("123.456789"))
    households[i] = replace(household, components={**household.components, FTC[0]: changed})
    retained = tuple(households)
    return replace(
        case.run,
        households=retained,
        results_sha256=results_sha256(retained) if refresh_digest else case.run.results_sha256,
    )


def test_changed_results_with_retained_digest_are_rejected(case: Case) -> None:
    with pytest.raises(ValueError, match="result|digest|hash"):
        build_report(case.population, _alter_delta(case, refresh_digest=False), FTC)


def test_delta_must_reconcile_even_with_a_fresh_digest(case: Case) -> None:
    with pytest.raises(ValueError, match="delta|reconcil|inconsistent"):
        build_report(case.population, _alter_delta(case, refresh_digest=True), FTC)


@pytest.mark.parametrize("field", ["run_id", "population_id", "population_version", "synthetic"])
def test_retained_identity_metadata_must_match_population(case: Case, field: str) -> None:
    altered = {
        "run_id": replace(case.run, run_id="caller-forged-run"),
        "population_id": replace(case.run, population_id="caller-forged-population"),
        "population_version": replace(
            case.run, population_version=case.run.population_version + 1
        ),
        "synthetic": replace(case.run, synthetic=not case.run.synthetic),
    }
    with pytest.raises(ValueError, match="identity|run|population|synthetic"):
        build_report(case.population, altered[field], FTC)


def test_parameter_sources_must_use_retained_artifact_hashes(case: Case) -> None:
    parameters = case.parameter_sets[0]
    changed = replace(
        parameters,
        artifact_sha256={path: "f" * 64 for path in parameters.artifact_sha256},
    )
    with pytest.raises(ValueError, match="artifact|hash|provenance"):
        build_report(case.population, case.run, FTC, parameter_sets=[changed])


def test_reform_values_cannot_be_presented_as_baseline_provenance(case: Case) -> None:
    parameters = case.parameter_sets[0]
    override = next(o for o in case.run.overridden if o.policy_id == parameters.policy_id)
    baseline = parameters.resolutions[override.parameter_id]
    changed = replace(
        parameters,
        resolutions={
            **parameters.resolutions,
            override.parameter_id: replace(baseline, value=override.reform_value),
        },
    )
    with pytest.raises(ValueError, match="baseline|parameter|provenance"):
        build_report(case.population, case.run, FTC, parameter_sets=[changed])


@pytest.mark.parametrize("change", ["source", "value"])
def test_overridden_baseline_fields_must_match_parameter_set(case: Case, change: str) -> None:
    parameters = case.parameter_sets[0]
    overridden = list(case.run.overridden)
    i = next(i for i, o in enumerate(overridden) if o.policy_id == parameters.policy_id)
    original = overridden[i]
    assert original.baseline_value is not None
    altered = (
        replace(original, baseline_source_id="invented-source")
        if change == "source"
        else replace(original, baseline_value=original.baseline_value + Decimal("0.123456789"))
    )
    overridden[i] = altered
    with pytest.raises(ValueError, match="baseline|parameter|provenance"):
        build_report(
            case.population,
            replace(case.run, overridden=tuple(overridden)),
            FTC,
            parameter_sets=[parameters],
        )


def test_reference_metadata_is_derived_from_retained_records(case: Case) -> None:
    report = build_report(case.population, case.run, FTC)
    scenario = report.section("scenario")
    facts = dict(scenario.facts)
    period = facts["reference_period"]
    versions = facts["policy_versions"]
    records = [h.record for h in case.run.validation.households if h.record is not None]
    assert records
    record = records[0]
    assert str(record.assessment_week.start) in period
    assert str(record.assessment_week.end) in period
    assert record.requested_wff_policy_version in versions
    assert record.requested_as_policy_version in versions
    assert "WFF" in period and "AS" in period
    assert scenario.status == "partial"
    assert any("annual" in missing.lower() for missing in scenario.unavailable)
    explicit = build_report(case.population, case.run, FTC, reference_period=period)
    assert dict(explicit.section("scenario").facts)["reference_period"] == period


def test_unrelated_caller_period_is_rejected(case: Case) -> None:
    with pytest.raises(ValueError, match="period"):
        build_report(case.population, case.run, FTC, reference_period="2099-2100")


def test_unrelated_caller_policy_version_is_rejected(case: Case) -> None:
    with pytest.raises(ValueError, match="version"):
        build_report(
            case.population,
            case.run,
            FTC,
            policy_versions={"working_for_families": "unrelated-version"},
        )


def test_optional_examples_and_paths_do_not_inherit_population_run_provenance(case: Case) -> None:
    report = build_report(
        case.population, case.run, FTC, examples=case.examples, withdrawal_paths=case.paths
    )
    for section_id in ("household_impacts", "incentive_analysis"):
        section = report.section(section_id)
        text = " ".join(
            [*section.unavailable, *(n.text for n in section.narrative)]
            + [note for table in section.tables for note in table.notes]
        ).lower()
        assert "separately supplied" in text
        assert all(case.run.run_id not in table.source_result_ids for table in section.tables)


def test_withdrawal_path_cannot_relabel_annual_components_as_weekly(case: Case) -> None:
    path = case.paths[0][1]
    assert path.policy == "working_for_families"
    changed = replace(path, unit="NZD per week")
    with pytest.raises(ValueError, match="unit|period"):
        build_report(case.population, case.run, FTC, withdrawal_paths=[("mislabeled", changed)])


def test_population_evidence_is_scenario_not_a_confidence_claim(case: Case) -> None:
    report = build_report(case.population, case.run, FTC)
    assert dict(report.section("data").facts)["evidence_class"] == "Scenario"


def _mutated_report(case: Case, target: str) -> EconomistReport:
    report = build_report(case.population, case.run, FTC)
    section = report.section("direct_fiscal")
    if target == "narrative":
        changed = replace(section, narrative=(Sentence("The invented change is 987654321.00."),))
    elif target == "table":
        table = section.tables[0]
        rows = list(table.rows)
        row = list(rows[0])
        row[table.column_index("change")] = Decimal("987654321.00")
        rows[0] = tuple(row)
        changed = replace(section, tables=(replace(table, rows=tuple(rows)),))
    else:
        changed = replace(section, facts=(("result_id", "invented-result"),))
    sections = tuple(changed if s is section else s for s in report.sections)
    return replace(report, sections=sections)


@pytest.mark.parametrize("renderer", [to_json, to_markdown, to_html])
@pytest.mark.parametrize("target", ["narrative", "table", "facts"])
def test_export_rejects_mutated_report_content(
    case: Case, renderer: Callable[[EconomistReport], str], target: str
) -> None:
    with pytest.raises(ValueError, match="report|content|hash|identity"):
        renderer(_mutated_report(case, target))


def test_duplicate_table_identifiers_are_rejected_explicitly(case: Case) -> None:
    report = build_report(case.population, case.run, FTC)
    duplicate = Section("duplicate", "Duplicate", tables=report.section("baseline").tables)
    changed = replace(report, sections=(*report.sections, duplicate))
    with pytest.raises(ValueError, match="duplicate"):
        changed.tables()


def test_colliding_path_labels_are_rejected_explicitly(case: Case) -> None:
    path = case.paths[0][1]
    with pytest.raises(ValueError, match="duplicate|collision"):
        build_report(case.population, case.run, FTC, withdrawal_paths=[("a-b", path), ("a b", path)])


@pytest.mark.parametrize(
    "title",
    [
        "[collect](https://example.invalid/collect)",
        '<img src="https://example.invalid/collect">',
        "plain\n# injected heading",
    ],
)
def test_caller_title_is_literal_markdown(case: Case, title: str) -> None:
    report = build_report(case.population, case.run, FTC, title=title)
    assert title not in to_markdown(report)


def test_example_labels_are_literal_markdown(case: Case) -> None:
    injected = '<img src="https://example.invalid/collect">'
    example = replace(case.examples[0], example_id=injected)
    report = build_report(case.population, case.run, FTC, examples=[example])
    assert injected not in to_markdown(report)
