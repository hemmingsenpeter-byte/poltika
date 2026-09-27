"""v0.2 Task 3.3: write the synthetic development population's spec.

The composition root for `calibration.derive_spec()`: it builds a
`DataContext` over a data root and writes the derived spec as YAML. It is
the only module outside `poltika.data` allowed to import it
(`tests/unit/data/test_boundary.py`).

    uv run python -m poltika.scenarios.microsim.calibrate_cli DATA_ROOT OUT.yaml
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

from poltika.data.context import DataContext
from poltika.scenarios.microsim.calibration import derive_spec
from poltika.scenarios.microsim.synthetic import SyntheticSpec


def render(data_root: Path) -> str:
    spec = derive_spec(DataContext(data_root))
    SyntheticSpec.model_validate(spec)
    return yaml.safe_dump(spec, sort_keys=False, allow_unicode=True, width=100)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: calibrate_cli DATA_ROOT OUT.yaml", file=sys.stderr)
        return 2
    Path(argv[1]).write_text(render(Path(argv[0])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
