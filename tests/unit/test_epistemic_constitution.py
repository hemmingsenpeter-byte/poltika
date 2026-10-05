"""Task 1.2 (the AI gate): the constitution names a gate for each kind of
artifact AI drafts, and every file path it names as a check exists. It does
not judge whether a check is sufficient; the table's Gap column says that."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONSTITUTION = ROOT / "doctrine" / "epistemic-constitution.md"

REQUIRED_KINDS = [
    "Source catalogue entry",
    "Specification rule",
    "Decision record",
    "Policy parameter value",
    "Protected expected value",
    "Fact-catalogue question",
    "Interaction edge",
    "Dataset snapshot",
    "Assumption",
    "Estimate",
    "LLM output",
    "Engine or code",
]


def _gate_rows() -> list[list[str]]:
    text = CONSTITUTION.read_text()
    section = text.split("## The AI gate (Task 1.2)\n", 1)[1].split("\n## ", 1)[0]
    rows = [line for line in section.splitlines() if line.startswith("| ")]
    cells = [[c.strip() for c in line.strip("|").split("|")] for line in rows]
    return [c for c in cells if len(c) == 4 and not set(c[0]) <= {"-", " "}][1:]


def test_every_kind_of_artifact_has_a_row_with_nonempty_cells() -> None:
    rows = _gate_rows()
    for kind in REQUIRED_KINDS:
        row = next((r for r in rows if r[0].startswith(kind)), None)
        assert row is not None, f"no AI-gate row for: {kind}"
        assert row[1] and row[2] and row[3], f"incomplete AI-gate row for: {kind}"


def test_every_named_check_exists_or_the_row_says_none_yet() -> None:
    for kind, _promotion, enforced, _gap in _gate_rows():
        paths = re.findall(r"`([A-Za-z0-9_./*-]+\.(?:py|yml|yaml|md|json))`", enforced)
        if not enforced.startswith("None yet"):
            assert paths, f"{kind}: names no check by file path and does not say none yet"
        # A none-yet row may still name today's related files; they must exist too.
        for path in paths:
            assert list(ROOT.glob(path)), f"{kind}: {path} does not exist"
