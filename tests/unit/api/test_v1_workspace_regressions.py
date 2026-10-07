"""Regressions for durable workspace context, provenance and coded validation."""

from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi.testclient import TestClient

from poltika.api import v1_scenarios
from poltika.api.household import HouseholdCalculationRequest, record_from_request
from poltika.api.main import app
from poltika.api.v1_blocks import CalculationChainBlock
from poltika.engines.assurance.provenance import build_combined_provenance_report
from poltika.scenarios.record import CodeIdentity, canonical_json, result_payload, run_scenario
from poltika.scenarios.store import StoredRun
from tests.conftest import AS_POLICY_DIR, WFF_POLICY_DIR
from tests.unit.api.test_household_api import _payload

client = TestClient(app)


@pytest.mark.parametrize(
    ("method", "path", "kwargs"),
    [
        ("POST", "/api/v1/scenarios", {"json": {}}),
        ("POST", "/api/v1/scenarios", {"content": "{"}),
        ("GET", "/api/v1/scenarios?limit=0", {}),
        ("GET", "/api/v1/scenarios?kind=unknown", {}),
        ("GET", "/api/v1/scenarios/not-an-id", {}),
    ],
)
def test_scenario_validation_errors_follow_the_declared_contract(
    method: str, path: str, kwargs: dict[str, Any]
) -> None:
    response = client.request(method, path, **kwargs)
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "invalid_scenario"
    assert isinstance(response.json()["detail"]["message"], str)


def test_legacy_validation_keeps_its_response() -> None:
    response = client.post("/household/calculate", json={})
    assert response.status_code == 422
    assert isinstance(response.json()["detail"], list)


@pytest.mark.parametrize(
    "url",
    [
        "postgresql+psycopg:/localhost/poltika",
        "postgresql+psycopg://localhost:notaport/poltika",
    ],
)
@pytest.mark.parametrize(
    "method,path,kwargs",
    [
        ("GET", "/api/v1/scenarios", {}),
        (
            "POST",
            "/api/v1/scenarios",
            {
                "json": {
                    "title": "Test",
                    "options": [
                        {
                            "label": "A",
                            "reform": {
                                "reform_id": "test",
                                "overrides": [
                                    {
                                        "policy_id": "working_for_families",
                                        "parameter_id": "family_tax_credit_abatement_threshold",
                                        "operation": "set",
                                        "value": "50000",
                                    }
                                ],
                            },
                        }
                    ],
                }
            },
        ),
        ("POST", f"/api/v1/scenarios/{'0' * 64}/runs", {}),
    ],
)
def test_malformed_postgresql_configuration_is_a_coded_storage_error(
    url: str, method: str, path: str, kwargs: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("POLTIKA_DATABASE_URL", url)
    response = client.request(method, path, **kwargs)
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "scenario_storage_unavailable"
    assert url not in response.text


@pytest.fixture(scope="module")
def original_run() -> StoredRun:
    request = HouseholdCalculationRequest.model_validate(_payload())
    run = run_scenario(
        record_from_request(request),
        WFF_POLICY_DIR,
        AS_POLICY_DIR,
        code=CodeIdentity("0.1.0", None, None, None),
    )
    return StoredRun(
        result_id=run.result_id,
        scenario_id=run.scenario_id,
        record=run.record,
        manifest=json.loads(canonical_json(run.manifest)),
        result=result_payload(run.result),
        reproducible=False,
        provenance=build_combined_provenance_report(run, WFF_POLICY_DIR, AS_POLICY_DIR),
    )


def test_household_context_and_calculation_steps_describe_the_original_run(
    original_run: StoredRun, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(v1_scenarios.config, "BASELINE_LABEL", "A later baseline")
    monkeypatch.setattr(v1_scenarios, "meta", lambda: (_ for _ in ()).throw(AssertionError()))
    store = SimpleNamespace(get_run=lambda _: original_run)
    workspace = v1_scenarios._household_workspace(
        store, original_run.scenario_id, original_run.result_id, []
    )
    assert workspace.context is not None
    assert workspace.context.policy_versions == {
        "working_for_families": original_run.record.requested_wff_policy_version,
        "accommodation_supplement": original_run.record.requested_as_policy_version,
    }
    assert "A later baseline" not in workspace.context.law_baseline
    assert all(
        p in workspace.context.reference_period
        for p in (
            *original_run.result["wff_period"],
            *original_run.result["accommodation_supplement_period"],
        )
    )
    chains = [
        b for tab in workspace.tabs for b in tab.blocks if isinstance(b, CalculationChainBlock)
    ]
    actual = [
        (s.component_id, s.step_id, s.rule_id, s.result, s.inputs) for b in chains for s in b.steps
    ]
    assert original_run.provenance is not None
    expected = [
        (
            component["component_id"],
            step["step_id"],
            step["rule_id"],
            step["result"],
            {key: str(value) for key, value in step["inputs"].items()},
        )
        for policy in ("working_for_families", "accommodation_supplement")
        for component in original_run.provenance[policy]["components"]
        for step in component["steps"]
    ]
    assert actual == expected and actual
    audit = next(tab for tab in workspace.tabs if tab.id == "audit")
    assert {"original_sources_working_for_families", "rules_family_tax_credit"} <= {
        block.id for block in audit.blocks
    }
    unresolved_rules = next(b for b in audit.blocks if b.id == "rules_in_work_tax_credit")
    assert "not calculated" in unresolved_rules.notes[0]
    assert "combined checks" not in unresolved_rules.notes[0]


def test_legacy_household_provenance_is_explicitly_unavailable() -> None:
    blocks = v1_scenarios._household_provenance_blocks(None)
    assert blocks[0].tone == "unavailable"
    assert "not retained" in blocks[0].text


def test_reform_context_reads_the_retained_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(v1_scenarios, "meta", lambda: (_ for _ in ()).throw(AssertionError()))
    payload = {
        "law_baseline": "Retained baseline",
        "synthetic": True,
        "population_label": "Retained population",
        "tabs": [
            {
                "id": "fiscal",
                "blocks": [
                    {
                        "id": "horizon",
                        "years": [
                            {"label": "Retained period", "note": "Original dates", "modelled": True}
                        ],
                    }
                ],
            },
            {
                "id": "assumptions",
                "blocks": [
                    {"id": "parameters_used", "rows": [["Retained policy", "Retained version"]]}
                ],
            },
        ],
    }
    context = v1_scenarios._context(payload)
    assert context.law_baseline == "Retained baseline"
    assert context.reference_period == "Retained period: Original dates"
    assert context.policy_versions == {"Retained policy": "Retained version"}
