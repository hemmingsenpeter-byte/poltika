"""Pins three integrity guards that no other test exercised (Claude review of
#154). The altered values are invented adversarial inputs, not statutory
expected values or policy calculations."""

from __future__ import annotations

import hashlib
from dataclasses import replace

import pytest

from poltika.scenarios.microsim.runner import results_sha256
from poltika.scenarios.reporting import report as rp
from poltika.scenarios.reporting.tables import SCENARIO_ASSUMPTION
from tests.unit.scenarios.reporting.conftest import FTC, Case


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
