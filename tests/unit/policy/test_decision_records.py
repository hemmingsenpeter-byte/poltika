"""Task 1.2 (the AI gate): an interpretation is Pete's decision, and a
record shows it. Mechanical shape only: this cannot show that Pete decided,
only that each record names him as owner, dates itself, and states the
ambiguity and the evidence (`doctrine/review-doctrine.md`)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

SPECS = Path(__file__).resolve().parents[3] / "policy_specs"
RECORDS = sorted(SPECS.glob("*/decisions/DEC-*.md"))


def test_decision_records_exist() -> None:
    assert RECORDS


@pytest.mark.parametrize("record", RECORDS, ids=lambda p: f"{p.parent.parent.name}/{p.name}")
def test_record_names_pete_a_date_the_ambiguity_and_the_evidence(record: Path) -> None:
    text = record.read_text()
    owner = re.search(r"^\*\*Decision owner:\*\*\s*(.+)$", text, re.MULTILINE)
    assert owner and "Pete" in owner.group(1), f"{record.name}: decision owner must name Pete"
    assert re.search(r"^\*\*Date:\*\*\s*\S+", text, re.MULTILINE), f"{record.name}: no date"
    assert re.search(r"^## Ambiguity\s*$", text, re.MULTILINE), f"{record.name}: no Ambiguity section"
    assert re.search(r"^## Evidence considered\s*$", text, re.MULTILINE), (
        f"{record.name}: no Evidence considered section"
    )
