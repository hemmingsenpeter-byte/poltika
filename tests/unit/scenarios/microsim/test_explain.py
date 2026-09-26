"""v0.2 Task 9.1: population explanations and their verification."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

import pytest

from poltika.policy.loader import load_policy_parameters
from poltika.scenarios.microsim.explain import (
    Figure,
    explain_population,
    fmt,
    render_text,
    verify,
)
from poltika.scenarios.microsim.runner import PopulationRun, run_population
from poltika.scenarios.record import CodeIdentity
from poltika.semantics.population import PopulationDataset
from tests.conftest import AS_POLICY_DIR, WFF_POLICY_DIR
from tests.unit.scenarios.microsim.test_runner import THRESHOLD, _population
from tests.unit.scenarios.test_population import GOLDEN
from tests.unit.scenarios.test_scenario_record import record_from_yaml

FTC = ("family_tax_credit",)


@pytest.fixture(scope="module")
def population_and_run() -> tuple[PopulationDataset, PopulationRun]:
    population = _population()
    run = run_population(
        population,
        THRESHOLD,
        WFF_POLICY_DIR,
        AS_POLICY_DIR,
        code=CodeIdentity("t", None, None, None),
    )
    return population, run


def test_run_records_what_the_reform_changed_with_baseline_evidence(
    population_and_run: tuple[PopulationDataset, PopulationRun],
) -> None:
    _, run = population_and_run
    record = record_from_yaml(GOLDEN[0])
    baseline = load_policy_parameters(
        WFF_POLICY_DIR,
        record.wff_lookup_date,
        requested_policy_version=record.requested_wff_policy_version,
    ).get("family_tax_credit_abatement_threshold")
    (o,) = run.overridden
    assert (o.policy_id, o.parameter_id, o.reform_value) == (
        "working_for_families",
        "family_tax_credit_abatement_threshold",
        Decimal(50000),
    )
    assert (o.baseline_value, o.baseline_source_id, o.baseline_locator) == (
        baseline.value,
        baseline.source_id,
        baseline.locator,
    )


def test_explanation_verifies_and_says_what_matters(
    population_and_run: tuple[PopulationDataset, PopulationRun],
) -> None:
    population, run = population_and_run
    explanation = explain_population(population, run, FTC)
    assert verify(explanation, population, run) == []
    text = render_text(explanation)
    assert text.startswith(run.label)
    assert "scenario assumption" in text and run.overridden[0].baseline_source_id in text
    assert "AS-10, WFF DEC-003" in text and "unchanged" in text
    assert "at full take-up" in text
    # largest cost driver first among the component sentences
    component_lines = [
        s.text for s in explanation.sentences if "static entitlement change" in s.text
    ]
    assert component_lines[0].startswith("family_tax_credit:")


def test_tampered_figure_or_text_is_caught(
    population_and_run: tuple[PopulationDataset, PopulationRun],
) -> None:
    population, run = population_and_run
    explanation = explain_population(population, run, FTC)
    index = next(
        i
        for i, s in enumerate(explanation.sentences)
        if s.figures and s.figures[0].key == "delta:family_tax_credit"
    )
    sentence = explanation.sentences[index]
    wrong = Figure("delta:family_tax_credit", sentence.figures[0].value + 1)
    tampered_value = replace(sentence, figures=(wrong, *sentence.figures[1:]))
    sentences = list(explanation.sentences)
    sentences[index] = tampered_value
    problems = verify(replace(explanation, sentences=tuple(sentences)), population, run)
    assert any("says" in p for p in problems) and any("not in its sentence" in p for p in problems)

    sentences[index] = replace(
        sentence, text=sentence.text.replace(fmt(sentence.figures[0].value), "0.00")
    )
    problems = verify(replace(explanation, sentences=tuple(sentences)), population, run)
    assert any("not in its sentence" in p for p in problems)


def test_explanation_for_another_run_is_refused(
    population_and_run: tuple[PopulationDataset, PopulationRun],
) -> None:
    population, run = population_and_run
    explanation = explain_population(population, run, FTC)
    assert "explanation is for a different run" in verify(
        replace(explanation, run_id="other"), population, run
    )
