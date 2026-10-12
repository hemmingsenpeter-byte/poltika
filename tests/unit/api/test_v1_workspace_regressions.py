"""Regressions for durable workspace context, provenance and coded validation."""

from __future__ import annotations

import csv
import io
import json
from copy import deepcopy
from datetime import UTC, datetime
from decimal import Decimal
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi.testclient import TestClient
from openpyxl import load_workbook
from pydantic import ValidationError

from poltika.api import v1_scenarios
from poltika.api.household import HouseholdCalculationRequest, record_from_request
from poltika.api.main import app
from poltika.api.v1_blocks import CalculationChainBlock, ModelRefBlock, Notice
from poltika.api.v1_scenarios import ScenarioItem
from poltika.engines.assurance.provenance import build_combined_provenance_report
from poltika.scenarios.record import CodeIdentity, canonical_json, result_payload, run_scenario
from poltika.scenarios.store import StoredRun
from tests.conftest import AS_POLICY_DIR, WFF_POLICY_DIR
from tests.unit.api.test_household_api import _payload
from tests.unit.api.test_v1_scenarios import _blocks
from tests.unit.api.test_workbench_api import _reform

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


def test_unresolved_component_steps_defer_to_the_reported_outcome() -> None:
    payload = _payload()
    payload["as_claimant_is_wff_claimant_or_partner"] = "unknown"
    request = HouseholdCalculationRequest.model_validate(payload)
    run = run_scenario(
        record_from_request(request),
        WFF_POLICY_DIR,
        AS_POLICY_DIR,
        code=CodeIdentity("0.1.0", None, None, None),
    )
    report = build_combined_provenance_report(run, WFF_POLICY_DIR, AS_POLICY_DIR)
    (component,) = report["accommodation_supplement"]["components"]
    assert component["outcome"] == "needs_review"
    assert component["steps"] and not component["rules_applied"]
    blocks = v1_scenarios._household_provenance_blocks(report)
    notice = next(
        b for b in blocks if isinstance(b, Notice) and b.id == "superseded_accommodation_supplement"
    )
    assert "reported outcome" in notice.text
    assert "combined checks" not in notice.text


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


# Synthetic transport regressions: values below are not statutory expectations.
RETAINED_SID = "a" * 64
RETAINED_RID = "b" * 64
RETAINED_OPTION_RID = "c" * 64
RETAINED_UNKNOWN_ID = "d" * 64


def _retained_table(table_id: str, *, exact: bool = False) -> dict[str, Any]:
    return {
        "type": "table",
        "id": table_id,
        "title": table_id,
        "columns": [
            {"id": "label", "label": "Label", "kind": "text"},
            {"id": "amount", "label": "Amount", "kind": "money"},
            {"id": "count", "label": "Households", "kind": "count"},
            {"id": "share", "label": "Share", "kind": "share"},
        ],
        "rows": [
            [
                "Retained household" if exact else "Retained aggregate",
                "1234.567",
                "1234567",
                "12.345",
            ],
            ["Unresolved", "needs_review", "not calculated", None],
        ],
        "notes": ["Synthetic transport fixture."],
    }


def _retained_list(block_id: str) -> dict[str, Any]:
    return {"type": "list", "id": block_id, "title": block_id, "items": ["Retained fixture."]}


