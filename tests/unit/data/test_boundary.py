"""v0.2 Task 1.7: the data dependency boundary (`REPOSITORY_STRUCTURE.md`).

Nothing outside `poltika.data` imports it, and nothing outside it names a
path under `data/`. Downstream code reads canonical variables through
`poltika.semantics.variables.CanonicalContext` only. A future composition
root that builds a `DataContext` gets an explicit entry in `ALLOWED`, in
the PR that creates it.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

SRC = Path(__file__).resolve().parents[3] / "src" / "poltika"
DATA_PACKAGE = SRC / "data"
ALLOWED: set[str] = {"scenarios/microsim/calibrate_cli.py", "scenarios/microsim/crossval_cli.py"}
_DATA_PATH = re.compile(r"""["'](?:\.\./)*data/(?:raw|processed|metadata)\b""")
# A path built with `/`: Path("data") / "raw", and the like.
_DATA_JOIN = re.compile(r"""["']data["']\s*\)?\s*/\s*["'](?:raw|processed|metadata)["']""")


def _outside_modules() -> list[Path]:
    return [p for p in SRC.rglob("*.py") if DATA_PACKAGE not in p.parents]


def _imports(path: Path) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names.add(node.module)
        elif isinstance(node, ast.ImportFrom) and node.level > 0:
            # A relative import, resolved against the module's own package.
            package = path.relative_to(SRC.parent).with_suffix("").parts[: -node.level]
            names.add(".".join((*package, node.module) if node.module else package))
    return names


def test_nothing_outside_the_data_layer_imports_it() -> None:
    offenders = sorted(
        str(p.relative_to(SRC))
        for p in _outside_modules()
        if str(p.relative_to(SRC)) not in ALLOWED
        and any(n == "poltika.data" or n.startswith("poltika.data.") for n in _imports(p))
    )
    assert offenders == []


def test_nothing_outside_the_data_layer_names_a_data_path() -> None:
    offenders = sorted(
        str(p.relative_to(SRC))
        for p in _outside_modules()
        if _DATA_PATH.search(p.read_text()) or _DATA_JOIN.search(p.read_text())
    )
    assert offenders == []


def test_the_data_layer_does_not_reach_downstream() -> None:
    forbidden = (
        "poltika.engines",
        "poltika.policy",
        "poltika.scenarios",
        "poltika.api",
        "poltika.llm",
    )
    offenders = sorted(
        f"{p.relative_to(SRC)}: {n}"
        for p in DATA_PACKAGE.rglob("*.py")
        for n in _imports(p)
        if n.startswith(forbidden)
    )
    assert offenders == []


def test_the_checks_would_catch_a_violation(tmp_path: Path) -> None:
    bad = tmp_path / "bad.py"
    bad.write_text('from poltika.data.context import DataContext\nopen("data/raw/x.csv")\n')
    assert "poltika.data.context" in _imports(bad)
    assert _DATA_PATH.search(bad.read_text())
