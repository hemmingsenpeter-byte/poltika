"""Task 30.4: frozen golden-household results as regression fixtures.

tests/fixtures/golden_results_v0_1.json freezes, for each golden household,
its scenario identity, the full deterministic result payload (outcomes,
values, reasons, periods, disagreements) and the SHA-256 of every policy
file the run bound. A changed output fails with an attribution:
- which bound policy, source, specification or decision file changed; or
- that none did, so the change came from calculator or runner code.

This follows ARCHITECTURE.md's change-attribution rule. No external dataset
exists for v0.1 (Tasks 10a/22a), so the policy-file hashes play the
snapshot role.

Regenerate deliberately, never to make a failing test pass without
understanding why:
    POLTIKA_UPDATE_GOLDEN_SNAPSHOT=1 uv run --extra dev pytest tests/regression/test_golden_result_snapshot.py
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pytest
import yaml

from poltika.scenarios.record import CodeIdentity, canonical_json, result_payload, run_scenario
from tests.conftest import AS_POLICY_DIR, WFF_POLICY_DIR
from tests.unit.scenarios.test_scenario_record import GOLDEN_PATH, record_from_yaml

SNAPSHOT_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "golden_results_v0_1.json"
# Code identity is excluded from the frozen payload: a new commit alone must
# not count as an output change. It is fixed here only to build a run.
_ANY_CODE = CodeIdentity("snapshot", None, None, None)


def _current() -> dict[str, Any]:
    snapshot: dict[str, Any] = {}
    for household in yaml.safe_load(GOLDEN_PATH.read_text())["households"]:
        run = run_scenario(record_from_yaml(household), WFF_POLICY_DIR, AS_POLICY_DIR, code=_ANY_CODE)
        snapshot[household["id"]] = {
            "scenario_id": run.scenario_id,
            "policy_files": dict(run.manifest.policy_files),
            "result": json.loads(canonical_json(result_payload(run.result))),
        }
    return snapshot


def _attribution(frozen: dict[str, Any], now: dict[str, Any]) -> str:
    changed = sorted(
        path
        for path in set(frozen["policy_files"]) | set(now["policy_files"])
        if frozen["policy_files"].get(path) != now["policy_files"].get(path)
    )
    if frozen["scenario_id"] != now["scenario_id"]:
        return "the golden household's own inputs changed (scenario identity differs)"
    if changed:
        return "bound policy artifacts changed: " + ", ".join(changed)
    return "no bound policy artifact changed -- the change comes from calculator or runner code"


def test_golden_results_match_the_frozen_snapshot() -> None:
    current = _current()
    if os.environ.get("POLTIKA_UPDATE_GOLDEN_SNAPSHOT") == "1":
        SNAPSHOT_PATH.write_text(json.dumps(current, sort_keys=True, indent=2) + "\n")
        pytest.skip("golden snapshot regenerated")
    frozen = json.loads(SNAPSHOT_PATH.read_text())
    assert sorted(frozen) == sorted(current), "golden household set changed; regenerate deliberately"
    mismatches = [
        f"{household_id}: {_attribution(frozen[household_id], current[household_id])}"
        for household_id in sorted(current)
        if frozen[household_id]["result"] != current[household_id]["result"]
    ]
    assert not mismatches, "golden results changed:\n" + "\n".join(mismatches)


def test_attribution_names_the_changed_artifact() -> None:
    files: dict[str, str] = {"a/policy.yaml": "1", "a/sources.yaml": "2"}
    frozen: dict[str, Any] = {"scenario_id": "s", "policy_files": files}
    assert "a/policy.yaml" in _attribution(frozen, {**frozen, "policy_files": {**files, "a/policy.yaml": "9"}})
    assert "calculator or runner code" in _attribution(frozen, dict(frozen))
    assert "inputs changed" in _attribution(frozen, {**frozen, "scenario_id": "t"})
