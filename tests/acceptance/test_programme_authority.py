"""Prevent agents from following competing or archived master programmes."""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
AUTHORITY = re.compile(r"<!-- poltika:master-build-order=([^ ]+) -->")
OPERATIONAL_FILES = (
    "AGENTS.md",
    "CLAUDE.md",
    "README.md",
    "BUILD_PLAN_PROGRAMME.md",
    "PROGRAMME_STATUS.md",
    "ROADMAP.md",
)


@pytest.mark.parametrize("name", OPERATIONAL_FILES)
def test_operational_files_declare_the_same_live_master(name: str) -> None:
    targets = AUTHORITY.findall((ROOT / name).read_text())
    assert targets == ["BUILD_PLAN_PROGRAMME.md"], (
        f"{name} must declare exactly one current master at the root"
    )
    assert (ROOT / targets[0]).is_file()


@pytest.mark.parametrize("name", ("AGENTS.md", "CLAUDE.md", "README.md"))
def test_agent_entry_points_do_not_restore_the_superseded_order(name: str) -> None:
    prose = (ROOT / name).read_text()
    assert "33 steps with Phase 0 foundations" not in prose
    assert "ADR-0019: the master build order" not in prose
    assert "what's being built now, in what order, and v0.1" not in prose


def test_adr0019_marks_sequencing_superseded_without_losing_the_record() -> None:
    prose = (ROOT / "adr/0019-decision-instrument-programme.md").read_text()
    status = prose.split("## Context", 1)[0]
    assert "superseded for programme sequencing" in status
    assert "0021-economist-first-pilot-programme.md" in status
    assert "## Decision" in prose
    assert "## Consequences" in prose