@pytest.fixture
def retained_reform(monkeypatch: pytest.MonkeyPatch) -> SimpleNamespace:
    first = {
        **_reform("1234.567", "retained_reform-first"),
        "description": "First retained_reform option.",
    }
    first["overrides"].append(
        {
            "policy_id": "accommodation_supplement",
            "parameter_id": "test_parameter",
            "operation": "add",
            "value": "2.345",
        }
    )
    second = {
        **_reform("1.2345", "retained_reform-second"),
        "description": "Second retained_reform option.",
    }
    second["overrides"][0]["operation"] = "multiply"
    options = [{"label": "Retained A", "reform": first}, {"label": "Retained B", "reform": second}]
    definition = {"law_baseline_date": "2000-01-01", "options": options}
    created_at = datetime(2000, 1, 1, tzinfo=UTC)
    scenario = SimpleNamespace(
        scenario_id=RETAINED_SID,
        title="Retained title",
        description="Retained description.",
        definition=definition,
        created_at=created_at,
    )
    payload = {
        "scenario": {"name": scenario.title, "version": None, "status": "draft"},
        "runs": [{"label": "Retained A", "run_id": RETAINED_OPTION_RID, "reproducible": False}],
        "law_baseline": "Retained synthetic baseline",
        "population_label": "Synthetic transport fixture — not an estimate for New Zealand",
        "synthetic": True,
        "headline": [
            {
                "measure_id": "family_tax_credit",
                "measure": "Retained measure",
                "option": "Retained A",
                "unit": "NZD per tax year",
                "change_total": "98765.4321",
                "mean_change": "1234.567",
                "better_off": "1234567",
                "worse_off": "2",
                "no_material_change": "3",
                "not_calculated": "4",
            }
        ],
        "tabs": [
            {
                "id": "fiscal",
                "title": "Fiscal",
                "status": "active",
                "blocks": [
                    {
                        "type": "horizon",
                        "id": "horizon",
                        "title": "Years",
                        "years": [
                            {"label": "Fixture year", "modelled": True, "note": "Retained period."},
                        ],
                    },
                    _retained_table("fiscal_components"),
                    _retained_table("fiscal_coverage"),
                ],
            },
            {
                "id": "households",
                "title": "Households",
                "status": "active",
                "blocks": [
                    _retained_table("winners_losers_family_tax_credit"),
                    _retained_table("worked_examples", exact=True),
                ],
            },
            {
                "id": "assumptions",
                "title": "Assumptions",
                "status": "active",
                "blocks": [
                    _retained_table("parameters_changed", exact=True),
                    _retained_table("parameters_used", exact=True),
                    _retained_list("decisions"),
                    _retained_list("limitations"),
                    _retained_list("run_identity"),
                    _retained_table("policy_artifacts", exact=True),
                ],
            },
        ],
    }
    results = {
        "workbench": payload,
        "distribution": [_retained_table("distribution_family_tax_credit_decile")],
        "context": {
            "law_baseline": payload["law_baseline"],
            "reference_period": "Retained fixture period",
            "policy_versions": {"fixture_policy": "retained_reform-version"},
            "population_label": payload["population_label"],
            "synthetic": True,
        },
    }
    run = SimpleNamespace(
        scenario_id=RETAINED_SID,
        run_id=RETAINED_RID,
        created_at=created_at,
        results=results,
        results_sha256="e" * 64,
        manifest=None,  # a run stored before migration 0003
    )
    store = SimpleNamespace(
        get_reform_scenario=lambda sid: scenario if sid == RETAINED_SID else None,
        get_reform_run=lambda rid: run if rid == RETAINED_RID else None,
        runs_of=lambda sid: [run] if sid == RETAINED_SID else [],
    )
    monkeypatch.setattr(v1_scenarios, "_store", lambda: store)
    monkeypatch.setattr(v1_scenarios, "_evidence_blocks", list)
    monkeypatch.setattr(v1_scenarios, "_models", lambda _: ModelRefBlock(id="models", models=[]))
    monkeypatch.setattr(
        v1_scenarios, "meta", lambda: SimpleNamespace(build=SimpleNamespace(commit=None))
    )

    def cannot_compute(*args: Any, **kwargs: Any) -> None:
        pytest.fail("Reading a retained_reform scenario must not run a live calculation")

    for name in ("execute_reform", "payload_and_options", "distribution_tables"):
        monkeypatch.setattr(v1_scenarios, name, cannot_compute)
    return SimpleNamespace(scenario=scenario, run=run, payload=payload, original=deepcopy(results))


def test_definition_preserves_complete_retained_settings(retained_reform: SimpleNamespace) -> None:
    response = client.get(f"/api/v1/scenarios/{RETAINED_SID}/definition")
    assert response.status_code == 200, response.text
    assert response.json() == {
        "title": retained_reform.scenario.title,
        "description": retained_reform.scenario.description,
        "options": retained_reform.scenario.definition["options"],
    }
    assert retained_reform.run.results == retained_reform.original


def test_retained_definition_that_no_longer_validates_is_a_coded_503(
    retained_reform: SimpleNamespace,
) -> None:
    retained_reform.scenario.definition["options"] = [{"label": "", "reform": {}}]
    response = client.get(f"/api/v1/scenarios/{RETAINED_SID}/definition")
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "scenario_storage_unavailable"


def test_a_new_run_of_a_retained_reform_that_no_longer_validates_is_a_coded_503(
    retained_reform: SimpleNamespace,
) -> None:
    retained_reform.scenario.definition["options"] = [{"label": "Option A", "reform": {}}]
    response = client.post(f"/api/v1/scenarios/{RETAINED_SID}/runs")
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "scenario_storage_unavailable"


