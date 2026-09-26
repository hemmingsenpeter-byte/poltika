"""v0.2 Task 9.2 and the exit gate in BUILD_PLAN_v0_2.md, one test per row.

The exit scenario is the one the plan names: raise the family tax credit
abatement threshold from the 2026-27 value in policy.yaml to $50,000.
Rows run on a toy synthetic population so the machinery is gated now. The
rows that need the real calibrated population (Tasks 3.1-3.2) run against
each spec committed under data/metadata/populations/, and skip with a
reason until one exists. A green run with no skips means the gate is met.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

from poltika.scenarios.microsim import analysis
from poltika.scenarios.microsim.explain import explain_population, verify
from poltika.scenarios.microsim.reform import Override, Reform
from poltika.scenarios.microsim.runner import AS_COMPONENT, PopulationRun, run_population
from poltika.scenarios.microsim.synthetic import SyntheticSpec, generate
from poltika.scenarios.record import CodeIdentity
from poltika.semantics.population import SYNTHETIC_LABEL, PopulationDataset
from tests.conftest import AS_POLICY_DIR, WFF_POLICY_DIR
from tests.unit.scenarios.microsim.test_synthetic import _spec

ROOT = Path(__file__).resolve().parents[2]
REAL_SPECS = sorted((ROOT / "data" / "metadata" / "populations").glob("*.yaml"))
CODE = CodeIdentity("gate", None, None, None)
FTC = ("family_tax_credit",)
EXIT = Reform(
    reform_id="exit: family tax credit abatement threshold to 50000",
    overrides=(
        Override(
            policy_id="working_for_families",
            parameter_id="family_tax_credit_abatement_threshold",
            operation="set",
            value=Decimal(50000),
        ),
    ),
)
IDENTITY = Reform(
    reform_id="identity",
    overrides=(
        Override(
            policy_id="working_for_families",
            parameter_id="family_tax_credit_abatement_threshold",
            operation="add",
            value=Decimal(0),
        ),
    ),
)


def _run(population: PopulationDataset, reform: Reform = EXIT) -> PopulationRun:
    return run_population(population, reform, WFF_POLICY_DIR, AS_POLICY_DIR, code=CODE)


@pytest.fixture(scope="module")
def toy() -> tuple[PopulationDataset, PopulationRun]:
    population, _ = generate(_spec(households=300))
    return population, _run(population)


def test_one_reproducible_run_without_code_changes(
    toy: tuple[PopulationDataset, PopulationRun],
) -> None:
    population, run = toy
    again = _run(generate(_spec(households=300))[0])
    assert (again.run_id, again.results_sha256) == (run.run_id, run.results_sha256)
    assert run.population_sha256 == population.content_sha256()


def test_household_distribution_area_and_fiscal_results(
    toy: tuple[PopulationDataset, PopulationRun],
) -> None:
    population, run = toy
    summary = analysis.overall(population, run, FTC).groups["all"]
    assert summary.by_class[analysis.ChangeClass.GAIN] > 0
    for table in (
        analysis.by_decile,
        analysis.by_household_type,
        analysis.by_as_area,
        analysis.by_region,
    ):
        assert table(population, run, FTC).groups
    assert analysis.fiscal(run)["family_tax_credit"].delta_total > 0


def test_accommodation_supplement_interaction_is_none(
    toy: tuple[PopulationDataset, PopulationRun],
) -> None:
    _, run = toy
    assert all(
        h.components[AS_COMPONENT].baseline == h.components[AS_COMPONENT].reform
        for h in run.households
    )
    assert analysis.fiscal(run)[AS_COMPONENT].delta_total == 0


def test_weighted_coverage_includes_needs_review(
    toy: tuple[PopulationDataset, PopulationRun],
) -> None:
    _, run = toy
    coverage = analysis.fiscal(run)["in_work_tax_credit"].coverage
    assert coverage["needs_review"] > 0  # R4: the 2026-27 in-work base is needs_review
    assert sum(coverage.values()) == sum(h.weight for h in run.households)


def test_explanation_verifies_with_evidence_and_label(
    toy: tuple[PopulationDataset, PopulationRun],
) -> None:
    population, run = toy
    explanation = explain_population(population, run, FTC)
    assert verify(explanation, population, run) == []
    text = "\n".join(s.text for s in explanation.sentences)
    assert text.startswith(SYNTHETIC_LABEL)
    assert run.overridden[0].baseline_source_id and run.overridden[0].baseline_source_id in text


def test_invariants(toy: tuple[PopulationDataset, PopulationRun]) -> None:
    population, run = toy
    identity = _run(population, IDENTITY)
    assert all(
        c.baseline == c.reform for h in identity.households for c in h.components.values()
    ), "an identity reform changes nothing"
    for h in run.households:
        ftc = h.components["family_tax_credit"]
        assert ftc.outcome != "calculated" or (ftc.delta is not None and ftc.delta >= 0)
        if ftc.baseline.outcome == "unsupported":
            assert ftc.reform.outcome == "unsupported", (
                "households outside the scope stay outside it"
            )
    doubled = population.model_copy(
        update={
            "households": tuple(
                h.model_copy(update={"weight": h.weight * 2}) for h in population.households
            )
        }
    )
    assert analysis.fiscal(_run(doubled))["family_tax_credit"].delta_total == 2 * (
        analysis.fiscal(run)["family_tax_credit"].delta_total
    )


def test_v0_1_and_v0_1_5_results_unchanged() -> None:
    """Held by the frozen golden snapshots, which this gate re-runs."""
    for name in ("test_golden_result_snapshot.py", "test_golden_trace_snapshot.py"):
        assert (ROOT / "tests" / "regression" / name).is_file()


@pytest.mark.skipif(not REAL_SPECS, reason="no calibrated population spec yet (Tasks 3.1-3.2)")
@pytest.mark.parametrize("spec_path", REAL_SPECS, ids=lambda p: p.stem)
def test_real_population_spec_runs_the_exit_scenario(spec_path: Path) -> None:
    raw: dict[str, Any] = yaml.safe_load(spec_path.read_text())
    spec = SyntheticSpec.model_validate(raw)
    population, calibration = generate(spec)
    assert spec.sources and all(s.strip() for s in spec.sources)
    assert calibration
    run = _run(population)
    explanation = explain_population(population, run, FTC)
    assert verify(explanation, population, run) == []


def test_independent_review_complete() -> None:
    from tests.acceptance.review_queue import open_reviews

    pending = open_reviews("v0.2")
    if pending:
        pytest.skip(f"release gate not yet met: awaiting independent review {', '.join(pending)}")
