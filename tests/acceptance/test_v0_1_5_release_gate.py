"""v0.1.5 Sprint 2 (S2.4): the release gate in BUILD_PLAN_v0_1_5.md, one
test per row. Rows only people can satisfy (an external pilot) skip with a
reason until docs/pilot/V0_1_5_PILOT_FINDINGS.md records them, so a green
run with no skips means the gate is met."""

from __future__ import annotations

import json
import re
from dataclasses import fields
from datetime import date
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from poltika.api.main import app
from poltika.engines.assurance.evidence import evidence_coverage
from poltika.engines.assurance.explanation import explain, verify
from poltika.engines.simulator.outcome import ComponentResult
from poltika.scenarios.record import CodeIdentity, canonical_json, result_payload, run_scenario
from tests.conftest import AS_POLICY_DIR, WFF_POLICY_DIR
from tests.unit.scenarios.test_scenario_record import GOLDEN_PATH, record_from_yaml

ROOT = Path(__file__).resolve().parents[2]
CLIENT = TestClient(app)
CODE = CodeIdentity("gate", None, None, None)
LOOKUP = date(2026, 6, 1)


def _pilot_runs() -> list[tuple[str, dict[str, Any]]]:
    return [
        (case["id"], CLIENT.post("/household/calculate", json=case["request"]).json())
        for case in CLIENT.get("/analyst/pilot-cases").json()
    ]


def _golden_components() -> list[tuple[str, str, ComponentResult]]:
    import yaml

    out = []
    for household in yaml.safe_load(GOLDEN_PATH.read_text())["households"]:
        result = run_scenario(record_from_yaml(household), WFF_POLICY_DIR, AS_POLICY_DIR, code=CODE).result
        for f in fields(result.wff):
            out.append((household["id"], f.name, getattr(result.wff, f.name)))
        out.append((household["id"], "accommodation_supplement", result.accommodation_supplement))
    return out


GOLDEN = _golden_components()
PILOT = _pilot_runs()


def test_gate_v0_1_results_unchanged() -> None:
    """Every golden result equals the frozen v0.1 snapshot."""
    import yaml

    frozen = json.loads((ROOT / "tests/fixtures/golden_results_v0_1.json").read_text())
    for household in yaml.safe_load(GOLDEN_PATH.read_text())["households"]:
        run = run_scenario(record_from_yaml(household), WFF_POLICY_DIR, AS_POLICY_DIR, code=CODE)
        assert json.loads(canonical_json(result_payload(run.result))) == frozen[household["id"]]["result"]


@pytest.mark.parametrize("policy_dir", [WFF_POLICY_DIR, AS_POLICY_DIR], ids=["wff", "as"])
def test_gate_protected_values_sourced_and_rules_evidence_linked(policy_dir: Path) -> None:
    assert evidence_coverage(policy_dir)["problems"] == []


def test_gate_calculated_path_rules_are_evidence_linked() -> None:
    rules = {r["rule_id"]: r for d in (WFF_POLICY_DIR, AS_POLICY_DIR) for r in evidence_coverage(d)["rules"]}
    for _, _, result in GOLDEN:
        assert result.trace is not None
        for step in result.trace.steps:
            assert rules[step.rule_id]["cites_primary_legislation"], step.step_id


def test_gate_explanations_consistent_with_results() -> None:
    for household, component, result in GOLDEN:
        assert verify(explain(component, result), result) == [], (household, component)
    for case_id, body in PILOT:
        for component, explanation in body["explanations"].items():
            result = body["accommodation_supplement"] if component == "accommodation_supplement" else body["wff"][component]
            assert (explanation["outcome"], explanation["value"]) == (result["outcome"], result["value"]), case_id


def test_gate_temporal_evidence() -> None:
    for _, component, result in GOLDEN:
        for e in explain(component, result).evidence:
            if e.effective_from:
                assert date.fromisoformat(e.effective_from) <= LOOKUP
                assert e.effective_to is None or LOOKUP < date.fromisoformat(e.effective_to)


def test_gate_missing_inputs_never_defaulted_and_needs_review_structured() -> None:
    for case_id, body in PILOT:
        for result in [*body["wff"].values(), body["accommodation_supplement"]]:
            if result["outcome"] != "calculated":
                assert result["value"] is None and result["code"], case_id
            if result["outcome"] == "needs_review":
                assert result["reason"], case_id


def test_gate_trace_available_for_every_calculated_result() -> None:
    for household, component, result in GOLDEN:
        if result.outcome == "calculated" and result.value:
            assert result.trace is not None and result.trace.steps, (household, component)


def test_gate_assumptions_surfaced() -> None:
    for _, component, result in GOLDEN:
        explanation = explain(component, result)
        assert result.trace is not None
        assert len(explanation.assumptions) == len(result.trace.inputs)


def test_gate_reproducible() -> None:
    import yaml

    for household in yaml.safe_load(GOLDEN_PATH.read_text())["households"]:
        record = record_from_yaml(household)
        first = run_scenario(record, WFF_POLICY_DIR, AS_POLICY_DIR, code=CODE)
        second = run_scenario(record, WFF_POLICY_DIR, AS_POLICY_DIR, code=CODE)
        assert first.result_id == second.result_id
        steps = lambda r: [c.trace.steps for c in (*[getattr(r.result.wff, f.name) for f in fields(r.result.wff)], r.result.accommodation_supplement)]
        assert steps(first) == steps(second)


FINDINGS = ROOT / "docs/pilot/V0_1_5_PILOT_FINDINGS.md"


def test_gate_no_open_p0_or_p1_findings() -> None:
    rows = [line for line in FINDINGS.read_text().splitlines() if re.match(r"^\| F\d+ \|", line)]
    open_blockers = [
        row for row in rows
        if (cells := [c.strip() for c in row.strip("|").split("|")])[3] in ("P0", "P1")
        and not cells[5].startswith("Fixed")
    ]
    assert not open_blockers, "open P0/P1 findings:\n" + "\n".join(open_blockers)


def test_gate_external_pilot_user() -> None:
    match = re.search(r"^- Pilot user:[ \t]*(\S.*)$", FINDINGS.read_text(), re.MULTILINE)
    if not match:
        pytest.skip("release gate not yet met: no external pilot user recorded in V0_1_5_PILOT_FINDINGS.md")


def test_gate_independent_review_complete() -> None:
    from tests.acceptance.review_queue import open_reviews

    pending = open_reviews("v0.1.5")
    if pending:
        pytest.skip(f"release gate not yet met: awaiting independent review {', '.join(pending)}")
