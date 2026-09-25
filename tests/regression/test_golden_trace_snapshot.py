"""v0.1.5 Task 7.2: frozen golden traces and explanations.

tests/fixtures/golden_traces_v0_1_5.json freezes, for each golden
household and component, the semantic structure of how the result was
reached -- outcome, value, reason code and category, missing facts, the
ordered calculation steps (id, rule, result), the parameters consulted,
and the explanation summary -- rather than prose punctuation. Any change
to a trace or explanation then shows up as a failing, attributable diff.

Regenerate deliberately, never to make a failing test pass without
understanding why:
    POLTIKA_UPDATE_GOLDEN_TRACES=1 uv run --extra dev pytest tests/regression/test_golden_trace_snapshot.py
"""

from __future__ import annotations

import json
import os
from dataclasses import fields
from pathlib import Path
from typing import Any

import pytest
import yaml

from poltika.engines.assurance.explanation import explain
from poltika.engines.simulator.outcome import ComponentResult
from poltika.engines.simulator.trace import plain
from poltika.scenarios.record import CodeIdentity, run_scenario
from tests.conftest import AS_POLICY_DIR, WFF_POLICY_DIR
from tests.unit.scenarios.test_scenario_record import GOLDEN_PATH, record_from_yaml

SNAPSHOT_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "golden_traces_v0_1_5.json"


def _component(component_id: str, result: ComponentResult) -> dict[str, Any]:
    assert result.trace is not None
    return {
        "outcome": result.outcome,
        "value": plain(result.value),
        "code": result.code,
        "category": result.category,
        "missing_facts": list(result.missing_facts),
        "steps": [[s.step_id, s.rule_id, plain(s.result)] for s in result.trace.steps],
        "parameters": [p.parameter_id for p in result.trace.parameters],
        "summary": explain(component_id, result).summary,
    }


def _current() -> dict[str, Any]:
    snapshot: dict[str, Any] = {}
    for household in yaml.safe_load(GOLDEN_PATH.read_text())["households"]:
        run = run_scenario(record_from_yaml(household), WFF_POLICY_DIR, AS_POLICY_DIR, code=CodeIdentity("0", None, None, None))
        wff = run.result.wff
        components = {f.name: getattr(wff, f.name) for f in fields(wff)}
        components["accommodation_supplement"] = run.result.accommodation_supplement
        snapshot[household["id"]] = {cid: _component(cid, r) for cid, r in components.items()}
    return snapshot


def test_golden_traces_match_the_frozen_snapshot() -> None:
    current = _current()
    if os.environ.get("POLTIKA_UPDATE_GOLDEN_TRACES") == "1":
        SNAPSHOT_PATH.write_text(json.dumps(current, sort_keys=True, indent=2) + "\n")
        pytest.skip("golden traces regenerated")
    frozen = json.loads(SNAPSHOT_PATH.read_text())
    assert sorted(frozen) == sorted(current), "golden household set changed; regenerate deliberately"
    changed = [
        f"{household}/{component}: {sorted(k for k in current[household][component] if current[household][component][k] != frozen[household][component].get(k))}"
        for household in sorted(current)
        for component in sorted(current[household])
        if current[household][component] != frozen[household].get(component)
    ]
    assert not changed, "golden traces changed:\n" + "\n".join(changed)
