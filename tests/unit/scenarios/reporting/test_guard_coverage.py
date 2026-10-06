"""Pins three integrity guards that no other test exercised (Claude review of
#154). The altered values are invented adversarial inputs, not statutory
expected values or policy calculations."""

from __future__ import annotations

import hashlib
from dataclasses import replace
from decimal import Decimal

import pytest

from poltika.scenarios.microsim.runner import (
    ComponentDelta,
    ComponentOutcomeValue,
    PopulationRun,
    results_sha256,
    run_population,
)
from poltika.scenarios.microsim.validation import RecordStatus
from poltika.scenarios.reporting import report as rp
from poltika.scenarios.reporting.charts import chart_from_table, render_svg, vega_lite
from poltika.scenarios.reporting.tables import SCENARIO_ASSUMPTION
from poltika.semantics.population import PersonRecord, PersonRole, PopulationDataset
from tests.conftest import AS_POLICY_DIR, WFF_POLICY_DIR
from tests.unit.scenarios.microsim.test_runner import THRESHOLD
from tests.unit.scenarios.reporting.conftest import CODE, FTC, Case


def test_retained_results_must_cover_every_validated_household(case: Case) -> None:
    # A dropped household with a freshly computed digest passes the digest
    # check; only the coverage check catches it.
    kept = case.run.households[1:]
    run = replace(case.run, households=kept, results_sha256=results_sha256(kept))
    with pytest.raises(ValueError, match="do not cover the validated households"):
        rp.build_report(case.population, run, FTC)


def test_scenario_assumption_resolutions_are_refused_as_baseline(case: Case) -> None:
    parameters = case.parameter_sets[0]
    overridden = {o.parameter_id for o in case.run.overridden}
    pid = next(p for p in sorted(parameters.resolutions) if p not in overridden)
    marked = replace(parameters.resolutions[pid], review_status=SCENARIO_ASSUMPTION)
    changed = replace(parameters, resolutions={**parameters.resolutions, pid: marked})
    with pytest.raises(ValueError, match="reform parameter values cannot be supplied"):
        rp.build_report(case.population, case.run, FTC, parameter_sets=[changed])


def _reidentified(report: rp.EconomistReport) -> rp.EconomistReport:
    draft = replace(report, report_id="")
    digest = hashlib.sha256(rp._dumps(rp._plain(draft, with_id=False)).encode()).hexdigest()
    return replace(report, report_id=digest)


@pytest.mark.parametrize("renderer", [rp.to_json, rp.to_markdown, rp.to_html])
def test_a_sentence_must_show_the_cell_it_references(case: Case, renderer: object) -> None:
    # Re-identified, so the digest check passes and only the reference check
    # can catch a sentence that no longer shows its referenced figure.
    report = rp.build_report(case.population, case.run, FTC)
    i, section = next(
        (i, s) for i, s in enumerate(report.sections) if s.section_id == "direct_fiscal"
    )
    first = section.narrative[0]
    assert first.refs
    altered = replace(
        section, narrative=(replace(first, text="No figure here."), *section.narrative[1:])
    )
    sections = (*report.sections[:i], altered, *report.sections[i + 1 :])
    forged = _reidentified(replace(report, sections=sections))
    with pytest.raises(ValueError, match="does not contain its referenced cell"):
        renderer(forged)  # type: ignore[operator]


# --- The remaining retained-run guards (Claude review of #154, second pass).
# Each tamper refreshes results_sha256, so only the named guard can catch it.


def _households_with(case: Case, change) -> tuple:  # type: ignore[no-untyped-def,type-arg]
    households = list(case.run.households)
    i = next(i for i, h in enumerate(households) if h.components[FTC[0]].outcome == "calculated")
    households[i] = change(households[i])
    return tuple(households)


def _with_component(household, **fields):  # type: ignore[no-untyped-def]
    delta = household.components[FTC[0]]
    return replace(household, components={**household.components, FTC[0]: replace(delta, **fields)})


def _rerun(case: Case, households: tuple) -> object:  # type: ignore[type-arg]
    return replace(case.run, households=households, results_sha256=results_sha256(households))


TAMPERS = {
    "weight": (lambda h: replace(h, weight=h.weight * 2), "weight/status"),
    "status": (lambda h: replace(h, record_status=RecordStatus.NEEDS_REVIEW), "weight/status"),
    "component dropped": (
        lambda h: replace(h, components={k: v for k, v in h.components.items() if k != FTC[0]}),
        "coverage is incomplete",
    ),
    "infinite delta": (lambda h: _with_component(h, delta=Decimal("Infinity")), "finite"),
    "baseline not calculated": (
        # The value is kept, so only the outcome check can catch it.
        lambda h: _with_component(
            h, baseline=replace(h.components[FTC[0]].baseline, outcome="needs_review")
        ),
        "delta is inconsistent",
    ),
    "baseline value missing": (
        lambda h: _with_component(h, baseline=replace(h.components[FTC[0]].baseline, value=None)),
        "delta is inconsistent",
    ),
    "reform not calculated": (
        lambda h: _with_component(
            h, reform=replace(h.components[FTC[0]].reform, outcome="needs_review")
        ),
        "delta is inconsistent",
    ),
    "reform value missing": (
        lambda h: _with_component(h, reform=replace(h.components[FTC[0]].reform, value=None)),
        "delta is inconsistent",
    ),
    "unresolved with a delta": (
        lambda h: _with_component(h, outcome="needs_review"),
        "must not carry a delta",
    ),
}


