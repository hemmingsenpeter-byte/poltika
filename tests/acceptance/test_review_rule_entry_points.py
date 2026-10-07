"""Every agent and contributor entry point carries the same review rule.

The shared paragraph is deliberately copied into nine entry points (ADR-0020),
so an agent that reads only one of them still gets the whole rule. This test
keeps the copies identical rather than deduplicating them."""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

SHARED_RULE = (
    "Independent review uses the other model from the author where practicable. "
    "Same-model review is supporting evidence and cannot clear a cross-model gate. "
    "Author preflight is a separate pass. Every preflight and review records its "
    "exact base and final head SHA. Any later commit, fix, rebase or integration "
    "of main invalidates final-head clearance and requires renewed review, except a "
    "mechanical main update as {where}. For mixed authorship, record coverage by "
    "semantic change and commit; each model's changes need the other model's review "
    "where cross-model review is required."
)
ENTRY_POINTS = (
    ".claude/agents/poltika-reviewer.md",
    ".claude/skills/pr-review-preflight/SKILL.md",
    ".claude/skills/pr-review/SKILL.md",
    "AGENTS.md",
    "BUILD_PLAN.md",
    "CLAUDE.md",
    "CONTRIBUTING.md",
    "doctrine/review-doctrine.md",
)
ADR = "adr/0020-delegated-acceptance.md"
STRICT = (
    "only as a full `pr-review` with primary-source re-derivation, recorded "
    "against the final head"
)
WEAKER_WORDINGS = (
    "if it independently derives the contract",
    "if it meets the independent-review standard",
)


def _prose(name: str) -> str:
    return " ".join((ROOT / name).read_text(encoding="utf-8").split())


@pytest.mark.parametrize("name", ENTRY_POINTS)
def test_entry_point_carries_the_shared_rule_and_mechanical_exemption(name: str) -> None:
    assert SHARED_RULE.format(where="ADR-0020 defines it") in _prose(name)


def test_adr0020_carries_the_rule_and_defines_the_mechanical_update() -> None:
    prose = _prose(ADR)
    assert SHARED_RULE.format(where="defined below") in prose
    definition = prose.split("**Mechanical main update (Pete, 6 October 2026).**", 1)[1]
    assert "has no conflict" in definition
    assert "git patch-id --stable" in definition
    assert "renews every gate" in definition


@pytest.mark.parametrize("name", ("CONTRIBUTING.md", "doctrine/review-doctrine.md"))
def test_single_claude_pass_uses_the_strict_standard(name: str) -> None:
    prose = _prose(name)
    assert STRICT in prose
    for weaker in WEAKER_WORDINGS:
        assert weaker not in prose
