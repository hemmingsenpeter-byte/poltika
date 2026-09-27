"""v0.2 Task 9.4: the cross-validation arithmetic and the committed report.

The arithmetic is checked on the toy population against a fake context; the
committed report must be what `crossval_cli.report()` writes from the
committed spec and snapshots, so it can't drift from the run it describes.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

from poltika.scenarios.microsim.crossval import compare
from poltika.scenarios.microsim.crossval_cli import BASELINE, report
from poltika.scenarios.microsim.runner import run_population
from poltika.scenarios.microsim.synthetic import generate
from poltika.scenarios.record import CodeIdentity
from poltika.semantics.variables import Lineage, Observation
from tests.conftest import AS_POLICY_DIR, WFF_POLICY_DIR
from tests.unit.scenarios.microsim.test_synthetic import _spec

ROOT = Path(__file__).resolve().parents[4]


class _Published:
    """Every published figure is 10 (in its own unit)."""

    def get(self, variable_id: str, on: date, vintage: str | None = None) -> Observation:
        lineage = Lineage(
            transformation_id="t",
            transformation_version=1,
            dataset_id="d",
            raw_snapshot_version=1,
            raw_sha256="0" * 64,
            source_organisation="o",
            publication="p",
            source_url_or_identifier="u",
            vintage="v",
            retrieval_date=date(2026, 9, 27),
        )
        return Observation(
            variable_id=variable_id,
            period_start=on,
            period_end=date(2030, 1, 1),
            value=Decimal(10),
            unit="u",
            lineage=lineage,
        )


def test_modelled_figures_are_weighted_baseline_values() -> None:
    population, _ = generate(_spec(households=200))
    run = run_population(
        population,
        BASELINE,
        WFF_POLICY_DIR,
        AS_POLICY_DIR,
        code=CodeIdentity("t", None, None, None),
    )
    rows = {r.measure: r for r in compare(population, run, _Published())}

    ftc = [(h.weight, h.components["family_tax_credit"].baseline) for h in run.households]
    expected_n = sum(
        (w for w, b in ftc if b.outcome == "calculated" and b.value and b.value > 0), Decimal(0)
    )
    expected_amount = sum(
        (w * b.value for w, b in ftc if b.outcome == "calculated" and b.value), Decimal(0)
    )
    families = rows["families with family tax credit"]
    assert families.modelled == expected_n and families.published == Decimal(10_000)
    assert rows["family tax credit entitlement"].modelled == expected_amount / 1_000_000
    assert families.covered_weight + families.uncovered_weight == sum(
        h.weight for h in run.households
    )
    assert all(r.reasons for r in rows.values())


def test_committed_report_is_the_generated_report() -> None:
    spec = ROOT / "data" / "metadata" / "populations" / "nz_synthetic_development.v1.yaml"
    committed = (ROOT / "docs" / "releases" / "V0_2_CROSS_VALIDATION.md").read_text()
    assert committed == report(ROOT / "data", spec, ROOT / "policy_specs")