def test_validation_error_outside_retained_data_is_not_a_storage_fault(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Only the sites that re-validate stored data may report a coded 503."""

    class _Store:
        def list_scenarios(self, *_: object) -> None:
            ScenarioItem.model_validate({})

    monkeypatch.setattr(v1_scenarios, "_store", lambda: _Store())
    with pytest.raises(ValidationError):
        TestClient(app, raise_server_exceptions=True).get("/api/v1/scenarios")


def test_unknown_definition_is_a_coded_404(retained_reform: SimpleNamespace) -> None:
    response = client.get(f"/api/v1/scenarios/{RETAINED_UNKNOWN_ID}/definition")
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "scenario_not_found"


@pytest.mark.parametrize("suffix", ["export.xlsx", "export/fiscal_components.csv"])
def test_exports_read_retained_values_without_computing(
    retained_reform: SimpleNamespace, suffix: str
) -> None:
    response = client.get(f"/api/v1/scenarios/{RETAINED_SID}/runs/{RETAINED_RID}/{suffix}")
    assert response.status_code == 200, response.text
    if suffix.endswith(".xlsx"):
        assert (
            response.headers["content-type"]
            == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        workbook = load_workbook(io.BytesIO(response.content))
        assert RETAINED_OPTION_RID in workbook["Summary"]["A2"].value
        fiscal_rows = list(workbook["Fiscal"].values)
        row = next(row for row in fiscal_rows if row[0] == "Retained aggregate")
        assert Decimal(str(row[1])) == Decimal(
            retained_reform.payload["tabs"][0]["blocks"][1]["rows"][0][1]
        )
        assert row[2] == 1234567
        assert any(row[1] == "needs_review" for row in fiscal_rows)
    else:
        assert response.headers["content-type"].startswith("text/csv")
        rows = list(csv.reader(io.StringIO(response.text)))
        assert RETAINED_OPTION_RID in rows[0][0]
        table = retained_reform.payload["tabs"][0]["blocks"][1]
        assert rows[1] == [column["label"] for column in table["columns"]]
        assert rows[2] == table["rows"][0]
        assert rows[3] == ["Unresolved", "needs_review", "not calculated", ""]
    assert "attachment" in response.headers["content-disposition"]
    assert retained_reform.run.results == retained_reform.original


@pytest.mark.parametrize("suffix", ["export.xlsx", "export/fiscal_components.csv"])
@pytest.mark.parametrize(
    "sid,rid", [(RETAINED_UNKNOWN_ID, RETAINED_RID), (RETAINED_SID, RETAINED_UNKNOWN_ID)]
)
def test_exports_require_run_ownership(
    retained_reform: SimpleNamespace, suffix: str, sid: str, rid: str
) -> None:
    response = client.get(f"/api/v1/scenarios/{sid}/runs/{rid}/{suffix}")
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "run_not_found"


@pytest.mark.parametrize("suffix", ["export.xlsx", "export/fiscal_components.csv"])
def test_exports_of_a_run_without_workbench_results_are_coded(
    retained_reform: SimpleNamespace, suffix: str
) -> None:
    del retained_reform.run.results["workbench"]
    response = client.get(f"/api/v1/scenarios/{RETAINED_SID}/runs/{RETAINED_RID}/{suffix}")
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "scenario_storage_unavailable"


def test_workspace_of_a_run_without_workbench_results_is_coded(
    retained_reform: SimpleNamespace,
) -> None:
    del retained_reform.run.results["workbench"]
    response = client.get(f"/api/v1/scenarios/{RETAINED_SID}/runs/{RETAINED_RID}")
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "scenario_storage_unavailable"


def test_a_missing_stored_table_is_a_coded_404(retained_reform: SimpleNamespace) -> None:
    response = client.get(
        f"/api/v1/scenarios/{RETAINED_SID}/runs/{RETAINED_RID}/export/missing_table.csv"
    )
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "table_not_found"


def test_population_precision_changes_only_aggregate_metadata(
    retained_reform: SimpleNamespace,
) -> None:
    response = client.get(f"/api/v1/scenarios/{RETAINED_SID}/runs/{RETAINED_RID}")
    assert response.status_code == 200, response.text
    workspace = response.json()
    aggregate_tables = [
        _blocks(workspace, "overview")["headline"],
        _blocks(workspace, "fiscal")["fiscal_components"],
        _blocks(workspace, "fiscal")["fiscal_coverage"],
        _blocks(workspace, "distribution")["winners_losers_family_tax_credit"],
        _blocks(workspace, "distribution")["distribution_family_tax_credit_decile"],
    ]
    for table in aggregate_tables:
        assert all(
            column["precision"]
            == ("household_rule" if column["kind"] == "text" else "population_estimate")
            for column in table["columns"]
        )
    for tab, table_id in [
        ("overview", "parameters_changed"),
        ("distribution", "worked_examples"),
        ("assumptions", "parameters_changed"),
        ("technical", "parameters_used"),
    ]:
        table = _blocks(workspace, tab)[table_id]
        assert {column["precision"] for column in table["columns"]} == {"household_rule"}
        assert table["rows"][0][1] == "1234.567"
    assert (
        _blocks(workspace, "fiscal")["fiscal_components"]["rows"]
        == retained_reform.payload["tabs"][0]["blocks"][1]["rows"]
    )
    assert (
        _blocks(workspace, "overview")["headline_family_tax_credit"]["values"][0]["value"]
        == "98765.4321"
    )
    assert retained_reform.run.results == retained_reform.original