@pytest.mark.parametrize("name", sorted(TAMPERS))
def test_each_retained_household_guard_bites(case: Case, name: str) -> None:
    change, message = TAMPERS[name]
    run = _rerun(case, _households_with(case, change))
    with pytest.raises(ValueError, match=message):
        rp.build_report(case.population, run, FTC)  # type: ignore[arg-type]


def test_retained_validation_must_match_the_population(case: Case) -> None:
    hid = case.run.validation.households[0].household_id
    weights = {**case.run.validation.weights, hid: case.run.validation.weights[hid] * 2}
    run = replace(case.run, validation=replace(case.run.validation, weights=weights))
    with pytest.raises(ValueError, match="retained validation does not match"):
        rp.build_report(case.population, run, FTC)


@pytest.fixture(scope="module")
def needs_review_case(case: Case) -> tuple[PopulationDataset, PopulationRun]:
    """The fixture population with one household's WFF facts saying single
    while its persons list a partner, which validation marks needs_review."""
    households = list(case.population.households)
    i, target = next(
        (i, h)
        for i, h in enumerate(households)
        if h.facts["household"]["wff"]["partner_status"] == "single"
    )
    households[i] = target.model_copy(
        update={"persons": (*target.persons, PersonRecord(person_id="px", role=PersonRole.PARTNER))}
    )
    population = case.population.model_copy(update={"households": tuple(households)})
    run = run_population(population, THRESHOLD, WFF_POLICY_DIR, AS_POLICY_DIR, code=CODE)
    return population, run


def test_a_needs_review_household_is_reported_and_never_zero(
    needs_review_case: tuple[PopulationDataset, PopulationRun],
) -> None:
    population, run = needs_review_case
    flagged = [h for h in run.households if h.record_status is RecordStatus.NEEDS_REVIEW]
    assert len(flagged) == 1
    report = rp.build_report(population, run, FTC)
    winners = report.tables()["winners_losers"]
    row = winners.row_index("needs review")
    assert winners.cell(row, "weight") == flagged[0].weight > 0
    assert winners.cell(row, "mean_change") is None


def test_a_needs_review_household_cannot_carry_a_calculated_delta(
    needs_review_case: tuple[PopulationDataset, PopulationRun],
) -> None:
    population, run = needs_review_case
    households = list(run.households)
    i = next(i for i, h in enumerate(households) if h.record_status is RecordStatus.NEEDS_REVIEW)
    calculated = ComponentOutcomeValue("calculated", Decimal(100), None)
    forged = ComponentDelta("calculated", calculated, calculated, Decimal(0))
    households[i] = replace(households[i], components={**households[i].components, FTC[0]: forged})
    kept = tuple(households)
    tampered = replace(run, households=kept, results_sha256=results_sha256(kept))
    with pytest.raises(ValueError, match="delta is inconsistent"):
        rp.build_report(population, tampered, FTC)


# --- Chart, parameter-set, section and reference guards.


def test_a_chart_refuses_a_same_id_table_with_changed_content(case: Case) -> None:
    report = rp.build_report(case.population, case.run, FTC)
    table = report.tables()["winners_losers"]
    spec = chart_from_table(table, "bar", "outcome", ("weight",))
    changed = replace(table, notes=(*table.notes, "changed"))
    for render in (render_svg, vega_lite):
        with pytest.raises(ValueError, match="was not made from this table"):
            render(spec, changed)


def test_parameter_sets_must_match_a_retained_date_and_appear_once(case: Case) -> None:
    parameters = case.parameter_sets[0]
    other_date = replace(parameters, modelled_date=parameters.modelled_date.replace(year=2001))
    for sets in ([other_date], [parameters, parameters]):
        with pytest.raises(ValueError, match="absent or duplicate"):
            rp.build_report(case.population, case.run, FTC, parameter_sets=sets)


def test_duplicate_section_ids_are_refused_on_export(case: Case) -> None:
    report = rp.build_report(case.population, case.run, FTC)
    scenario = report.section("scenario")
    assert not scenario.tables
    doubled = replace(report, sections=(*report.sections, scenario))
    with pytest.raises(ValueError, match="duplicate report section identifier"):
        rp.to_json(doubled)


@pytest.mark.parametrize(
    "ref", [("no_such_table", 0), ("winners_losers", -1), ("winners_losers", 99)]
)
def test_references_to_absent_cells_are_refused(case: Case, ref: tuple[str, int]) -> None:
    report = rp.build_report(case.population, case.run, FTC)
    i, section = next((i, s) for i, s in enumerate(report.sections) if s.section_id == "data")
    bad = rp.Sentence("A sentence.", (rp.CellRef(ref[0], ref[1], "weight"),))
    altered = replace(section, narrative=(*section.narrative, bad))
    forged = _reidentified(
        replace(report, sections=(*report.sections[:i], altered, *report.sections[i + 1 :]))
    )
    with pytest.raises(ValueError, match="absent table cell"):
        rp.to_markdown(forged)


def test_a_newline_in_caller_text_stays_on_one_markdown_line(case: Case) -> None:
    report = rp.build_report(case.population, case.run, FTC, title="first\nsecond")
    assert "# first second" in rp.to_markdown(report)
