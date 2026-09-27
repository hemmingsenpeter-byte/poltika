"""v0.2 Task 9.4: write the cross-validation report.

The composition root for `crossval.compare()`: it builds a `DataContext`,
generates the population from its committed spec, runs the baseline (an
identity reform) and writes the Markdown report. Allowed to import
`poltika.data` by `tests/unit/data/test_boundary.py`.

    uv run python -m poltika.scenarios.microsim.crossval_cli DATA_ROOT SPEC.yaml POLICY_SPECS OUT.md
"""

from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

import yaml

from poltika.data.context import DataContext
from poltika.scenarios.microsim.crossval import compare, render_markdown
from poltika.scenarios.microsim.reform import Operation, Override, Reform
from poltika.scenarios.microsim.runner import run_population
from poltika.scenarios.microsim.synthetic import SyntheticSpec, generate
from poltika.scenarios.record import CodeIdentity

BASELINE = Reform(
    reform_id="baseline (identity)",
    overrides=(
        Override(
            policy_id="working_for_families",
            parameter_id="family_tax_credit_abatement_threshold",
            operation=Operation.ADD,
            value=Decimal(0),
        ),
    ),
)


def report(data_root: Path, spec_path: Path, policy_specs: Path) -> str:
    spec = SyntheticSpec.model_validate(yaml.safe_load(spec_path.read_text()))
    population, _ = generate(spec)
    run = run_population(
        population,
        BASELINE,
        policy_specs / "working_for_families",
        policy_specs / "accommodation_supplement",
        code=CodeIdentity("crossval", None, None, None),
    )
    return render_markdown(compare(population, run, DataContext(data_root)), run) + "\n"


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        print("usage: crossval_cli DATA_ROOT SPEC.yaml POLICY_SPECS OUT.md", file=sys.stderr)
        return 2
    Path(argv[3]).write_text(report(Path(argv[0]), Path(argv[1]), Path(argv[2])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
